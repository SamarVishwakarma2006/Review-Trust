"""Deterministic experimental signals, derived evidence and conservative privacy masking."""

import re
import time
import unicodedata
from collections import defaultdict

from app.ingestion import IngestedReviews, ReviewInputError
from app.results import (
    AnalysisResult,
    Confidence,
    Coverage,
    DisplayReview,
    FieldCoverage,
    Finding,
    FractionEvidence,
    PhraseMatch,
    ReviewEvidence,
    Score,
    SignalCoverage,
    WarningInfo,
)
from app.schemas import REVIEW_FIELDS

INCENTIVE_PHRASES = (
    "in exchange for a review",
    "received this product for free",
    "received a free product",
    "discount in exchange for",
)
_EMAIL = re.compile(r"(?<![\w.+-])[\w.+-]{1,64}@[a-z0-9-]{1,63}(?:\.[a-z0-9-]{1,63})+", re.I)
_PHONE = re.compile(r"(?<!\w)\+?[0-9][0-9 ().-]{5,40}[0-9](?!\w)")
_PLACEHOLDER = re.compile(r"\[(?:EMAIL|PHONE)_REDACTED\]")
_WORDS = re.compile(r"[^\W_]+")
_INCENTIVE_PATTERNS = [
    (phrase, re.compile(r"(?<!\w)" + r"\s+".join(map(re.escape, phrase.split())) + r"(?!\w)", re.I))
    for phrase in INCENTIVE_PHRASES
]


def check_deadline(deadline: float) -> None:
    if time.monotonic() >= deadline:
        raise ReviewInputError("analysis_timeout", "Analysis exceeded its execution budget.", 503)


def redact(text: str, counts: dict[str, int]) -> str:
    text = unicodedata.normalize("NFKC", text)

    def email(match: re.Match) -> str:
        counts["email"] += 1
        return "[EMAIL_REDACTED]"

    def phone(match: re.Match) -> str:
        if 7 <= sum(character.isdigit() for character in match[0]) <= 15:
            counts["phone"] += 1
            return "[PHONE_REDACTED]"
        return match[0]

    return _PHONE.sub(phone, _EMAIL.sub(email, text))


def _text_finding(signal_id, eligible, total, matching, evidence, explanation):
    available = eligible >= 10
    refs = list(dict.fromkeys(ref for item in evidence for ref in item.review_refs))
    return Finding(
        signal_id=signal_id,
        value=FractionEvidence(
            matching_reviews=matching, eligible_reviews=eligible, fraction=matching / eligible
        )
        if available
        else None,
        assessment=("observed" if matching else "not_observed") if available else "unavailable",
        explanation=explanation
        if available
        else "At least 10 reviews with five word tokens are required.",
        supporting_review_refs=refs if available else [],
        evidence=evidence if available else [],
        matching_review_count=matching if available else 0,
        references_truncated=available and matching > len(refs),
        required_fields=["text"],
        coverage=SignalCoverage(
            eligible=eligible, evaluated=eligible if available else 0, total=total
        ),
        availability_reason=None if available else "insufficient_eligible_text",
    )


