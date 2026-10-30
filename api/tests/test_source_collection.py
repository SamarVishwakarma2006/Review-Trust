"""Offline policy/accounting checks only; no live transport or source permissions."""

from datetime import UTC, datetime, timedelta
from urllib.parse import parse_qs, urlsplit

import pytest

from app.ingestion import ReviewInputError
from app.source_collection import (
    CollectionBudget,
    SourcePolicy,
    SourceQuota,
    product_request,
    validate_addresses,
)

NOW = datetime(2026, 10, 31, tzinfo=UTC)
URL = "https://shop.example/product/example-headphones/"
REGISTRY = {"shop.example": SourcePolicy("shop.example", NOW + timedelta(days=1))}
HEADERS = ((b"content-type", b"application/json"),)


class Clock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


def budget(attempts=20, overall=110):
    clock = Clock()
    quota = SourceQuota(attempts, 60, clock=clock)
    return CollectionBudget(overall, quota, clock=clock), clock


def test_default_registry_stays_closed_and_fixed_path_uses_only_slug():
    with pytest.raises(ReviewInputError) as caught:
        product_request(URL, now=NOW)
    assert caught.value.code == "unsupported_source"
    request = product_request(
        URL.replace("shop.example", "SHOP.EXAMPLE:443"), registry=REGISTRY, now=NOW
    )
    assert request.host == "shop.example"
    parts = urlsplit(request.path)
    assert parts.path == "/wp-json/wc/v3/products"
    assert parse_qs(parts.query) == {
        "slug": ["example-headphones"],
        "per_page": ["2"],
        "_fields": ["id,name,slug,type,parent_id,variations"],
    }
    assert "example-headphones" not in repr(request)


@pytest.mark.parametrize(
    "url",
    [
        "http://shop.example/product/a/",
        "file:///etc/passwd",
        "https://[",
        "https://shop.example:80/product/a/",
        "https://shop.example:/product/a/",
        "https://user@shop.example/product/a/",
        "https://shop.example./product/a/",
        "https://127.0.0.1/product/a/",
        "https://[::1]/product/a/",
        "https://2130706433/product/a/",
        "https://shop.example\\@bad.example/product/a/",
        URL + "?",
        URL + "#",
        URL + "?token=secret",
        URL + "\n",
        "https://shop.example/product/../a/",
        "https://shop.example/product/a%2fb/",
        "https://shop.example/product/%252e/",
        "https://shóp.example/product/a/",
        "https://shop.example/product/a",
        "https://shop.example/product/" + "a" * 101 + "/",
        "https://shop.example/" + "a" * 2048,
    ],
)
def test_rejected_url_never_builds_an_outbound_target(url):
    with pytest.raises(ReviewInputError) as caught:
        product_request(url, registry=REGISTRY, now=NOW)
    assert caught.value.code == "invalid_product_url"
    assert "secret" not in str(caught.value)


def test_source_suffix_spoof_and_expiry_or_mismatched_binding_reject():
    with pytest.raises(ReviewInputError) as caught:
        product_request(
            URL.replace("shop.example", "shop.example.evil.example"), registry=REGISTRY, now=NOW
        )
    assert caught.value.code == "unsupported_source"
    for registry in (
        {"shop.example": SourcePolicy("shop.example", NOW)},
        {"shop.example": SourcePolicy("another.example", NOW + timedelta(days=1))},
        {},
    ):
        with pytest.raises(ReviewInputError):
            product_request(URL, registry=registry, now=NOW)


@pytest.mark.parametrize(
    "host", ["127.0.0.1", "localhost", "bad.example.", "xn--test.example", "bad_thing.example"]
)
def test_invalid_trusted_policy_is_not_accepted(host):
    with pytest.raises(ValueError, match="Invalid source policy"):
        SourcePolicy(host, NOW)


@pytest.mark.parametrize(
    "addresses",
    [
        (),
        ("127.0.0.1",),
        ("0.0.0.0",),
        ("169.254.169.254",),
        ("10.0.0.1",),
        ("172.16.0.1",),
        ("192.168.0.1",),
        ("100.64.0.1",),
        ("224.0.0.1",),
        ("::1",),
        ("fe80::1",),
        ("fc00::1",),
        ("ff02::1",),
        ("::ffff:8.8.8.8",),
        ("64:ff9b::a00:1",),
        ("2002:0808:0808::1",),
        ("2606:4700:4700::1111%eth0",),
        ("8.8.8.8", "192.168.1.1"),
        ("not-an-address",),
        ("8.8.8.8",) * 33,
    ],
)
def test_all_dns_answers_must_pass_destination_policy(addresses):
    with pytest.raises(ReviewInputError) as caught:
        validate_addresses(addresses)
    assert caught.value.code == "source_destination_blocked"
    assert "169.254" not in str(caught.value)


def test_public_answers_and_real_internal_public_range_override():
    assert validate_addresses(("8.8.8.8", "2606:4700:4700::1111")) == (
        "8.8.8.8",
        "2606:4700:4700::1111",
    )
    with pytest.raises(ReviewInputError):
        validate_addresses(("8.8.8.8",), denied_networks=("8.8.8.0/24",))


