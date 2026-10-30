"""Offline collection guards. No resolver, socket client, credentials or HTTP route."""

import ipaddress
import math
import re
import time
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import MappingProxyType
from urllib.parse import urlencode, urlsplit

from app.ingestion import ReviewInputError
from app.source_parser import MAX_PAGE_BYTES

_HOST = re.compile(
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?)+"
)
_PRODUCT_PATH = re.compile(r"/product/([a-z0-9]+(?:-[a-z0-9]+)*)/")
_MESSAGES = {
    "invalid_product_url": (422, "Supply a supported product link."),
    "unsupported_source": (422, "This product source is not supported."),
    "source_not_ready": (503, "Product collection is not available for this source."),
    "source_destination_blocked": (403, "The source destination is not permitted."),
    "request_timeout": (503, "The collection time budget was exceeded."),
    "source_rate_limited": (503, "Source request capacity is temporarily unavailable."),
    "source_limit": (502, "Source response exceeds the allowed limit."),
    "source_data_invalid": (502, "Source data could not be validated."),
    "source_redirect": (502, "The source returned an unsupported redirect."),
    "source_access_unavailable": (503, "Source access is currently unavailable."),
    "source_unavailable": (502, "The source is currently unavailable."),
}


def _error(code: str) -> ReviewInputError:
    status, message = _MESSAGES[code]
    return ReviewInputError(code, message, status)


@dataclass(frozen=True)
class SourcePolicy:
    """Trusted server configuration only; construction is not permission evidence."""

    host: str = field(repr=False)
    expires_at: datetime

    def __post_init__(self):
        if (
            not _HOST.fullmatch(self.host)
            or len(self.host) > 253
            or any(part.startswith("xn--") for part in self.host.split("."))
            or self.expires_at.utcoffset() is None
        ):
            raise ValueError("Invalid source policy configuration.")
        try:
            ipaddress.ip_address(self.host)
        except ValueError:
            return
        raise ValueError("Invalid source policy configuration.")


# No source is approved. A future registry needs E02 rights and E03 transport/egress evidence.
SOURCE_REGISTRY: Mapping[str, SourcePolicy] = MappingProxyType({})


@dataclass(frozen=True)
class RequestTarget:
    host: str = field(repr=False)
    path: str = field(repr=False)


def product_request(
    url: str,
    *,
    registry: Mapping[str, SourcePolicy] = SOURCE_REGISTRY,
    now: datetime | None = None,
) -> RequestTarget:
    """Extract a supported slug; never forward the user URL to a transport."""
    if (
        not isinstance(url, str)
        or not 1 <= len(url) <= 2048
        or not url.isascii()
        or any(ord(c) <= 32 or ord(c) == 127 for c in url)
        or any(c in url for c in "\\?#%")
    ):
        raise _error("invalid_product_url")
    try:
        parsed = urlsplit(url)
    except ValueError:
        raise _error("invalid_product_url") from None
    host = parsed.hostname or ""
    if (
        parsed.scheme != "https"
        or not _HOST.fullmatch(host)
        or parsed.netloc.lower() not in (host, host + ":443")
    ):
        raise _error("invalid_product_url")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise _error("invalid_product_url")
    path = _PRODUCT_PATH.fullmatch(parsed.path)
    if path is None or len(path[1]) > 100:
        raise _error("invalid_product_url")
    policy = registry.get(host)
    if policy is None:
        raise _error("unsupported_source")
    if policy.host != host or policy.expires_at <= (now or datetime.now(UTC)):
        raise _error("source_not_ready")
    query = urlencode(
        {
            "slug": path[1],
            "per_page": 2,
            "_fields": "id,name,slug,type,parent_id,variations",
        }
    )
    return RequestTarget(host, "/wp-json/wc/v3/products?" + query)


def validate_addresses(addresses: tuple[str, ...], *, denied_networks: tuple[str, ...] = ()):
    """Validate all DNS answers; a future transport must pin the returned peer itself."""
    try:
        networks = tuple(
            ipaddress.ip_network(value)
            for value in (
                "64:ff9b::/96",
                "64:ff9b:1::/48",
                "2002::/16",
                "2001::/32",
                *denied_networks,
            )
        )
        if not addresses or len(addresses) > 32:
            raise ValueError
        result = tuple(ipaddress.ip_address(value) for value in addresses)
        if any(
            not ip.is_global
            or ip.is_multicast
            or ip.is_reserved
            or getattr(ip, "ipv4_mapped", None) is not None
            or "%" in str(ip)
            or any(ip in network for network in networks)
            for ip in result
        ):
            raise ValueError
    except ValueError:
        raise _error("source_destination_blocked") from None
    return tuple(str(ip) for ip in result)


