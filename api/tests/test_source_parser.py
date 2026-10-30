"""Authored response mechanics only; no live source or training permission implied."""

import json
from dataclasses import asdict
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from app.ingestion import ReviewInputError
from app.source_parser import MAX_PAGE_BYTES, parse_product, parse_review_page

FIXTURES = Path(__file__).parent / "fixtures"
TODAY = date(2026, 10, 31)


def product():
    return json.loads((FIXTURES / "source_product.json").read_text(encoding="utf-8"))


def records():
    return json.loads((FIXTURES / "source_reviews.json").read_text(encoding="utf-8"))


def encoded(value):
    return json.dumps(value, ensure_ascii=False).encode("utf-8")


def page(value):
    return parse_review_page(encoded(value), product_id=101, today=TODAY)


def test_authored_product_identity_and_variable_product_scope():
    parsed = parse_product(encoded(product()), expected_slug="example-headphones")
    assert parsed.source_id == 101
    assert parsed.title == "Authored Example Headphones"
    assert parsed.kind == "variable" and parsed.variant_ids == (102, 103)
    assert "permalink" not in asdict(parsed)
    assert "Headphones" not in repr(parsed)


def test_page_preserves_text_utc_and_nulls_and_discards_personal_fields():
    parsed = page(records())
    assert parsed == page(records())
    first, second = parsed
    assert first.review.text == (
        "The synthetic headphones sound clear & fit well.\n\n"
        "Battery lasts through my example session. 🎧"
    )
    assert first.review.timestamp == datetime(2024, 2, 1, 10, 30, tzinfo=UTC)
    assert first.review.rating == 4 and first.review.verified_purchase is True
    assert second.review.rating is None and second.review.timestamp is None
    assert second.review.verified_purchase is None
    assert first.review.product_id == "101" and first.review.source_id is None
    stored = str(asdict(first))
    for sentinel in ("AUTHORED_NAME_SENTINEL", "authored@example.invalid", "IGNORE THIS"):
        assert sentinel not in stored and sentinel not in repr(parsed)


def test_empty_missing_optional_fields_and_same_text_different_ids():
    assert page([]) == ()
    rows = records()
    rows[1] = rows[0] | {"id": 2}
    for row in rows:
        for key in ("rating", "date_created_gmt", "verified"):
            row.pop(key)
    parsed = page(rows)
    assert len(parsed) == 2 and parsed[0].review.text == parsed[1].review.text
    assert parsed[0].source_id != parsed[1].source_id


@pytest.mark.parametrize(
    "change",
    [
        {"id": True},
        {"id": 0},
        {"id": 2**53},
        {"product_id": 102},
        {"product_id": True},
        {"status": "hold"},
        {"status": None},
        {"review": None},
        {"review": "<p> </p>"},
        {"review": "\x00"},
        {"review": "\ud800"},
        {"review": "x" * 5001},
        {"review": "x" * 20_001},
        {"rating": 0},
        {"rating": 6},
        {"rating": True},
        {"rating": "5"},
        {"verified": "true"},
        {"verified": 1},
        {"date_created_gmt": ""},
        {"date_created_gmt": "2024-02-30T10:00:00"},
        {"date_created_gmt": "2024-02-01T10:00:00+05:30"},
        {"date_created_gmt": "2099-01-01T00:00:00"},
    ],
)
def test_invalid_row_rejects_whole_page_with_safe_error(change):
    rows = records()
    rows[1] |= change
    # Surrogates must be transmitted as JSON escapes to exercise the source decoder.
    data = json.dumps(rows).encode("utf-8")
    with pytest.raises(ReviewInputError) as caught:
        parse_review_page(data, product_id=101, today=TODAY)
    assert caught.value.code == "source_data_invalid" and caught.value.status_code == 502
    assert str(caught.value) == "Source data could not be validated."
    assert "authored@example.invalid" not in repr(caught.value)


