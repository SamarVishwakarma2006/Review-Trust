"""Unwired product-metadata transport. No source is registered or permitted by default."""

import ipaddress
import ssl
from collections.abc import Awaitable, Mapping

import anyio
import h11
from anyio import connect_tcp
from anyio.abc import SocketAttribute

from app.ingestion import ReviewInputError, decode_json
from app.source_collection import (
    SOURCE_REGISTRY,
    CollectionBudget,
    SourcePolicy,
    _error,
    product_request,
    validate_addresses,
)
from app.source_parser import MAX_PAGE_BYTES

IO_TIMEOUT = 1.0
HEADER_LIMIT = 16_384
WIRE_LIMIT = HEADER_LIMIT + MAX_PAGE_BYTES


async def _io(operation: Awaitable, budget: CollectionBudget):
    with anyio.fail_after(min(IO_TIMEOUT, max(0, budget.deadline - budget.clock()))):
        return await operation


async def fetch_product_metadata(
    url: str,
    addresses: tuple[str, ...],
    budget: CollectionBudget,
    *,
    authorization: bytes | None = None,
    registry: Mapping[str, SourcePolicy] = SOURCE_REGISTRY,
    denied_networks: tuple[str, ...] = (),
) -> bytes:
    """GET one fixed metadata request using caller-resolved, revalidated addresses.

    Internal server arguments only. A bounded resolver, permission/egress evidence and
    API admission integration are still required before any live source activation.
    """
    target = product_request(url, registry=registry)
    if (
        not isinstance(authorization, bytes)
        or not 1 <= len(authorization) <= 4096
        or any(c < 32 or c > 126 for c in authorization)
    ):
        raise _error("source_not_ready")
    peer = validate_addresses(addresses, denied_networks=denied_networks)[0]
    budget.reserve()
    stream = None
    try:
        with anyio.fail_after(max(0, budget.deadline - budget.clock())):
            context = ssl.create_default_context()
            stream = await _io(
                connect_tcp(peer, 443, tls=True, tls_hostname=target.host, ssl_context=context),
                budget,
            )
            budget.check()
            try:
                actual = stream.extra(SocketAttribute.remote_address)
                if (
                    ipaddress.ip_address(actual[0]) != ipaddress.ip_address(peer)
                    or actual[1] != 443
                ):
                    raise ValueError
            except (ValueError, LookupError, anyio.TypedAttributeLookupError):
                raise _error("source_destination_blocked") from None

            connection = h11.Connection(h11.CLIENT, max_incomplete_event_size=HEADER_LIMIT)
            request = h11.Request(
                method=b"GET",
                target=target.path.encode("ascii"),
                headers=[
                    (b"Host", target.host.encode("ascii")),
                    (b"Authorization", authorization),
                    (b"Accept", b"application/json"),
                    (b"Accept-Encoding", b"identity"),
                    (b"Connection", b"close"),
                ],
            )
            await _io(
                stream.send(connection.send(request) + connection.send(h11.EndOfMessage())), budget
            )

            # Bound raw headers before feeding h11, which otherwise normalizes duplicates.
            prefix = bytearray()
            while b"\r\n\r\n" not in prefix:
                remaining = HEADER_LIMIT - len(prefix)
                if remaining <= 0:
                    raise _error("source_limit")
                chunk = await _io(stream.receive(remaining), budget)
                if not chunk:
                    raise _error("source_data_invalid")
                prefix.extend(chunk)
            header, _ = bytes(prefix).split(b"\r\n\r\n", 1)
            lines = header.split(b"\r\n")[1:]
            if len(lines) > 32:
                raise _error("source_limit")
            raw_headers = []
            for line in lines:
                if b":" not in line:
                    raise _error("source_data_invalid")
                name, value = line.split(b":", 1)
                raw_headers.append((name, value.strip(b" ")))
            connection.receive_data(bytes(prefix))
            event = connection.next_event()
            if not isinstance(event, h11.Response):
                raise _error("source_data_invalid")
            body = budget.response(event.status_code, tuple(raw_headers))
            result = bytearray()
            wire_bytes = len(prefix)
            while True:
                event = connection.next_event()
                if event is h11.NEED_DATA:
                    try:
                        chunk = await _io(stream.receive(16_384), budget)
                    except anyio.EndOfStream:
                        chunk = b""
                    wire_bytes += len(chunk)
                    if wire_bytes > WIRE_LIMIT:
                        raise _error("source_limit")
                    connection.receive_data(chunk)
                elif isinstance(event, h11.Data):
                    data = bytes(event.data)
                    body.accept(data)
                    result.extend(data)
                elif isinstance(event, h11.EndOfMessage):
                    body.finish()
                    if event.headers or connection.trailing_data[0]:
                        raise _error("source_data_invalid")
                    try:
                        decode_json(bytes(result))
                    except ReviewInputError:
                        raise _error("source_data_invalid") from None
                    budget.check()
                    # Rights removal/expiry during the request must stop output too.
                    if product_request(url, registry=registry) != target:
                        raise _error("source_not_ready")
                    return bytes(result)
                else:
                    raise _error("source_data_invalid")
    except TimeoutError:
        raise _error("request_timeout") from None
    except h11.ProtocolError:
        raise _error("source_data_invalid") from None
    except (OSError, anyio.BrokenResourceError, anyio.ClosedResourceError, anyio.EndOfStream):
        raise _error("source_unavailable") from None
    finally:
        if stream is not None:
            await anyio.aclose_forcefully(stream)
