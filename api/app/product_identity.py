"""Conservative offline matching of validated, source-declared catalog identity."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductIdentity(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    source: str = Field(min_length=1, max_length=100)
    listing_id: str = Field(min_length=1, max_length=100)
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    region: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = Field(default=None, min_length=1, max_length=100)
    connectivity: str | None = Field(default=None, min_length=1, max_length=100)
    capacity: str | None = Field(default=None, min_length=1, max_length=100)
    bundle: str | None = Field(default=None, min_length=1, max_length=100)
    quantity: int | None = Field(default=None, ge=1, le=100)
    condition: Literal["new", "used", "refurbished"] | None = None
    seller_id: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("*", mode="after")
    @classmethod
    def clean_text(cls, value):
        if isinstance(value, str):
            value = value.strip()
            if not value or any(ord(c) < 32 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
                raise ValueError("Invalid identity text")
        return value


class IdentityMatch(BaseModel):
    version: Literal["rt-identity-0.1.0"] = "rt-identity-0.1.0"
    status: Literal["same_variant", "different", "unresolved"]
    reason_fields: tuple[str, ...]
    seller_relation: Literal["same", "different", "unknown"]


FIELDS = (
    "brand",
    "model",
    "region",
    "color",
    "connectivity",
    "capacity",
    "bundle",
    "quantity",
    "condition",
)


def match_products(left: ProductIdentity, right: ProductIdentity) -> IdentityMatch:
    """Exact declared values only; no title similarity, identifier guessing or network.

    Catalog adapters must establish field semantics before calling this function.
    Unknown fields never match, even on the same listing. Seller IDs are site-scoped.
    """
    different = tuple(
        field
        for field in FIELDS
        if getattr(left, field) is not None
        and getattr(right, field) is not None
        and getattr(left, field) != getattr(right, field)
    )
    missing = tuple(
        field for field in FIELDS if getattr(left, field) is None or getattr(right, field) is None
    )
    seller = "unknown"
    if left.source == right.source and left.seller_id and right.seller_id:
        seller = "same" if left.seller_id == right.seller_id else "different"
    # Conflicting descriptions of one listing require resolution, not a merge.
    conflict = left.source == right.source and left.listing_id == right.listing_id and different
    status = (
        "unresolved"
        if conflict
        else "different"
        if different
        else "unresolved"
        if missing
        else "same_variant"
    )
    return IdentityMatch(status=status, reason_fields=different or missing, seller_relation=seller)
