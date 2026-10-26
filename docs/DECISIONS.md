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

Deferred: dependency versions to Step 2; full lexicon to Step 6; dataset/license choices to Step 7; score defensibility and performance thresholds to Step 10; operator contact to Step 11; hosting/log retention and deployment-specific enforcement to Steps 12–13.
