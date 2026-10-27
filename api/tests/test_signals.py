"""Synthetic methodology fixtures; these verify mechanics, not authenticity accuracy."""

import math
from datetime import date, timedelta

import pytest
from test_analysis import result, reviews

from app import signals
from app.ingestion import ReviewInputError


def finding(rows, index):
    return result(rows).findings[index]


def dates(days):
    return [
        row | {"timestamp": (date(2020, 1, 1) + timedelta(days=day)).isoformat()}
        for row, day in zip(reviews(len(days)), days, strict=True)
    ]


def test_near_duplicate_punctuation_and_added_word_pairs_have_real_cosines():
    text = " ".join(f"term{i}" for i in range(80))
    rows = reviews()
    rows[0]["text"] = text
    rows[1]["text"] = text + " indeed"
    rows[2]["text"] = text + "!"
    output = result(rows)
    f = output.findings[0]
    assert f.value.matching_reviews == 3
    assert output.score.value == 85
    assert all(e.match_kind == "tfidf" for e in f.evidence)
    assert all(0.90 <= e.similarity <= 1 for e in f.evidence)
    assert f.evidence[0].review_refs == ["r1", "r2"]
    assert result(list(reversed(rows))).score == output.score


def test_cosine_matches_independent_two_document_formula_and_inclusive_boundary(monkeypatch):
    # Shared a-b terms have IDF 1, unique c/d terms have 1 + log(3/2).
    rows = [("r1", "a b c"), ("r2", "a b d")]
    expected = 3 / (3 + 2 * (1 + math.log(3 / 2)) ** 2)
    monkeypatch.setattr(signals, "SIMILARITY_THRESHOLD", expected - 1e-12)
    n, evidence, limited = signals.repetition(rows, lambda: None)
    assert not limited and n == 2
    assert evidence[0].similarity == pytest.approx(expected, abs=1e-14)
    monkeypatch.setattr(signals, "SIMILARITY_THRESHOLD", expected + 1e-12)
    assert signals.repetition(rows, lambda: None)[0] == 0
    # Exactly equal vectors give cosine 1, accepted at an inclusive threshold of 1.
    monkeypatch.setattr(signals, "SIMILARITY_THRESHOLD", 1.0)
    assert signals.repetition([("r1", "a b c"), ("r2", "a b c")], lambda: None)[0] == 2


def test_feature_limit_withholds_score_even_when_context_signals_are_available(monkeypatch):
    monkeypatch.setattr(signals, "FEATURE_LIMIT", 5)
    rows = [
        r | {"rating": 5, "timestamp": "2020-01-01", "text": r["text"] + " excellent"}
        for r in reviews()
    ]
    rows[-1]["timestamp"] = "2020-02-01"
    output = result(rows)
    assert output.score.value is None
    assert output.score.reason_codes == ["scoring_signal_unavailable"]
    assert output.findings[0].availability_reason == "feature_limit"
    assert output.findings[0].value is None
    assert output.findings[0].evidence == []
    assert output.score.evaluated_signal_ids == ["incentive_language"]
    assert len(output.coverage.evaluated_signal_ids) == 4


def test_actual_feature_cap_is_bounded_and_returns_no_partial_repetition():
    rows = [{"text": " ".join(f"word{r}x{c}" for c in range(300))} for r in range(40)]
    output = result(rows)
    assert output.findings[0].availability_reason == "feature_limit"
    assert output.score.value is None


def test_deadline_is_checked_inside_pair_loop():
    calls = 0

    def check():
        nonlocal calls
        calls += 1
        if calls == 43:  # 20 vocabulary + 20 vector checks, then comparisons.
            raise ReviewInputError(
                "analysis_timeout", "Analysis exceeded its execution budget.", 503
            )

    with pytest.raises(ReviewInputError):
        signals.repetition(
            [(f"r{i}", "five identical words in this review") for i in range(20)], check
        )
    assert calls == 43


@pytest.mark.parametrize(
    "days,assessment,start,end,matches",
    [
        ([0] * 9 + [2] + list(range(10, 20)), "unavailable", None, None, 0),
        ([0] * 9 + [2] + list(range(20, 30)), "observed", "2020-01-01", "2020-01-03", 10),
        ([0] * 9 + [3] + list(range(20, 30)), "not_observed", "2020-01-01", "2020-01-03", 0),
        ([0] * 10 + [28] * 10, "observed", "2020-01-01", "2020-01-03", 10),
        (list(range(0, 60, 3)), "not_observed", "2020-01-01", "2020-01-03", 0),
    ],
)
def test_burst_span_window_threshold_tie_and_negative(days, assessment, start, end, matches):
    f = finding(dates(days), 2)
    assert f.assessment == assessment
    assert f.matching_review_count == matches
    if start:
        assert f.value.window_start == start
        assert f.value.window_end == end
    else:
        assert f.availability_reason == "insufficient_time_span"


