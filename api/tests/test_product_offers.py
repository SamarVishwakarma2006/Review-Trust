import time
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.ingestion import ReviewInputError
from app.product_identity import ProductIdentity
from app.product_offers import AuthoredOffer, OfferRequest, compare_offers

NOW = datetime(2026, 11, 1, tzinfo=UTC)
IDENTITY = ProductIdentity(
    source="authored",
    listing_id="1",
    brand="Example",
    model="H1",
    region="IN",
    color="black",
    connectivity="wired",
    capacity="not_applicable",
    bundle="headphones_only",
    quantity=1,
    condition="new",
    seller_id="s1",
)


def offer(**changes):
    return AuthoredOffer(
        **(
            dict(
                identity=IDENTITY,
                currency="INR",
                observed_at=NOW,
                delivery_context="authored_delivery",
                available=True,
                purchase_terms="unconditional",
                price="0.10",
                shipping="0.20",
                tax="0",
                mandatory_fees="0",
            )
            | changes
        )
    )


def request(*offers):
    return OfferRequest(
        target=IDENTITY,
        delivery_context="authored_delivery",
        now=NOW,
        max_age_seconds=3600,
        offers=offers,
    )


def run(*offers):
    return compare_offers(request(*offers), time.monotonic() + 5)


def test_decimal_totals_ties_and_empty():
    result = run(offer(), offer(), offer(price="1"))
    assert result.decisions[0].total == "0.30"
    assert result.lowest_total_refs == ("o1", "o2") and result.comparison_complete
    assert not run().comparison_complete and not run().lowest_total_refs


@pytest.mark.parametrize(
    "changes,reason",
    [
        ({"observed_at": NOW - timedelta(seconds=3601)}, "stale"),
        ({"observed_at": NOW + timedelta(seconds=1)}, "future_observation"),
        ({"currency": "USD"}, "currency_mismatch"),
        ({"purchase_terms": "subscription"}, "conditional_or_unknown_terms"),
        ({"purchase_terms": "membership"}, "conditional_or_unknown_terms"),
        ({"purchase_terms": "coupon"}, "conditional_or_unknown_terms"),
        ({"shipping": None}, "incomplete_total"),
        ({"tax": None}, "incomplete_total"),
        ({"mandatory_fees": None}, "incomplete_total"),
        ({"available": None}, "stock_unavailable_or_unknown"),
        ({"available": False}, "stock_unavailable_or_unknown"),
        ({"delivery_context": "other"}, "delivery_context_mismatch"),
        (
            {"identity": IDENTITY.model_copy(update={"color": "white"})},
            "identity_unresolved_or_different",
        ),
        ({"identity": IDENTITY.model_copy(update={"seller_id": None})}, "seller_unknown"),
    ],
)
def test_unusable_offer_withholds_comparison(changes, reason):
    result = run(offer(), offer(**changes))
    assert result.decisions[1].total is None and reason in result.decisions[1].reasons
    assert not result.lowest_total_refs and not result.comparison_complete


@pytest.mark.parametrize(
    "value", [True, 1.2, "NaN", "Infinity", "-1", "1.001", "1e2", "1000000000"]
)
def test_invalid_money(value):
    with pytest.raises(ValidationError):
        offer(price=value)


def test_time_bounds_input_bounds_and_deadline():
    assert run(offer(observed_at=NOW - timedelta(seconds=3600))).comparison_complete
    with pytest.raises(ValidationError):
        offer(observed_at=NOW.replace(tzinfo=None))
    with pytest.raises(ValidationError):
        request(*([offer()] * 51))
    with pytest.raises(ValidationError):
        offer(evidence_origin="collected")
    with pytest.raises(ReviewInputError):
        compare_offers(request(), 0)
