# Threat model

Step 1 proposal, updated through Step 4 on 2026-10-27. The table records requirements and residual risks; implemented controls below have focused local verification, not a completed security audit. Security verification is required in Step 12 and production in Step 13.

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

## Step 4 implementation evidence

Actual-byte and multipart-envelope caps, strict headers/content encoding, in-memory no-spool callbacks, row/field limits, exact origin allowlist, safe result/error contracts, conservative email/phone masking, hashed bounded token buckets, two-request admission, slow-body deadline and cancellation slot retention have focused tests. Unexpected errors log only a fixed error code and random request ID. Multipart parser diagnostics are silenced because malformed headers can contain private values. The local development command disables access logs and proxy headers.

Retained release work: measured peak-load/time/memory behavior; provider logs and retention; proxy/edge enforcement across instances; TLS and host connection/header/write budgets; dependency and rendering audits; dataset/model integrity; public methodology/contact content. Cooperative CPU deadline checks do not preempt a bounded library call, and masking is incomplete. Application controls do not establish production compliance or protection against distributed abuse.

## Step 5 browser boundary

Implemented: trusted build-time API origin, credential-free/no-store/non-redirecting requests, explicit domain/language declaration, personal-data removal notice, bounded local file reads, fixed transmitted filename, safe error presentation and checked consumed result fields. Review/header text uses React escaping; no HTML rendering or browser storage. Abort/generation guards prevent stale results after reset/cancel/unmount, and a client deadline bounds waiting without bypassing server worker retention.

Verified locally through synthetic interaction/limit tests and browser JSON/CSV flows. Browser CSV checks are convenience only; all server controls remain authoritative. This does not certify provider logging, browser extensions, complete anonymization, secure memory erasure, production CORS/TLS, comprehensive accessibility or dependency security. Existing Steps 12/13 release gates remain open.

## Step 6 signal boundaries

Sparse feature construction and at most 124,750 review pairs remain under existing body/row/text bounds and cooperative deadline checks. A vocabulary above 20,000 features yields explicit unavailability and withholds the score, avoiding silent feature pruning. Existing admission/cancellation controls remain unchanged. Maximum-row and over-feature-cap synthetic fixtures exercise these paths; this is not a measured production load/memory benchmark.

Lexicon abstention and contextual-only metadata signals limit unsupported conclusions but cannot establish accurate sentiment/authenticity. Evidence now includes submitted ratings and normalized UTC dates only where relevant; raw identifiers remain excluded. Masking precedes all text computations, including polarity; title text is excluded from signals. Browser evidence remains escaped and methodology-version checked. Resource benchmarking and independent validity evaluation remain Step 10; full dependency/security/deployment review remains Steps 12–13.

## Step 7 offline research boundary

Primary-source metadata was inspected without downloading third-party review archives or contacting dataset owners. Candidate rights/label/domain uncertainty is recorded, and the CLI rejects real candidate sources before normal input processing. The only admitted input is a declared synthetic source; training remains disabled in code. This admission declaration does not prove that arbitrary files are genuinely synthetic, so operators must still use reviewed fixtures and minimize input.

Offline inputs have byte/row/text/annotation bounds and strict fields; fixed error codes avoid exposing submitted text/paths. Only hashes, opaque experiment keys and aggregate quality/partition data enter manifests. Hashes can be linkable or guessable and are not anonymization. Existing outputs are create-only under ignored artifacts; no server upload retention, network retrieval, remote code execution or public research endpoint is added.

Product and detected duplicate connected components stay within one partition. Fixed trigram similarity misses some paraphrases, and source product-group mapping can be wrong; these remain experiment-review risks. The tool rejects oversized inputs rather than chunking independently. Manifest checks detect changed bytes/cards/labels/membership, but provenance truth, reviewer independence, external evidence quality, permissions, full-corpus leakage and real-world validity cannot be established by hashes or synthetic tests.

## Step 8 evaluation boundary

No real source admission, data acquisition, learned-model loading, training or probability calibration was introduced. The evaluator rejects source admission/training flag changes for a new review rather than treating them as authority. It recomputes the Step 7 freeze before exercising controlled production cases. Catalog/manifest/implementation hashes support reproducibility, not truth, rights or anonymization.

Authored scenarios expose template/negation/paraphrase/sarcasm/masking limitations and abstention gates but cannot establish real-world validity. Report fields keep classifier metrics unavailable and confidence unset. Bounded verification reads, create-only artifact outputs, safe fixed failures, decimal-aware JSON comparison and no raw-review report content have integrity tests. Existing API transport/admission/cancellation controls and all production release gates remain in force; the offline evaluator does not certify those deployments.
