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