def test_burst_coverage_boundaries_and_timezone_normalization():
    rows = dates([0] * 10 + list(range(20, 30)))
    rows[9]["timestamp"] = "2020-01-04T00:30:00+02:00"  # UTC Jan 3, included.
    assert finding(rows + reviews(5), 2).assessment == "observed"
    assert finding(rows + reviews(6), 2).availability_reason == "low_timestamp_coverage"
    assert finding(rows[:19], 2).availability_reason == "insufficient_dated_reviews"
    evidence = finding(rows, 2).evidence
    assert evidence[-1].timestamp_day == "2020-01-03"
    assert evidence[-1].review_refs == ["r10"]
    assert finding(dates([0] * 19 + [27]), 2).availability_reason == "insufficient_time_span"
    assert finding(dates([0] * 19 + [28]), 2).assessment == "observed"


@pytest.mark.parametrize(
    "ratings,assessment",
    [
        ([4] * 18 + [3.5] * 2, "observed"),
        ([4] * 17 + [3.5] * 3, "not_observed"),
        ([2] * 18 + [2.5] * 2, "observed"),
        ([2] * 17 + [2.5] * 3, "not_observed"),
        ([1, 2, 3, 4, 5] * 4, "not_observed"),
    ],
)
def test_rating_exact_histogram_mean_and_thresholds(ratings, assessment):
    rows = [r | {"rating": rating} for r, rating in zip(reviews(), ratings, strict=True)]
    f = finding(rows, 3)
    assert f.assessment == assessment
    assert sum(b.count for b in f.value.histogram) == 20
    assert f.value.mean == pytest.approx(sum(ratings) / 20)
    assert [b.rating for b in f.value.histogram] == sorted(set(ratings))
    assert all(e.rating in ratings for e in f.evidence)
    assert result(rows).score == result(reviews()).score
    assert finding(rows + reviews(5), 3).availability_reason is None
    assert finding(rows + reviews(6), 3).availability_reason == "low_rating_coverage"
    assert finding(rows[:19], 3).availability_reason == "insufficient_rated_reviews"


@pytest.mark.parametrize(
    "text",
    [
        "not good",
        "never terrible",
        "no good",
        "without great features",
        "isn't excellent",
        "isn’t excellent",
        "good but broken",
        "good and bad",
        "excellent?",
        '"great"',
        "'great'",
        "‘excellent’",
        "If this were good",
        "I wish this was great",
        "yeah right excellent",
        "excellent /s",
        "The screen illuminates the room",
        "goodness",
        "good's",
        "barely good",
    ],
)
def test_polarity_abstains_on_ambiguous_or_unsupported_wording(text):
    assert signals.polarity(text) == (None, [])


@pytest.mark.parametrize(
    "text,rating,assessment",
    [
        ("The display is excellent and very clear.", 2, "observed"),
        ("The display is terrible and very dim.", 4, "observed"),
        ("The display is excellent and very clear.", 4, "not_observed"),
        ("The display is terrible and very dim.", 2, "not_observed"),
        ("The display is excellent and very clear.", 3, "not_observed"),
    ],
)
def test_disagreement_eligibility_threshold_extremes_and_real_spans(text, rating, assessment):
    rows = [{"text": text, "rating": rating}] * 20
    output = result(rows)
    f = output.findings[4]
    assert f.assessment == assessment
    assert f.coverage.eligible == 20
    assert finding(rows[:19], 4).availability_reason == "insufficient_supported_polarity"
    for e in f.evidence:
        for m in e.matches:
            assert output.reviews[0].text[m.start : m.end].casefold() == m.phrase
    # Context has its own eligibility gate; short text does not magically enable the score.
    short = result([{"text": "excellent", "rating": 1}] * 20)
    assert short.findings[4].assessment == "observed"
    assert short.score.value is None
    assert "scoring_signal_unavailable" in short.score.reason_codes


def test_disagreement_masks_before_matching_and_titles_never_supply_polarity():
    output = result(
        [
            {
                "text": "Contact excellent@example.com for details about this display.",
                "title": "excellent",
                "rating": 1,
            }
        ]
        * 20
    )
    assert output.findings[4].coverage.eligible == 0
    assert "excellent@example.com" not in output.model_dump_json()
    assert signals.polarity("[EMAIL_REDACTED] excellent")[1][0].start == 17


def test_evidence_caps_and_matching_counts_for_all_signals():
    rows = [
        {
            "text": "This excellent display received this product for free.",
            "rating": 1,
            "timestamp": "2020-01-01",
        }
    ] * 29
    rows += [
        {
            "text": "This excellent display received this product for free.",
            "rating": 1,
            "timestamp": "2020-02-01",
        }
    ]
    output = result(rows)
    assert output.score.value == 0
    assert output.score.evaluated_signal_ids == ["text_repetition", "incentive_language"]
    for f in output.findings:
        assert f.assessment == "observed"
        assert f.references_truncated
        assert len(f.supporting_review_refs) <= 20
        assert f.matching_review_count >= 29
        assert set(f.supporting_review_refs) <= {r.ref for r in output.reviews}
    assert output.confidence.level is None


def test_maximum_rows_and_aggregate_text_keep_complete_counts():
    text = "A synthetic display works with this useful battery. " * 9
    output = result([{"text": text}] * 500)
    assert output.review_count == 500
    assert output.findings[0].value.matching_reviews == 500
    assert output.score.value == 0


def test_polarity_evidence_uses_the_same_tokens_as_direction():
    text = "😀 good's excellent device"
    direction, cues = signals.polarity(text)
    assert direction == "positive"
    assert [cue.phrase for cue in cues] == ["excellent"]
    assert text[cues[0].start : cues[0].end] == "excellent"
