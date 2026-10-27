"""Canonical input contracts. These models do not establish review authenticity."""

import re
from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationInfo,
    field_validator,
    model_validator,
)
from pydantic_core import PydanticCustomError

MAX_BODY_BYTES = 1_048_576
MAX_REVIEWS = 500
MAX_TEXT_LENGTH = 5_000
MAX_TOTAL_TEXT_LENGTH = 250_000
MAX_ERRORS = 20

Text = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAX_TEXT_LENGTH)
]
Identifier = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]
Title = Annotated[str, StringConstraints(strip_whitespace=True, max_length=300)]


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, hide_input_in_errors=True, frozen=True)


class ReviewInput(InputModel):
    text: Text = Field(repr=False)
    rating: float | None = None
    timestamp: date | datetime | None = None
    product_id: Identifier | None = Field(default=None, repr=False)
    title: Title | None = Field(default=None, repr=False)
    verified_purchase: bool | None = None
    source_id: Identifier | None = Field(default=None, repr=False)

    @field_validator("*", mode="before")
    @classmethod
    def reject_invalid_characters(cls, value: object) -> object:
        if isinstance(value, str) and (
            "\x00" in value or any(0xD800 <= ord(character) <= 0xDFFF for character in value)
        ):
            raise PydanticCustomError("invalid_characters", "Unsupported characters in field.")
        return value

    @field_validator("rating", mode="before")
    @classmethod
    def valid_rating(cls, value: object) -> object:
        invalid_decimal = isinstance(value, Decimal) and (
            not value.is_finite() or not 1 <= value <= 5
        )
        if invalid_decimal or (type(value) in {int, float} and not 1 <= value <= 5):
            raise PydanticCustomError("rating_range", "Rating must be finite and between 1 and 5.")
        return value

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_timestamp(cls, value: object, info: ValidationInfo) -> date | datetime | None:
        if value is None:
            return None
        if isinstance(value, str):
            try:
                if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
                    value = date.fromisoformat(value)
                elif re.fullmatch(
                    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
                    r"(?:\.[0-9]{1,6})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])",
                    value,
                ):
                    value = datetime.fromisoformat(value)
                else:
                    raise ValueError
            except ValueError:
                raise PydanticCustomError(
                    "timestamp_format", "Use an ISO date or timezone-aware ISO datetime."
                ) from None
        if isinstance(value, datetime):
            if value.utcoffset() is None:
                raise PydanticCustomError("timestamp_timezone", "Datetime requires a timezone.")
            try:
                value = value.astimezone(UTC)
            except (OverflowError, ValueError):
                raise PydanticCustomError("timestamp_format", "Datetime is out of range.") from None
        if not isinstance(value, date):
            raise PydanticCustomError("timestamp_format", "Timestamp must be a date or datetime.")
        today = (info.context or {}).get("today", datetime.now(UTC).date())
        timestamp_date = value.date() if isinstance(value, datetime) else value
        if timestamp_date > today:
            raise PydanticCustomError("timestamp_future", "Timestamp date cannot be in the future.")
        return value


REVIEW_FIELDS = frozenset(ReviewInput.model_fields)


class ReviewSubmission(InputModel):
    schema_version: Literal["1"]
    category: Literal["electronics"]
    language: Literal["en"]
    origin: Literal["paste", "csv"]
    reviews: list[ReviewInput] = Field(min_length=1, max_length=MAX_REVIEWS, repr=False)

    @model_validator(mode="after")
    def validate_collection(self) -> Self:
        if sum(len(review.text) + len(review.title or "") for review in self.reviews) > (
            MAX_TOTAL_TEXT_LENGTH
        ):
            raise PydanticCustomError("total_text_limit", "Combined text exceeds the input limit.")
        product_ids = {
            review.product_id for review in self.reviews if review.product_id is not None
        }
        if len(product_ids) > 1:
            raise PydanticCustomError("mixed_products", "Submit reviews for one product at a time.")
        return self
