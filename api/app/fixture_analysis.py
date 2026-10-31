"""Offline authored-fixture analysis. Not imported by the public product route."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import Field

from app.analysis import analyze_fields, check_deadline, redact
from app.results import AnalysisResult, Coverage, ResultModel, Score
from app.schemas import ReviewInput
from app.source_sample import SourceSample


class FixtureCoverage(Coverage):
    source_declaration: Literal["authored_fixture"] = "authored_fixture"


class FixtureAnalysis(AnalysisResult):
    schema_version: Literal["2"] = "2"
    origin: Literal["authored_fixture"] = "authored_fixture"
    coverage: FixtureCoverage


class FixtureReport(ResultModel):
    schema_version: Literal["2"] = "2"
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"
    ingestion_version: Literal["rt-fixture-analysis-0.1.0"] = "rt-fixture-analysis-0.1.0"
    status: Literal["complete", "partial", "empty"]
    stop_reason: Literal["exhausted", "row_limit", "page_limit", "source_window", "empty"]
    product_ref: Literal["p1"] = "p1"
    product_title: str = Field(max_length=300, repr=False)
    variant_scope: Literal["combined", "unknown"]
    fetched_records: int = Field(ge=0, le=500)
    overlap_records: int = Field(ge=0, le=500)
    analyzed_reviews: int = Field(ge=0, le=500)
    pages_fetched: int = Field(ge=1, le=5)
    window_started_at: datetime
    window_finished_at: datetime
    selection_order: Literal["newest_first"] = "newest_first"
    available_reviews: None = None
    count_scope: Literal["unknown"] = "unknown"
    analysis: FixtureAnalysis | None


@dataclass(frozen=True)
class _FixtureSubmission:
    reviews: tuple[ReviewInput, ...]
    origin: Literal["authored_fixture"] = "authored_fixture"


@dataclass(frozen=True)
class _FixtureBatch:
    submission: _FixtureSubmission
    warnings: tuple = ()

    @property
    def review_refs(self):
        return tuple(f"r{i}" for i in range(1, len(self.submission.reviews) + 1))


def analyze_fixture_sample(sample: SourceSample, deadline: float) -> bytes:
    """Validate and serialize one bounded fixture envelope inside the caller's worker."""
    from app.ingestion import ReviewInputError

    check_deadline(deadline)
    analysis = None
    if sample.reviews:
        fields = analyze_fields(_FixtureBatch(_FixtureSubmission(sample.reviews)), deadline)
        fields["schema_version"] = "2"
        score = fields["score"]
        fields["score"] = Score(
            status="insufficient_evidence" if score.reason_codes else "withheld",
            value=None,
            reason_codes=["public_score_not_validated", *score.reason_codes],
            evaluated_signal_ids=score.evaluated_signal_ids,
        )
        fields["limitations"].insert(
            0, "Authored synthetic fixtures only; no live source evidence."
        )
        fields["limitations"].insert(
            1, "Redaction counts cover this analysis pass over an already masked fixture sample."
        )
        analysis = FixtureAnalysis(**fields)
    title = redact(sample.product.title, {"email": 0, "phone": 0})
    if len(title) > 300:
        raise ReviewInputError("source_limit", "Source sample exceeds the allowed limit.", 502)
    report = FixtureReport(
        status=sample.status,
        stop_reason=sample.stop_reason,
        product_title=title,
        variant_scope=sample.variant_scope,
        fetched_records=sample.fetched_records,
        overlap_records=sample.overlap_records,
        analyzed_reviews=len(sample.reviews),
        pages_fetched=sample.pages_fetched,
        window_started_at=sample.window_started_at,
        window_finished_at=sample.window_finished_at,
        analysis=analysis,
    )
    body = report.model_dump_json().encode("utf-8")
    if len(body) > 2_097_152:
        raise ReviewInputError("response_limit", "Result exceeds the response limit.", 413)
    check_deadline(deadline)
    return body
