# Model card — no-train baseline

Decision date: 2026-10-28. Step 8 outcome: **NO TRAIN**. No learned model or weights were produced. The baseline remains the deterministic production panel under rt-patterns-0.3.0-experimental (offline arithmetic retained; public HTTP values withheld). This card describes an unvalidated experimental system, not an authenticity classifier.

## Evidence for the decision

The Step 7 audit dated 2026-10-27 admits only project-authored synthetic fixtures. No new permission or target evidence was supplied before this decision. The recorded real candidates remain not_approved; their exact limitations and primary references are in [dataset audit](DATASET_AUDIT.md) and ml/sources.json. This step relies on that frozen audit, not a new acquisition or legal review.

The research tool's current gates do not establish an independently documented, permitted, in-domain deception target. Ratings, purchase flags, sentiment, platform filtering, detector outputs and authored scenario votes do not substitute for such a target. Training or calibrating on those labels would answer a different question while implying unsupported authenticity performance. No real review corpus was acquired, no annotation round occurred and no test labels were selected to improve a model.

## Baseline and intended use

| Item | Current state |
| --- | --- |
| Learned classifier / fitted weights | None |
| Training / validation / independent model test support | Not established for a real target |
| Baseline | Production exact/TF-IDF repetition, incentive mentions and contextual timing/rating/lexicon rules |
| Score | Experimental fixed two-signal max penalty and existing withholding gates |
| Target of the baseline | Observable patterns in the declared submitted subset |
| Contextual signals | Timing, rating distribution and rating/text disagreement; do not change the score |
| Probability / calibration | Unavailable |
| Confidence level | Unset; not validated |
| New dependencies / serialized model loading | None |

The descriptive TF-IDF vocabulary is computed only within each submitted subset as specified in SPEC.md; it is not a supervised model trained across research splits. The Step 7 synthetic membership manifest is recomputed for integrity only. Its scenario labels are not used to fit, tune or estimate classifier performance. The Step 8 authored mechanical cases are a separate regression suite, not an independent held-out model test set.

## Evaluation performed

[Evaluation record](EVALUATION.md) and ml/fixtures/mechanics.expected.json record 17 fixed synthetic cases against the actual production analysis function. Their expected counts, availability and arithmetic outcomes were declared as mechanics, not deception labels. Evidence references/spans, unset confidence, withheld-score semantics, metadata independence and selected redaction/feature-limit behavior were checked. Successful reproduction includes intentionally visible failure modes and does not establish detection validity.

Precision, recall, F1, confusion matrix and probability calibration are null with an explicit no-independent-target reason. No percentage accuracy, real-world false-positive rate or calibration estimate is justified. The Step 8 evaluation did not measure time/memory; the separate Step 10 measurements are linked below.

## Failure modes and use limits

Templates, duplicate ingestion and common product descriptions can qualify as repetition. Negated/quoted incentive phrases remain mentions and can lower the experimental index. Unlisted wording can be missed. Normalization or masking may collapse differences, while masking still misses personal details. The narrow lexicon can abstain excessively or misread unmarked sarcasm/aspects. Missing metadata and unsupported wording leave context unavailable; a value of 100 does not verify authenticity or product quality.

Source sampling, corpus composition, language, collection method and time shifts remain unvalidated. The controlled fixture strings are deliberately simple and sometimes indexed to isolate mechanics; they are not representative natural review distributions. Nothing in this card supports accounts, public authenticity labels, purchasing recommendations or a validated confidence scale.

## Conditions for revisiting training

A new research revision must establish permitted acquisition/use/retention/excerpts, actual electronics/language relevance, independently documented target semantics, an audited annotation round, real class support and missingness, and an appropriate global product/duplicate grouping review. Freeze the target, source artifacts, splits and evaluation protocol first. Fit learned preprocessing/vocabularies on train only, tune on validation only and reserve an independent test for the declared evaluation. Changes to source admission, split logic or target validity need reviewed code/card updates; editing a source JSON flag cannot enable this runner to train.

Until those gates are satisfied, continue with transparent findings and mechanical robustness checks. Step 10 explicitly did not justify public numeric scores: publish findings/coverage with the score withheld. Step 12 must enforce and verify that release policy before deployment. The current loopback development index remains experimental. These outcomes do not approve deployment.

## Step 10 measured report

The [benchmark](BENCHMARK.md) and [measurement record](benchmarks/20261028.json) add three fresh-process wall/CPU/RSS samples for nine authored resource cases, six fixed sampling observations and controlled admission/rate/slow-body probes. The original 17 mechanics cases and report remain unchanged. The same 40-row batch yields index 50 in full, 0 or 100 for its respective halves and 45 for the fixed seeded sample. This is sample sensitivity, not a confidence interval or real-world error estimate.

NFKC expansion of a valid 756,092-byte stress request produces an 8,275,593-byte response; declared language is not language detection. No hosting budget or browser rendering claim follows from fast local API measurements. No limit was raised; resource amplification, production worker/proxy behavior, browser timings and score-release enforcement remain security/deployment gates. NO TRAIN, null supervised metrics and unset confidence are unchanged.


## Step 12 security update

Both HTTP routes and the browser now enforce public numeric withholding, without an opt-out. The offline library retains the unvalidated formula and all seventeen authored outcomes. Methodology 0.3.0 adds normalized/masked text budgets and bounded public serialization. The prior expansion stress input now returns a safe 413 instead of an 8.3 MB response. Source/version bindings were intentionally reviewed/refreshed; current measurements are in [Step 12 record](benchmarks/20261028-step12.json), with the original Step 10 record preserved as historical. [Security audit](SECURITY_AUDIT.md) records local fixes and unresolved owner/provider launch gates. NO TRAIN, unsupported independent metrics and unset confidence remain unchanged.
