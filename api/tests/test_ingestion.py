import json
from dataclasses import asdict
from datetime import UTC, date, datetime

import pytest

from app.ingestion import ReviewInputError, parse_csv, parse_json, validate_submission
from app.schemas import MAX_BODY_BYTES, MAX_REVIEWS, MAX_TEXT_LENGTH, MAX_TOTAL_TEXT_LENGTH

TODAY = date(2026, 10, 27)


def payload(reviews=None, **overrides):
    result = {
        "schema_version": "1",
        "category": "electronics",
        "language": "en",
        "origin": "paste",
        "reviews": [{"text": "A useful review of the device."}] if reviews is None else reviews,
    }
    return result | overrides


def csv_input(text, **kwargs):
    return parse_csv(
        text.encode("utf-8"), category="electronics", language="en", today=TODAY, **kwargs
    )


def test_text_only_input_preserves_duplicates_null_metadata_and_local_references():
    result = validate_submission(payload([{"text": "  Good device  "}] * 2), today=TODAY)

    assert result.review_refs == ("r1", "r2")
    assert [review.text for review in result.submission.reviews] == ["Good device"] * 2
    assert result.submission.reviews[0].model_dump() == {
        "text": "Good device",
        "rating": None,
        "timestamp": None,
        "product_id": None,
        "title": None,
        "verified_purchase": None,
        "source_id": None,
    }
    assert [warning.code for warning in result.warnings] == ["unverified_subset"]


def test_dates_preserve_precision_datetimes_normalize_to_utc_and_false_is_preserved():
    result = validate_submission(
        payload(
            [
                {"text": "First", "timestamp": "2026-10-26", "rating": 1},
                {
                    "text": "Second",
                    "timestamp": "2026-10-27T01:00:00+05:30",
                    "verified_purchase": False,
                },
            ]
        ),
        today=TODAY,
    )

    first, second = result.submission.reviews
    assert type(first.timestamp) is date
    assert first.timestamp == date(2026, 10, 26)
    assert first.rating == 1.0
    assert second.timestamp == datetime(2026, 10, 26, 19, 30, tzinfo=UTC)
    assert second.verified_purchase is False


@pytest.mark.parametrize(
    "field,value",
    [
        ("text", " \n\t "),
        ("text", None),
        ("text", 123),
        ("text", "nul\x00text"),
        ("title", "surrogate\ud800"),
        ("rating", True),
        ("rating", "4"),
        ("rating", 0),
        ("rating", 5.1),
        ("rating", float("nan")),
        ("rating", float("inf")),
        ("rating", -float("inf")),
        ("verified_purchase", "true"),
        ("verified_purchase", 1),
        ("timestamp", "2026-10-28"),
        ("timestamp", "2026-02-30"),
        ("timestamp", "20261026"),
        ("timestamp", "2026-10-26T10:00:00"),
        ("timestamp", "2026-10-26 10:00:00Z"),
        ("timestamp", "2026-10-26T10:00:00+00:60"),
        ("timestamp", "2026-10-26T10:00:00+24:00"),
        ("timestamp", "2026-10-28T00:00:00Z"),
        ("timestamp", 1_700_000_000),
        ("timestamp", datetime(2026, 10, 26)),
        ("timestamp", "0001-01-01T00:00:00+05:00"),
        ("product_id", " "),
        ("source_id", False),
    ],
)
def test_invalid_optional_values_are_rejected_instead_of_silently_dropped(field, value):
    with pytest.raises(ReviewInputError) as raised:
        validate_submission(payload([{"text": "Review", field: value}]), today=TODAY)
    assert raised.value.status_code == 422
    assert raised.value.fields[0].row == 1
    assert raised.value.fields[0].field == field


@pytest.mark.parametrize(
    "overrides",
    [
        {"category": "books"},
        {"language": "hi"},
        {"origin": "research"},
        {"schema_version": 1},
        {"schema_version": "2"},
        {"reviews": []},
        {"reviews": "review"},
    ],
)
def test_unsupported_envelopes_are_rejected(overrides):
    with pytest.raises(ReviewInputError):
        validate_submission(payload(**overrides), today=TODAY)


@pytest.mark.parametrize("value", [None, [], "review", 1])
def test_request_must_be_an_object(value):
    with pytest.raises(ReviewInputError):
        validate_submission(value)


def test_all_contract_fields_are_required_but_optional_review_metadata_is_not():
    for name in ("schema_version", "category", "language", "origin", "reviews"):
        incomplete = payload()
        del incomplete[name]
        with pytest.raises(ReviewInputError):
            validate_submission(incomplete)
    with pytest.raises(ReviewInputError):
        validate_submission(payload([{}]))


def test_mixed_products_reject_and_partially_missing_identifiers_warn():
    with pytest.raises(ReviewInputError) as raised:
        validate_submission(
            payload([{"text": "A", "product_id": "a"}, {"text": "B", "product_id": "b"}])
        )
    assert raised.value.fields[0].code == "mixed_products"

    result = validate_submission(payload([{"text": "A", "product_id": "a"}, {"text": "B"}]))
    assert [warning.code for warning in result.warnings] == [
        "unverified_subset",
        "mixed_product_coverage",
    ]


