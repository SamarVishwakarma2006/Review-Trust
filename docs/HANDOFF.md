# ReviewTrust handoff

Date: 2026-10-27. Last verified step: Step 6 — Explainable Detection Signals.

Status: COMPLETED. Manual commit pending under the user's instruction. Step 7 has not started.

## Changes and files

- Added api/app/signals.py: bounded sparse unigram/bigram TF-IDF repetition, UTC three-day timing windows, exact rating-value distributions and frozen rt-en-polarity-0.1 disagreement with conservative abstention. Uses only the standard library; no dependencies or datasets added.
- Updated api/app/analysis.py and results.py to methodology rt-patterns-0.2.0-experimental, typed contextual values/evidence and explicit availability reasons. Repetition/incentives remain the only scoring signals. Preserve max aggregation, exact half-up rounding, coverage gates, masking and unset confidence.
- Added api/tests/test_signals.py; updated test_analysis.py and test_api.py. Fixtures cover thresholds, UTC normalization, cosine formula, exact/near pairs, feature-cap withholding, deadlines, metadata/order invariance, cue spans, abstention, evidence caps, maximum rows and JSON/CSV equivalence.
- Updated web/lib/api.ts, web/app/results.tsx and web/tests/page.test.tsx to validate the matching methodology and display similarity method, histogram, timing window and rating/date/polarity evidence. Contextual findings are visibly outside the score.
- Updated AGENTS.md, README.md checklist, SPEC.md methodology/acceptance, docs/API.md, FRONTEND.md, DECISIONS.md, THREAT_MODEL.md and this file.

## Actual verification

`./scripts/check.ps1`: PASS (186 backend tests, 13 frontend tests, pip dependency check, Ruff lint/format, frontend lint/type check and optimized production build).

Final review aligned polarity evidence tokenization with the direction rule, preventing a cue inside an apostrophe-containing non-cue token from being reported. Added an emoji/offset regression. After this backend-only change: **187 backend tests passed**, Ruff lint/format PASS (14 Python files). Frontend source did not change after the successful full check.

Live in-app browser with loopback API and web services: uploaded a 20-row synthetic CSV with ratings/dates. All five findings returned observed, timing window Jan 1–3 contained 19/20 dated reviews across a 31-day span, rating histogram showed twenty 1-star ratings, and lexicon disagreement exposed supported positive direction. Score 0 arose from intentionally repeated/incentive fixture text, not a measured authenticity judgment. Contextual-only labels, version and unvalidated confidence were visible. Browser error log was empty. Screenshot: ignored .tmp/step6-results.png. Temporary servers were stopped.

Full resource benchmarking and independent validity evaluation are still Step 10. Targeted tests are not proof of production performance, sentiment/deception accuracy, complete anonymization or comprehensive accessibility. Remote GitHub Actions was not run or verified by this step.

## Integration notes and limitations

- Read SPEC.md section 5 for the complete frozen algorithm and lexicon, including whole-row abstention and exact eligibility/window/tie rules. Methodology changes require another version bump and regression fixtures.
- TF-IDF fits only within the submitted eligible rows, including duplicates. Raw TF, smoothed IDF, L2 normalization, no stemming/stop words; exact equality or cosine >=0.90 qualifies. At most 20,000 features; overflow marks repetition unavailable and withholds the score instead of pruning or returning an exact-only score. Existing timeouts return no partial analysis.
- All-pairs sparse comparison is bounded to 124,750 pairs and checks the cooperative deadline. Full CPU/memory/concurrency measurements remain Step 10. The maximum-row fixture and feature-cap fixture are mechanical tests, not benchmarks.
- Score.evaluated_signal_ids contains only available repetition/incentive methods; Coverage.evaluated_signal_ids also includes contextual methods. Availability of context cannot substitute for a missing scoring signal. Metadata removal cannot improve or alter the score.
- Timing requires >=20 dates, >=80% coverage and >=28 elapsed days. Rating distribution requires >=20 ratings and >=80% coverage. Disagreement requires >=20 rated supported-direction rows and explicitly reports its denominator; it does not impose the scoring panel's five-token gate or an extra 80% gate.
- Sparse lexical rules miss many meanings, languages, negations and sarcasm. Quoted/negated incentive phrases still count as mentions, never conduct. No classifier was trained and no confidence level is justified.
- Evidence may return submitted rating and normalized UTC day alongside redacted text; IDs remain omitted. Phrase/cue offsets index displayed Unicode code points. Pair previews are at most ten; single-row evidence at most twenty. Truncation flags refer to omitted matching references, not every omitted pair.
- Browser rejects methodology versions other than rt-patterns-0.2.0-experimental; deploy matching web/API builds. No stored-result migration is needed because results are not persisted. Final UI polish is Step 9.
- Existing privacy, single-process admission/cancellation, proxy/provider retention/TLS and dependency audit limitations remain in force. ESLint 9 maintenance is still D15.

## Git and manual TODO

Starting HEAD: 4e785f9 (Added review submission and initial evidence interface), branch main. The user's Step 5 commit was present and the working tree was clean before Step 6. No staging, commit or push was performed by the assistant.

Review and commit manually from the repository root:

```powershell
git status --short
git diff -- api web AGENTS.md README.md SPEC.md docs
git add api web AGENTS.md README.md SPEC.md docs
git diff --cached --stat
git diff --cached
git commit -m "feat: add versioned explainable review detection signals"
git status --short
git show --stat --oneline HEAD
```

Manual TODO: review/commit Step 6, keep the recommended model/effort, then say next. No push is required for step completion.

## ACTION REQUIRED — CODEX MODEL FOR NEXT STEP

Current: Step 6, recommended GPT-6.1 Sol — High. Next: Step 7 — Dataset Audit and Labelling System.

KEEP GPT-6.1 Sol — High if already selected; no switch required. User controls model settings; no automatic switch is claimed. Fallback if selectable: GPT-5.6 Sol — High.

Complexity: Complex. Next scope: audit dataset provenance, license/permissions, electronics relevance, language, label provenance and data quality; design reproducible manifests and product/duplicate-cluster splits that prevent leakage. Do not assume sentiment/platform labels are deception ground truth; unsupported targets must lead to a documented no-train decision rather than invented labels. Test audit/split mechanics with synthetic fixtures and run the full project checks. Request manual escalation on a concrete unresolved permission/provenance, target-validity or leakage blocker. Stop until next.
