import asyncio
import json
import threading
import time

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import main
from app.ingestion import ReviewInputError
from app.main import create_app
from app.schemas import MAX_BODY_BYTES
from app.security import Controls, Settings


def payload(rows=None):
    return {
        "schema_version": "1",
        "category": "electronics",
        "language": "en",
        "origin": "paste",
        "reviews": reviews() if rows is None else rows,
    }


def make_app(**settings):
    return create_app(Settings(rate_per_minute=600, rate_burst=100, **settings))


def reviews(count=20):
    return [{"text": f"The screen and battery work for sample {index}."} for index in range(count)]


@pytest.fixture
def client():
    with TestClient(make_app(), raise_server_exceptions=False) as session:
        yield session


def test_health_is_minimal_and_analysis_returns_structured_result(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}
    response = client.post("/v1/analyze", json=payload())
    assert response.status_code == 200
    assert response.json()["score"]["value"] == 100
    assert response.json()["confidence"]["level"] is None
    assert response.headers["cache-control"] == "no-store"
    assert len(response.headers["x-request-id"]) == 32
    assert response.headers["x-content-type-options"] == "nosniff"


def test_errors_are_safe_structured_uncached_and_do_not_trust_client_request_ids(client):
    secret = "SENTINEL_PRIVATE_INPUT"
    data = payload([{"text": "Review", "rating": secret, secret: secret}] * 30)
    response = client.post("/v1/analyze", json=data, headers={"X-Request-ID": secret})
    assert response.status_code == 422
    error = response.json()["error"]
    assert len(error["fields"]) == 20
    assert error["total_errors"] == 60
    assert error["request_id"] == response.headers["x-request-id"]
    assert secret not in response.text
    assert secret not in str(dict(response.headers))
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize(
    "headers,body,status",
    [
        ({"Content-Type": "text/plain"}, b"{}", 415),
        ({"Content-Type": "application/json; charset=latin-1"}, b"{}", 415),
        ({"Content-Type": "application/json", "Content-Encoding": "gzip"}, b"{}", 415),
        ({"Content-Type": "application/json"}, b'{"a":1,"a":2}', 400),
        ({"Content-Type": "application/json"}, b"\xff", 400),
        ({"Content-Type": "application/json"}, b"x" * (MAX_BODY_BYTES + 1), 413),
    ],
    ids=["media", "charset", "compression", "duplicate-keys", "encoding", "body-limit"],
)
def test_request_format_and_body_limits_are_enforced(client, headers, body, status):
    response = client.post("/v1/analyze", content=body, headers=headers)
    assert response.status_code == status
    assert response.json()["error"]["code"]


