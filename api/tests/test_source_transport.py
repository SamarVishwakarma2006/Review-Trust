"""Synthetic streams only. Tests do not approve a source or open network sockets."""

import ssl
import time
from datetime import UTC, datetime

import anyio
import pytest

from app import source_transport as transport
from app.ingestion import ReviewInputError
from app.source_collection import CollectionBudget, SourcePolicy, SourceQuota

URL = "https://shop.example/product/authored-headphones/"
AUTH = b"Bearer AUTHORED_SECRET_NOT_A_CREDENTIAL"


def registry():
    return {"shop.example": SourcePolicy("shop.example", datetime(2099, 1, 1, tzinfo=UTC))}


def response(body=b"[]", headers=b"", status=b"200 OK"):
    return (
        b"HTTP/1.1 " + status + b"\r\nContent-Type: application/json\r\n" + headers + b"\r\n" + body
    )


class Stream:
    def __init__(self, raw, *, peer=("8.8.8.8", 443), stall=False, on_send=None):
        self.raw, self.peer, self.stall, self.on_send = raw, peer, stall, on_send
        self.sent = b""
        self.closed = False
        self.read_sizes = []

    def extra(self, attribute):
        return self.peer

    async def send(self, data):
        self.sent += data
        if self.on_send:
            self.on_send()

    async def receive(self, max_bytes):
        self.read_sizes.append(max_bytes)
        if self.stall:
            await anyio.sleep_forever()
        if not self.raw:
            raise anyio.EndOfStream
        chunk, self.raw = self.raw[:max_bytes], self.raw[max_bytes:]
        return chunk

    async def aclose(self):
        self.closed = True


def setup(monkeypatch, stream, *, connect_error=None):
    calls = []

    async def connect(peer, port, **kwargs):
        calls.append((peer, port, kwargs))
        if connect_error:
            raise connect_error
        return stream

    monkeypatch.setattr(transport, "connect_tcp", connect)
    return calls


def fetch(**overrides):
    async def run():
        kwargs = {
            "authorization": AUTH,
            "registry": registry(),
        } | overrides
        return await transport.fetch_product_metadata(
            URL,
            ("8.8.8.8",),
            CollectionBudget(time.monotonic() + 10, SourceQuota(20, 60)),
            **kwargs,
        )

    return anyio.run(run)


def test_peer_pinning_and_original_tls_host_with_no_ambient_headers(monkeypatch):
    stream = Stream(response(headers=b"Content-Length: 2\r\n"))
    calls = setup(monkeypatch, stream)
    assert fetch() == b"[]" and stream.closed
    assert len(calls) == 1 and calls[0][:2] == ("8.8.8.8", 443)
    tls = calls[0][2]
    assert tls["tls"] is True and tls["tls_hostname"] == "shop.example"
    assert tls["ssl_context"].check_hostname is True
    assert tls["ssl_context"].verify_mode == ssl.CERT_REQUIRED
    assert stream.sent.startswith(b"GET /wp-json/wc/v3/products?")
    assert b"Host: shop.example" in stream.sent and AUTH in stream.sent
    assert b"Cookie" not in stream.sent and b"Accept-Encoding: identity" in stream.sent


def test_default_registry_or_missing_credentials_stops_before_connect(monkeypatch):
    calls = setup(monkeypatch, Stream(response()))
    for overrides in ({"registry": {}}, {"authorization": None}, {"authorization": b"x\r\ny"}):
        with pytest.raises(ReviewInputError):
            fetch(**overrides)
    assert calls == []


@pytest.mark.parametrize("peer", [("127.0.0.1", 443), ("8.8.4.4", 443), ("8.8.8.8", 80)])
def test_connected_peer_mismatch_closes_before_sending_auth(monkeypatch, peer):
    stream = Stream(response(), peer=peer)
    setup(monkeypatch, stream)
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == "source_destination_blocked"
    assert stream.closed and stream.sent == b""


def test_certificate_failure_is_safe_and_not_retried(monkeypatch):
    stream = Stream(response())
    calls = setup(monkeypatch, stream, connect_error=ssl.SSLError("PRIVATE_SENTINEL"))
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == "source_unavailable" and len(calls) == 1
    assert "PRIVATE_SENTINEL" not in str(caught.value) and stream.sent == b""


