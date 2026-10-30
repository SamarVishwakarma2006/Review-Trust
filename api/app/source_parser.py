"""Offline WooCommerce-shaped response parser. No source access or HTTP integration."""

import re
from dataclasses import dataclass, field
from datetime import date
from html.parser import HTMLParser
from typing import Literal

from pydantic import TypeAdapter, ValidationError

from app.ingestion import ReviewInputError, decode_json
from app.schemas import MAX_TOTAL_TEXT_LENGTH, ReviewInput, Title

ADAPTER_VERSION = "rt-woocommerce-parser-0.1.0"
MAX_PAGE_BYTES = 262_144
_UTC_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}")
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _invalid() -> ReviewInputError:
    return ReviewInputError("source_data_invalid", "Source data could not be validated.", 502)


def _id(value: object) -> int:
    if type(value) is not int or not 1 <= value <= 2**53 - 1:
        raise _invalid()
    return value


def _string(value: object, maximum: int) -> str:
    if (
        not isinstance(value, str)
        or len(value) > maximum
        or any(char == "\x00" or 0xD800 <= ord(char) <= 0xDFFF for char in value)
    ):
        raise _invalid()
    return value


class _Text(HTMLParser):
    """Extract inert text; never return source HTML, attributes or executable content."""

    _hidden = {"script", "style", "template", "iframe", "object"}
    _breaks = {"p", "div", "br", "li", "ul", "ol", "tr", "td", "h1", "h2", "h3"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag in self._hidden:
            self.hidden.append(tag)
        elif not self.hidden and tag in self._breaks:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in self.hidden:
            del self.hidden[self.hidden.index(tag) :]
        elif not self.hidden and tag in self._breaks:
            self.parts.append("\n")

    def handle_startendtag(self, tag, attrs):
        if not self.hidden and tag in self._breaks:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def _text(value: object) -> str:
    parser = _Text()
    try:
        parser.feed(_string(value, 20_000))
        parser.close()
    except (AssertionError, ValueError):
        raise _invalid() from None
    return "".join(parser.parts).strip()


def _decode(data: bytes) -> object:
    if not isinstance(data, bytes):
        raise _invalid()
    if len(data) > MAX_PAGE_BYTES:
        raise ReviewInputError("source_limit", "Source response exceeds the allowed limit.", 502)
    try:
        return decode_json(data)
    except ReviewInputError:
        raise _invalid() from None


@dataclass(frozen=True)
class SourceProduct:
    source_id: int = field(repr=False)
    slug: str = field(repr=False)
    title: str = field(repr=False)
    kind: Literal["simple", "variable"]
    variant_ids: tuple[int, ...] = field(repr=False)


@dataclass(frozen=True)
class SourceReview:
    source_id: int = field(repr=False)
    review: ReviewInput = field(repr=False)


def parse_product(data: bytes, *, expected_slug: str) -> SourceProduct:
    """Parse one resolved product, preserving identity without trusting remote URLs."""
    payload = _decode(data)
    if not isinstance(payload, dict):
        raise _invalid()
    slug = _string(payload.get("slug"), 100)
    if not _SLUG.fullmatch(slug) or slug != expected_slug:
        raise _invalid()
    kind = payload.get("type")
    if kind not in ("simple", "variable"):
        raise _invalid()
    parent = payload.get("parent_id", 0)
    if type(parent) is not int or parent != 0:
        raise _invalid()
    variants = payload.get("variations")
    if not isinstance(variants, list) or len(variants) > 100:
        raise _invalid()
    ids = tuple(_id(value) for value in variants)
    if len(set(ids)) != len(ids) or payload.get("id") in ids or (kind == "simple" and ids):
        raise _invalid()
    try:
        title = TypeAdapter(Title).validate_python(_text(payload.get("name")))
    except ValidationError:
        raise _invalid() from None
    if not title:
        raise _invalid()
    return SourceProduct(_id(payload.get("id")), slug, title, kind, ids)


def parse_review_page(data: bytes, *, product_id: int, today: date) -> tuple[SourceReview, ...]:
    """Validate a whole page atomically. Empty is valid; malformed rows never disappear."""
    _id(product_id)
    payload = _decode(data)
    if not isinstance(payload, list):
        raise _invalid()
    if len(payload) > 100:
        raise ReviewInputError("source_limit", "Source response exceeds the allowed limit.", 502)
    rows = []
    seen = set()
    total = 0
    for record in payload:
        if not isinstance(record, dict):
            raise _invalid()
        source_id = _id(record.get("id"))
        if source_id in seen or _id(record.get("product_id")) != product_id:
            raise _invalid()
        seen.add(source_id)
        if record.get("status") != "approved":
            raise _invalid()
        timestamp = record.get("date_created_gmt")
        if timestamp is not None:
            timestamp = _string(timestamp, 19)
            if not _UTC_DATE.fullmatch(timestamp):
                raise _invalid()
            timestamp += "Z"
        try:
            review = ReviewInput.model_validate(
                {
                    "text": _text(record.get("review")),
                    "rating": record.get("rating"),
                    "timestamp": timestamp,
                    "verified_purchase": record.get("verified"),
                    "product_id": str(product_id),
                },
                context={"today": today},
            )
        except ValidationError:
            raise _invalid() from None
        total += len(review.text)
        if total > MAX_TOTAL_TEXT_LENGTH:
            raise ReviewInputError(
                "source_limit", "Source response exceeds the allowed limit.", 502
            )
        rows.append(SourceReview(source_id, review))
    return tuple(rows)