def test_cors_allows_exact_origin_on_success_and_error_but_rejects_other_origins(client):
    origin = "http://127.0.0.1:3000"
    for data, status in ((payload(), 200), ({}, 422)):
        response = client.post("/v1/analyze", json=data, headers={"Origin": origin})
        assert response.status_code == status
        assert response.headers["access-control-allow-origin"] == origin
        assert "access-control-allow-credentials" not in response.headers
    preflight = client.options(
        "/v1/analyze",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert preflight.status_code == 200
    assert preflight.headers["cache-control"] == "no-store"
    rejected = client.post(
        "/v1/analyze", json=payload(), headers={"Origin": "https://untrusted.example"}
    )
    assert rejected.status_code == 403
    assert "access-control-allow-origin" not in rejected.headers


def test_unsupported_routes_and_methods_do_not_echo_request_details(client):
    response = client.get("/secret-SENTINEL")
    assert response.status_code == 404
    assert "SENTINEL" not in response.text
    assert client.get("/v1/analyze").status_code == 405


def test_csv_upload_matches_json_analysis_without_spooling_or_exposing_names(client, monkeypatch):
    def no_file(*args, **kwargs):
        raise AssertionError("Upload parser attempted to create a temporary file")

    monkeypatch.setattr("tempfile.SpooledTemporaryFile", no_file)
    monkeypatch.setattr("tempfile.NamedTemporaryFile", no_file)
    csv = "Opinion,ReviewerName\n" + "\n".join(row["text"] + ",SENTINEL_NAME" for row in reviews())
    response = client.post(
        "/v1/analyze/csv",
        files={"file": ("../../private.csv", csv.encode(), "text/csv")},
        data={
            "category": "electronics",
            "language": "en",
            "schema_version": "1",
            "mapping": json.dumps({"Opinion": "text"}),
        },
    )
    assert response.status_code == 200, response.text
    assert "SENTINEL_NAME" not in response.text
    assert "private.csv" not in response.text
    output = response.json()
    json_result = client.post("/v1/analyze", json=payload()).json()
    for field in ("score", "reviews", "findings", "confidence"):
        assert output[field] == json_result[field]
    assert output["warnings"][-1] == {"code": "unmapped_columns", "column_positions": [2]}


@pytest.mark.parametrize(
    "changes,status",
    [
        ({"language": None}, 422),
        ({"category": "books"}, 422),
        ({"mapping": "null"}, 422),
        ({"mapping": '{"text":"text","text":"rating"}'}, 400),
        ({"extra": "SENTINEL"}, 422),
        ({"category": "x" * 65}, 413),
    ],
)
def test_csv_form_metadata_is_strict(client, changes, status):
    data = {"category": "electronics", "language": "en", "schema_version": "1"} | changes
    data = {key: value for key, value in data.items() if value is not None}
    response = client.post(
        "/v1/analyze/csv",
        files={"file": ("reviews.csv", b"text\nGood device\n", "text/csv")},
        data=data,
    )
    assert response.status_code == status, response.text
    assert "SENTINEL" not in response.text


def test_csv_rejects_duplicate_files_bad_media_and_incomplete_multipart(client):
    data = {"category": "electronics", "language": "en", "schema_version": "1"}
    duplicate = client.post(
        "/v1/analyze/csv",
        data=data,
        files=[("file", ("a.csv", b"text\nGood\n")), ("file", ("b.csv", b"text\nGood\n"))],
    )
    assert duplicate.status_code == 422
    bad_media = client.post(
        "/v1/analyze/csv", data=data, files={"file": ("a.zip", b"not-csv", "application/zip")}
    )
    assert bad_media.status_code == 415
    incomplete = client.post(
        "/v1/analyze/csv",
        content=b"--abc\r\n",
        headers={"Content-Type": "multipart/form-data; boundary=abc"},
    )
    assert incomplete.status_code == 400


def test_multipart_limit_includes_envelope_and_mapping_is_bounded(client):
    data = {"category": "electronics", "language": "en", "schema_version": "1"}
    oversized = client.post(
        "/v1/analyze/csv",
        data=data,
        files={"file": ("reviews.csv", b"x" * MAX_BODY_BYTES, "text/csv")},
    )
    assert oversized.status_code == 413
    assert oversized.json()["error"]["code"] == "body_limit"
    large_mapping = client.post(
        "/v1/analyze/csv",
        data=data | {"mapping": " " * 4097},
        files={"file": ("reviews.csv", b"text\nGood device\n", "text/csv")},
    )
    assert large_mapping.status_code == 413
    assert large_mapping.json()["error"]["code"] == "multipart_field_limit"


def test_multipart_parser_diagnostics_do_not_log_malformed_private_headers(client, caplog):
    body = (
        b'--abc\r\nContent-Disposition: form-data; name="file"; filename="'
        + b"SENTINEL_PRIVATE_HEADER" * 500
        + b'"\r\n\r\ntext\nGood\n\r\n--abc--\r\n'
    )
    response = client.post(
        "/v1/analyze/csv",
        content=body,
        headers={"Content-Type": "multipart/form-data; boundary=abc"},
    )
    assert response.status_code == 400
    assert "SENTINEL" not in response.text + caplog.text


def test_json_request_accepts_exact_byte_limit_and_rejects_duplicate_content_type(client):
    data = json.dumps(payload()).encode()
    response = client.post(
        "/v1/analyze",
        content=data + b" " * (MAX_BODY_BYTES - len(data)),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 200
    duplicate = client.post(
        "/v1/analyze",
        content=data,
        headers=[("Content-Type", "application/json"), ("Content-Type", "text/plain")],
    )
    assert duplicate.status_code == 400


def test_metadata_and_personal_identifiers_do_not_leak_through_api_results(client):
    rows = [
        {
            "text": "The screen and battery work well. Contact user@example.com",
            "title": "Call +1 202 555 0123",
            "product_id": "SENTINEL_PRODUCT",
            "source_id": "SENTINEL_SOURCE",
        }
    ] * 20
    response = client.post("/v1/analyze", json=payload(rows))
    assert response.status_code == 200
    assert "SENTINEL" not in response.text
    assert "user@example.com" not in response.text
    assert "202 555 0123" not in response.text
    assert response.json()["coverage"]["redactions"] == {"email": 20, "phone": 20}


def test_unexpected_exception_is_sanitized_without_logging_reviews(client, monkeypatch, caplog):
    def fail(*args, **kwargs):
        raise RuntimeError("SENTINEL_PRIVATE_INPUT")

    monkeypatch.setattr(main, "analyze", fail)
    response = client.post("/v1/analyze", json=payload())
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "internal_error"
    assert "SENTINEL" not in response.text + caplog.text


def test_rate_limiting_ignores_forged_forwarding_headers_and_does_not_limit_health():
    with TestClient(create_app(Settings())) as session:
        for address in ("1.1.1.1", "2.2.2.2"):
            assert (
                session.post(
                    "/v1/analyze", json={}, headers={"X-Forwarded-For": address}
                ).status_code
                == 422
            )
        response = session.post("/v1/analyze", json={}, headers={"X-Forwarded-For": "3.3.3.3"})
        assert response.status_code == 429
        assert int(response.headers["retry-after"]) >= 1
        assert session.get("/health").status_code == 200


def test_limiter_refills_expires_keys_and_fails_closed_at_capacity():
    controls = Controls(Settings(limiter_capacity=1))
    controls.rate_check("private-client-a", 0)
    controls.rate_check("private-client-a", 0)
    with pytest.raises(ReviewInputError) as raised:
        controls.rate_check("private-client-a", 0)
    assert raised.value.status_code == 429
    controls.rate_check("private-client-a", 6)
    with pytest.raises(ReviewInputError) as raised:
        controls.rate_check("private-client-b", 6)
    assert raised.value.code == "limiter_capacity"
    controls.rate_check("private-client-b", 67)
    assert len(controls._clients) == 1
    assert all(isinstance(key, bytes) and len(key) == 32 for key in controls._clients)


@pytest.mark.parametrize(
    "settings",
    [
        {"allowed_origins": ["*"]},
        {"allowed_origins": ["https://example.com/path"]},
        {"allowed_origins": ["https://user:password@example.com"]},
        {"allowed_origins": ["https://example.com\n"]},
        {"allowed_origins": ["https://例子.example"]},
        {"max_concurrent": 3},
        {"rate_per_minute": 0},
        {"timeout_seconds": float("inf")},
        {"rate_per_minute": 1, "rate_burst": 2},
    ],
)
def test_invalid_server_configuration_fails_at_startup(settings):
    with pytest.raises(ValidationError):
        Settings(**settings)


def test_environment_configuration_is_explicit_and_validated(monkeypatch):
    monkeypatch.setenv("REVIEWTRUST_ALLOWED_ORIGINS", "https://reviewtrust.example")
    monkeypatch.setenv("REVIEWTRUST_RATE_PER_MINUTE", "20")
    assert Settings.from_env().allowed_origins == ("https://reviewtrust.example",)
    assert Settings.from_env().rate_per_minute == 20


async def exchange(app, chunks, headers=None, receive_delay=0):
    messages = []
    incoming = [
        {"type": "http.request", "body": chunk, "more_body": index < len(chunks) - 1}
        for index, chunk in enumerate(chunks)
    ]

    async def receive():
        await asyncio.sleep(receive_delay)
        return incoming.pop(0) if incoming else {"type": "http.disconnect"}

    async def send(message):
        messages.append(message)

    await app(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "scheme": "http",
            "path": "/v1/analyze",
            "raw_path": b"/v1/analyze",
            "query_string": b"",
            "root_path": "",
            "server": ("test", 80),
            "client": ("203.0.113.1", 1234),
            "headers": [(b"content-type", b"application/json")] + (headers or []),
        },
        receive,
        send,
    )
    status = next(
        message["status"] for message in messages if message["type"] == "http.response.start"
    )
    body = b"".join(
        message.get("body", b"") for message in messages if message["type"] == "http.response.body"
    )
    return status, json.loads(body)


def test_stream_limits_enforce_actual_bytes_without_or_with_false_content_length():
    valid = json.dumps(payload()).encode()
    assert asyncio.run(exchange(make_app(), [valid[:20], valid[20:]]))[0] == 200
    for headers in ([], [(b"content-length", b"1")]):
        status, body = asyncio.run(exchange(make_app(), [b" " * MAX_BODY_BYTES, b"x"], headers))
        assert status == 413
        assert body["error"]["code"] == "body_limit"
    assert asyncio.run(exchange(make_app(), [b"{}"], [(b"content-length", b"1")]))[0] == 400
    assert (
        asyncio.run(
            exchange(make_app(), [b"{}"], [(b"content-length", b"2"), (b"content-length", b"2")])
        )[0]
        == 400
    )


def test_slow_request_body_times_out_and_releases_admission():
    app = make_app(timeout_seconds=0.01)
    status, body = asyncio.run(exchange(app, [b"{}"], receive_delay=0.05))
    assert status == 503
    assert body["error"]["code"] == "request_timeout"
    assert app.state.controls.active == 0


def test_cancellation_keeps_slot_until_cpu_worker_finishes(monkeypatch):
    started, finish = threading.Event(), threading.Event()
    original = main.analyze

    def blocking(batch, deadline):
        started.set()
        assert finish.wait(3)
        return original(batch, deadline)

    monkeypatch.setattr(main, "analyze", blocking)
    app = make_app(max_concurrent=1)

    async def scenario():
        first = asyncio.create_task(exchange(app, [json.dumps(payload()).encode()]))
        try:
            assert await asyncio.to_thread(started.wait, 1)
            assert (await exchange(app, [b"{}"]))[0] == 503
            first.cancel()
            with pytest.raises(asyncio.CancelledError):
                await first
            assert app.state.controls.active == 1
        finally:
            finish.set()
        for _ in range(100):
            if app.state.controls.active == 0:
                break
            await asyncio.sleep(0.01)
        assert app.state.controls.active == 0

    asyncio.run(scenario())


def test_cpu_deadline_does_not_return_success_or_abandon_running_work(monkeypatch):
    original = main.analyze

    def delayed(batch, deadline):
        time.sleep(0.02)
        return original(batch, deadline)

    monkeypatch.setattr(main, "analyze", delayed)
    app = make_app(timeout_seconds=0.01)
    with TestClient(app) as session:
        response = session.post("/v1/analyze", json=payload())
    assert response.status_code == 503
    assert app.state.controls.active == 0