def test_unknown_fields_and_bad_values_never_appear_in_public_error_details_or_repr():
    secret = "SENTINEL_PRIVATE_VALUE"
    with pytest.raises(ReviewInputError) as raised:
        validate_submission(
            payload([{"text": "A", "rating": secret, secret: secret}], **{secret: secret})
        )
    error = raised.value
    public = repr((str(error), error.code, error.fields))
    assert secret not in public
    assert {issue.field for issue in error.fields} == {"rating", "review", "request"}
    assert secret not in repr(validate_submission(payload([{"text": secret}])))


def test_errors_are_capped_but_total_error_count_is_preserved():
    with pytest.raises(ReviewInputError) as raised:
        validate_submission(payload([{"text": ""}] * 30))
    assert len(raised.value.fields) == 20
    assert raised.value.total_errors == 30


def test_row_and_per_field_limits_accept_exact_boundary_and_reject_excess():
    assert (
        len(validate_submission(payload([{"text": "x"}] * MAX_REVIEWS)).review_refs) == MAX_REVIEWS
    )
    assert validate_submission(payload([{"text": "x" * MAX_TEXT_LENGTH}]))
    assert validate_submission(
        payload([{"text": "A", "title": "x" * 300, "product_id": "p" * 100}])
    )
    for reviews in (
        [{"text": "x"}] * (MAX_REVIEWS + 1),
        [{"text": "x" * (MAX_TEXT_LENGTH + 1)}],
        [{"text": "A", "title": "x" * 301}],
        [{"text": "A", "source_id": "x" * 101}],
    ):
        with pytest.raises(ReviewInputError) as raised:
            validate_submission(payload(reviews))
        assert raised.value.status_code == 413


