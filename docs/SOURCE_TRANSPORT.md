# E05 continuation — bounded metadata transport

Date: 2026-10-31. Status: **transport component implemented and tested with synthetic streams; full E05 remains BLOCKED.** No source is approved, resolver integrated, egress restriction verified or real provider accessed. E06 has not started. The website's serving routes do not import or call this transport.

## What changed

`api/app/source_transport.py` adds `fetch_product_metadata` using the existing runtime dependencies AnyIO and h11 plus Python's SSL library. No dependency, generic browser crawler, custom HTTP parser, queue, database or endpoint was added. The transport only handles the fixed product metadata lookup produced by `source_collection.product_request`; it does not fetch a user URL or reviews, paginate, resolve product identity, produce findings or return a public product report.

Inputs are internal server arguments: a candidate product URL, trusted source registry, server-held authorization bytes, caller-resolved addresses, collection budget and real deployment network exclusions. The default registry remains empty and authorization absent, so ordinary/default invocation fails before any connection. Test-only policy injection does not admit a merchant or prove permission. No environment switch enables live collection.

The transport revalidates every supplied address using existing destination guards, selects only the first validated IP and makes one connection attempt. It does not resolve names or fall back/retry. AnyIO is passed the numeric peer with port 443, `tls=True`, the original source hostname as `tls_hostname` and a fresh default SSL context with hostname/certificate verification. After connection it checks the actual socket peer address/port before sending authorization. Fixed GET/Host/Accept/identity encoding/Connection-close headers are generated internally. No proxy, cookie jar, netrc or ambient HTTP authentication exists in this path. Authorization is bounded server-only printable bytes and is never placed in the URL.

Each connect/write/read awaits an actual AnyIO timeout, capped at one second or the remaining collection deadline. An outer timeout covers the whole operation. Reads request at most 16 KiB; raw response headers are capped before feeding them to h11. Duplicate/framing headers are checked before h11's normalization, retaining the previous safeguards. h11 handles HTTP framing and chunk decoding; trailer fields and already-buffered extra messages are rejected. Unexpected media/compression, redirect/access/status/schema/length/size errors yield fixed safe errors, never partial success. The body must be strict UTF-8 JSON before it is returned as internal bytes.

There is also a stricter raw HTTP byte ceiling of 278,528 bytes per exchange (16 KiB headers plus 256 KiB wire payload). Chunk framing overhead consumes that ceiling; a fully sized body with excessive chunk overhead can be rejected. Existing decoded-body and aggregate budgets remain in force. These are initial unmeasured bounds, not advertised source capacity.

Source membership/expiry is checked again before output, so removal or expiry during a request discards the result. Every owned stream is force-closed in finally, including successful calls, errors, stalled reads/writes and caller cancellation. Attempt reservations are not refunded. A timeout immediately after connection still closes the returned stream before sending credentials. The caller must still integrate existing API admission and keep any separately running CPU work admitted until it finishes.

## Verification and its limits

Twenty-eight cases in `api/tests/test_source_transport.py` replace only the module's connector binding with authored synthetic streams. Tests do not patch the shared AnyIO connector or open real sockets. They cover configured numeric peer/original TLS hostname/secure context, empty-registry and missing-secret refusal, mismatch before authentication, simulated certificate failure/no retry, redirects/auth/throttle errors, malformed/truncated/non-JSON/compressed bodies, raw header/length/byte caps, chunk framing/trailers, revocation, actual timed stalled reads/writes and cancellation/cleanup.

The native behavior was inspected in the installed pinned AnyIO implementation: `_core/_sockets.py` takes a numeric-address path and passes the original TLS hostname to TLSStream; `streams/tls.py` exposes underlying socket attributes and handles forced closure. This is implementation evidence, not a live DNS-rebinding, certificate-handshake or provider egress test. No supported retailer, permission, provider data or production capacity is claimed.

The initial restricted test run stalled and was interrupted; the synthetic suite completed outside that restriction. Two large-body parametrizations initially produced test setup errors with oversized automatic IDs; short descriptive IDs resolved the setup problem. Final checks pass without disabling cases or guards.

Full repository verification: 358 backend tests, 28 offline tests, 27 frontend tests; dependency consistency, Ruff, ESLint, type checking and production build pass. Both current frozen research reports verify unchanged. The local site was opened for the owner and still displays the existing paste/CSV interface, because this transport is unconnected.

## Still blocked before live activation or E05 completion

- E02 source permission/access, target market, narrowed credential capability, quota/cost, expiry/revocation and permitted field/display use.
- A bounded source DNS resolver, actual resolver-to-peer workflow and provider/network egress restrictions, with independent verification. Supplied-address tests cannot stand in for real resolver/egress controls.
- A reviewed source registry and secret loading arrangement, source-wide concurrency and existing API admission integration. No publicly selectable endpoint, IP list or authorization header may be exposed.
- An actual permitted provider probe and source-specific schema/limits evidence. Metadata JSON transport success alone does not establish review access or validate product identity.
- Later E06 sample/pagination/provenance and E07/E08 API/UI work. No live feature can be simulated using these tests.

This continues E05; it does not silently skip to E06 or pass E02. Contact stays blank, public numeric scores withheld, NO TRAIN, deployment deferred. See [SOURCE_COLLECTION.md](SOURCE_COLLECTION.md) for the existing guards and [URL_INGESTION.md](URL_INGESTION.md) for the complete planned contract.
