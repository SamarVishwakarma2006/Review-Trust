import time

import pytest

from app.analysis import analyze
from app.ingestion import ReviewInputError, validate_submission
from app.results import METHODOLOGY_VERSION, AnalysisResult


def reviews(count=20):
    return [{"text": f"The screen and battery work for sample {index}."} for index in range(count)]


def result(rows):
    batch = validate_submission(
        {
            "schema_version": "1",
            "category": "electronics",
            "language": "en",
            "origin": "paste",
            "reviews": rows,
        }
    )
    return analyze(batch, time.monotonic() + 10)


def test_complete_result_is_explicitly_experimental_and_context_signals_are_unavailable():
    output = result(reviews())
    assert output.score.value == 100
    assert output.score.status == "experimental"
    assert output.methodology_version == METHODOLOGY_VERSION
    assert output.experimental is True
    assert output.confidence.level is None
    assert output.confidence.status == "not_validated"
    assert output.coverage.evaluated_signal_ids == ["text_repetition", "incentive_language"]
    assert len(output.coverage.unavailable_signal_ids) == 3
    for finding in output.findings[2:]:
        assert finding.value is None
        assert finding.assessment == "unavailable"
        assert finding.availability_reason in {
            "insufficient_dated_reviews",
            "insufficient_rated_reviews",
            "insufficient_supported_polarity",
        }
        assert finding.supporting_review_refs == []
        assert finding.coverage.evaluated == 0
    assert AnalysisResult.model_validate_json(output.model_dump_json()) == output


def test_exact_repetition_and_incentives_follow_max_aggregation_not_addition():
    rows = reviews()
    for index in range(5):
        rows[index]["text"] = "This repeated review describes a useful screen."
    assert result(rows).score.value == 75
    for index in range(5, 13):
        rows[index]["text"] += " I received this product for free."
    output = result(rows)
    assert output.score.value == 60
    assert [finding.value.matching_reviews for finding in output.findings[:2]] == [5, 8]
    assert [finding.value.fraction for finding in output.findings[:2]] == [0.25, 0.4]


@pytest.mark.parametrize("count,expected", [(0, 100), (2, 90), (5, 75), (10, 50), (20, 0)])
def test_increasing_repetition_cannot_improve_score(count, expected):
    rows = reviews()
    for index in range(count):
        rows[index]["text"] = "These identical words describe the same device."
    assert result(rows).score.value == expected


def test_half_up_rounding_uses_exact_arithmetic():
    rows = reviews(200)
    for index in range(177):
        rows[index]["text"] = "These identical words describe the same device."
    assert result(rows).score.value == 12  # 100 * (1 - 177/200) = 11.5


@pytest.mark.parametrize("count", [1, 9, 10, 19])
def test_small_submissions_withhold_score_and_keep_signal_availability_separate(count):
    output = result(reviews(count))
    assert output.score.status == "insufficient_evidence"
    assert output.score.value is None
    assert "too_few_reviews" in output.score.reason_codes
    assert output.findings[0].availability_reason == (
        "insufficient_eligible_text" if count < 10 else None
    )


def test_eligibility_and_coverage_gates_are_enforced_at_boundaries():
    assert result(reviews() + [{"text": "Good"}] * 5).score.value == 100
    low_coverage = result(reviews() + [{"text": "Good"}] * 6)
    assert low_coverage.score.value is None
    assert low_coverage.score.reason_codes == ["low_text_coverage"]
    too_few = result(reviews(19) + [{"text": "Good"}])
    assert too_few.score.value is None
    assert "too_few_eligible_reviews" in too_few.score.reason_codes
    assert too_few.coverage.signals["text_repetition"].eligible == 19


def test_metadata_removal_and_input_order_do_not_change_score():
    rows = reviews()
    for index in range(5):
        rows[index]["text"] = "The same text appears on several reviews."
    with_metadata = [
        row | {"rating": 5, "timestamp": "2020-01-01", "verified_purchase": True} for row in rows
    ]
    assert result(with_metadata).score == result(rows).score == result(list(reversed(rows))).score
    coverage = result(with_metadata).coverage
    assert coverage.fields["rating"].present == 20
    assert coverage.fields["verified_purchase"].present == 20
    assert coverage.signals["rating_distribution"].evaluated == 20


def test_evidence_references_resolve_and_repetition_pairs_are_actual_matches():
    output = result([{"text": "A very useful review of this device."}] * 30)
    finding = output.findings[0]
    by_ref = {review.ref: review.text for review in output.reviews}
    assert finding.matching_review_count == 30
    assert finding.references_truncated is True
    assert len(finding.supporting_review_refs) <= 20
    for item in finding.evidence:
        first, second = item.review_refs
        assert first != second
        assert by_ref[first] == by_ref[second]
    assert set(finding.supporting_review_refs) <= by_ref.keys()


def test_incentive_evidence_records_real_spans_and_does_not_infer_participation():
    rows = reviews()
    rows[0]["text"] = "I never RECEIVED this product for free; this is a quotation."
    output = result(rows)
    finding = output.findings[1]
    assert finding.matching_review_count == 1
    evidence = finding.evidence[0]
    match = evidence.matches[0]
    assert evidence.review_refs == ["r1"]
    assert output.reviews[0].text[match.start : match.end].casefold() == match.phrase
    assert "do not establish participation" in finding.explanation


def test_normalization_and_privacy_masking_happen_before_matching_and_output():
    rows = [
        {
            "text": "Ｆｉｖｅ useful words describe this device. Contact user@example.com",
            "title": "Call +1 (202) 555-0123",
            "product_id": "SECRET-PRODUCT",
            "source_id": "SECRET-SOURCE",
        }
    ] * 20
    output = result(rows)
    encoded = output.model_dump_json()
    for secret in ("user@example.com", "202) 555-0123", "SECRET-PRODUCT", "SECRET-SOURCE"):
        assert secret not in encoded
    assert output.coverage.redactions == {"email": 20, "phone": 20}
    assert output.reviews[0].text.startswith("Five useful")
    assert output.reviews[0].title == "Call [PHONE_REDACTED]"
    assert output.score.value == 0


def test_redaction_placeholders_do_not_supply_word_tokens_or_create_scored_blank_reviews():
    output = result([{"text": "one two three user@example.com +1 202 555 0123"}] * 20)
    assert output.coverage.signals["text_repetition"].eligible == 0
    assert output.score.value is None
    assert output.findings[0].value is None
    assert output.findings[0].supporting_review_refs == []


def test_expired_budget_returns_no_partial_result():
    batch = validate_submission(
        {
            "schema_version": "1",
            "category": "electronics",
            "language": "en",
            "origin": "paste",
            "reviews": reviews(),
        }
    )
    with pytest.raises(ReviewInputError) as raised:
        analyze(batch, time.monotonic() - 1)
    assert raised.value.status_code == 503