@pytest.mark.parametrize(
    "raw,code",
    [
        (
            response(status=b"302 Found", headers=b"Location: https://private.example/\r\n"),
            "source_redirect",
        ),
        (response(status=b"401 Unauthorized"), "source_access_unavailable"),
        (
            response(status=b"429 Too Many Requests", headers=b"Retry-After: 2\r\n"),
            "source_rate_limited",
        ),
        (
            response(b"{}", headers=b"Content-Length: 2\r\nContent-Length: 2\r\n"),
            "source_data_invalid",
        ),
        (response(headers=b"Content-Encoding: gzip\r\n"), "source_data_invalid"),
        (response(b"[", headers=b"Content-Length: 2\r\n"), "source_data_invalid"),
        (response(b"NaN", headers=b"Content-Length: 3\r\n"), "source_data_invalid"),
        (response(b"\xff", headers=b"Content-Length: 1\r\n"), "source_data_invalid"),
        (response(b"not json"), "source_data_invalid"),
        (response(headers=b"X-Large: " + b"x" * 16_384 + b"\r\n"), "source_limit"),
        (response(headers=b"X-A: x\r\n" * 33), "source_limit"),
        (response(headers=b"Content-Length: 262145\r\n"), "source_limit"),
        (response(b"x" * 262_145), "source_limit"),
        (b"malformed\r\n\r\n", "source_data_invalid"),
    ],
    ids=lambda value: f"response-{len(value)}" if isinstance(value, bytes) else value,
)
def test_failure_closes_stream_and_never_returns_partial_body(monkeypatch, raw, code):
    stream = Stream(raw)
    calls = setup(monkeypatch, stream)
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == code
    assert AUTH.decode() not in str(caught.value)
    assert stream.closed and len(calls) == 1


def test_chunked_data_uses_h11_framing_and_trailers_are_rejected(monkeypatch):
    raw = response(b"2\r\n[]\r\n0\r\n\r\n", headers=b"Transfer-Encoding: chunked\r\n")
    stream = Stream(raw)
    setup(monkeypatch, stream)
    assert fetch() == b"[]" and stream.closed
    stream = Stream(raw.replace(b"0\r\n\r\n", b"0\r\nX-Trailer: hidden\r\n\r\n"))
    setup(monkeypatch, stream)
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == "source_data_invalid" and stream.closed


def test_source_revocation_during_request_discards_output(monkeypatch):
    policies = registry()
    stream = Stream(response(), on_send=policies.clear)
    setup(monkeypatch, stream)
    with pytest.raises(ReviewInputError):
        fetch(registry=policies)
    assert stream.closed


def test_stalled_read_is_actually_timed_out_and_closed(monkeypatch):
    stream = Stream(b"", stall=True)
    setup(monkeypatch, stream)
    monkeypatch.setattr(transport, "IO_TIMEOUT", 0.01)
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == "request_timeout" and stream.closed


def test_cancellation_closes_owned_stream(monkeypatch):
    stream = Stream(b"", stall=True)
    setup(monkeypatch, stream)

    async def run():
        async with anyio.create_task_group() as group:

            async def work():
                await transport.fetch_product_metadata(
                    URL,
                    ("8.8.8.8",),
                    CollectionBudget(time.monotonic() + 10, SourceQuota(20, 60)),
                    authorization=AUTH,
                    registry=registry(),
                )

            group.start_soon(work)
            while not stream.read_sizes:
                await anyio.sleep(0)
            group.cancel_scope.cancel()

    anyio.run(run)
    assert stream.closed


def test_mixed_dns_answers_are_rejected_before_connection(monkeypatch):
    calls = setup(monkeypatch, Stream(response()))

    async def run():
        await transport.fetch_product_metadata(
            URL,
            ("8.8.8.8", "127.0.0.1"),
            CollectionBudget(time.monotonic() + 10, SourceQuota(20, 60)),
            authorization=AUTH,
            registry=registry(),
        )

    with pytest.raises(ReviewInputError) as caught:
        anyio.run(run)
    assert caught.value.code == "source_destination_blocked" and calls == []


def test_deadline_immediately_after_connect_still_closes_returned_stream(monkeypatch):
    stream = Stream(response())
    tick = [100.0]

    async def connect(*args, **kwargs):
        tick[0] = 105.0
        return stream

    monkeypatch.setattr(transport, "connect_tcp", connect)

    async def run():
        quota = SourceQuota(20, 60, clock=lambda: tick[0])
        budget = CollectionBudget(110, quota, clock=lambda: tick[0])
        await transport.fetch_product_metadata(
            URL, ("8.8.8.8",), budget, authorization=AUTH, registry=registry()
        )

    with pytest.raises(ReviewInputError) as caught:
        anyio.run(run)
    assert caught.value.code == "request_timeout" and stream.closed and not stream.sent


def test_stalled_body_is_timed_out_after_valid_headers(monkeypatch):
    class StalledBody(Stream):
        async def receive(self, max_bytes):
            result = await super().receive(max_bytes)
            self.stall = True
            return result

    stream = StalledBody(response(b"", headers=b"Content-Length: 2\r\n"))
    setup(monkeypatch, stream)
    monkeypatch.setattr(transport, "IO_TIMEOUT", 0.01)
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == "request_timeout" and stream.closed


def test_stalled_send_is_timed_out_and_closed(monkeypatch):
    class StalledSend(Stream):
        async def send(self, data):
            await anyio.sleep_forever()

    stream = StalledSend(response())
    setup(monkeypatch, stream)
    monkeypatch.setattr(transport, "IO_TIMEOUT", 0.01)
    with pytest.raises(ReviewInputError) as caught:
        fetch()
    assert caught.value.code == "request_timeout" and stream.closed
