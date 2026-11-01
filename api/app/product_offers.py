"""Offline authored offer totals and conservative comparison eligibility."""

import re
from datetime import datetime
from decimal import Decimal, localcontext
from typing import Annotated, Literal

from pydantic import AwareDatetime, BeforeValidator, Field

from app.analysis import check_deadline
from app.product_identity import ProductIdentity, match_products
from app.schemas import InputModel


def money(value):
    # Require bounded decimal strings; binary floats never enter price arithmetic.
    if not isinstance(value, str) or not re.fullmatch(
        r"(?:0|[1-9][0-9]{0,8})(?:\.[0-9]{1,2})?", value
    ):
        raise ValueError("Use a nonnegative decimal amount with at most two decimal places")
    return Decimal(value)


Money = Annotated[Decimal, BeforeValidator(money)]


class AuthoredOffer(InputModel):
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"
    identity: ProductIdentity
    currency: Literal["INR", "USD", "EUR"]
    observed_at: AwareDatetime
    delivery_context: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    available: bool | None = None
    purchase_terms: Literal["unconditional", "subscription", "membership", "coupon", "unknown"] = (
        "unknown"
    )
    price: Money | None = None
    shipping: Money | None = None
    tax: Money | None = None
    mandatory_fees: Money | None = None


class OfferRequest(InputModel):
    target: ProductIdentity
    currency: Literal["INR", "USD", "EUR"] = "INR"
    delivery_context: str = Field(min_length=1, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    now: AwareDatetime
    max_age_seconds: int = Field(ge=1, le=86400)
    offers: tuple[AuthoredOffer, ...] = Field(max_length=50)


class OfferDecision(InputModel):
    ref: str
    status: Literal["comparable", "unavailable"]
    reasons: tuple[str, ...]
    currency: Literal["INR", "USD", "EUR"]
    observed_at: datetime
    total: str | None


class OfferComparison(InputModel):
    version: Literal["rt-offers-0.1.0"] = "rt-offers-0.1.0"
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"
    decisions: tuple[OfferDecision, ...]
    lowest_total_refs: tuple[str, ...]
    comparison_complete: bool


def compare_offers(request: OfferRequest, deadline: float) -> OfferComparison:
    """Lowest totals are reported only when every supplied offer is comparable.

    Explicit zero means a charge is included/free; null means unknown. All amounts
    refer to the complete listed bundle/quantity, never an inferred per-unit price.
    """
    check_deadline(deadline)
    decisions = []
    totals = []
    for index, offer in enumerate(request.offers, 1):
        check_deadline(deadline)
        reasons = []
        if match_products(request.target, offer.identity).status != "same_variant":
            reasons.append("identity_unresolved_or_different")
        if offer.identity.seller_id is None:
            reasons.append("seller_unknown")
        if offer.currency != request.currency:
            reasons.append("currency_mismatch")
        if offer.delivery_context != request.delivery_context:
            reasons.append("delivery_context_mismatch")
        age = (request.now - offer.observed_at).total_seconds()
        if age < 0:
            reasons.append("future_observation")
        elif age > request.max_age_seconds:
            reasons.append("stale")
        if offer.available is not True:
            reasons.append("stock_unavailable_or_unknown")
        if offer.purchase_terms != "unconditional":
            reasons.append("conditional_or_unknown_terms")
        amounts = (offer.price, offer.shipping, offer.tax, offer.mandatory_fees)
        if any(amount is None for amount in amounts):
            reasons.append("incomplete_total")
        ref = f"o{index}"
        total = None
        if not reasons:
            with localcontext() as context:
                context.prec = 28
                amount = sum(amounts, Decimal(0))
                total = format(amount, ".2f")
            totals.append((ref, amount))
        decisions.append(
            OfferDecision(
                ref=ref,
                status="unavailable" if reasons else "comparable",
                reasons=tuple(reasons),
                currency=offer.currency,
                observed_at=offer.observed_at,
                total=total,
            )
        )
    complete = bool(decisions) and len(totals) == len(decisions)
    lowest = min((amount for _, amount in totals), default=None)
    check_deadline(deadline)
    return OfferComparison(
        decisions=tuple(decisions),
        comparison_complete=complete,
        lowest_total_refs=tuple(ref for ref, amount in totals if complete and amount == lowest),
    )
