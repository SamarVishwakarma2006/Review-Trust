# E19 local verification — 2026-11-02

Scope: working tree based on main commit 5183304, with documentation-only E18/E19
changes. Status: local synthetic verification passed; full E19 remains PARTIAL /
BLOCKED on real-source acceptance. This is not a product-link release approval.

## Supported-source matrix

| Path | Actual support | Limitation |
| --- | --- | --- |
| v1 paste/CSV | Bounded submitted-review analysis | User supplied; no source authenticity claim |
| v2 demo | Fixed authored analysis/comparison/brand examples | No external products or reviews |
| v2 products | Validated requests, fail-closed response | No activated collector or approved source |
| WooCommerce component | Offline parser and unwired transport guards | No merchant access or live egress proof |
| Amazon.in / Bright Data | Owner-reported account, setup deferred | No admitted source/rights or tested live adapter |
| Flipkart / other retailers | No live support | No universal URL crawling |

## Actual checks

scripts/check.ps1 passed: 500 backend, 28 offline and 35 frontend tests; dependency
consistency, Ruff formatting/lint, ESLint, TypeScript and production build passed.
The tests include cancellation slot retention, owned-stream cleanup, admission,
rate limits, body/response bounds, fail-closed product requests, fixture provenance,
score withholding and escaped evidence/offset validation. Frozen reports passed
unchanged. No new runtime code or dependency was required.

Fresh bounded benchmark: docs/benchmarks/20261102-e19.json, created via
ml.benchmark and verified successfully (benchmark_passed no_train). This records
the existing nine synthetic workloads in three fresh processes each, sampling and
admission/rate/deadline probes. It does not benchmark live providers or the new
comparison/brand UI. Historical reports remain intact; timings are observations,
not equality requirements or throughput guarantees.

Browser walkthrough exercised brand_gaps against the local API: 20/8/0 rows,
complete/partial/empty samples, 2-of-3 negative battery wording, duplicate groups,
unknown offer totals and withheld score/confidence. Local tab retained for inspection.
This is authored data, not a successful real URL collection. Previous E14 local
measurements remain in PRODUCT_COMPARISON.md; they are not provider capacity evidence.

## Remaining release gates

Real URL-to-report-to-alternatives acceptance cannot run until permitted source
access and a tested adapter exist. Verify rights, live peer-bound TLS/DNS/egress,
quotas, pagination/date/variant semantics, privacy/logging/retention and representative
owner acceptance before claiming full E19. Dedicated mobile/keyboard release QA and
live fan-out/provider resource measurements remain pending. No hosted CI, public
HTTPS, production CSP/CORS, rollback or provider-memory verification is claimed.

E20 remains DEFERRED under the owner's no-deployment instruction. Contact remains
blank. Existing DEPLOYMENT.md is preparation, not a launch authorization. Training
does not unblock any source-access or deployment gate. The next useful owner action
is resume provider setup with credentials kept outside chat/source control.
