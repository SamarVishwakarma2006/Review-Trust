"""Bounded in-memory input adapters; use these to keep public errors free of input values."""

import csv
import io
import json
import re
from dataclasses import dataclass, field
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import ValidationError

from app.schemas import (
    MAX_BODY_BYTES,
    MAX_ERRORS,
    MAX_REVIEWS,
    MAX_TEXT_LENGTH,
    REVIEW_FIELDS,
    ReviewSubmission,
)

MAX_CSV_COLUMNS = 50
MAX_CSV_HEADER_LENGTH = 100
_PUBLIC_FIELDS = REVIEW_FIELDS | frozenset(ReviewSubmission.model_fields)
_DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)")


@dataclass(frozen=True)
class FieldIssue:
    row: int | None
    field: str
    code: str


class ReviewInputError(Exception):
    """Safe to render; no underlying exception, input values or arbitrary field names."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 422,
        fields: tuple[FieldIssue, ...] = (),
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.total_errors = len(fields)
        self.fields = fields[:MAX_ERRORS]


@dataclass(frozen=True)
class InputWarning:
    code: Literal["unverified_subset", "mixed_product_coverage", "unmapped_columns"]
    column_positions: tuple[int, ...] = ()


@dataclass(frozen=True)
class IngestedReviews:
    submission: ReviewSubmission = field(repr=False)
    warnings: tuple[InputWarning, ...]

    @property
    def review_refs(self) -> tuple[str, ...]:
        return tuple(f"r{index}" for index in range(1, len(self.submission.reviews) + 1))


def validate_submission(payload: object, *, today: date | None = None) -> IngestedReviews:
    """Validate decoded canonical input atomically; API code must not expose Pydantic errors."""
    if not isinstance(payload, dict):
        raise ReviewInputError("invalid_submission", "Submit a review request object.")
    try:
        submission = ReviewSubmission.model_validate(
            payload, context={"today": today if today is not None else datetime.now(UTC).date()}
        )
    except ValidationError as error:
        issues = []
        oversized = False
        for detail in error.errors(include_url=False, include_context=False, include_input=False):
            location = detail["loc"]
            row = None
            if len(location) >= 2 and location[0] == "reviews" and type(location[1]) is int:
                row = location[1] + 1
            name = location[-1] if location else "request"
            name = name if name in _PUBLIC_FIELDS else ("review" if row else "request")
            issues.append(FieldIssue(row=row, field=name, code=detail["type"]))
            oversized |= detail["type"] in {"string_too_long", "too_long", "total_text_limit"}
        raise ReviewInputError(
            "input_limit" if oversized else "invalid_submission",
            "Input exceeds the allowed limits." if oversized else "Correct the indicated fields.",
            413 if oversized else 422,
            tuple(issues),
        ) from None
    warnings = [InputWarning("unverified_subset")]
    known_products = sum(review.product_id is not None for review in submission.reviews)
    if 0 < known_products < len(submission.reviews):
        warnings.append(InputWarning("mixed_product_coverage"))
    return IngestedReviews(submission, tuple(warnings))


def _check_body(data: bytes) -> None:
    if not isinstance(data, bytes):
        raise ReviewInputError("unsupported_input", "Supply UTF-8 encoded bytes.", 415)
    if len(data) > MAX_BODY_BYTES:
        raise ReviewInputError("body_limit", "Input exceeds the byte limit.", 413)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _reject_json_constant(value: str) -> None:
    raise ValueError


def decode_json(data: bytes) -> object:
    """Bounded strict JSON decoding, also used for multipart column mapping."""
    _check_body(data)
    try:
        return json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_json_constant,
            parse_float=Decimal,
        )
    except (UnicodeDecodeError, ValueError, ArithmeticError, RecursionError):
        raise ReviewInputError(
            "malformed_json", "Supply valid UTF-8 JSON without duplicate keys.", 400
        ) from None


def parse_json(data: bytes, *, today: date | None = None) -> IngestedReviews:
    result = validate_submission(decode_json(data), today=today)
    if result.submission.origin != "paste":
        raise ReviewInputError("origin_mismatch", "JSON submissions must use paste origin.")
    return result


def _validate_csv_quotes(text: str) -> None:
    # csv.reader(strict=True) still permits a bare quote inside an unquoted cell.
    state = "start"
    for character in text:
        if state == "quoted":
            if character == '"':
                state = "closed"
        elif state == "closed" and character == '"':
            state = "quoted"
        elif character in ",\r\n":
            state = "start"
        elif state == "start":
            state = "quoted" if character == '"' else "unquoted"
        elif state == "closed" or character == '"':
            raise ReviewInputError("malformed_csv", "Check CSV quoting and delimiters.", 400)
    if state == "quoted":
        raise ReviewInputError("malformed_csv", "Check CSV quoting and delimiters.", 400)


def _column_mapping(headers: list[str], mapping: object) -> dict[int, str]:
    if mapping is None:
        mapping = {header: header for header in headers if header in REVIEW_FIELDS}
    if (
        not isinstance(mapping, dict)
        or len(mapping) > len(REVIEW_FIELDS)
        or any(
            not isinstance(source, str)
            or not isinstance(target, str)
            or source not in headers
            or target not in REVIEW_FIELDS
            for source, target in mapping.items()
        )
        or len(set(mapping.values())) != len(mapping)
        or "text" not in mapping.values()
    ):
        raise ReviewInputError(
            "csv_mapping", "Map one existing column to text and each optional field at most once."
        )
    return {headers.index(source): target for source, target in mapping.items()}


def _csv_value(name: str, value: str) -> object:
    if name == "text":
        return value
    value = value.strip()
    if not value:
        return None
    if name == "rating" and _DECIMAL.fullmatch(value):
        return Decimal(value)
    if name == "verified_purchase" and value in {"true", "false"}:
        return value == "true"
    return value


def parse_csv(
    data: bytes,
    *,
    category: str,
    language: str,
    mapping: object = None,
    schema_version: str = "1",
    today: date | None = None,
) -> IngestedReviews:
    """Mapping uses source header -> canonical field; errors count the header as record 1."""
    _check_body(data)
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ReviewInputError(
            "csv_encoding", "Use UTF-8 CSV, optionally with a BOM.", 415
        ) from None
    if "\x00" in text:
        raise ReviewInputError("csv_characters", "CSV contains unsupported characters.", 400)
    _validate_csv_quotes(text)
    reader = csv.reader(io.StringIO(text, newline=""), strict=True)
    records = []
    try:
        headers = [header.strip() for header in next(reader, [])]
        if not headers or any(not header for header in headers):
            raise ReviewInputError("csv_header", "CSV requires a nonempty header for every column.")
        if len(headers) > MAX_CSV_COLUMNS or any(
            len(header) > MAX_CSV_HEADER_LENGTH for header in headers
        ):
            raise ReviewInputError(
                "csv_header_limit", "CSV headers exceed the allowed limits.", 413
            )
        if len(set(headers)) != len(headers):
            raise ReviewInputError(
                "csv_header", "CSV column headers must be unique after trimming."
            )
        columns = _column_mapping(headers, mapping)
        for row_number, cells in enumerate(reader, start=2):
            if row_number > MAX_REVIEWS + 1:
                raise ReviewInputError("row_limit", "CSV exceeds the review row limit.", 413)
            if len(cells) != len(headers):
                raise ReviewInputError(
                    "csv_columns",
                    "Each CSV record must have the same number of columns as its header.",
                    400,
                    (FieldIssue(row_number, "csv", "column_count"),),
                )
            if any(len(cell) > MAX_TEXT_LENGTH for cell in cells):
                raise ReviewInputError(
                    "csv_cell_limit",
                    "A CSV cell exceeds the character limit.",
                    413,
                    (FieldIssue(row_number, "csv", "cell_limit"),),
                )
            records.append(
                {name: _csv_value(name, cells[index]) for index, name in columns.items()}
            )
    except csv.Error as error:
        oversized = "field larger than field limit" in str(error)
        raise ReviewInputError(
            "csv_cell_limit" if oversized else "malformed_csv",
            "A CSV cell exceeds the limit." if oversized else "Check CSV quoting and delimiters.",
            413 if oversized else 400,
        ) from None
    try:
        result = validate_submission(
            {
                "schema_version": schema_version,
                "category": category,
                "language": language,
                "origin": "csv",
                "reviews": records,
            },
            today=today,
        )
    except ReviewInputError as error:
        error.fields = tuple(
            FieldIssue(issue.row + 1 if issue.row is not None else None, issue.field, issue.code)
            for issue in error.fields
        )
        raise
    discarded = tuple(index + 1 for index in range(len(headers)) if index not in columns)
    warnings = result.warnings + (
        (InputWarning("unmapped_columns", discarded),) if discarded else ()
    )
    return IngestedReviews(result.submission, warnings)