@pytest.mark.parametrize("value", [{}, None, [None], [42]])
def test_wrong_page_schema_rejects(value):
    with pytest.raises(ReviewInputError, match="Source data could not be validated"):
        page(value)


def test_duplicate_id_is_not_silently_dropped():
    row = records()[0]
    for other in (row, row | {"review": "A conflicting authored review."}):
        with pytest.raises(ReviewInputError):
            page([row, other])


@pytest.mark.parametrize(
    "change",
    [
        {"id": False},
        {"id": -1},
        {"name": None},
        {"name": " "},
        {"name": "x" * 301},
        {"slug": "another-product"},
        {"slug": "../example"},
        {"type": "variation"},
        {"type": "new-unsupported-kind"},
        {"parent_id": 100},
        {"variations": None},
        {"variations": [102, 102]},
        {"variations": [101]},
        {"variations": [True]},
        {"variations": list(range(200, 301))},
        {"type": "simple", "variations": [102]},
    ],
)
def test_invalid_product_and_variant_identity(change):
    with pytest.raises(ReviewInputError) as caught:
        parse_product(encoded(product() | change), expected_slug="example-headphones")
    assert caught.value.code == "source_data_invalid"


def test_simple_product_and_required_fields():
    obj = product() | {"type": "simple", "variations": []}
    assert parse_product(encoded(obj), expected_slug=obj["slug"]).variant_ids == ()
    for key in ("id", "slug", "name", "type", "variations"):
        missing = dict(obj)
        del missing[key]
        with pytest.raises(ReviewInputError):
            parse_product(encoded(missing), expected_slug=obj["slug"])


def test_required_review_fields_and_parent_boolean_reject():
    for key in ("id", "product_id", "status", "review"):
        row = records()[0]
        del row[key]
        with pytest.raises(ReviewInputError):
            page([row])
    with pytest.raises(ReviewInputError):
        parse_product(encoded(product() | {"parent_id": False}), expected_slug="example-headphones")


def test_aggregate_text_and_malformed_html_reject_safely():
    rows = [
        {"id": i, "product_id": 101, "status": "approved", "review": "x" * 5000}
        for i in range(1, 52)
    ]
    assert len(encoded(rows)) < MAX_PAGE_BYTES
    with pytest.raises(ReviewInputError) as caught:
        page(rows)
    assert caught.value.code == "source_limit"
    with pytest.raises(ReviewInputError) as caught:
        page([records()[0] | {"review": "<![broken]>"}])
    assert caught.value.code == "source_data_invalid"


@pytest.mark.parametrize("data", [b'{"id":1,"id":2}', b"NaN", b"\xff", b"[", b"{}"])
def test_untrusted_bytes_reject_without_decoder_details(data):
    with pytest.raises(ReviewInputError) as caught:
        parse_review_page(data, product_id=101, today=TODAY)
    assert caught.value.code == "source_data_invalid"


def test_body_and_page_ceiling_reject_instead_of_truncate():
    for data in (b" " * (MAX_PAGE_BYTES + 1), encoded([records()[0]] * 101)):
        with pytest.raises(ReviewInputError) as caught:
            parse_review_page(data, product_id=101, today=TODAY)
        assert caught.value.code == "source_limit"


def test_html_is_inert_and_hidden_content_is_omitted():
    row = records()[0] | {
        "review": "<p>Clear<br/>sound</p><!--ignored--><style>hidden</style>"
        '<template><b>hidden</b></template><iframe src="https://example.invalid">hidden</iframe>'
        "<object>hidden</object><script/>Still text &lt;img src=x onerror=alert(1)&gt;"
    }
    text = page([row])[0].review.text
    assert "hidden" not in text and "ignored" not in text
    assert "Clear\nsound" in text
    # Decoded tag-looking prose stays text; consumers must keep React escaping.
    assert "<img src=x onerror=alert(1)>" in text
