"""Proposed collected-source v2 output contracts; no collection or route activation."""

from datetime import UTC, datetime
from typing import Annotated, Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, StringConstraints, field_validator, model_validator

from app.results import AnalysisResult, Coverage, ResultModel, Score

Text = Annotated[str, StringConstraints(min_length=1, max_length=300)]


class PublicScore(Score):
    status: Literal["withheld", "insufficient_evidence"]
    value: None = None

    @model_validator(mode="after")
    def withholding_reason(self) -> Self:
        if "public_score_not_validated" not in self.reason_codes:
            raise ValueError("Public score withholding must be disclosed.")
        return self


class CollectedCoverage(Coverage):
    source_declaration: Literal["collected"] = "collected"


class CollectedAnalysis(AnalysisResult):
    schema_version: Literal["2"] = "2"
    origin: Literal["collected"] = "collected"
    coverage: CollectedCoverage
    score: PublicScore


class SourceInfo(ResultModel):
    id: Annotated[str, StringConstraints(pattern=r"^[a-z0-9-]{1,100}$")]
    adapter_version: Annotated[str, StringConstraints(min_length=1, max_length=100)]
    retrieved_at: datetime
    attribution: Text

    @field_validator("retrieved_at")
    @classmethod
    def utc_time(cls, value):
        if value.utcoffset() is None:
            raise ValueError("Timezone required.")
        return value.astimezone(UTC)


class ProductInfo(ResultModel):
    ref: Literal["p1"] = "p1"
    title: Text
    canonical_url: Annotated[str, StringConstraints(min_length=1, max_length=2048)]
    variant: Annotated[str, StringConstraints(min_length=1, max_length=100)] | None = None

    @field_validator("canonical_url")
    @classmethod
    def safe_link(cls, value):
        if not value.isascii() or any(ord(c) <= 32 or ord(c) == 127 for c in value):
            raise ValueError("Invalid canonical link.")
        parsed = urlsplit(value)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
            or any(c in value for c in "\\?#%")
            or parsed.netloc.lower() not in (parsed.hostname, parsed.hostname + ":443")
        ):
            raise ValueError("Invalid canonical link.")
        return value


class CollectionInfo(ResultModel):
    status: Literal["complete", "partial", "empty"]
    stop_reason: Literal["exhausted", "row_limit", "page_limit", "source_window", "empty"]
    fetched_records: int = Field(ge=0, le=500)
    analyzed_reviews: int = Field(ge=0, le=500)
    overlap_records: int = Field(ge=0, le=500)
    pages_fetched: int = Field(ge=0, le=5)
    available_reviews: int | None = Field(default=None, ge=0)
    count_scope: Literal["selected_product", "unknown"] = "unknown"
    selection_order: Literal["newest_first"] = "newest_first"
    variant_scope: Literal["selected_variant", "combined", "unknown"]
    window_started_at: datetime
    window_finished_at: datetime

    @field_validator("window_started_at", "window_finished_at")
    @classmethod
    def utc_time(cls, value):
        return SourceInfo.utc_time(value)

    @model_validator(mode="after")
    def coherent(self) -> Self:
        if self.window_finished_at < self.window_started_at:
            raise ValueError("Invalid collection window.")
        if self.fetched_records != self.analyzed_reviews + self.overlap_records:
            raise ValueError("Inconsistent record counts.")
        if self.fetched_records > 100 * self.pages_fetched:
            raise ValueError("Inconsistent page count.")
        if (self.available_reviews is None) != (self.count_scope == "unknown"):
            raise ValueError("Unknown totals require unknown scope.")
        if self.available_reviews is not None and self.available_reviews < self.analyzed_reviews:
            raise ValueError("Total is smaller than sample.")
        if self.status == "complete" and (
            self.stop_reason != "exhausted" or not self.analyzed_reviews
        ):
            raise ValueError("Completion requires nonempty exhausted selection.")
        if self.status == "empty" and (self.stop_reason != "empty" or self.analyzed_reviews):
            raise ValueError("Empty requires an exhausted empty selection.")
        if self.status == "partial" and self.stop_reason not in (
            "row_limit",
            "page_limit",
            "source_window",
        ):
            raise ValueError("Partial selection requires a bounded stop reason.")
        if self.stop_reason == "row_limit" and self.analyzed_reviews != 500:
            raise ValueError("Row limit requires 500 retained reviews.")
        if self.stop_reason == "page_limit" and self.pages_fetched != 5:
            raise ValueError("Page limit requires five pages.")
        return self


class ProductAnalysisResultV2(ResultModel):
    schema_version: Literal["2"] = "2"
    ingestion_version: Literal["rt-product-ingestion-0.1.0"] = "rt-product-ingestion-0.1.0"
    source: SourceInfo
    product: ProductInfo
    collection: CollectionInfo
    analysis: CollectedAnalysis | None

    @model_validator(mode="after")
    def coherent(self) -> Self:
        count = self.collection.analyzed_reviews
        if (self.analysis is None) != (count == 0):
            raise ValueError("Analysis availability must match the retained count.")
        if self.analysis is not None:
            if self.analysis.review_count != count or self.analysis.coverage.total_reviews != count:
                raise ValueError("Analysis and collection counts disagree.")
            if len(self.analysis.reviews) != count:
                raise ValueError("Displayed count disagrees.")
        if self.source.retrieved_at != self.collection.window_finished_at:
            raise ValueError("Source time must match collection completion.")
        if (self.product.variant is not None) != (
            self.collection.variant_scope == "selected_variant"
        ):
            raise ValueError("Variant label must match selected variant scope.")
        return self
