# ReviewTrust handoff

Date: 2026-10-28. Last verified step: Step 10 — Benchmark and Model Report.

## REVIEWTRUST STEP HANDOFF

Step/status: Step 10 COMPLETED, with documented public-release concerns. Manual commit pending. Step 11 has not started. Public deployment and numeric publication are not approved.

## Changes and files

- Added ml/benchmark.py: nine authored resource workloads, three fresh bounded subprocesses each, exact request hashes, wall/CPU/process peak RSS, runtime/settings and implementation hashes checked before/after measurement. Timings include a complete in-process TestClient POST, excluding imports/setup/socket/provider latency. No dependency changed; the pinned transport uses httpx2.
- Added controlled two-slot dense-load, default-rate and slow-body-timeout probes; six sampling scenarios use seed 20261028. Preserved the original 17-case mechanics evaluation, source admission, no-train decision and production methodology/arithmetic.
- Added docs/benchmarks/20261028.json, reviewed synthetic measurement record. Report SHA-256: bfddc63f8d29c5dcc0c7785e595f50305262e933a5f966109577ed3c0335b7d8. No raw reviews or local user paths. New outputs are create-only under ignored ml/artifacts/.
- Added ml/tests/test_benchmark.py: seven integrity checks for record/source/input tampering, measurements/summaries, exact ceilings, output confinement/overwrite, three fresh bounded subprocesses per case and safe timeout errors. Existing unittest/CI discovery includes these without speed assertions on shared hosts.
- Added docs/BENCHMARK.md with measured tables, hardware/runtime, measurement boundaries, failure analysis, reproduction and release decision. Updated MODEL_CARD.md, EVALUATION.md, DECISIONS.md (D50–D53), THREAT_MODEL.md, SPEC.md, README.md, ml/README.md, AGENTS.md and this handoff.

## Actual verification

`./scripts/check.ps1`: PASS.

- pip check: no broken requirements.
- Backend: 187 pytest tests passed; Ruff lint/format passed (14 files). Streaming, CPU timeout and worker-cancellation slot-retention regressions remain passing.
- Offline: 28 unittest tests passed, including seven benchmark integrity tests; Ruff lint/format passed (eight Python files).
- Frontend: 20 tests passed; ESLint, route type generation/TypeScript and optimized production build passed. No frontend implementation changed.
- `api/.venv/Scripts/python.exe -m ml.benchmark --output ml/artifacts/step10-20261028-verified.json`: PASS, 27 isolated resource samples, admission/rate/slow-body probes and sampling observations. Reviewed output copied to docs/benchmarks/20261028.json.
- `api/.venv/Scripts/python.exe -m ml.benchmark --verify docs/benchmarks/20261028.json`: PASS. Verification binds hashes/outcomes without demanding timing equality. The unchanged frozen Step 8 mechanics report is also verified by the offline tests.

Resource medians: 20 distinct rows 26.36 ms; 500 dense rows 1,412.43 ms; maximum aggregate text 157.57 ms; exact 1 MiB JSON 23.87 ms; 500-row Unicode CSV 200.85 ms; feature withholding 51.29 ms; Unicode expansion 1,520.33 ms. Highest observed single-child lifetime peak RSS: 86.89 MiB. These are local observations, not provider capacity or worst-case guarantees.

Two controlled dense requests completed in approximately 4.30 seconds; third returned 503 analysis_busy, health returned 200 and slots returned to zero. Default three immediate requests returned 200/200/429. Delayed receive under a shortened budget returned 503 request_timeout with admission released. Barrier-controlled elapsed time is not steady-state throughput.

The production frontend opened on loopback. Browser read-only evaluation did not expose the Performance API; browser timings/transfer budgets remain N/A. Static emitted JS/CSS file inventory is separately labelled in the report. Temporary browser tab and server were closed/stopped. No remote CI, provider load test, deployment or public release was run or verified.

Early harness construction corrected CSV padding/point counting, UTF-8 stress encoding, installed httpx2 metadata and the actual analysis_busy code before final capture. Only the verified final record is a committed candidate; ignored intermediate artifacts are not references.

## Findings and release prerequisites

- NO TRAIN remains explicit; all real candidates remain not_approved. No independent precision/recall/F1/confusion matrix/calibration or confidence level is available. Fixture agreement is not authenticity accuracy.
- One fixed batch scores 50 overall, 0 for its first half, 100 for its last half and 45 for the fixed seeded sample. Row/coverage gates withhold correctly. Metadata removal preserves scoring in the frozen mechanics case.
- Public numeric scores are NOT APPROVED. Enforce findings/coverage with score withheld across API/UI before deployment, and verify the release policy in Step 12. Current loopback development retains rt-patterns-0.2.0-experimental arithmetic; withholding is not already enforced in code. This decision completes Step 10 without completing release gates.
- Unicode normalization expands a valid 756,092-byte request into an 8,275,593-byte response. Declared English is not language detection. Keep current ceilings; review normalized/output bounds, browser rendering and provider memory/worker budgets before release. Do not silently truncate evidence or change methodology without version/fixture review.
- No comparable prior baseline exists. Record absolute timings only. Browser/provider timing, production proxy/disconnect behavior, sustained loads, aggregate memory and hosted capacity remain unresolved release measurements. Step 12 must bound these risks; Step 13 must verify deployment.
- The optional gstack helper was unavailable; its measurement principles were applied through the repository harness. No helper installation or telemetry occurred. Restoring it with /gstack-upgrade is optional and separate.

## Git and manual TODO

Starting HEAD: f455449 (Polished score coverage and supporting evidence interface), branch main. The user's Step 9 commit was present and the tree was clean before Step 10. Verified origin: https://github.com/SamarVishwakarma2006/Review-Trust.git. No staging, commit or push was performed by the assistant.

Review and commit manually from repository root:

```powershell
git status --short
git diff
git add AGENTS.md README.md SPEC.md docs ml/README.md ml/benchmark.py ml/tests/test_benchmark.py
git diff --cached --stat
git diff --cached
git commit -m "test: add reproducible resource benchmarks and score release decision"
git status --short
git show --stat --oneline HEAD
```

Manual TODO: review/commit Step 10, manually select the next recommended model/effort, then say next. Step 11 requires a real user-supplied contact/dispute destination before completion. No push is required for completion.

## ACTION REQUIRED — CODEX MODEL FOR NEXT STEP

Current: Step 10, recommended GPT-6.1 Sol — High. Next: Step 11 — Public Website and Product Content.

SWITCH manually to GPT-6 Luna — Medium if selectable. User performs the switch; no automatic switch is claimed. Fallback if selectable: GPT-5.6 Luna — Medium. Use GPT-6.1 Sol — Medium if implementation complexity exceeds Luna's scope (fallback GPT-5.6 Sol — Medium if selectable).

Complexity: Simple/Moderate. Next scope: landing page, how-it-works, methodology/limitations, privacy and a functioning contact/dispute mechanism using a real destination, with responsive navigation/accessibility checks. Preserve experimental/no-train limitations and the public-score release prerequisite. Test links, mobile/keyboard flows, contact behavior and existing analyzer interactions; run relevant checks and the full suite. Ask for the contact destination early while completing independent content. Escalate manually on a concrete contact/privacy, scope or implementation blocker; never invent an address, add persistence or deploy without authorization. Stop until next.