class SourceQuota:
    """Shared on one event loop; attempted/cancelled calls are never refunded."""

    # ponytail: process-local accounting; require shared/provider hard caps before multi-worker use.
    def __init__(self, attempts: int, window_seconds: float, *, clock=time.monotonic):
        if (
            type(attempts) is not int
            or attempts < 1
            or not math.isfinite(window_seconds)
            or window_seconds <= 0
        ):
            raise ValueError("Invalid source quota configuration.")
        self.limit, self.window, self.clock = attempts, window_seconds, clock
        self.started, self.used, self.cooldown = clock(), 0, 0.0

    def reserve(self):
        now = self.clock()
        if now < self.cooldown:
            raise _error("source_rate_limited")
        if now - self.started >= self.window:
            self.started, self.used = now, 0
        if self.used >= self.limit:
            raise _error("source_rate_limited")
        self.used += 1


class CollectionBudget:
    """Accounting helper, not a network timeout or a cancellation implementation."""

    def __init__(self, overall_deadline: float, quota: SourceQuota, *, clock=time.monotonic):
        if not math.isfinite(overall_deadline):
            raise ValueError("Invalid collection deadline.")
        self.clock, self.quota = clock, quota
        self.deadline = min(overall_deadline, clock() + 4)
        self.attempts, self.total_bytes = 0, 0

    def check(self):
        if self.clock() >= self.deadline:
            raise _error("request_timeout")

    def reserve(self):
        self.check()
        if self.attempts >= 6:
            raise _error("source_limit")
        self.quota.reserve()
        self.attempts += 1

    def response(self, status: int, headers: tuple[tuple[bytes, bytes], ...]):
        self.check()
        if len(headers) > 32 or sum(len(k) + len(v) for k, v in headers) > 16_384:
            raise _error("source_limit")
        values = {}
        for name, value in headers:
            if not re.fullmatch(rb"[!#$%&'*+.^_`|~0-9A-Za-z-]+", name) or any(
                c < 32 or c == 127 for c in value
            ):
                raise _error("source_data_invalid")
            name = name.lower()
            if name in values and name in {
                b"content-type",
                b"content-length",
                b"content-encoding",
                b"transfer-encoding",
            }:
                raise _error("source_data_invalid")
            values[name] = value
        if 300 <= status < 400:
            raise _error("source_redirect")
        if status in (401, 403):
            raise _error("source_access_unavailable")
        if status == 429:
            retry = values.get(b"retry-after", b"")
            seconds = min(int(retry), 60) if len(retry) <= 3 and retry.isdigit() else 60
            self.quota.cooldown = max(self.quota.cooldown, self.clock() + max(1, seconds))
            raise _error("source_rate_limited")
        if status != 200:
            raise _error("source_unavailable")
        media = values.get(b"content-type", b"").lower().replace(b" ", b"")
        if (
            media not in (b"application/json", b"application/json;charset=utf-8")
            or values.get(b"content-encoding", b"identity").lower() != b"identity"
        ):
            raise _error("source_data_invalid")
        length = values.get(b"content-length")
        transfer = values.get(b"transfer-encoding")
        if transfer not in (None, b"chunked") or (transfer is not None and length is not None):
            raise _error("source_data_invalid")
        if length is not None and (len(length) > 7 or not length.isdigit()):
            raise _error("source_data_invalid")
        expected = int(length) if length is not None else None
        if expected is not None and expected > MAX_PAGE_BYTES:
            raise _error("source_limit")
        return ResponseBudget(self, expected)


class ResponseBudget:
    def __init__(self, collection: CollectionBudget, expected: int | None):
        self.collection, self.expected, self.received = collection, expected, 0
        self.finished = False

    def accept(self, chunk: bytes):
        self.collection.check()
        if self.finished or not isinstance(chunk, bytes):
            raise _error("source_data_invalid")
        size = len(chunk)
        if self.received + size > MAX_PAGE_BYTES or self.collection.total_bytes + size > 1_048_576:
            raise _error("source_limit")
        self.received += size
        self.collection.total_bytes += size
        if self.expected is not None and self.received > self.expected:
            raise _error("source_data_invalid")

    def finish(self):
        self.collection.check()
        if self.finished:
            raise _error("source_data_invalid")
        if self.expected is not None and self.received != self.expected:
            raise _error("source_data_invalid")
        self.finished = True
