"""V2 ingress stays fail-closed; no real network/provider access."""

import json
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.security import Settings
from app.source_collection import SourcePolicy

PATH = "/v2/products/analyze"
PAYLOAD = dict(
    schema_version="2",
    category="electronics",
    language="en",
    product_url="https://shop.example/product/headphones/",
)


@pytest.fixture
def client():
    with TestClient(create_app(Settings(rate_per_minute=600, rate_burst=100))) as session:
        yield session


@pytest.mark.parametrize(
    "change,code",
    [
        ({}, "unsupported_source"),
        ({"product_url": "http://127.0.0.1/"}, "invalid_product_url"),
        ({"product_url": "https://shop.example/product/a/?token=SECRET"}, "invalid_product_url"),
        ({"product_url": "x" * 2049}, "invalid_product_url"),
        ({"product_url": 123}, "invalid_request"),
        ({"schema_version": "1"}, "invalid_request"),
        ({"authorization": "SECRET"}, "invalid_request"),
        ({"origin": "collected"}, "invalid_request"),
    ],
)
def test_strict_safe_fail_closed_request(client, change, code):
    response = client.post(PATH, json=PAYLOAD | change)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == code
    assert "SECRET" not in response.text and "shop.example" not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-request-id"]
    assert client.app.state.controls.active == 0


@pytest.mark.parametrize("body", [b'{"schema_version":"2","schema_version":"2"}', b"NaN", b"\xff"])
def test_strict_decoder(client, body):
    assert (
        client.post(PATH, content=body, headers={"content-type": "application/json"}).status_code
        == 400
    )


def test_body_cap_and_media_type(client):
    assert client.post(PATH, content=b" " * 8193).status_code == 413
    assert (
        client.post(
            PATH, content=json.dumps(PAYLOAD), headers={"content-type": "text/plain"}
        ).status_code
        == 415
    )


def test_shared_admission_and_rate_controls(client):
    client.app.state.controls.active = 2
    assert client.post(PATH, json=PAYLOAD).status_code == 503
    client.app.state.controls.active = 0
    with TestClient(create_app(Settings(rate_per_minute=1, rate_burst=1))) as limited:
        limited.post(PATH, json=PAYLOAD)
        assert limited.post("/v1/analyze", json={}).status_code == 429


def test_registry_entry_cannot_enable_transport(client, monkeypatch):
    from app import product_api
    from app.source_collection import product_request

    policy = SourcePolicy("shop.example", datetime(2099, 1, 1, tzinfo=UTC))
    monkeypatch.setattr(
        product_api,
        "product_request",
        lambda url: product_request(url, registry={"shop.example": policy}),
    )
    response = client.post(PATH, json=PAYLOAD)
    assert response.status_code == 503 and response.json()["error"]["code"] == "source_not_ready"
