"""Versioned descriptive signals. No learned classifier or authenticity inference."""

import math
import re
from collections import Counter
from collections.abc import Callable
from datetime import date, datetime

from app.results import (
    AvailabilityReason,
    BurstEvidence,
    DisplayReview,
    Finding,
    FractionEvidence,
    PhraseMatch,
    RatingBin,
    RatingEvidence,
    ReviewEvidence,
    SignalCoverage,
    SignalId,
)
from app.schemas import ReviewInput

WORDS = re.compile(r"[^\W_]+")
FEATURE_LIMIT = 20_000
SIMILARITY_THRESHOLD = 0.90
LEXICON_VERSION = "rt-en-polarity-0.1"
POSITIVE = frozenset({"good", "great", "excellent", "superb", "amazing", "perfect"})
NEGATIVE = frozenset({"bad", "poor", "terrible", "awful", "broken", "useless"})
ABSTAIN = frozenset(
    {
        "no",
        "not",
        "never",
        "nor",
        "neither",
        "without",
        "hardly",
        "barely",
        "scarcely",
        "cannot",
        "unless",
        "if",
        "wish",
        "but",
        "however",
        "although",
        "though",
    }
)
_POLARITY_WORDS = re.compile(r"[^\W_]+(?:['’][^\W_]+)?")
_PLACEHOLDER = re.compile(r"\[(?:EMAIL|PHONE)_REDACTED\]")


def repetition(
    rows: list[tuple[str, str]], check: Callable[[], None]
) -> tuple[int, list[ReviewEvidence], bool]:
    """Exact normalized text OR raw-count/smoothed-IDF unigram+bigram cosine.

    No vocabulary pruning: over-cap input makes the whole signal unavailable,
    avoiding artificially high similarity from silently discarded rare terms.
    """
    counts = []
    frequencies: Counter[tuple[str, ...]] = Counter()
    for _, text in rows:
        check()
        words = WORDS.findall(text)
        terms = Counter((word,) for word in words)
        terms.update(zip(words, words[1:]))
        frequencies.update(terms.keys())
        if len(frequencies) > FEATURE_LIMIT:
            return 0, [], True
        counts.append(terms)
    vectors = []
    for terms in counts:
        check()
        weighted = {
            term: n * (math.log((1 + len(rows)) / (1 + frequencies[term])) + 1)
            for term, n in sorted(terms.items())
        }
        norm = math.sqrt(math.fsum(v * v for v in weighted.values()))
        vectors.append({term: v / norm for term, v in weighted.items()})
    matched: set[str] = set()
    evidence = []
    # ponytail: bounded all-pairs sparse comparison (<=124,750); profile before indexing.
    for i, (ref, text) in enumerate(rows):
        for j in range(i + 1, len(rows)):
            check()
            other_ref, other_text = rows[j]
            exact = text == other_text
            small, large = sorted((vectors[i], vectors[j]), key=len)
            similarity = (
                1.0
                if exact
                else min(1.0, math.fsum(v * large.get(term, 0.0) for term, v in small.items()))
            )
            if exact or similarity >= SIMILARITY_THRESHOLD:
                matched.update((ref, other_ref))
                if len(evidence) < 10:
                    evidence.append(
                        ReviewEvidence(
                            review_refs=[ref, other_ref],
                            match_kind="exact" if exact else "tfidf",
                            similarity=similarity,
                        )
                    )
    return len(matched), evidence, False


def contextual_finding(
    signal: SignalId,
    required: list[str],
    eligible: int,
    total: int,
    reason: AvailabilityReason | None,
    value: BurstEvidence | RatingEvidence | FractionEvidence | None,
    matches: list[ReviewEvidence],
    explanation: str,
) -> Finding:
    evidence = matches[:20] if reason is None else []
    return Finding(
        signal_id=signal,
        required_fields=required,
        value=value if reason is None else None,
        assessment="unavailable" if reason else "observed" if matches else "not_observed",
        explanation=explanation,
        availability_reason=reason,
        supporting_review_refs=[e.review_refs[0] for e in evidence],
        evidence=evidence,
        matching_review_count=len(matches) if reason is None else 0,
        references_truncated=reason is None and len(matches) > 20,
        coverage=SignalCoverage(
            eligible=eligible, evaluated=eligible if reason is None else 0, total=total
        ),
    )


def burst(rows: list[ReviewInput], refs: tuple[str, ...], check: Callable[[], None]) -> Finding:
    dated = []
    for ref, row in zip(refs, rows, strict=True):
        check()
        day = row.timestamp.date() if isinstance(row.timestamp, datetime) else row.timestamp
        if day is not None:
            dated.append((day, ref))
    count, total = len(dated), len(rows)
    span = (max(d for d, _ in dated) - min(d for d, _ in dated)).days if dated else 0
    reason = (
        "insufficient_dated_reviews"
        if count < 20
        else (
            "low_timestamp_coverage"
            if count * 5 < total * 4
            else ("insufficient_time_span" if span < 28 else None)
        )
    )
    if reason:
        return contextual_finding(
            "review_burst",
            ["timestamp"],
            count,
            total,
            reason,
            None,
            [],
            f"Timing requires 20 dated reviews, 80% date coverage and a 28-day span; "
            f"received {count}/{total} dated reviews spanning {span} days.",
        )
    ordered = sorted(dated)
    right = 0
    best_count, best_start = 0, ordered[0][0]
    for left, (start, _) in enumerate(ordered):
        check()
        # Ordinals avoid overflow for valid dates near year 9999.
        while right < count and ordered[right][0].toordinal() <= start.toordinal() + 2:
            right += 1
        if right - left > best_count:
            best_count, best_start = right - left, start
    end_ordinal = min(date.max.toordinal(), best_start.toordinal() + 2)
    end = date.fromordinal(end_ordinal)
    observed = best_count * 2 >= count
    matches = [
        ReviewEvidence(review_refs=[ref], timestamp_day=day.isoformat())
        for day, ref in dated
        if observed and best_start <= day <= end
    ]
    value = BurstEvidence(
        matching_reviews=best_count,
        eligible_reviews=count,
        fraction=best_count / count,
        window_start=best_start.isoformat(),
        window_end=end.isoformat(),
        observed_span_days=span,
    )
    return contextual_finding(
        "review_burst",
        ["timestamp"],
        count,
        total,
        None,
        value,
        matches,
        f"The busiest inclusive three-day UTC window, {best_start} to {end}, contains "
        f"{best_count}/{count} dated reviews. The 50% threshold is "
        f"{'met' if observed else 'not met'}. Ties use the earliest observed start day. "
        "Launches, promotions and selected samples can explain timing concentrations.",
    )


