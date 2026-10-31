# E06 — Authored-fixture sample assembly

Date: 2026-10-31. COMPLETE for the owner's explicitly authorized synthetic-only scope. E02/E05 live collection remain BLOCKED. E07 integration has not started.

`api/app/source_sample.py` exposes a pure `assemble_fixture_sample` over 1–5 sequential JSON page buffers and a previously parsed product. No network, credential, provider total, persistence, dependency or serving-route changes. Every result says `evidence_origin=authored_fixture`. It is not a public analysis envelope or a v1 submission.

## Selection and coverage policy

- Apply existing strict page parsing to every row; errors reject the entire sample. Empty intermediate pages reject. Never skip invalid records or truncate.
- Compare request-local stable IDs before masking. Identical canonical records across pages are counted as overlap and retained once. Conflicting content or metadata rejects atomically. Same text from distinct IDs remains separate. Within-page duplicate IDs still reject under E04.
- Initial selection is newest_first. Known UTC timestamps must be nonincreasing across unique records, including page boundaries. Null dates remain null; their ordering cannot be established. No claim of provider snapshot stability follows from this check.
- Explicit fixture exhaustion permits complete for nonempty samples or empty for zero rows. This refers only to the authored selected window. A short or empty last page alone cannot prove exhaustion. Without an exhaustion marker, report partial with row_limit at 500 unique reviews, otherwise page_limit at five pages, otherwise source_window. Zero rows without exhaustion remain partial, not a proven empty product.
- Available total is always null, count_scope unknown; no percentage or all-reviews claim. Counters distinguish fetched records, identical overlap and retained review count (`len(reviews)`). Provider selected-window limits remain unknown separately from software ceilings.
- Product identity stays exact and internal. Variable parent products disclose combined scope; simple products disclose unknown. Never infer a selected child variant. UTC window timestamps describe supplied fixture collection provenance, not the review-date range or measured network timing.

Bounds: 1 MiB aggregate page bytes, 256 KiB/page, 100 rows/page, five pages, 500 retained reviews and existing 5,000/300/250,000 normalized text limits. Reuse existing NFKC/email/phone masking before returning canonical reviews; it is incomplete privacy protection, not anonymization. Product metadata is internal, not a masked public title. Source IDs remain internal comparison keys, and raw canonical records exist transiently for conflict checks. No logs or persisted samples.

## Verification

19 authored cases exercise overlap/conflicts, repeated prose from distinct IDs, explicit versus unknown exhaustion, page/row/text/byte bounds, known-date ordering, malformed/mixed-product pages, nulls, UTC provenance and masking amplification. Full checks pass: 377 backend, 28 offline, 27 frontend tests; dependency check, Ruff, ESLint, typecheck and production build. Both frozen research reports verify unchanged.

Live source exhaustion, sorting, review availability, actual variant attribution, timeouts and provider quotas are unverified. This function deliberately accepts authored bytes only and makes no transport calls. E07 must later integrate an appropriately versioned collected-origin API, deadlines/admission and public serialization without mislabeling these fixtures. E02/E05 permission and network gates still control real access. No training or deployment.

The local website was opened after restarting its loopback development server outside socket restrictions. It still shows Paste reviews / Upload CSV; no product-link result is simulated.
