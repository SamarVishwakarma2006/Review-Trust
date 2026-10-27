# ReviewTrust handoff

Date: 2026-10-27. Last verified step: Step 7 — Dataset Audit and Labelling System.

Status: COMPLETED. Manual commit pending under the user's instruction. Step 8 has not started.

## Changes and files

- Added docs/DATASET_AUDIT.md and ml/sources.json: primary-source metadata audit of Amazon Reviews'23 Electronics, YelpCHI and the Ott ACL 2011 study. All real candidates remain not_approved because relevant permission/target/domain gates are unresolved. No archives or real review text were downloaded and no contact was made.
- Added docs/LABELLING.md: rt-labels-0.1 target definitions, independent role votes, external-evidence requirements, proxy/uncertainty abstention, blinded review, conflict retention and versioned adjudication. No real annotation round or human-agreement statistic is claimed.
- Added ml/audit.py: standard-library bounded normalized JSONL validation, consensus mechanics, quality counts, product/exact/near connected components, label-independent deterministic split assignment, create-only manifests and full recomputation verification. Only synthetic-fixture-v1 is admitted; training_authorized is always false.
- Added ml/fixtures/synthetic.jsonl and synthetic.manifest.json, plus ml/tests/test_audit.py. Only project-authored synthetic text is versioned; generated research outputs stay ignored.
- Updated ml/README.md, scripts/check.ps1 and .github/workflows/ci.yml for offline usage/tests/lint without new dependencies.
- Updated AGENTS.md, README.md checklist, SPEC.md dataset/acceptance rules, docs/DECISIONS.md, THREAT_MODEL.md and this handoff. Public API, scoring methodology and browser implementation are unchanged.

## Actual verification

`./scripts/check.ps1`: PASS.

- pip dependency check: no broken requirements.
- Backend pytest: 187 passed; Ruff lint/format passed (14 backend Python files).
- Offline unittest: 13 passed, including permission rejection before record-file access, consensus/proxy/conflict behavior, exact/near threshold and transitive grouping, product separation, input/aggregate/decimal/Unicode limits, deterministic label-independent membership, giant-component diagnostics, frozen manifest equivalence, tamper detection and no-overwrite/output confinement.
- Offline Ruff lint/format: PASS using api/pyproject.toml.
- Frontend Vitest: 13 passed; ESLint, Next route generation/TypeScript and optimized production build: PASS.
- CLI wrote an ignored synthetic manifest and verified it by full recomputation. The committed expected manifest also verifies. Source bytes were normalized to LF so Windows and Ubuntu checkout semantics agree with .gitattributes.
- Document links, seven checked roadmap steps, merge-marker/whitespace checks, PowerShell script syntax and empty staging area verified locally.

Configured CI now includes offline tests and lint. No remote GitHub Actions run was executed or verified. No real-data validity/performance/accuracy metric was measured. No development servers were needed or started for this offline-only step.

## Synthetic audit result

24 authored rows; 12 product groups; one cross-product exact duplicate joins two products, yielding 11 connected components, largest size 4. No near pair in the committed fixture; separate transitive and exact-threshold tests cover near grouping. Missing ratings: 8; missing dates: 6. Text lengths: 65–73 code points, 1,672 total. Synthetic scenario labels: 12 per class. Default seed 20261027 gives train 20, validation 2 and test 2, each with both scenario classes. There are no split diagnostics in this fixture. These are mechanical fixture results, not real-world data or model evaluation.

Exact fixture artifact SHA-256: cfa6c6f552a1587c8f4124839e021eaa67fa440b8d54b792835a55798d5ad4ff.
Frozen synthetic manifest SHA-256: ba609938be807bf2539ef48766f3faf54a1ee8b267a91b66a281b07785d56582.

## Integration notes and limitations

- Read docs/DATASET_AUDIT.md, docs/LABELLING.md and ml/README.md before Step 8. Source cards distinguish published reports from unmeasured local quantities. A source download, repository wrapper licence or approval to another person is not ReviewTrust admission.
- This is a bounded synthetic research harness, with no real-data admission override or training command. CLI source checks run before normal record processing; audit also enforces the synthetic source ID. Declaring an arbitrary file synthetic is not proof of its provenance. Real admission needs a reviewed implementation/card revision with actual rights, scope and target evidence.
- Input limits: 10 MiB, 500 rows, 5,000 text code points each and 250,000 aggregate. Strict fields/IDs/dates/ratings/votes, duplicate IDs/keys and malformed input reject atomically. No silent truncation, filtering or independent chunk splits.
- Product groups must already map the same underlying product across releases. Normalized equality/trigram Jaccard >=0.80 and shared product keys form one transitive graph before splitting. Undetected paraphrases and incorrect product mapping remain leakage risks; larger datasets need a reviewed global index.
- SHA-256 seeded component buckets use expected 70/15/15 group proportions without labels or rebalancing. Empty/missing-class/incomplete-scope partitions are explicit diagnostics. Do not reroll seeds or divide components to obtain convenient metrics.
- Scenario consensus requires at least two distinct supported unanimous role votes and evidence references; proxies, missing evidence, unknown votes and conflicts abstain. Distinct strings do not establish real reviewer independence or evidence truth. The resolver's external_documentation branch is not real-data admission authority.
- Manifests freeze exact bytes, selected source card, pipeline/seed, record/group/text hashes, labels and membership. They omit body text/product keys/paths; hashes are not anonymization guarantees. Real data and derived artifacts remain governed by permissions/retention and ignored by Git. Only synthetic examples are committed.
- Deployed methodology remains rt-patterns-0.2.0-experimental, confidence unset. Full resource/validity evaluation, proxy/provider privacy/security and deployment gates remain later work. ESLint 9 maintenance remains D15.

## Git and manual TODO

Starting HEAD: 778754a (Added versioned explainable review detection signals), branch main. The user's Step 6 commit was present and the working tree was clean before Step 7. Verified origin: https://github.com/SamarVishwakarma2006/Review-Trust.git. No staging, commit or push was performed by the assistant.

Review and commit manually from the repository root:

```powershell
git status --short
git diff -- ml scripts/check.ps1 .github/workflows/ci.yml AGENTS.md README.md SPEC.md docs
git add ml scripts/check.ps1 .github/workflows/ci.yml AGENTS.md README.md SPEC.md docs
git diff --cached --stat
git diff --cached
git commit -m "feat: add dataset audit and reproducible labelling splits"
git status --short
git show --stat --oneline HEAD
```

Manual TODO: review/commit Step 7, keep the recommended model/effort, then say next. No push is required for step completion.

## ACTION REQUIRED — CODEX MODEL FOR NEXT STEP

Current: Step 7, recommended GPT-6.1 Sol — High. Next: Step 8 — ML Baseline and Evaluation.

KEEP GPT-6.1 Sol — High if already selected; no switch required. User controls model/effort; no automatic switch is claimed. Fallback if selectable: GPT-5.6 Sol — High.

Complexity: Complex. Step 8 must explicitly assess training eligibility from the source/label audit. Current evidence supplies no admitted electronics deception target, so prepare a documented no-train outcome and justified heuristic/mechanical evaluation unless new evidence resolves those gates. Do not train on synthetic scenarios/proxy labels as authenticity truth or fabricate independent precision/recall/calibration. Test any evaluation workflow and regression invariants, preserve frozen splits/train-only learned preprocessing, and run the full repository checks. Request manual escalation on a concrete unresolved target-validity, permission/provenance or leakage blocker. Stop until next.