def analyze(batch: IngestedReviews, deadline: float) -> AnalysisResult:
    check_deadline(deadline)
    total = len(batch.submission.reviews)
    counts = {"email": 0, "phone": 0}
    display = []
    groups = defaultdict(list)
    incentives = []
    eligible = 0
    for ref, review in zip(batch.review_refs, batch.submission.reviews, strict=True):
        check_deadline(deadline)
        text = redact(review.text, counts)
        title = redact(review.title, counts) if review.title is not None else None
        display.append(DisplayReview(ref=ref, text=text, title=title))
        normalized = " ".join(_PLACEHOLDER.sub(" ", text).casefold().split())
        if len(_WORDS.findall(normalized)) < 5:
            continue
        eligible += 1
        groups[normalized].append(ref)
        matches = []
        for phrase, pattern in _INCENTIVE_PATTERNS:
            match = pattern.search(text)
            if match:
                matches.append(PhraseMatch(phrase=phrase, start=match.start(), end=match.end()))
        if matches:
            incentives.append(ReviewEvidence(review_refs=[ref], matches=matches))
    duplicate_count = 0
    pairs = []
    for refs in groups.values():
        check_deadline(deadline)
        if len(refs) > 1:
            duplicate_count += len(refs)
            for ref in refs[1:]:
                if len(pairs) < 10:
                    pairs.append(ReviewEvidence(review_refs=[refs[0], ref]))
    findings = [
        _text_finding(
            "text_repetition",
            eligible,
            total,
            duplicate_count,
            pairs,
            f"{duplicate_count} of {eligible} eligible reviews share exact normalized text "
            "with another review. Templates and duplicate ingestion are alternative explanations; "
            "are not evaluated in this version.",
        ),
        _text_finding(
            "incentive_language",
            eligible,
            total,
            len(incentives),
            incentives[:20],
            f"{len(incentives)} of {eligible} eligible reviews mention a listed incentive phrase. "
            "Mentions, quotations and negations do not establish participation or manipulation.",
        ),
    ]
    for signal_id, required in (
        ("review_burst", ["timestamp"]),
        ("rating_distribution", ["rating"]),
        ("rating_text_disagreement", ["rating", "text"]),
    ):
        # No eligibility claim for a contextual method that has not been implemented.
        findings.append(
            Finding(
                signal_id=signal_id,
                value=None,
                assessment="unavailable",
                explanation="This signal is not implemented in this methodology version.",
                supporting_review_refs=[],
                evidence=[],
                matching_review_count=0,
                references_truncated=False,
                required_fields=required,
                coverage=SignalCoverage(eligible=0, evaluated=0, total=total),
                availability_reason="not_implemented",
            )
        )
    evaluated = [finding.signal_id for finding in findings if finding.availability_reason is None]
    reasons = []
    if total < 20:
        reasons.append("too_few_reviews")
    if eligible < 20:
        reasons.append("too_few_eligible_reviews")
    if eligible * 5 < total * 4:
        reasons.append("low_text_coverage")
    if len(evaluated) < 2:
        reasons.append("scoring_signal_unavailable")
    # Exact half-up rounding of 100 * (1 - max(d, i)); avoids float half-boundary errors.
    value = (
        (200 * (eligible - max(duplicate_count, len(incentives))) + eligible) // (2 * eligible)
        if not reasons
        else None
    )
    field_coverage = {}
    for name in sorted(REVIEW_FIELDS):
        present = sum(getattr(review, name) is not None for review in batch.submission.reviews)
        field_coverage[name] = FieldCoverage(present=present, missing=total - present)
    result = AnalysisResult(
        origin=batch.submission.origin,
        review_count=total,
        score=Score(
            status="insufficient_evidence" if reasons else "experimental",
            value=value,
            reason_codes=reasons,
            evaluated_signal_ids=evaluated,
        ),
        coverage=Coverage(
            total_reviews=total,
            fields=field_coverage,
            signals={finding.signal_id: finding.coverage for finding in findings},
            evaluated_signal_ids=evaluated,
            unavailable_signal_ids=[
                finding.signal_id for finding in findings if finding.availability_reason is not None
            ],
            source_declaration=batch.submission.origin,
            redactions=counts,
        ),
        confidence=Confidence(),
        findings=findings,
        reviews=display,
        warnings=[
            WarningInfo(code=warning.code, column_positions=list(warning.column_positions))
            for warning in batch.warnings
        ],
        limitations=[
            "Experimental, unvalidated pattern index; not a probability of authenticity "
            "or product quality.",
            "Only the submitted unverified subset is analyzed; it may not represent "
            "all product reviews.",
            "A score of 100 means neither included pattern was observed in eligible text, "
            "not verified authenticity.",
            "Exact repetition and a limited English phrase list miss many patterns "
            "and can produce false positives.",
            "Email/phone masking is incomplete and may hide benign numbers; "
            "remove personal details before submitting.",
            "Names and other personal details may remain in review text; "
            "no full anonymization is claimed.",
            "Masking and normalization may remove distinctions between reviews; "
            "redaction placeholders are excluded from matching.",
            "Timing, rating distribution, sentiment disagreement and "
            "near-duplicate similarity are unavailable.",
        ],
    )
    check_deadline(deadline)
    return result
