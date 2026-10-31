"""Fixture-only analysis contracts and admitted worker integration."""

import json
import time
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient

from app.fixture_analysis import analyze_fixture_sample
from app.ingestion import ReviewInputError
from app.main import create_app
from app.security import run_worker
from app.source_parser import parse_product
from app.source_sample import assemble_fixture_sample

FIXTURES = Path(__file__).parent / "fixtures"
NOW = datetime(2026, 10, 31, tzinfo=UTC)


def sample(empty=False, exhausted=True):
    product = parse_product(
        (FIXTURES / "source_product.json").read_bytes(), expected_slug="example-headphones"
    )
    return assemble_fixture_sample(
        (b"[]" if empty else (FIXTURES / "source_reviews.json").read_bytes(),),
        product=product,
        window_started_at=NOW,
        window_finished_at=NOW,
        exhausted=exhausted,
    )


@pytest.mark.parametrize(
    "empty,exhausted,status",
    [
        (False, True, "complete"),
        (False, False, "partial"),
        (True, True, "empty"),
        (True, False, "partial"),
    ],
)
def test_versioned_fixture_provenance_empty_and_withheld_score(empty, exhausted, status):
    body = analyze_fixture_sample(sample(empty, exhausted), time.monotonic() + 10)
    report = json.loads(body)
    assert report["status"] == status
    assert report["schema_version"] == "2" and report["evidence_origin"] == "authored_fixture"
    assert report["available_reviews"] is None
    if empty:
        assert report["analysis"] is None and report["analyzed_reviews"] == 0
    else:
        result = report["analysis"]
        assert result["schema_version"] == "2" and result["origin"] == "authored_fixture"
        assert result["coverage"]["source_declaration"] == "authored_fixture"
        assert result["score"]["value"] is None
        assert "public_score_not_validated" in result["score"]["reason_codes"]
        assert result["confidence"]["level"] is None
        assert [row["ref"] for row in result["reviews"]] == ["r1", "r2"]
    assert "AUTHORED_NAME_SENTINEL" not in body.decode()


def test_deadline_and_title_normalization_bounds_are_atomic():
    with pytest.raises(ReviewInputError) as error:
        analyze_fixture_sample(sample(), time.monotonic() - 1)
    assert error.value.code == "analysis_timeout"
    value = sample()
    value = replace(value, product=replace(value.product, title="\ufdfa" * 100))
    with pytest.raises(ReviewInputError) as error:
        analyze_fixture_sample(value, time.monotonic() + 10)
    assert error.value.code == "source_limit"


def test_whole_envelope_byte_limit(monkeypatch):
    from app.fixture_analysis import FixtureReport

    monkeypatch.setattr(FixtureReport, "model_dump_json", lambda self: "x" * 2097153)
    with pytest.raises(ReviewInputError) as error:
        analyze_fixture_sample(sample(True), time.monotonic() + 10)
    assert error.value.code == "response_limit"


def test_fixture_success_in_test_only_route_reuses_admission_and_worker():
    api = create_app()
    path = "/v2/products/analyze"
    api.router.routes[:] = [
        route for route in api.router.routes if getattr(route, "path", None) != path
    ]

    async def fixture_route(request: Request):
        deadline = request.state.deadline

        def work():
            return Response(
                analyze_fixture_sample(sample(), deadline), media_type="application/json"
            )

        return await run_worker(request, work)

    api.add_api_route(path, fixture_route, methods=["POST"])
    with TestClient(api) as client:
        response = client.post(path, json={})
        assert (
            response.status_code == 200 and response.json()["evidence_origin"] == "authored_fixture"
        )
        assert response.headers["cache-control"] == "no-store"
        assert api.state.controls.active == 0
