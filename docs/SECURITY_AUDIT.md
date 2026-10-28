# Step 12 — Pre-deployment security audit

Date: 2026-10-28. **Repository audit and fixes complete. Public launch: NO GO until the owner/provider gates below are verified.** No service was deployed, account accessed, mailbox contacted, secret created or public URL fetched by the application. This is a scoped engineering review, not a penetration-test or compliance certification.

## Scope and approach

Reviewed FastAPI ingestion, multipart callbacks, canonical schemas, masking/normalization, signal computation, response construction, errors/logging, origin/rate/admission controls and cancellation; Next/React input/results, response validation, contact/privacy content, headers, runtime/build configuration; pinned npm/Python dependencies, ignored artifacts and offline evaluation boundaries. Existing tests and targeted live loopback probes supplied evidence. No arbitrary outbound fetching, user models, accounts, database, persisted uploads or application analytics were introduced.

Ponytail was applied throughout: enforce withholding once at the shared HTTP boundary; keep the audited pure offline arithmetic; reject excessive data instead of inventing truncation; reuse multipart's native 8,192-byte header cap; use Next's supported nonce mechanism; add no dependency, service, cache, queue, authentication system or configurable score escape hatch. Scope stayed within Step 12. Existing pending Step 11 files were preserved.

## Findings and disposition

| ID / priority | Evidence and consequence | Resolution / verification |
| --- | --- | --- |
| S12-01 High — unapproved numeric publication | Both API routes returned numeric indices despite the Step 10 decision. A browser-only concealment would leave the HTTP response exposed. | main.py replaces the score with null and public_score_not_validated for both routes, retaining evidence/coverage and sample gate reasons. UI validates null/policy/status and never renders a number, even from a forged prop. No environment/origin bypass exists. JSON/CSV and consumer regressions pass. |
| S12-02 High — normalization/output amplification | The Step 10 authored 756,092-byte request produced 8,275,593 response bytes. Raw-input ceilings alone did not bound normalized display text. | After NFKC/masking, enforce 5,000 points per text, 300 per title and 250,000 aggregate; reject atomically with 413 normalized_text_limit, never truncate. Serialize inside the admitted worker and cap UTF-8 output at 2 MiB; check deadline afterward. New per-field/aggregate/serialization regressions pass. Same Unicode request now yields a 175-byte 413. |
| S12-03 Medium — absent browser containment | Production pages had no CSP or anti-framing/referrer policy. Escaping existed, but there was no browser script containment layer. | proxy.ts issues a fresh nonce, overwrites supplied CSP, forwards it to Next and sets response CSP/no-store/nosniff/DENY/no-referrer/permissions headers. Dynamic rendering supplies matching nonces to every framework/inline script. Live checks cover five routes and 404; all script tags match fresh nonces. No unsafe-inline or unsafe-eval in production script policy. |
| S12-04 Medium — public/legacy response mismatch | Merely removing the rendered number could accept an old API or present withholding as a zero. | Version rt-patterns-0.3.0-experimental; new withheld status/reason. Browser rejects old method, any numeric value and missing policy. Zero/100 rejection and direct-render concealment are tested. Offline raw arithmetic is explicitly separate. |
| S12-05 Reviewed — HTTP/parser abuse | Body bytes including envelope, invalid/false lengths, compressed input, malformed CSV/JSON, duplicate headers, deadlines, finite rating bounds and bounded features/pairs. | Existing authoritative guards retained. Native multipart max_header_count=2/max_header_size=8192 already handled the proposed guard, so duplicate callback guards were removed. Giant part-header regression returns a safe parser error. |
| S12-06 Reviewed — privacy/SSRF/XSS/logging | Input, errors, UI text, filenames, body cleanup, request-local references and offline subprocess use. | React text/mark nodes escape hostile content; no HTML sink/eval/pickle/request-driven fetching found. Unknown keys/PII remain absent from public validation errors; unexpected logs contain fixed code/random ID only. Existing regressions remain passing. Access logs/proxy trust are disabled in the loopback command. Masking remains incomplete. |
| S12-07 Reviewed — resource admission/cancellation | Two slots, no unbounded queue, hashed bounded peer buckets, slow bodies and cancelled clients. | Existing worker retention on cancellation preserved. New benchmark: two dense requests complete in approximately 2.93 seconds; third returns analysis_busy, health remains 200 and slots return to zero. Default immediate requests 200/200/429; shortened slow-body timeout returns request_timeout and releases admission. These are controlled local probes, not hosted throughput. |

No unresolved critical repository finding was identified in this scope. That does not close deployment gates or prove absence of vulnerabilities.

## CSP tradeoffs and runtime

The pinned Next 16.4.3 bundled CSP/proxy guidance requires per-request nonces and dynamic rendering. Home remains a synchronous component; layout selects force-dynamic. This intentionally trades static HTML caching for fresh script nonces. Page responses are no-store; fingerprinted framework assets retain native caching. Production script-src uses nonce/strict-dynamic, with no eval/inline exemption; development alone allows unsafe-eval for framework tooling. connect-src includes only self and the configured trusted API origin (development also allows loopback HMR sockets).

style-src permits unsafe-inline because the existing CSS chart bars set bounded numeric widths; this is an explicit style exception, not a script exception. Images/fonts stay local or permitted image data; object, base, forms and framing are blocked. Contact is an explicit mail link only when configured, not a form. TLS/HSTS and provider header preservation remain deployment checks. No cached nonce or static-generation workaround was added.

