"""Explicit public result/error contracts; no raw identifiers or reviewer names."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

METHODOLOGY_VERSION = "rt-patterns-0.1.0-experimental"
SignalId = Literal[
    "text_repetition",
    "incentive_language",
    "review_burst",
    "rating_distribution",
    "rating_text_disagreement",
]


class ResultModel(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class SignalCoverage(ResultModel):
    eligible: int = Field(ge=0)
    evaluated: int = Field(ge=0)
    total: int = Field(ge=1)


class FractionEvidence(ResultModel):
    matching_reviews: int = Field(ge=0)
    eligible_reviews: int = Field(ge=1)
    fraction: float = Field(ge=0, le=1)


class PhraseMatch(ResultModel):
    phrase: str
    start: int = Field(ge=0)
    end: int = Field(ge=1)


class ReviewEvidence(ResultModel):
    review_refs: list[str] = Field(min_length=1, max_length=2)
    matches: list[PhraseMatch] = Field(default_factory=list, max_length=4)


class Finding(ResultModel):
    signal_id: SignalId
    value: FractionEvidence | None
    assessment: Literal["observed", "not_observed", "unavailable"]
    explanation: str
    supporting_review_refs: list[str] = Field(max_length=20)
    evidence: list[ReviewEvidence] = Field(max_length=20)
    matching_review_count: int = Field(ge=0)
    references_truncated: bool
    required_fields: list[str]
    coverage: SignalCoverage
    availability_reason: Literal["insufficient_eligible_text", "not_implemented"] | None
    methodology_version: Literal["rt-patterns-0.1.0-experimental"] = METHODOLOGY_VERSION


class Score(ResultModel):
    status: Literal["experimental", "insufficient_evidence"]
    value: int | None = Field(ge=0, le=100)
    reason_codes: list[
        Literal[
            "too_few_reviews",
            "too_few_eligible_reviews",
            "low_text_coverage",
            "scoring_signal_unavailable",
        ]
    ]
    evaluated_signal_ids: list[SignalId]


class Confidence(ResultModel):
    status: Literal["not_validated"] = "not_validated"
    level: None = None
    explanation: str = "Confidence has not been validated; inspect evidence coverage instead."


class FieldCoverage(ResultModel):
    present: int = Field(ge=0)
    missing: int = Field(ge=0)


class Coverage(ResultModel):
    total_reviews: int = Field(ge=1)
    fields: dict[str, FieldCoverage]
    signals: dict[SignalId, SignalCoverage]
    evaluated_signal_ids: list[SignalId]
    unavailable_signal_ids: list[SignalId]
    source_declaration: Literal["paste", "csv"]
    scope: Literal["unverified_subset"] = "unverified_subset"
    redactions: dict[Literal["email", "phone"], int]


class DisplayReview(ResultModel):
    ref: str
    text: str = Field(repr=False)
    title: str | None = Field(default=None, repr=False)


class WarningInfo(ResultModel):
    code: Literal["unverified_subset", "mixed_product_coverage", "unmapped_columns"]
    column_positions: list[int]


class AnalysisResult(ResultModel):
    schema_version: Literal["1"] = "1"
    methodology_version: Literal["rt-patterns-0.1.0-experimental"] = METHODOLOGY_VERSION
    experimental: Literal[True] = True
    origin: Literal["paste", "csv"]
    scope: Literal["submitted_subset"] = "submitted_subset"
    review_count: int = Field(ge=1, le=500)
    score: Score
    coverage: Coverage
    confidence: Confidence
    findings: list[Finding]
    reviews: list[DisplayReview] = Field(repr=False)
    warnings: list[WarningInfo]
    limitations: list[str]


class ErrorField(ResultModel):
    row: int | None
    field: str
    code: str


class ErrorDetail(ResultModel):
    code: str
    message: str
    fields: list[ErrorField] = Field(max_length=20)
    total_errors: int = Field(ge=0)
    request_id: str


class ErrorResponse(ResultModel):
    error: ErrorDetail
