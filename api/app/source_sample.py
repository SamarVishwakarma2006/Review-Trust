"""Offline sample assembly only. Does not collect data or establish source permission."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal

from app.analysis import redact
from app.ingestion import ReviewInputError
from app.schemas import MAX_REVIEWS, MAX_TEXT_LENGTH, MAX_TOTAL_TEXT_LENGTH, ReviewInput
from app.source_parser import SourceProduct, parse_review_page


@dataclass(frozen=True)
class SourceSample:
    product: SourceProduct = field(repr=False)
    reviews: tuple[ReviewInput, ...] = field(repr=False)
    window_started_at: datetime
    window_finished_at: datetime
    status: Literal["complete", "partial", "empty"]
    stop_reason: Literal["exhausted", "row_limit", "page_limit", "source_window", "empty"]
    fetched_records: int
    overlap_records: int
    pages_fetched: int
    variant_scope: Literal["combined", "unknown"]
    selection_order: Literal["newest_first"] = "newest_first"
    available_reviews: None = None
    count_scope: Literal["unknown"] = "unknown"
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"


def assemble_fixture_sample(
    pages: tuple[bytes, ...],
    *,
    product: SourceProduct,
    window_started_at: datetime,
    window_finished_at: datetime,
    exhausted: bool,
) -> SourceSample:
    """Assemble sequential authored pages, collapsing only identical cross-page IDs.

    Exhaustion is an explicit fixture marker, never inferred from a short page.
    This function is deliberately not a v1 submission or a public v2 envelope.
    """

    def invalid():
        return ReviewInputError("source_data_invalid", "Source data could not be validated.", 502)

    if (
        type(pages) is not tuple
        or not 1 <= len(pages) <= 5
        or any(type(page) is not bytes for page in pages)
        or type(exhausted) is not bool
        or any(
            not isinstance(value, datetime) or value.utcoffset() is None
            for value in (window_started_at, window_finished_at)
        )
    ):
        raise invalid()
    start, finish = (value.astimezone(UTC) for value in (window_started_at, window_finished_at))
    if finish < start:
        raise invalid()
    if sum(map(len, pages)) > 1_048_576:
        raise ReviewInputError("source_limit", "Source sample exceeds the allowed limit.", 502)
    seen = {}
    reviews = []
    fetched = overlap = text_length = 0
    last_timestamp = None
    counts = {"email": 0, "phone": 0}
    for index, page in enumerate(pages):
        rows = parse_review_page(page, product_id=product.source_id, today=finish.date())
        if not rows and index != len(pages) - 1:
            raise invalid()
        for row in rows:
            fetched += 1
            previous = seen.get(row.source_id)
            if previous is not None:
                if previous != row.review:
                    raise invalid()
                overlap += 1
                continue
            timestamp = row.review.timestamp
            if timestamp is not None:
                if last_timestamp is not None and timestamp > last_timestamp:
                    raise invalid()
                last_timestamp = timestamp
            seen[row.source_id] = row.review
            text = redact(row.review.text, counts)
            title = redact(row.review.title, counts) if row.review.title is not None else None
            text_length += len(text) + len(title or "")
            if (
                len(reviews) >= MAX_REVIEWS
                or len(text) > MAX_TEXT_LENGTH
                or len(title or "") > 300
                or text_length > MAX_TOTAL_TEXT_LENGTH
            ):
                raise ReviewInputError(
                    "source_limit", "Source sample exceeds the allowed limit.", 502
                )
            reviews.append(row.review.model_copy(update={"text": text, "title": title}))
    reason = (
        ("exhausted" if reviews else "empty")
        if exhausted
        else "row_limit"
        if len(reviews) == MAX_REVIEWS
        else "page_limit"
        if len(pages) == 5
        else "source_window"
    )
    return SourceSample(
        product=product,
        reviews=tuple(reviews),
        window_started_at=start,
        window_finished_at=finish,
        status=("complete" if reviews else "empty") if exhausted else "partial",
        stop_reason=reason,
        fetched_records=fetched,
        overlap_records=overlap,
        pages_fetched=len(pages),
        variant_scope="combined" if product.kind == "variable" else "unknown",
    )