API JSON and safe errors carry default-src none/frame-ancestors none, no-referrer, no-store and nosniff. Public response serialization is bounded inside the admitted worker rather than left to untracked work after admission release. Cooperative deadlines still cannot preempt a single bounded library call. A failed/oversized response yields no partial result.

## Dependency and source checks

[Dependency evidence](security/dependencies-20261028.json) binds the exact requirements and npm lockfile SHA-256 values checked. `npm --prefix web audit --json` reported zero advisories (548 total dependency entries in its metadata). [OSV querybatch](https://google.github.io/osv.dev/post-v1-querybatch/) checked all 25 exact PyPI pins from runtime/development requirements: zero returned advisories and no pagination token. Only package names/versions were sent. No dependency was installed, replaced or force-resolved. No report is a supply-chain certification or guarantee about future advisories.

The retained ESLint 9 pin/deprecation was reviewed as D15 maintenance debt, with no advisory returned by this scan; compatibility pins were not forcibly changed. No tracked secret/config file was found beyond the intentionally public .env.example files. The application has one trusted build-time API fetch and no request-driven outbound backend requests. Offline runners use trusted local Python paths and argument lists, not shell interpolation; training stays disabled.

Repeat npm audit and the pinned dependency check before deployment. To repeat the recorded Python query using PowerShell:

```powershell
$record = Get-Content docs/security/dependencies-20261028.json -Raw | ConvertFrom-Json
$body = @{queries = $record.python.queries} | ConvertTo-Json -Depth 8
Invoke-RestMethod -Method Post -Uri https://api.osv.dev/v1/querybatch -ContentType application/json -Body $body
```

Review any new advisories and pagination; zero results are only a point-in-time database observation.

## Verification and versioned research

- Backend: 194 tests, including seven added security cases; privacy/error/stream/timeout/cancellation and raw-library arithmetic regressions retained.
- Frontend: 27 tests, including production policy/nonce and numeric-response rejection checks; analyzer reset/abort, contact and escaped evidence remain covered. Type checking, lint and production build pass. Next reports dynamic page routes plus Proxy.
- Offline: 28 integrity tests pass. All 17 declared mechanical case outcomes and cross-case relations are unchanged. The refreshed mechanics reference binds methodology 0.3.0 and changed source bytes; it does not reinterpret fixtures as accuracy.
- New [Step 12 measurement record](benchmarks/20261028-step12.json), runner rt-resource-benchmark-0.2.0: 27 fresh-process samples; public-score withholding verified and normalization rejection expected. Record hash 33b84a98302b5c5f412f38f05822f66689ba6e8a359369bd4c8120919cbc7d6a. The original Step 10 record is preserved as historical evidence and intentionally no longer verifies against changed source.
- Largest observed accepted resource case: 500 dense rows, median 1,437.28 ms and peak lifetime RSS 60.43 MiB. Unicode normalization rejection: median 46.66 ms, 52.29 MiB. These are absolute local measurements; changed methodology/input outcome prevents treating them as a universal speed regression comparison.
- Live production HTTP: every script tag on home, four information routes and 404 had the matching fresh CSP nonce, no-store semantics and no production unsafe-eval. Browser hydrated, mapped/uploaded a 500-row/250,000-point synthetic CSV and displayed Score withheld, 500 rows and unset confidence. At 320px, document client/scroll widths were both 305px before/after opening 20 supporting text blocks. Browser error log empty. No browser timing or hosted capacity claim is made. Temporary tab/viewport and servers cleaned up.

Reproduce with `./scripts/check.ps1`, `api/.venv/Scripts/python.exe -m ml.evaluate --verify ml/fixtures/mechanics.expected.json`, and `api/.venv/Scripts/python.exe -m ml.benchmark --verify docs/benchmarks/20261028-step12.json`. New resource measurements use a fresh create-only path under ignored ml/artifacts/. New remote GitHub Actions execution was not verified.

## Required before public launch — owner/provider gates

1. **Monitored contact:** CONTACT_EMAIL remains intentionally blank under the owner's override. Configure a real destination, rebuild, verify recipient/mailbox operation and privacy/retention practices. No invented address or automatic message sending.
2. **Actual HTTPS origins and integration:** select owned API/web domains; set trusted NEXT_PUBLIC_API_URL and exact HTTPS CORS origins; rebuild and verify headers/nonces, no credential forwarding, no redirects and real cross-origin errors. Keep noindex until launch approval. Default loopback URLs are development configuration.
3. **Provider resource/edge/proxy controls:** verify one process/instance, CPU/RAM headroom, worst accepted input under concurrent load, sockets/header/body/connection/write timeouts and edge quotas. Keep no-proxy-headers until actual trusted-hop identity is established; otherwise peer aggregation is deliberately conservative. Do not trust arbitrary forwarding headers or add workers without shared edge enforcement. No database/Redis is warranted merely to anticipate scale.
4. **Provider privacy and operational evidence:** inspect body capture/APM/crash dumps, buffers, access/deploy logs, retention/access controls and deletion settings on the actual accounts; record owners and actual plan. Disable app access logs/body capture and unwanted exporters. [Render documents plan-dependent log retention](https://render.com/docs/logging), so application memory-only handling cannot certify provider non-retention. Verify TLS/HSTS, deployed header preservation and live remote CI before approval.

These are release gates, not waivers or assertions that a provider already meets them. Step 13 must resolve them against concrete configured services before public traffic. If they cannot be demonstrated, keep deployment private or stop release. No public launch approval was granted by this local audit.
