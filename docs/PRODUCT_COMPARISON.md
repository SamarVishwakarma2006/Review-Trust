# E14 authored comparison

The synthetic comparison is complete; real-source E14 acceptance remains pending
source access and live collection. POST /v2/demo/analyze additionally accepts
compare, compare_gaps and compare_empty. It never accepts a URL or fetches data.

demo_comparison.py composes the existing candidate selector, per-product fixture
analysis and dated offer comparison. A fixed catalog contains an original and two
alternatives: wireless over-ear headphones with microphones. All identity fields
are authored; titles and public analysis retain synthetic provenance. Same-product
offers are compared separately for each product. There is no cross-product quality
winner, learned ranking or weighting: original first, then eligible catalog order.

The API returns rt-comparison-0.1.0 with one to three products, each with its role,
FixtureReport and OfferComparison. This version's fixed specifications and delivery
context are disclosed in the UI; this is not a general catalog response contract.
Samples have 20/8/12 rows; the gaps example has an incomplete eight-row sample and
a zero-row sample, plus unknown mandatory fees. Equal complete offer totals keep
both references. Missing evidence never earns a favorable rank. Native disclosures
show counts, bounded supporting wording and review-pattern findings.

One admitted worker sequentially analyzes at most three products (40 authored rows
total), with at most six offers, no external calls and no provider spend. Shared
rate/admission controls, deadline, cancellation retention and input limits remain.
The final aggregate also enforces the 2 MiB response ceiling; evidence is not truncated.
Browser validation checks nested fixture reports, offer provenance, totals, dates,
coverage and tie references. Existing request generation/abort/reset guards apply.

Local observation 2026-11-01: full example 262 ms / 29,693 UTF-8 bytes; gaps example
14 ms / 20,380 bytes through local HTTP including client overhead. Single observations,
not capacity or latency guarantees. The next request was rate-limited and is excluded.
No live-provider fan-out latency/cost was measured. Existing frozen benchmarks are
unchanged and do not measure this new comparison path.

Verification: full scripts/check.ps1 passed (498 backend, 28 offline, 33 frontend;
lint, formatting, types, build). API tests cover three scenarios, bounds, public
score withholding, incomplete samples, unknown totals and ties. UI tests cover
validation and no-alternative/missing-evidence rendering/reset. Live access,
deployment, training and contact setup remain deferred.
