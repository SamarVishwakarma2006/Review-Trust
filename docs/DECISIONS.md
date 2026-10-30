# Decisions

2026-10-27; Step 1. Accepted design direction unless explicitly marked experimental.

| ID | Decision | Alternatives and rationale |
| --- | --- | --- |
| D01 | Next.js browser UI calls one FastAPI service directly | A Next.js proxy duplicates request limits and data exposure; no demonstrated need. Exact CORS origins required. |
| D02 | Ephemeral synchronous bounded analysis, no database | Saved histories/accounts/queues expand privacy and operations without v1 requirements. |
| D03 | English electronics, one product per request | Broad language/category support requires separate evaluation. Declarations remain unverified. |
| D04 | Deterministic signals before supervised ML | No approved labels yet. Embeddings and external AI calls add cost without established benefit. |
| D05 | Experimental fixed two-signal index using max penalty | Weighted all-signal sums would imply unsupported weights and reward missing metadata. Proposed formula remains unvalidated; public score may be withheld. |
| D06 | Separate coverage and confidence; confidence unset | Rule agreement and review count do not establish certainty. No probability/authenticity interpretation. |
| D07 | Preserve duplicates as evidence, group duplicates for evaluation splits | Deduplicating user input erases a signal; splitting duplicates across test/training leaks information. |
| D08 | Server CSV parser, explicit mapping, atomic validation | Silent coercion/dropping obscures evidence. Client-only validation is bypassable. |
| D09 | No stored IDs or public export in v1 | Stable reviewer tracking and sharing are unnecessary privacy exposure. |
| D10 | Single API process initially; verified edge abuse controls before scaling | Per-process limiters cannot enforce global limits. Do not add distributed infrastructure without measured need. |

Deferred: full lexicon to Step 6; dataset/license choices to Step 7; score defensibility and performance thresholds to Step 10; operator contact to Step 11; hosting/log retention and deployment-specific enforcement to Steps 12–13.

## Step 2 — Development foundation

- D11: Use Node 24 and Python 3.12 as documented/CI runtime baselines. Pin npm direct dependencies and commit its lockfile; separate fully pinned Python runtime and development requirements. Do not install data-science packages before the corresponding work requires them.
- D12: A synchronous React foundation page and a minimal API root status permit startup and smoke testing without implementing Step 3/4/5 features. No runtime API URL configuration or CORS is needed until browser/API integration; no secrets are currently used.
- D13: Vitest plus React Testing Library covers the page; pytest plus FastAPI TestClient covers the backend; Ruff provides Python lint/format checks. Use the current Starlette-supported httpx2 test transport. CI runs on Ubuntu; local Windows startup is verified separately.
- D14: Preserve the user's Git history and `main` branch. Resolve the committed README conflict markers by keeping the full ReviewTrust documentation. User performs staging, commits and pushes manually after each step.
- D15: Pin ESLint 9.39.5 because the current React/import/accessibility plugins bundled with eslint-config-next reject ESLint 10 in their peer ranges. ESLint 9 emits an upstream end-of-support warning; this is a development-tool maintenance limitation, not a reason to override peer requirements. Revisit when those plugins support ESLint 10 and during Step 12. npm install reported zero known vulnerabilities at setup time; this is not a security guarantee.

