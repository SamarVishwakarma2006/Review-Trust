# Step 8 evaluation record

Date: 2026-10-28. Outcome: documented no-train decision plus reproducible synthetic mechanics evaluation. See [model card](MODEL_CARD.md) for the decision and [dataset audit](DATASET_AUDIT.md) for the recorded data limitations.

## Reproduction

From the repository root with the pinned API environment:

```powershell
& ./api/.venv/Scripts/python.exe -m ml.evaluate --output ml/artifacts/my-mechanics.json
& ./api/.venv/Scripts/python.exe -m ml.evaluate --verify ml/artifacts/my-mechanics.json
& ./api/.venv/Scripts/python.exe -m ml.evaluate --verify ml/fixtures/mechanics.expected.json
& ./api/.venv/Scripts/python.exe -m unittest discover -s ml/tests -v
```

On Unix use api/.venv/bin/python. The runner reuses the local production analysis code and existing pinned dependencies. It performs no network calls, training, label fitting or model loading. --output creates a new ignored artifact only under ml/artifacts/ and refuses overwrite. --verify recomputes the complete report. Safe fixed errors and a nonzero exit indicate a mismatch, changed source gate, invalid audit freeze or failed mechanical check. A report containing failed checks also returns nonzero; file existence alone is not successful verification.

Evaluation version: rt-mechanics-eval-0.1.0. Production methodology: rt-patterns-0.2.0-experimental. Cases and expected outcomes are declared in ml/mechanical_cases.py. Reports bind canonical source-catalog hash, the recomputed Step 7 audit manifest, and LF-normalized source hashes for the runner, case definitions, auditor and production analysis/contracts/ingestion code. Production code hashes use CRLF-to-LF normalization for Windows/Ubuntu reproducibility; the Step 7 fixture still binds exact LF input bytes. Reports omit raw review bodies, titles, per-review evidence and local user paths; repository-relative implementation filenames identify the code being checked.

The Step 7 manifest and source cards were preserved. The runner verifies synthetic membership integrity without fitting/tuning on those labels. No separate real classifier test set exists. A changed audit/catalog/admission state requires a new documented training review; this executable always takes the no-train path for the current evidence and has no training override.

## Actual mechanical outcomes

All 17 cases matched their declared outcomes; the three cross-case checks also passed. These are regression checks, not a numerator/denominator for model accuracy.

| Authored case | Observed experimental score | Mechanical observation / limit |
| --- | --- | --- |
| Distinct indexed control | 100 | Neither scoring pattern observed; missing contextual metadata remains unavailable |
| Shared template / duplicate ingestion | 0 | All 20 rows qualify as repetition; no deception inference follows |
| Long near repetition | 85 | Three of twenty rows have qualifying partners |
| Negated incentive mention | 0 | Twenty mentions count even though wording is negated |
| Quoted incentive mention | 0 | Twenty quoted mentions count; no participation is established |
| Unlisted incentive-like paraphrase | 100 | Fixed phrase inventory misses the authored alternative wording |
| Short text | Withheld | No eligible five-token rows |
| Nineteen-review subset | Withheld | Available findings do not satisfy the score sample gate |
| Low eligible-text coverage | Withheld | Twenty eligible rows among twenty-six fall below 80% |
| Unicode-equivalent bodies | 0 | Normalization merges the authored surface forms |
| Masked contact collision | 0 | Twenty synthetic addresses are masked; remaining bodies repeat |
| Declared launch / concentrated ratings | 100 | Timing and rating concentration observed as context only |
| Metadata removed | 100 | Same score object as the launch/rating case, with context unavailable |
| Authored unmarked sarcasm | 100 | Positive lexicon cue yields 20 contextual disagreements at rating 1 despite the author's negative reading |
| Negated polarity | 100 | Whole-row negation rule abstains on all twenty rows; context unavailable |
| Feature vocabulary overflow | Withheld | Repetition unavailable with feature_limit; other context cannot replace a scoring signal |
| Instruction-like text | 100 | Authored instruction string remains inert review text |

Per-case checks verify declared score, score status, selected signal assessment/matching/eligible counts, confidence unset, evidence references and real spans, scoring-panel membership, methodology agreement and null/zero-evaluation semantics for unavailable findings. Cross-case checks verify metadata-removal score equality, twenty masked email occurrences and feature-cap withholding. Complete measured counts/statuses are in the frozen JSON; the table is a readable summary.

These cases intentionally include ways an index could be misread. A passing template or negation case does not mean a detection false positive has been ruled out. The sarcasm reading is authored scenario context, not independently collected sentiment truth. No empirical population false-positive/negative rates are computed. Indexed controls and predeclared expectations verify implementation consistency; they do not validate thresholds or sampling representativeness.

## Unavailable supervised results

| Metric | Result | Reason |
| --- | --- | --- |
| Precision, recall, F1 | Not available (null) | No independent admitted in-domain deception target |
| Confusion matrix / real class support | Not available (null) | No evaluated real classifier test labels |
| Probability calibration | Not available (null) | No probability model or suitable independent target |
| Confidence level | Unset | Mechanical agreement does not validate confidence |

The runner does not coerce these unavailable values to zero or score synthetic votes as authenticity labels. It tests that edits to approval flags, metrics, frozen artifacts and expected outputs cannot silently pass recomputation.

## Frozen reference and remaining work

Catalog SHA-256: 93ac7ddc7f58951eeced1bdcd5498ac1b6496142df4f8a0b10288b5496ab9f2c.
Step 7 audit manifest SHA-256: ba609938be807bf2539ef48766f3faf54a1ee8b267a91b66a281b07785d56582.
Step 8 report SHA-256: 66fd5aae9491b220e449ef4430546b039e955ea010e997fe6c6575251b12b288.

The frozen reference includes implementation hashes, so changing detector or runner code requires reviewing the resulting report difference and intentionally updating the reference alongside the appropriate methodology/evaluation version. Never refresh expected outcomes merely to hide a failed check. No real data, trained model or synthetic classifier accuracy was produced. Full resource/robustness benchmarking and the numeric-score release decision remain Step 10; security/provider/deployment gates remain Steps 12–13. Local passing checks do not establish remote CI execution.