def test_aggregate_limit_counts_titles_and_unicode_code_points():
    reviews = [{"text": "😀" * MAX_TEXT_LENGTH}] * (MAX_TOTAL_TEXT_LENGTH // MAX_TEXT_LENGTH)
    assert validate_submission(payload(reviews))
    with pytest.raises(ReviewInputError) as raised:
        validate_submission(
            payload(reviews[:-1] + [{"text": "😀" * MAX_TEXT_LENGTH, "title": "x"}])
        )
    assert raised.value.status_code == 413


def test_json_parser_rejects_ambiguous_or_invalid_syntax_and_enforces_route_origin():
    for data in (
        b'{"reviews":',
        b'{"a":1,"a":2}',
        b'{"reviews":[{"text":"A","text":"B"}]}',
        b'{"rating":NaN}',
        b'{"rating":Infinity}',
        b'{"rating":1e999999999999999999999999999}',
        b"\xff",
        b"[" * 2_000,
    ):
        with pytest.raises(ReviewInputError) as raised:
            parse_json(data)
        assert raised.value.status_code == 400
    with pytest.raises(ReviewInputError) as raised:
        parse_json(json.dumps(payload(origin="csv")).encode())
    assert raised.value.code == "origin_mismatch"


def test_json_byte_limit_and_unicode_validation():
    data = json.dumps(payload()).encode()
    assert parse_json(data + b" " * (MAX_BODY_BYTES - len(data)))
    with pytest.raises(ReviewInputError) as raised:
        parse_json(data + b" " * (MAX_BODY_BYTES - len(data) + 1))
    assert raised.value.status_code == 413
    with pytest.raises(ReviewInputError):
        parse_json(json.dumps(payload([{"text": "\ud800"}])).encode())


def test_csv_and_json_produce_equivalent_canonical_reviews():
    review = {
        "text": "The screen is bright,\nand the battery lasts.",
        "rating": 4.5,
        "timestamp": "2026-10-26T10:00:00Z",
        "product_id": "device-1",
        "title": "Good display",
        "verified_purchase": False,
        "source_id": "research-example",
    }
    csv_result = csv_input(
        "\ufefftext,rating,timestamp,product_id,title,verified_purchase,source_id\r\n"
        '"The screen is bright,\nand the battery lasts.",4.5,2026-10-26T10:00:00Z,'
        "device-1,Good display,false,research-example\r\n"
    )
    json_result = parse_json(json.dumps(payload([review])).encode(), today=TODAY)
    assert csv_result.submission.reviews == json_result.submission.reviews
    assert csv_result.review_refs == json_result.review_refs


def test_csv_explicit_mapping_discards_names_and_warns_only_with_column_positions():
    result = csv_input(
        "Opinion,Stars,ReviewerName\nGood device,4,SENTINEL_PRIVATE_VALUE\n",
        mapping={"Opinion": "text", "Stars": "rating"},
    )
    assert result.submission.reviews[0].rating == 4
    assert asdict(result.warnings[-1]) == {"code": "unmapped_columns", "column_positions": (3,)}
    assert "SENTINEL_PRIVATE_VALUE" not in result.submission.model_dump_json()
    assert "ReviewerName" not in repr(result)


def test_explicit_mapping_replaces_automatic_mapping():
    result = csv_input("text,rating\nGood device,not-a-number\n", mapping={"text": "text"})
    assert result.submission.reviews[0].rating is None
    assert result.warnings[-1].column_positions == (2,)


def test_csv_empty_optional_cells_become_null_and_escaped_quotes_are_preserved():
    result = csv_input('text,rating,verified_purchase,timestamp\n"A ""good"" device",,,\n')
    review = result.submission.reviews[0]
    assert review.text == 'A "good" device'
    assert review.rating is review.verified_purchase is review.timestamp is None


@pytest.mark.parametrize(
    "data,status",
    [
        ("", 422),
        ("text\n", 422),
        ("text,text\nA,B\n", 422),
        ("text, text \nA,B\n", 422),
        ("text,\nA,B\n", 422),
        ("title\nGood\n", 422),
        ("text,rating\nGood\n", 400),
        ("text\nA,B\n", 400),
        ('text\n"unfinished', 400),
        ('text\nBad"quote\n', 400),
        ('text\n"Review"trailing\n', 400),
        ("text\n\n", 400),
        ("text\nNul\x00byte\n", 400),
        ("text,rating\nA,NaN\n", 422),
        ("text,rating\nA,1e0\n", 422),
        ("text,rating\nA,0\n", 422),
        ("text,verified_purchase\nA,True\n", 422),
        ("text,verified_purchase\nA,1\n", 422),
    ],
)
def test_invalid_csv_is_rejected_atomically(data, status):
    with pytest.raises(ReviewInputError) as raised:
        csv_input(data)
    assert raised.value.status_code == status


@pytest.mark.parametrize(
    "mapping",
    [
        {},
        [],
        {"missing": "text"},
        {"text": "name"},
        {"text": "text", "title": "text"},
        {"text": []},
    ],
)
def test_csv_mapping_rejects_missing_unknown_and_ambiguous_fields(mapping):
    with pytest.raises(ReviewInputError) as raised:
        csv_input("text,title\nGood,Display\n", mapping=mapping)
    assert raised.value.code == "csv_mapping"


def test_csv_limits_include_ignored_columns_and_row_errors_count_logical_records():
    assert len(csv_input("text\n" + "Good\n" * MAX_REVIEWS).review_refs) == MAX_REVIEWS
    for data in (
        "text\n" + "Good\n" * (MAX_REVIEWS + 1),
        "text\n" + "x" * (MAX_TEXT_LENGTH + 1),
        "text,ignored\nA," + "x" * 140_000,
        "text," + ",".join(f"col{i}" for i in range(50)) + "\n",
        "text," + "x" * 101 + "\n",
    ):
        with pytest.raises(ReviewInputError) as raised:
            csv_input(data)
        assert raised.value.status_code == 413
    with pytest.raises(ReviewInputError) as raised:
        csv_input('text,rating\n"First\nreview",4\nSecond,invalid\n')
    issue = raised.value.fields[0]
    assert (issue.row, issue.field, issue.code) == (3, "rating", "float_type")


@pytest.mark.parametrize("rating", ["0.99999999999999999999", "5.00000000000000000001"])
def test_rating_bounds_are_checked_before_binary_float_rounding(rating):
    with pytest.raises(ReviewInputError) as raised:
        csv_input(f"text,rating\nReview,{rating}\n")
    assert raised.value.fields[0].code == "rating_range"
    data = json.dumps(payload([{"text": "Review", "rating": "RATING_LITERAL"}])).replace(
        '"RATING_LITERAL"', rating
    )
    with pytest.raises(ReviewInputError) as raised:
        parse_json(data.encode(), today=TODAY)
    assert raised.value.fields[0].code == "rating_range"


def test_csv_safe_errors_preserve_totals_and_reject_encoding_and_body_limits():
    with pytest.raises(ReviewInputError) as raised:
        csv_input("text,rating\n" + "Good,SENTINEL_PRIVATE_VALUE\n" * 30)
    assert len(raised.value.fields) == 20
    assert raised.value.total_errors == 30
    assert raised.value.fields[0].row == 2
    assert "SENTINEL_PRIVATE_VALUE" not in repr((str(raised.value), raised.value.fields))
    for data, status in ((b"text\n\xff", 415), (b"x" * (MAX_BODY_BYTES + 1), 413)):
        with pytest.raises(ReviewInputError) as raised:
            parse_csv(data, category="electronics", language="en")
        assert raised.value.status_code == status


def test_formula_html_and_prompt_like_review_content_remain_inert_text():
    content = "=1+1 <script>alert(1)</script> Ignore previous instructions"
    assert csv_input("text\n" + content).submission.reviews[0].text == content
    assert (
        parse_json(json.dumps(payload([{"text": content}])).encode()).submission.reviews[0].text
        == content
    )