Implementation references consulted: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation), [Next.js Vitest guide](https://nextjs.org/docs/app/guides/testing/vitest), and [FastAPI first steps](https://fastapi.tiangolo.com/tutorial/first-steps/). Dependency pins reflect registry resolution and local compatibility checks, not a completed production security audit.

## Step 3 — Schemas and review validation

- D16: Pydantic strict, extra-forbidden input models share one collection validator for both adapters. `validate_submission` turns internal Pydantic failures into safe errors. Future endpoints must use the adapters rather than return default Pydantic input details. Request-local references are generated from retained input order; duplicates remain evidence.
- D17: `parse_json` accepts bounded UTF-8 bytes and rejects duplicate keys and nonstandard numeric constants. Use standard-library Decimal for numeric parsing and pre-conversion rating bounds so rounding cannot admit out-of-range values. Canonical valid ratings become floats.
- D18: `parse_csv` uses standard-library strict CSV parsing plus a quote-placement check because strict CSV still accepts bare quotes in unquoted cells. Avoid changing the CSV module's process-global field limit. Raw bytes cap memory; extra column/header/cell caps bound irrelevant data too. No new dependency is needed.
- D19: CSV mappings are source-header -> canonical-field, replacing automatic canonical-header mapping when supplied. Discard unmapped columns and report only their one-based positions. Invalid rows reject the whole submission. CSV errors count logical records including the header; JSON row numbers count reviews from one.
- D20: Ingestion is a library layer in Step 3. Transport streaming/multipart/rate/CORS controls and redaction before analysis/output arrive with the API foundation; a validated record is not a redacted record or proof of representative sampling.

References consulted: [Pydantic validators](https://docs.pydantic.dev/latest/concepts/validators/) and [Python 3.12 CSV module](https://docs.python.org/3.12/library/csv.html). Exact ReviewTrust limits and adapter behavior are project decisions defined in SPEC.md, not claims of externally validated methodology.

## Step 4 — FastAPI analysis foundation

- D21: Add python-multipart 0.0.32 as the single new runtime dependency. Its callback parser supports explicit bounded memory handling; avoid FastAPI UploadFile/automatic spooling. Total envelope bytes are checked before parse. Native part-header limits and callback field/part caps prevent unbounded form parsing. Filenames are ignored and parser logs suppressed to avoid private-header exposure.
- D22: Keep a single serving process with two admitted analysis requests and no unbounded CPU queue. Count actual body bytes and apply a read deadline; run bounded parsing/analysis in workers with cooperative deadline checks. Shield tasks and retain admission until worker completion after cancellation. Do not return a timeout while abandoning untracked CPU work.
- D23: Use ephemeral scoped HMAC peer keys, bounded token buckets and exact CORS configuration; no persistent IP table or shared infrastructure. Disable proxy headers in the local command. Shared edge enforcement and proxy trust must be verified before production scaling. CORS is not authentication; origin-less clients remain supported.
- D24: Version implemented scoring as rt-patterns-0.1.0-experimental. Implement only exact repetition and four declared incentive phrases, preserving max aggregation and evidence gates. Integer arithmetic provides exact half-up rounding. Three contextual signals remain not_implemented. No unvalidated confidence level or probability claim.
- D25: Normalize/mask before scoring and display; omit opaque product/source IDs from output. Common email/phone masking cannot guarantee anonymization. Placeholders do not supply word tokens. Derive duplicate pairs and real phrase spans from computed evidence; never generate post-hoc explanations.
- D26: Safe errors include server-generated request IDs; unexpected failure logs include only fixed error code and ID. Preserve the development root response, add minimal health, disable slash redirects, and keep interactive docs disabled. API usage/configuration is documented in docs/API.md; native CORS preflight text is a documented protocol exception to JSON errors.

Reference: [python-multipart streaming callback documentation](https://multipart.fastapiexpert.com/). Starlette request/CORS behavior was also checked against the installed pinned package source. Provider, dependency and full threat-model audits remain future release gates.

## Step 5 — Functional Next.js application

- D27: Keep the page synchronous with one client input component and a small results component. Use native controls, fetch, AbortController, FormData and a bounded header-only preview rather than adding form/CSV/state libraries. Optional metadata uses CSV; bulk splitting remains deferred.
- D28: NEXT_PUBLIC_API_URL is a trusted build-time origin, with loopback default. Browser requests omit credentials, refuse redirects and caching, and never send the local filename. No proxy, persistence or analytics is introduced. Provider data handling remains a release gate.
- D29: Generation guards reject stale request/file-read completions after cancel/reset/change/unmount. A 35-second browser deadline bounds waiting without claiming to terminate server workers. Failed requests preserve editable input; prior results clear on edits.
- D30: Validate consumed result fields at the browser boundary, display safe structured errors rather than raw messages, and render evidence through React text nodes. Initial results expose all unavailable/experimental/coverage caveats. No new methodology or confidence estimate; polish remains Step 9.

Framework guidance consulted locally: bundled Next.js server/client component and environment-variable guides for the pinned version. No new dependency was needed.

## Step 6 — Explainable detection signals

- D31: Implement bounded sparse unigram/bigram TF-IDF with Python standard-library Counters and math, avoiding a new numerical/ML runtime for a maximum of 500 rows. Use raw TF, smoothed IDF, L2 normalization, inclusive 0.90 cosine and no stemming/stop words. Check cooperative deadlines during construction and pair comparisons. No learned authenticity classifier or dataset is involved.
- D32: Exceeding 20,000 features makes repetition unavailable and withholds the score. Pruning frequent/rare features could manufacture similarity, so no silent fallback to an exact-only score under the same version. Available contextual findings do not satisfy scoring-panel availability.
- D33: Bump methodology to rt-patterns-0.2.0-experimental. Preserve the two-signal max formula, exact rounding and gates. Timing, rating concentration and lexicon disagreement stay contextual; report metadata counts and reasons rather than treating absence as safety. Window starts are observed UTC days, with earliest-start tie breaking; exact decimal rating values retain their own bins.
- D34: Freeze rt-en-polarity-0.1 as a small declared word inventory with whole-row abstention for negation, contrast, conditional/quoted/question/sarcasm markers and mixed/unsupported directions. This is intentionally narrow and unvalidated. Only rated supported rows enter its denominator. No confidence or deception interpretation.
- D35: Extend typed result values/evidence with cosine method, window summary, rating histogram and rating/polarity/date evidence. The frontend accepts the matching methodology and displays evidence as plain text. Keep bounded previews and total matching counts. Numerical or detector changes require another methodology revision and regression fixtures; historical scores are not interchangeable.

## Step 7 — Dataset audit and labelling workflow

- D36: Audit primary release descriptions, maintainer permission statements and label origin before acquiring data. Amazon Reviews'23 Electronics, YelpCHI and Ott ACL 2011 remain not_approved for ReviewTrust. Unacquired-data quality is marked unmeasured. No emails, archives, real review excerpts or unsupported licence/accuracy claims are introduced.
- D37: Add a bounded standard-library offline JSONL tool under ml/, separate from the public one-product API. Only project-authored synthetic fixtures are admitted. The hard-coded synthetic admission and training_authorized=false prevent a source-card flag from becoming a real-data training override. Real admission needs reviewed implementation/provenance changes, not an inferred licence.
- D38: Use a fixed lexical leakage grouping rule (NFKC/casefold word normalization, exact text and trigram Jaccard >=0.80) plus product keys, then full connected components. This avoids fitting TF-IDF or learned preprocessing on the held-out corpus. It catches only declared overlaps; paraphrase leakage and larger-corpus grouping still require review. Inputs over 500 rows reject rather than split independently in chunks.
- D39: Two distinct role-coded unanimous supported votes with reviewed evidence may resolve a scenario label; proxies, missing evidence, unknown votes and disagreements abstain. No majority shortcut or claim that different role IDs prove independent humans. Freeze the rubric/ledger and document any later adjudication under a new artifact version. No real annotation round has occurred.
- D40: Assign entire components using a versioned seeded SHA-256 bucket policy with expected 70/15/15 group shares, without labels, rebalancing or seed rerolls. Freeze exact bytes, selected source card, groups, labels and test memberships in a canonical manifest. Refuse overwrite, verify complete recomputation, omit raw review bodies/product keys/paths, and keep real derived hashes subject to original privacy/rights restrictions.
- D41: Reuse the existing Python 3.12 runtime with unittest and Ruff; extend local checks and CI without adding research/ML dependencies. Commit only synthetic inputs and their expected manifest. Step 8 remains an explicit train/no-train decision; current audit supplies no approved electronics deception target and does not perform training or evaluation.

## Step 8 — No-train baseline and reproducible evaluation

- D42: Complete the roadmap's explicit no-train alternative. The frozen Step 7 audit has no admitted real electronics deception target; synthetic/proxy labels do not justify an authenticity classifier, learned confidence or probability calibration. Record the decision in docs/MODEL_CARD.md and machine-readable report fields without introducing ML dependencies or a model artifact.
- D43: Reuse the actual production analysis function as the baseline in a separate authored mechanical suite. Predeclare expected counts/gates/arithmetic, include misinterpretation and failure scenarios, and report them as regression outcomes rather than classification metrics. Preserve existing production methodology and scoring.
- D44: Bind reports to the source catalog, verified Step 7 manifest and LF-normalized implementation hashes. Keep create-only ignored outputs and complete recomputation verification; compare strict JSON representations on both sides so decimal fractions round-trip correctly. Freeze a synthetic reference and test no-train/approval/metric/evidence/report integrity. No raw review bodies or local user paths enter the report.
- D45: Leave supervised precision, recall, F1, confusion matrix and calibration unavailable with explicit reasons. Do not convert unavailable metrics to zero, train on scenario votes, tune thresholds to these examples or substitute fixture pass counts for independent accuracy. Resource benchmarks, numeric-score defensibility and release audits remain later roadmap steps.

## Step 9 — Score and evidence interface

- D46: Use a disclosed navigation order for three initial findings: observed patterns, unavailable gaps, then not_observed; scoring methods first within each state, preserving returned order otherwise. Do not invent severity weights, hide the rest of the panel or change numeric scoring.
- D47: Native radio/disclosure controls and CSS bars cover the concrete chart needs without dependencies. Eligible/evaluated counts always retain denominators; exact rating bins have text equivalents. No time series is invented from a single returned window. All score values use the same styling and unavailable never becomes zero.
- D48: Render evidence through escaped React text/mark nodes, interpreting Python span offsets as Unicode code points and merging overlapping ranges. Reject reversed/out-of-bounds response spans before rendering. Keep actual references, context, pair-method details and bounded-preview notes; highlights are not conduct labels.
- D49: Keep confidence unset, the no-train model limitation visible and scope confined to the submitted subset. Preserve form cancellation/reset/error behavior and verify mobile/keyboard flow with real API-shaped synthetic data. No export, sharing, persistence, trained model or methodology change is justified by this UI step.

## Step 10 — Measured benchmark and score release

- D50: Use the existing pinned API TestClient and standard-library subprocess/timing/native RSS interfaces. Three fresh processes per authored case isolate lifetime memory peaks; record all samples, medians/maxima, settings and exact input/implementation hashes. Exclude socket/provider latency explicitly. Preserve an immutable reviewed synthetic record, create-only ignored reruns and verification without asserting noisy timing equality. No new package or speed assertion on shared CI is needed. Starlette's pinned transport requires httpx2 distribution metadata.
- D51: Keep production limits unchanged. Test default rate separately from a controlled two-slot admission probe with a declared rate override. Record slow-body termination and retain worker-cancellation regression coverage. Measurements on this Windows machine do not size hosting or certify production disconnect/proxy behavior. Record browser timing as unavailable when instrumentation cannot expose it.
- D52: Explicitly withhold numeric scores before public release: sample selection changes 0 to 100 within one authored batch, and the admitted evidence still supplies no independent target/calibration. Keep the current experimental local development arithmetic unchanged; require Step 12 to enforce/verify findings-and-coverage release behavior across API/UI before Step 13 deployment. No trained model or confidence is justified.
- D53: Treat measured NFKC response amplification (756,092 input bytes to 8,275,593 output bytes) as a concrete release-review item. Do not silently truncate evidence, claim language detection or raise ceilings based on local throughput. Review production memory/response/browser rendering budgets and any required normalization/output change with regression fixtures and a methodology revision if semantics change.

## Step 11 — Public information and contact deferral

- D54: Keep home synchronous and retain the existing client Analyzer. Add four static information routes and shared native navigation/footer/skip links rather than another framework, menu dependency or content system. Keep the existing visual language, route titles, noindex and explicit development/release limits.
- D55: Honor the user's explicit request to leave contact blank for later editing. Store an empty CONTACT_EMAIL in web/lib/contact.ts; render a blank address space with honest unavailable messaging and no fake mail/form action. A future real address enables only a trimmed/encoded mailto link, with privacy copy derived from the same setting. This overrides the Step 11 completion requirement, while a configured and checked monitored channel remains a launch prerequisite. No mailbox was contacted or verified.
- D56: Describe actual data flow and limitations: original CSV bytes reach the API, common masking is incomplete, memory cleanup is not secure erasure, and provider/mailbox retention is not verified. Content is an implementation description, not legal/privacy certification. Preserve no-train, unvalidated confidence, unchanged experimental arithmetic and the requirement to enforce numeric withholding before public release.


## Step 12 — Minimal security repairs

- D57: Enforce unconditional public score withholding in the shared worker result path, for JSON and CSV, without a configuration bypass. Preserve raw offline research arithmetic. Reject numeric/missing-policy/old-version responses in the browser and never render numbers from direct props. Version methodology 0.3.0 for the public contract/resource-gate change.
- D58: Reject post-NFKC/masking text/title/aggregate overflow under existing 5,000/300/250,000 point ceilings. Bound UTF-8 result serialization to 2 MiB inside admission and check deadline afterward. No silent truncation, output cache or custom serializer. Reuse multipart's installed native header budget rather than add a duplicate callback guard.
- D59: Use Next's native per-request nonce/strict-dynamic support and force-dynamic rendering, trading static HTML caching for a fresh nonce. Keep the synchronous home component; no new security dependency. Production scripts allow neither inline nor eval exemption; style inline is retained for numeric chart widths. No-store and anti-framing/referrer/permissions headers accompany CSP.
- D60: Preserve historical Step 10 measurements, intentionally capture a new source-bound Step 12 record, and compare all seventeen mechanical outcomes/relations before refreshing reference hashes. Keep NO TRAIN and unavailable independent metrics. Point-in-time npm/OSV checks returned no advisories; retain compatible ESLint pins without forcing peer resolution.
- D61: Finish the repository audit while explicitly withholding public-launch approval until monitored contact and actual provider TLS/origins/proxy/edge/resource/logging/retention evidence are verified. No speculative distributed infrastructure or deployment in this step. Ponytail full governs minimal fixes, never removal of security/validation.

## Step 13 — Preparation only by owner request

- D62: The owner explicitly requested “prepare only, keep contact blank.” Prepare native Render/Vercel dashboard settings and a hosted verification/rollback runbook; create no services, deploy nothing and keep Step 13 unchecked. Reuse pinned runtimes, existing checks and native hosting; no Docker, deployment SDK, new dependency or speculative infrastructure. Contact remains empty. Future public release requires actual owner/provider evidence and a compatible API/web pair; pre-withholding methodology 0.2.0 is not a safe rollback target.


## E00 — Product-link expansion planning

- D63: Preserve historical steps and use E01–E20 for incremental product-link development, with owner/assistant tasks, dependencies, acceptance and manual commit checkpoints. Start with source feasibility and permitted access before network implementation. Reuse existing analysis; distinguish product feedback, manipulation, AI authorship and authenticity. Training and LLM experiments are conditional on target validity, rights and measured need. Deployment remains deferred. Planning is not implementation or data admission.


## E01 — Source feasibility

- D64: Complete documentation-level source feasibility with a conditional merchant-authorized WooCommerce/headphones pilot recommendation and an explicit unresolved live-access blocker. Catalog/average-rating APIs do not establish review-body access. Amazon's current docs direct PA-API users to Creators API; Best Buy reviewed fields are aggregates; Bazaarvoice documents Enterprise/client prerequisites; Flipkart review-text access remains unverified. Country, final retailer/category, budget and actual permissions/access require owner choices in E02. No data source, dataset, training, purchase or network implementation is admitted by this research.


## E02 — Access preparation and live-source blocker

- D65: The owner confirmed no store/provider access. Record E02 as BLOCKED rather than equating a technical API schema, a Read key or a synthetic store with permission to analyze real reviews. Prepare an unapproved source card, separate-use checklist, least-privilege access guidance, unsent merchant request and future minimal probe plan. No access grant, merchant message, agreement, data request or source admission occurred. Keep E03 dependent work pending until the gate is satisfied or the owner explicitly changes scope.


## E03 — Independent source-neutral URL ingestion design

- D66: Treat explicit owner “do step 3” as E03 design authorization despite E02 access being blocked. Complete source-neutral design, preserve the access blocker, and allow only authored-fixture E04 work next. No live fetcher or source permission is created by this exception.
- D67: Proposed version-2 product endpoint/envelope preserves collection provenance and server-assigned collected origin without falsifying existing v1 paste/csv/research types. Reuse pure signal behavior with null public scores/confidence, explicit empty/partial sample states and atomic failure on invalid/upstream errors. Existing runtime schemas and methodology stay unchanged until implementation.
- D68: Fixed source/product requests, empty approved registry, DNS-to-peer binding with hostname-verified TLS, no redirects/retries/ambient credentials, restricted egress and scoped secrets/rights/quotas are activation requirements. Begin synchronous within shared two-slot/ten-second admission, four-second collection and bounded page/byte/header budgets; measure before introducing jobs/infrastructure or raising limits. These are design decisions, not verified controls.


## E04 — Authored source-parser mechanics

- D69: Add one pure offline WooCommerce-shaped parser using existing strict JSON decoding, safe ReviewInputError, canonical ReviewInput/Title validation and standard-library HTMLParser. Retain positive source IDs only internally, reject wrong identity/nonapproved status/duplicate IDs/malformed supplied metadata atomically, preserve duplicate wording from distinct source IDs, require explicit UTC source-field semantics and caller date. Ignore unconsumed provider fields including reviewer identity. Bound raw HTML, response bytes, page rows and text; defer masking/signals/public collected origin to their reviewed integration boundaries. No HTTP integration, source admission, new dependency or rewritten source-bound benchmark.


## E05 — Offline collection safeguards and remaining blocker

- D70: Implement reusable, transport-free request/destination/response/quota guards with an empty default registry and no dependency/credentials/network integration. Keep E05 BLOCKED: E02 rights/access and actual connection-bound TLS, restricted egress, timed I/O and cancellation cannot be certified by isolated accounting tests. No mock result is a real collection success; do not advance E06 automatically.
- D71: Honor owner workflow preferences: open the local site after each step and identify backend-only changes honestly; use natural, descriptive human commit messages from this checkpoint onward. No automatic staging/committing/pushing.
