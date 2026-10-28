# ReviewTrust handoff

Date: 2026-10-28. Last verified step: Step 8 — ML Baseline and Evaluation.

Status: COMPLETED through the roadmap's explicit NO TRAIN alternative. Manual commit pending under the user's instruction. Step 9 has not started.

## Changes and files

- Added docs/MODEL_CARD.md: no-train decision based on the recorded Step 7 admission/target limits, production heuristic baseline, unavailable supervised results and conditions for reopening training. No classifier or learned weights were produced.
- Added ml/mechanical_cases.py: seventeen authored synthetic mechanics/limitation cases, with declared score and signal-count expectations. They are not deception ground truth or independent model test labels.
- Added ml/evaluate.py: reuse production analysis, verify the existing audit freeze, report no_train and null supervised metrics, check evidence/score/availability invariants, bind catalog/audit/code hashes, and support create-only output/full recomputation verification.
- Added ml/fixtures/mechanics.expected.json and ml/tests/test_evaluate.py: frozen synthetic report and eight evaluation integrity tests. Existing offline unittest discovery and CI pick them up without workflow/dependency changes.
- Added docs/EVALUATION.md with actual case outcomes, known failure modes, unavailable metrics, hashes and reproduction commands.
- Updated AGENTS.md, README.md checklist, SPEC.md acceptance/evaluation rules, ml/README.md and docs/DATASET_AUDIT.md follow-up, DECISIONS.md and THREAT_MODEL.md, plus this handoff.
- Production API/browser/scoring code, dependency pins, source cards and Step 7 manifest are unchanged. Methodology remains rt-patterns-0.2.0-experimental.

## Actual verification

`./scripts/check.ps1`: PASS.

- pip dependency check: no broken requirements.
- Backend pytest: 187 passed; Ruff lint/format PASS (14 backend Python files).
- Offline unittest: 21 passed (13 audit/split tests retained, 8 evaluation integrity tests added); Ruff lint/format PASS.
- Frontend Vitest: 13 passed; ESLint, Next route generation/TypeScript and optimized production build: PASS.
- Actual CLI output and full --verify against both generated and committed mechanical report: PASS. Report creation refuses overwrite; verification compares through the same strict JSON decoder on both sides so fractional results round-trip correctly.
- Document links, eight completed roadmap entries, conflict-marker/whitespace checks and empty staging area verified locally.

Evaluation integrity tests cover no-train/source-flag rejection, expected-score mismatch, broken evidence/reference/confidence detection, changed audit freeze, deterministic reference equality, altered metric/report verification, output confinement/no overwrite, safe unexpected failures and nonzero failure status.

No remote GitHub Actions run was executed or verified. No development server, real data acquisition, annotation round, model training, independent validity study or resource benchmark was performed. The no-train path is a completed decision, not a claim that an unsupported classifier was built.

## Actual mechanical result and limits

17 authored cases matched their declared outcomes; three cross-case relations passed. The cases reproduce distinct controls, shared templates, near repetition, quoted/negated/unlisted incentive wording, short/small/low-coverage subsets, Unicode normalization, masking collisions, contextual launches/ratings, metadata removal, unmarked sarcasm, negation abstention, feature overflow and instruction-like text.

Notable outcomes: templates and negated/quoted mentions can give score 0; unlisted wording can give 100; the authored sarcasm example triggers a contextual lexical disagreement; feature overflow withholds the score. These are implementation/limitation demonstrations, not empirical real-world false-positive or false-negative rates. The baseline does not become validated merely because it reproduces its declared rules.

Precision, recall, F1, confusion matrix and calibration remain null with an explicit no-independent-admitted-target reason. Trained model is null and training_authorized=false. Confidence remains unset. No synthetic-label classifier or percentage accuracy was created.

Evaluation version: rt-mechanics-eval-0.1.0.
Catalog SHA-256: 93ac7ddc7f58951eeced1bdcd5498ac1b6496142df4f8a0b10288b5496ab9f2c.
Preserved Step 7 audit manifest SHA-256: ba609938be807bf2539ef48766f3faf54a1ee8b267a91b66a281b07785d56582.
Frozen Step 8 report SHA-256: 66fd5aae9491b220e449ef4430546b039e955ea010e997fe6c6575251b12b288.

## Reproduction and integration

From repository root:

```powershell
& ./api/.venv/Scripts/python.exe -m ml.evaluate --output ml/artifacts/my-mechanics.json
& ./api/.venv/Scripts/python.exe -m ml.evaluate --verify ml/artifacts/my-mechanics.json
& ./api/.venv/Scripts/python.exe -m ml.evaluate --verify ml/fixtures/mechanics.expected.json
```

Use a new output name if one exists; never replace a frozen report to hide differences. Unix uses api/.venv/bin/python. The runner uses the existing pinned API environment and imports trusted local production source; no ML package was added. Reports contain status/counts and known code filenames, not review bodies or local user paths. Catalog/audit/implementation changes must be reviewed and versioned appropriately before intentionally updating the reference. Code hashes normalize CRLF to LF for cross-platform source consistency; the Step 7 data artifact still binds exact bytes.

The Step 7 synthetic holdout is recomputed for integrity only, not used to train/tune/evaluate a classifier. The Step 8 regression suite is separate and has no independent target labels. Reopening training requires new admitted rights/scope/target evidence and a reviewed implementation/source-card revision. The runner has no training override. Full performance/robustness benchmarks and numeric-score defensibility remain Step 10; security/provider/deployment gates remain Steps 12–13. ESLint 9 maintenance remains D15.

## Git and manual TODO

Starting HEAD: 072e08e (Added dataset audit and reproducible labelling splits), branch main. The user's Step 7 commit was present and the working tree was clean before Step 8. Verified origin: https://github.com/SamarVishwakarma2006/Review-Trust.git. No staging, commit or push was performed by the assistant.

Review and commit manually from repository root:

```powershell
git status --short
git diff -- ml AGENTS.md README.md SPEC.md docs
git add ml AGENTS.md README.md SPEC.md docs
git diff --cached --stat
git diff --cached
git commit -m "feat: document no-train baseline and reproducible mechanics evaluation"
git status --short
git show --stat --oneline HEAD
```

Manual TODO: review/commit Step 8, manually select the next recommended effort, then say next. No push is required for step completion.

## ACTION REQUIRED — CODEX MODEL FOR NEXT STEP

Current: Step 8, recommended GPT-6.1 Sol — High. Next: Step 9 — Final Trust Score and Evidence UI.

KEEP GPT-6.1 Sol and SWITCH reasoning effort to Medium. Exact next recommendation: GPT-6.1 Sol — Medium. User performs the switch; no automatic switch is claimed. Fallback if selectable: GPT-5.6 Sol — Medium.

Complexity: Moderate. Presentation work can use Medium while preserving the existing typed contracts and frozen methodology. Next scope: polished score/insufficient-evidence presentation, visible coverage/confidence limitations, prioritised computed findings, inspectable supporting reviews and justified accessible charts with text equivalents. Export/sharing stays deferred unless separately justified and privacy-safe; no scoring/model redesign belongs to this UI step. Test result/error/abort/reset flows, evidence accuracy, escaped text, keyboard/focus, mobile layout and API compatibility, then run the full check. Request manual escalation on a concrete unresolved privacy/rendering, accessibility or cross-system contract blocker. Stop until next.
