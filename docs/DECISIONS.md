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