def test_attempts_are_charged_shared_and_never_refunded():
    b, clock = budget(attempts=2)
    other = CollectionBudget(110, b.quota, clock=clock)
    b.reserve()
    other.reserve()
    with pytest.raises(ReviewInputError) as caught:
        b.reserve()
    assert caught.value.code == "source_rate_limited" and b.quota.used == 2
    clock.now += 60
    b.quota.reserve()
    assert b.quota.used == 1


def test_six_attempts_and_absolute_deadline_not_reset_by_activity():
    b, clock = budget()
    for _ in range(6):
        b.reserve()
    with pytest.raises(ReviewInputError) as caught:
        b.reserve()
    assert caught.value.code == "source_limit"
    clock.now = 104
    with pytest.raises(ReviewInputError) as caught:
        b.response(200, HEADERS)
    assert caught.value.code == "request_timeout"
    b, clock = budget(overall=101)
    clock.now = 101
    with pytest.raises(ReviewInputError):
        b.reserve()


@pytest.mark.parametrize(
    "status,code",
    [
        (301, "source_redirect"),
        (302, "source_redirect"),
        (307, "source_redirect"),
        (401, "source_access_unavailable"),
        (403, "source_access_unavailable"),
        (500, "source_unavailable"),
        (404, "source_unavailable"),
        (204, "source_unavailable"),
    ],
)
def test_upstream_errors_are_safe_and_no_retry_is_started(status, code):
    b, _ = budget()
    b.reserve()
    with pytest.raises(ReviewInputError) as caught:
        b.response(status, HEADERS + ((b"location", b"https://private.invalid/secret"),))
    assert caught.value.code == code and b.attempts == 1
    assert "secret" not in str(caught.value)


@pytest.mark.parametrize("retry", [b"2", b"999", b"999999999999999999999", b"a date", b"0"])
def test_provider_cooldown_is_bounded_without_sleep_or_retry(retry):
    b, clock = budget()
    with pytest.raises(ReviewInputError) as caught:
        b.response(429, HEADERS + ((b"retry-after", retry),))
    assert caught.value.code == "source_rate_limited"
    assert 1 <= b.quota.cooldown - clock.now <= 60
    with pytest.raises(ReviewInputError):
        b.quota.reserve()
    clock.now = b.quota.cooldown
    b.quota.reserve()


@pytest.mark.parametrize(
    "headers",
    [
        (),
        ((b"content-type", b"text/html"),),
        HEADERS + ((b"Content-Type", b"application/json"),),
        HEADERS + ((b"content-encoding", b"gzip"),),
        HEADERS + ((b"content-length", b"-1"),),
        HEADERS + ((b"content-length", b"2"), (b"Content-Length", b"2")),
        HEADERS + ((b"content-length", b"2"), (b"transfer-encoding", b"chunked")),
        HEADERS + ((b"transfer-encoding", b"other"),),
        HEADERS + ((b"bad header", b"x"),),
        HEADERS + ((b"x-test", b"x\r\ny"),),
    ],
)
def test_invalid_headers_and_compression_reject(headers):
    b, _ = budget()
    with pytest.raises(ReviewInputError) as caught:
        b.response(200, headers)
    assert caught.value.code == "source_data_invalid"


def test_bounded_headers_body_stream_count_and_length_mismatch():
    b, _ = budget()
    for headers in (
        HEADERS + ((b"x", b"x" * 16_384),),
        HEADERS + ((b"x", b"1"),) * 32,
        HEADERS + ((b"content-length", b"262145"),),
    ):
        with pytest.raises(ReviewInputError) as caught:
            b.response(200, headers)
        assert caught.value.code == "source_limit"
    body = b.response(200, HEADERS + ((b"content-length", b"2"),))
    body.accept(b"[")
    with pytest.raises(ReviewInputError):
        body.finish()
    body.accept(b"]")
    body.finish()
    with pytest.raises(ReviewInputError):
        body.accept(b"x")
    body = b.response(200, HEADERS)
    with pytest.raises(ReviewInputError) as caught:
        body.accept(b"x" * 262_145)
    assert caught.value.code == "source_limit"


def test_aggregate_bytes_and_chunked_body_are_counted_without_content_length():
    b, _ = budget()
    for _ in range(4):
        body = b.response(200, HEADERS + ((b"transfer-encoding", b"chunked"),))
        body.accept(b"x" * 262_144)
        body.finish()
    body = b.response(200, HEADERS)
    with pytest.raises(ReviewInputError) as caught:
        body.accept(b"x")
    assert caught.value.code == "source_limit" and b.total_bytes == 1_048_576


def test_finished_response_rejects_further_chunks_and_duplicate_completion():
    b, _ = budget()
    body = b.response(200, HEADERS)
    body.accept(b"[]")
    body.finish()
    for operation in (lambda: body.accept(b"extra"), body.finish):
        with pytest.raises(ReviewInputError) as caught:
            operation()
        assert caught.value.code == "source_data_invalid"


def test_body_accounting_checks_deadline_between_chunks():
    b, clock = budget()
    body = b.response(200, HEADERS)
    body.accept(b"[")
    clock.now = 104
    with pytest.raises(ReviewInputError) as caught:
        body.accept(b"]")
    assert caught.value.code == "request_timeout"
    assert body.received == 1
