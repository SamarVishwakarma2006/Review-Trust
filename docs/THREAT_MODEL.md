# Threat model

Step 1 proposal, 2026-10-27. Controls below are requirements, not implemented guarantees. Security verification is required in Step 12 and production in Step 13.

Assets: submitted text/metadata, user privacy, service availability, methodology integrity, evidence references and deployment secrets. Actors: normal users, abusive anonymous clients, malicious CSV/review authors, misleading dataset publishers and dependency attackers. Boundaries: browser/API, parser/canonical records, public data/offline training, build/deployment and hosting logs.

| Threat / boundary | Required control and verification | Residual risk |
| --- | --- | --- |
| Huge/chunked bodies, CSV bombs, similarity CPU exhaustion | Stream-count bytes before parse, no compression/archives, bounded fields/rows/features, bounded pair processing, concurrency/deadline enforcement; test maxima and stalled work | Anonymous distributed abuse still possible |
| Rate-limit bypass / forged forwarding headers | Configurable initial 10 analyses/minute/client, burst 2; trust proxy headers only from verified deployment proxy; bounded in-memory limiter (10,000 keys, TTL 60 seconds, reject new clients at capacity); single process until shared edge enforcement verified | NAT users share limits, restarts reset state; CORS does not prevent abuse |
| Upload persistence / path traversal | Ignore filenames; parse bounded bytes in memory without default multipart disk spooling; no upload storage, reject extra files, verify request cleanup and disconnect | Hosting/platform buffers require verification |
| XSS / malicious review instructions | Render as escaped text; no raw HTML/Markdown execution, dynamic code, shell or model calls; strict CSP when frontend exists; hostile-content tests | Users can submit misleading prose |
| PII in text, errors, telemetry | Discard unused/name columns, mask email/phone before processing and output, redact validation errors; disable body logging/tracing/crash payloads; test with recognizable sentinel PII | Names and other personal details may remain; no claim of full anonymization |
| Retention / client leaks | No-store responses, no browser persistence, reset state, no analytics payload capture; inspect host logging/retention and disable access logs where possible | Browser extensions, screenshots and provider infrastructure outside app control |
| Identifier tracking | Request-local row IDs only; no persistent reviewer pseudonyms in v1; short-lived IP limiter keys scoped with process-ephemeral keyed hash, never logged | Network operators see connection metadata |
| SSRF / data exfiltration | No URL fetching, link previews or remote model/data loading from request fields; source IDs are opaque | Future URL feature requires separate explicit approval/review |
| Model/data supply chain | License/provenance audit, pinned dependencies, lockfiles, vulnerability checks; load only trusted versioned artifacts; never accept serialized models from users | Audits do not guarantee absence of malicious packages/data |
| Misleading score / label leakage | Experimental badge, fixed signal panel, withholding gates, alternative explanations, grouped independent evaluation, no unsupported confidence | Selection bias and adaptive manipulation remain unresolved |
| Secrets / deployment misconfiguration | Environment secrets, exact origin allowlist without credentials, safe errors, TLS, minimal health output; verify preview/prod configuration separately | Incorrect host/proxy setup can defeat application assumptions |

Initial budget/limit values are hypotheses to test in Step 10. Do not add Redis solely to satisfy a hypothetical distributed deployment. If deployment topology cannot enforce the design, block release or choose a verified native edge control. Endpoint access requires no account; rate controls protect availability and are not identity verification.

No legal compliance certification is implied. Dataset licenses and production privacy disclosures need review against actual sources, providers and deployment jurisdictions.
