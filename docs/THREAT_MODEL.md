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

## Step 9 results boundary

The results view keeps experimental/withheld states, unvalidated confidence, evidence gaps and a disclosed non-severity navigation order visible. Chart bars have denominator text and native keyboard controls; no probability or risk-band interpretation is added. Raw review/title content remains escaped React text, including highlighted matches. Code-point range splitting and response checks reject reversed/out-of-bounds offsets rather than trusting them as markup. No export/sharing/persistence or new chart dependency was introduced.

Synthetic API-shaped fixtures cover unsafe-looking text, Unicode highlights, chart values and unavailable states. Live loopback JSON/CSV, keyboard focus/controls and mobile overflow were targeted checks, not a comprehensive rendering/security/accessibility certification. Provider, dependency, resource and production release gates remain open.

## Step 10 measurement and release boundary

The benchmark only builds authored synthetic requests and reports aggregate outcomes/hashes, never submitted review text or local user paths. Each resource sample runs in a new subprocess with a 45-second containment timeout; this is a harness safeguard, not a replacement for cooperative production deadlines. Source fingerprints before/after measurement, exact request hashes, checksums, create-only ignored outputs and stored-record verification protect against accidental drift. Hashes do not establish validity, privacy or rights.

Controlled two-slot load, default rate, slow-body timeout and existing cancellation tests cover local behavior. No provider, proxy, TLS, worker-process aggregate, sustained-load or public browser performance certification is implied. Local response amplification is observed: a 756,092-byte Unicode request expands to an 8,275,593-byte response after normalization. Step 12 must review response/normalized-text bounds and worst-case browser rendering against deployment memory budgets before approval. Existing raw-input caps stay in force; this step does not silently truncate or change methodology.

Public numeric scoring is not approved by the synthetic evidence. Step 12 must enforce and test score withholding across API/UI before public deployment; development-only experimental numbers must not be mistaken for that release policy already being implemented. Findings/coverage and explicit unvalidated confidence remain the intended public behavior. No new training authorization or source admission occurred.

## Step 11 content and contact boundary

The information pages retain noindex and identify the service as a development preview. They describe observable patterns without accusations, classifier accuracy, validated confidence or purchasing advice. Static privacy copy distinguishes raw upload bytes from canonical filtering and acknowledges incomplete masking, ordinary memory cleanup and unverified provider retention. No new data collection, cookie/analytics integration, proxy or API route was introduced.

The owner explicitly deferred the contact destination. A blank constant produces blank address space plus unavailable messaging, with no mailto/form or implied operational dispute intake. A configured owner address will be escaped as text and encoded in a fixed-subject mailto link; sending remains an explicit action in the visitor's email client. Synthetic tests cover both states. This is not proof that a mailbox is monitored or messages delivered. Add/check the real destination and mailbox privacy/retention practices before public launch.

Targeted keyboard, mobile/desktop, navigation and live analyzer checks complement the existing suite without certifying complete accessibility/security. Public numeric-score withholding still requires API/UI enforcement in Step 12. Unicode response amplification, worst-case rendering, provider limits/logs, proxy behavior and deployment verification remain open release gates. No public deployment was performed.


## Step 12 security update

The local audit is complete: see [SECURITY_AUDIT.md](SECURITY_AUDIT.md). Both HTTP routes and UI enforce null scores; only the offline library retains numerical arithmetic. Methodology 0.3.0 adds normalized/masked text limits and 2 MiB serialization rejection. Next pages now render dynamically with fresh script nonces, no-store and anti-framing/referrer/permissions headers; inline chart styles remain documented. Escaped evidence, cancellation/reset and intentional blank contact are preserved. Current benchmark is benchmarks/20261028-step12.json; the original Step 10 record is historical. Contact setup and actual provider TLS/proxy/logging/retention/edge/resource verification remain prerequisites to public launch. No deployment was performed.


## E03 planned URL-ingestion boundary — not implemented

Owner-authorized independent design dated 2026-10-31: [URL_INGESTION.md](URL_INGESTION.md). Current application still has no URL fetcher; E02 permission/access remains blocked. This section specifies future controls, not implementation evidence. Threats now additionally include malicious source administrators, compromised provider responses/DNS, stolen source credentials and anonymous requests that spend provider quota.

| New threat / boundary | Required future control and verification | Remaining limit / gate |
| --- | --- | --- |
| URL parser disagreements, host-suffix/path injection | Exact registered origin/path, bounded source/product token, server-built fixed API requests; reject credentials, fragments, queries, encoded separators, backslashes, IP literals and unsupported schemes before DNS | International/query-based source URLs require explicit extension; no universal crawler |
| DNS rebinding/private-network/metadata access | Validate all A/AAAA including mapped IPv4, special-use and real internal routes; connect only to validated peer with original TLS SNI/certificate verification; restrict egress and test fallback | No ordinary resolve-then-fetch shortcut; client/host guarantees must be demonstrated in E05 |
| Redirect/ambient credential exfiltration | Reject all redirects; no environment proxy/netrc/cookies; scoped header secret bound to fixed registered API host | Approved retailer URL alone does not approve a second API host |
| Broad merchant key/private customer exposure | Verify associated user's read capabilities, avoid broad manager credentials, minimize selected fields, strip PII immediately, bounded memory-only buffers, fixed safe error logs | Read key is not product-only scope; merchant/access review remains E02 |
| Quota/cost abuse and slow provider responses | Shared two-slot admission/peer buckets, source-wide quota/cooldown, six total GET attempts, no retries, streamed byte/header limits, absolute collection/overall deadlines and provider hard spending caps if chargeable | One process only; restart/rollout quota resets and actual upstream capacity must be addressed before activation |
| Silent sample bias/forged success/product variants | Explicit bounded sample provenance, deterministic ordering, known source-ID overlap only; preserve equal text with distinct IDs; reject inconsistent/invalid data, unknown totals stay null | API samples/moderation are not all customer experience or deception truth |
| Stale rights/source withdrawal | Empty registry default, approved use/expiry/revocation bindings, recheck before response; no raw-review persistence/redistribution/training assumption | Technical API access cannot establish rights; do not activate before E02 |
| Provider HTML/instruction/data injection | UTF-8 JSON transport, inert text extraction for approved review fields, canonical validation/masking, React escaping, no external images/scripts/model/tool execution | Masking remains incomplete; no authenticity/quality verdict |
| Timeout/cancellation orphan work | One deadline from body through whole-envelope capped serialization; close upstream streams/cancel I/O and retain admission for running CPU work | Browser AbortController alone does not establish server cleanup |

