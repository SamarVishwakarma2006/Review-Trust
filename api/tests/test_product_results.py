"""Authored wire-contract examples only; never evidence of provider access."""

from copy import deepcopy
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.product_results import ProductAnalysisResultV2, PublicScore

NOW = datetime(2026, 10, 31, tzinfo=UTC)


def payload():
    return dict(
        source=dict(
            id="authored-contract",
            adapter_version="authored-0.1",
            retrieved_at=NOW,
            attribution="Authored contract example",
        ),
        product=dict(
            title="Synthetic headphones", canonical_url="https://shop.example/product/headphones/"
        ),
        collection=dict(
            status="empty",
            stop_reason="empty",
            fetched_records=0,
            analyzed_reviews=0,
            overlap_records=0,
            pages_fetched=1,
            variant_scope="unknown",
            window_started_at=NOW,
            window_finished_at=NOW,
        ),
        analysis=None,
    )


def test_empty_and_unknown_zero_partial_round_trip_without_invented_totals():
    value = ProductAnalysisResultV2.model_validate(payload())
    assert ProductAnalysisResultV2.model_validate_json(value.model_dump_json()) == value
    assert value.analysis is None and value.collection.available_reviews is None
    body = payload()
    body["collection"].update(status="partial", stop_reason="source_window")
    assert ProductAnalysisResultV2.model_validate(body).collection.status == "partial"


@pytest.mark.parametrize(
    "change",
    [
        dict(status="complete", stop_reason="exhausted"),
        dict(status="empty", stop_reason="source_window"),
        dict(status="partial", stop_reason="exhausted"),
        dict(overlap_records=1),
        dict(fetched_records=101, overlap_records=101),
        dict(pages_fetched=6),
        dict(window_finished_at=NOW - timedelta(seconds=1)),
        dict(window_started_at=NOW.replace(tzinfo=None)),
        dict(available_reviews=0),
        dict(count_scope="selected_product"),
        dict(status="partial", stop_reason="row_limit"),
        dict(status="partial", stop_reason="page_limit"),
        dict(analyzed_reviews=1, fetched_records=1),
    ],
)
def test_collection_inconsistency_rejects_atomically(change):
    body = payload()
    body["collection"].update(change)
    with pytest.raises(ValidationError):
        ProductAnalysisResultV2.model_validate(body)


@pytest.mark.parametrize(
    "change",
    [
        dict(schema_version="1"),
        dict(ingestion_version="draft"),
        dict(secret="must not be accepted"),
    ],
)
def test_wrong_version_and_extra_fields_reject(change):
    with pytest.raises(ValidationError):
        ProductAnalysisResultV2.model_validate(payload() | change)


@pytest.mark.parametrize(
    "link",
    [
        "http://shop.example/",
        "https://user:secret@shop.example/",
        "https://shop.example/?token=x",
        "https://shop.example/#x",
        "https://shop.example:444/",
        "https://shop.example/\\evil",
        "https://shop.example/%2f",
    ],
)
def test_unsafe_canonical_link_rejects(link):
    body = payload()
    body["product"]["canonical_url"] = link
    with pytest.raises(ValidationError):
        ProductAnalysisResultV2.model_validate(body)


def test_no_numeric_or_undisclosed_public_score():
    safe = dict(
        status="withheld",
        value=None,
        reason_codes=["public_score_not_validated"],
        evaluated_signal_ids=[],
    )
    assert PublicScore(**safe).value is None
    for change in [
        dict(value=0),
        dict(value=100),
        dict(status="experimental"),
        dict(reason_codes=[]),
    ]:
        with pytest.raises(ValidationError):
            PublicScore(**(safe | change))


def test_retrieval_time_variant_and_title_bounds_reject():
    for section, change in [
        ("source", dict(retrieved_at=NOW + timedelta(seconds=1))),
        ("product", dict(variant="invented variant")),
        ("product", dict(title="x" * 301)),
    ]:
        body = deepcopy(payload())
        body[section].update(change)
        with pytest.raises(ValidationError):
            ProductAnalysisResultV2.model_validate(body)


def nonempty_payload():
    import time
    from types import SimpleNamespace

    from app.analysis import analyze_fields
    from app.schemas import ReviewInput

    # Authored hypothetical collected-wire example, not an actual collection or origin conversion.
    batch = SimpleNamespace(
        submission=SimpleNamespace(
            origin="collected", reviews=(ReviewInput(text="Authored example sound."),)
        ),
        review_refs=("r1",),
        warnings=(),
    )
    fields = analyze_fields(batch, time.monotonic() + 10)
    fields["schema_version"] = "2"
    fields["score"] = PublicScore(
        status="insufficient_evidence",
        value=None,
        reason_codes=["public_score_not_validated", *fields["score"].reason_codes],
        evaluated_signal_ids=[],
    )
    body = payload()
    body["collection"].update(
        status="complete", stop_reason="exhausted", fetched_records=1, analyzed_reviews=1
    )
    body["analysis"] = fields
    return body


def test_nonempty_complete_partial_and_collected_contract_round_trip():
    body = nonempty_payload()
    result = ProductAnalysisResultV2.model_validate(body)
    assert result.analysis.origin == "collected" and result.analysis.schema_version == "2"
    assert result.analysis.score.value is None and result.analysis.confidence.level is None
    assert ProductAnalysisResultV2.model_validate_json(result.model_dump_json()) == result
    body["collection"].update(status="partial", stop_reason="source_window")
    assert ProductAnalysisResultV2.model_validate(body).collection.status == "partial"


@pytest.mark.parametrize(
    "field,value",
    [
        ("origin", "paste"),
        ("origin", "authored_fixture"),
        ("schema_version", "1"),
        ("review_count", 2),
    ],
)
def test_nonempty_wrong_origin_version_and_count_reject(field, value):
    body = nonempty_payload()
    body["analysis"][field] = value
    with pytest.raises(ValidationError):
        ProductAnalysisResultV2.model_validate(body)