def rating_distribution(rows: list[ReviewInput], refs: tuple[str, ...]) -> Finding:
    rated = [
        (ref, row.rating) for ref, row in zip(refs, rows, strict=True) if row.rating is not None
    ]
    count, total = len(rated), len(rows)
    reason = (
        "insufficient_rated_reviews"
        if count < 20
        else ("low_rating_coverage" if count * 5 < total * 4 else None)
    )
    if reason:
        return contextual_finding(
            "rating_distribution",
            ["rating"],
            count,
            total,
            reason,
            None,
            [],
            f"Rating distribution requires 20 ratings and 80% coverage; received {count}/{total}.",
        )
    histogram = Counter(rating for _, rating in rated)
    low = sum(n for rating, n in histogram.items() if rating <= 2)
    high = sum(n for rating, n in histogram.items() if rating >= 4)
    low_observed, high_observed = low * 10 >= 9 * count, high * 10 >= 9 * count
    matches = [
        ReviewEvidence(review_refs=[ref], rating=rating)
        for ref, rating in rated
        if (low_observed and rating <= 2) or (high_observed and rating >= 4)
    ]
    value = RatingEvidence(
        rated_reviews=count,
        histogram=[RatingBin(rating=rating, count=n) for rating, n in sorted(histogram.items())],
        mean=math.fsum(rating for _, rating in rated) / count,
        low_share=low / count,
        high_share=high / count,
    )
    return contextual_finding(
        "rating_distribution",
        ["rating"],
        count,
        total,
        None,
        value,
        matches,
        f"{low}/{count} ratings are at most 2 and {high}/{count} are at least 4; "
        f"mean {value.mean:.4f}. The 90% concentration threshold is "
        f"{'met' if matches else 'not met'}. "
        "Product quality and sample selection can explain this.",
    )


def polarity(text: str) -> tuple[str | None, list[PhraseMatch]]:
    # Preserve display offsets while excluding masking placeholders.
    cleaned = _PLACEHOLDER.sub(lambda m: " " * len(m[0]), text)
    words = _POLARITY_WORDS.findall(cleaned.casefold())
    if (
        set(words) & ABSTAIN
        or any(w.endswith(("n't", "n’t")) for w in words)
        or any(c in cleaned for c in '"“”‘’?')
        or re.search(r"(?<!\w)'|'(?!\w)", cleaned)
        or "/s" in cleaned.casefold()
        or "yeah right" in cleaned.casefold()
    ):
        return None, []
    positive, negative = bool(set(words) & POSITIVE), bool(set(words) & NEGATIVE)
    if positive == negative:
        return None, []
    direction = "positive" if positive else "negative"
    matches = [
        PhraseMatch(phrase=m[0].casefold(), start=m.start(), end=m.end())
        for m in _POLARITY_WORDS.finditer(cleaned)
        if m[0].casefold() in POSITIVE | NEGATIVE
    ][:4]
    return direction, matches


def disagreement(
    rows: list[ReviewInput], display: list[DisplayReview], check: Callable[[], None]
) -> Finding:
    eligible = 0
    matches = []
    for row, shown in zip(rows, display, strict=True):
        check()
        if row.rating is None:
            continue
        direction, cues = polarity(shown.text)
        if direction is None:
            continue
        eligible += 1
        if (row.rating <= 2 and direction == "positive") or (
            row.rating >= 4 and direction == "negative"
        ):
            matches.append(
                ReviewEvidence(
                    review_refs=[shown.ref], rating=row.rating, polarity=direction, matches=cues
                )
            )
    reason = "insufficient_supported_polarity" if eligible < 20 else None
    value = (
        FractionEvidence(
            matching_reviews=len(matches),
            eligible_reviews=eligible,
            fraction=len(matches) / eligible,
        )
        if reason is None
        else None
    )
    explanation = (
        f"{len(matches)}/{eligible} rated reviews with supported wording disagree with the "
        "lexicon direction (rating <=2 with positive words, or >=4 with negative words). "
        if reason is None
        else f"At least 20 rated reviews with supported wording are required; found {eligible}. "
    )
    return contextual_finding(
        "rating_text_disagreement",
        ["rating", "text"],
        eligible,
        len(rows),
        reason,
        value,
        matches,
        explanation + f"Lexicon {LEXICON_VERSION}; negated, mixed, quoted, "
        "conditional and unsupported wording abstains. "
        "Sarcasm and aspect differences remain limitations. "
        "This is a contextual rule, not a validated sentiment or deception classifier.",
    )