Review source: [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), read 2026-10-31 in the browser. Source principles informed design; specific limits are unmeasured project choices. E04 synthetic fixture work can proceed independently if requested; live collection, source admission, production privacy/egress/capacity and E20 deployment remain gated. No new security control is claimed implemented by this documentation.


## E04 offline parser implementation evidence

The new source parser is not imported by serving endpoints and cannot fetch a URL. Authored synthetic fixture tests cover strict source-byte decoding, safe fixed errors, schema/identity/UTC/rating checks, PII field exclusion, inert HTML extraction, page/field/aggregate rejection and preserved repeated wording. Repr suppresses raw content, but internal records are not safe public output or log payloads: common masking and post-normalization ceilings still belong to the shared analysis boundary. HTMLParser returns plain text, including decoded tag-looking prose, so future consumers must retain React escaping. No source rights or transport/egress/admission guarantees are established by this offline parser. Cross-page overlap and variant provenance remain E06; E02 access remains blocked.


## E05 offline safeguard evidence, not live transport assurance

New isolated guards reject unsupported URL/host forms, expired candidate policy, prohibited supplied IPv4/IPv6 answer sets, redirects/compression/framing errors and bounded attempts/bytes/deadlines. Source quotas/cooldown are process-local and do not persist through restart or enforce provider billing. Default registry is empty. Tests use synthetic values only, no actual DNS/network/credentials. The serving app does not import these guards. Destination validation does not prove connected peer identity; post-parse header checks do not bound socket header buffering; inter-chunk checks do not interrupt blocked reads. Actual DNS/TLS binding, egress, narrowed secrets, provider rights, absolute I/O timeout and cancellation/admission cleanup remain unimplemented and block E05 activation. No live crawler or production security claim is justified by this checkpoint.


## E05 transport component, tested without real network access

The unwired metadata transport configures numeric peer/original-host certificate verification and checks actual peer before authorization, uses fixed request templates, rejects redirects and ambiguous raw headers before HTTP normalization, bounds actual stream waits/raw reads and force-closes owned streams under synthetic cancellation/error cases. Default source registry is still empty. Tests inspect native connector arguments and replace only the local module connector binding; there is no live TLS/certificate/provider probe. Source permission, bounded DNS and actual resolver-to-peer flow, network egress, key capability/secret loading, shared concurrency/admission and production resource controls remain activation gates. Source revocation/expiry before return discards output. These tests narrow the earlier transport implementation gap but do not establish real-world SSRF protection or approved source access. See SOURCE_TRANSPORT.md.


## E06 fixture-only evidence

Offline sample assembly rejects conflicting stable IDs and malformed pages atomically, bounds cross-page bytes/text/rows, masks prose with existing incomplete masking and preserves null metadata/unknown totals. Known-date sort checks cannot establish source stability or ordering of undated records. Provider totals, variant-level review attribution, pagination exhaustion and rights remain unverified. No serving route imports the fixture assembler, no real data is admitted and E02/E05 gates remain blocked. See [SOURCE_SAMPLE.md](SOURCE_SAMPLE.md).


E07 ingress checkpoint (2026-10-31): POST /v2/products/analyze is implemented fail-closed with strict typed request validation, 8 KiB actual-body limit and shared v1 rate/admission/deadline/worker controls. No success analysis path, fixture loader, collector or source activation is wired. E07 remains PARTIAL/BLOCKED for full integration; E02/E05 live gates remain blocked, E08 pending. See PRODUCT_API.md. Earlier no-product-endpoint statements are historical.


E07 fixture-analysis continuation (2026-10-31): api/app/fixture_analysis.py now validates/serializes authored-fixture schema-v2 analysis with explicit authored_fixture origin/declaration, null public score/confidence, collection counters/windows/order, masked bounded product title and null analysis for zero reviews. Existing analyzer field calculations are shared by a small analyze_fields extraction; v1 still validates AnalysisResult and accepts only paste/csv input. No production route loads fixtures or returns success. E07 remains PARTIAL for production collected-origin contracts/integration; E02/E05 live gates blocked, E08 pending. Seven authored cases include a test-only admitted HTTP route, not a production success claim. No new dependency, source, model or deployment.


E07 collected-result contracts checkpoint (2026-10-31): api/app/product_results.py defines typed source/product/collection and schema-v2 collected analysis models. PublicScore forbids numeric values/experimental status and requires public_score_not_validated. Cross-field checks enforce selected-window completion/empty/partial reasons, page/count accounting, unknown versus source-reported totals, UTC windows/retrieval agreement, variant-label scope and nested analysis counts/origin/version. Thirty-one authored contract cases pass. These models do not collect or authorize data, do not convert fixture origin and are not wired to a production success route or frontend consumer. E07 remains PARTIAL; E02/E05 live gates blocked, E08 pending. Existing bound implementation files/reports unchanged; no dependency, training or deployment.
