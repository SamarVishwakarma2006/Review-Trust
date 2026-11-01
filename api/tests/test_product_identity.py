import pytest
from pydantic import ValidationError

from app.product_identity import FIELDS, ProductIdentity, match_products


def product(**changes):
    return ProductIdentity(
        **(
            dict(
                source="authored-a",
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
            | changes
        )
    )


def test_same_variant_keeps_seller_and_site_separate():
    result = match_products(product(), product(source="authored-b"))
    assert result.status == "same_variant" and result.seller_relation == "unknown"
    result = match_products(product(), product(listing_id="2", seller_id="s2"))
    assert result.status == "same_variant" and result.seller_relation == "different"


@pytest.mark.parametrize("field", FIELDS)
def test_missing_fields_never_match(field):
    result = match_products(product(), product(**{field: None}))
    assert result.status == "unresolved" and field in result.reason_fields


@pytest.mark.parametrize(
    "field,value",
    [
        ("model", "H2"),
        ("region", "US"),
        ("capacity", "64GB"),
        ("bundle", "with_case"),
        ("quantity", 2),
        ("condition", "used"),
    ],
)
def test_variant_mismatch_and_conflicting_same_listing(field, value):
    assert (
        match_products(product(), product(listing_id="2", **{field: value})).status == "different"
    )
    assert match_products(product(), product(**{field: value})).status == "unresolved"


@pytest.mark.parametrize(
    "changes", [{"quantity": True}, {"model": " "}, {"source": "a\x00"}, {"title": "Same title"}]
)
def test_invalid_identity(changes):
    with pytest.raises(ValidationError):
        product(**changes)
