# Offline research — Step 7

The source audit and bounded labelling/split workflow are implemented. No real dataset is admitted for training. Step 8 completed the no-train decision and synthetic mechanics evaluation; no classifier has been trained.

Read [dataset audit](../docs/DATASET_AUDIT.md), [labelling protocol](../docs/LABELLING.md) and SPEC.md section 6. Source cards are in sources.json. Only project-authored synthetic rows and their expected manifest are versioned under fixtures/.

## Run from the repository root

Use the existing Python 3.12 API virtual environment; the research tool itself uses only the standard library:

```powershell
& ./api/.venv/Scripts/python.exe ml/audit.py --source synthetic-fixture-v1 --records ml/fixtures/synthetic.jsonl --output ml/artifacts/my-synthetic.manifest.json
& ./api/.venv/Scripts/python.exe ml/audit.py --source synthetic-fixture-v1 --records ml/fixtures/synthetic.jsonl --verify ml/artifacts/my-synthetic.manifest.json
& ./api/.venv/Scripts/python.exe ml/audit.py --source synthetic-fixture-v1 --records ml/fixtures/synthetic.jsonl --verify ml/fixtures/synthetic.manifest.json
```

On Unix substitute api/.venv/bin/python. Output creation refuses an existing filename; use --verify for repeatability rather than replacing the frozen manifest. Keep the default seed 20261027 for this fixture. Changing seed, records, source card or pipeline changes the manifest and must be reviewed as a new experiment. Do not search seeds for favourable results.

```powershell
& ./api/.venv/Scripts/python.exe -m unittest discover -s ml/tests -v
& ./api/.venv/Scripts/python.exe -m ruff check ml --config api/pyproject.toml
& ./api/.venv/Scripts/python.exe -m ruff format --check ml --config api/pyproject.toml
```

These run in scripts/check.ps1 and the configured CI workflow. Local checks do not establish remote CI execution.

## Input and output

The offline JSONL contract is separate from the public one-product API. Each line is one object with exactly record_id, product_group, text, rating, timestamp, category, language and votes. See the synthetic fixture for the shape. record_id and non-null product_group are 64-character lowercase hex experiment keys. Real identifiers must be minimized upstream; these are not reviewer IDs. Names, links, images, credentials and extra keys are rejected as fields; names can still occur inside text, so privacy review remains necessary.

text is nonblank, up to 5,000 Unicode code points, without NUL/unpaired surrogates. rating is null or a numeric 1–5 (booleans/coercion rejected, Decimal bounds checked before float conversion). timestamp is null or a valid YYYY-MM-DD; a future adapter must normalize source datetime/timezone semantics before producing days. category is electronics/other/unknown and language is en/other/unknown. Product IDs may be null for quality reporting, but this blocks a usable split. This offline schema reports unsupported scope rather than silently filtering it. Blank lines, duplicate IDs/JSON keys, malformed JSON and non-finite numbers reject atomically.

Budgets: 10 MiB artifact, at most 500 records, 250,000 aggregate text code points. Oversized inputs reject, never truncate or process independently in chunks. Large-corpus admission needs a separately reviewed global grouping implementation; arbitrary chunks can leak duplicates across partitions. The current CLI deliberately admits only synthetic-fixture-v1 before opening its record path. A changed source card cannot authorize real training: the implementation also requires this synthetic source and always writes training_authorized=false.

Audit outputs contain counts, time range, opaque record/group/text hashes, source-card and exact artifact SHA-256, seed, pipeline version, partition membership and manifest SHA-256. Text, product keys, votes, evidence content, annotator identities and file paths are omitted. Hashes are reproducibility identifiers, not anonymization guarantees. Keep real data and derived artifacts under ignored ml/data/ and ml/artifacts/ only after admission; only synthetic examples are committed. No public upload or application persistence is added.

## Frozen split algorithm

Pipeline rt-audit-split-0.1.0 groups the entire admitted bounded corpus before assigning partitions. Normalize text using Unicode NFKC, casefold, and Unicode letter/digit tokens excluding underscores; punctuation and whitespace collapse. Join all rows with the same non-null product_group. Across products, join equal normalized texts and word-trigram sets with Jaccard >=0.80, compared as 5*intersection >=4*union. Texts with fewer than three tokens get exact matching only. Connected components propagate transitively through both product and duplicate edges. This fixed lexical rule is independent of the production scoring TF-IDF and fits no vocabulary on validation/test data. Paraphrases and other undetected overlaps remain a limitation, not a leakage-proof guarantee.

Sort records by their opaque record_id. Component hash = SHA-256 of canonical sorted member-ID JSON. Bucket = integer SHA-256 of pipeline_version:seed:component_hash modulo 100. Buckets 0–69 train, 70–84 validation, 85–99 test. A component always stays whole. These are expected group proportions, not exact row ratios; no stratification, class-driven rebalancing or seed rerolling. Labels never affect assignment. Empty partitions, missing binary support/unknown labels, unsupported language/category and missing product groups are explicit diagnostics. Do not use diagnostic-bearing splits for a supervised experiment.

The manifest freezes exact input bytes, selected source card, labels, groups and test membership. --verify recomputes and compares the complete report; source-byte, label, metadata or grouping changes fail verification. --output only writes a new file under ml/artifacts/ and refuses overwrite. The committed fixture manifest tests Windows/Ubuntu repeatability with LF source bytes from .gitattributes. Training preprocessing, vocabulary selection and thresholds must be fitted/tuned using train/validation only; test stays untouched until the declared evaluation. Sampling/source/time-shift choices and all excluded records must be documented for any future real experiment.

## Step 8 — No-train decision and mechanics evaluation

Step 8 explicitly chose NO TRAIN because the recorded source audit supplies no admitted real electronics deception target. See [model card](../docs/MODEL_CARD.md) and [evaluation record](../docs/EVALUATION.md). No classifier, learned weights, ML package or calibration was added. The current production heuristic panel remains the baseline.

Run `api/.venv/Scripts/python.exe -m ml.evaluate --output ml/artifacts/my-mechanics.json` from the repository root, then `--verify ml/artifacts/my-mechanics.json` or `--verify ml/fixtures/mechanics.expected.json`. Use the existing API environment because this runner imports the pinned production analysis dependencies; the audit/split tool itself remains standard-library only. It runs 17 authored cases, checks the existing source/manifest freeze, and writes summaries/implementation hashes without raw review bodies. Output is create-only. Decimal-fraction report comparison uses the same strict JSON decoder on both sides to preserve round-trip verification.

The current runner rejects changed source admission/training flags for manual review and always reports no_train; it does not offer a training override. Precision/recall/F1/confusion matrix/calibration remain explicitly null. Mechanical expected outcomes do not establish classifier accuracy. The existing unittest discovery command and CI checks include evaluation integrity tests automatically.

## Step 10 — Resource and robustness benchmark

Run `api/.venv/Scripts/python.exe -m ml.benchmark --output ml/artifacts/my-benchmark.json` with a new output name. Each of nine fixed synthetic resource workloads runs in three fresh bounded child processes; default API TestClient POST timings and process peak RSS are measured without socket/provider latency. Controlled admission, rate and shortened slow-body budget probes remain separate. Six sampling cases use seed 20261028 without rerolling. No raw review bodies or local paths are written to reports. Only generated synthetic requests are used; there is no arbitrary input path or acquisition/training option.

`--verify docs/benchmarks/20261028.json` checks the reviewed stored record against source/request hashes, summaries, outcomes and current no-train mechanics. It does not rerun noisy timings; missing memory is null. The report records the default settings, exact installed package versions and source freeze before/after the run. New output is create-only under ignored ml/artifacts/; an intentional reviewed synthetic snapshot lives in docs/benchmarks/. The existing unittest/CI workflow discovers benchmark integrity tests without adding a speed threshold on shared CI hosts.

See [benchmark report](../docs/BENCHMARK.md) for actual measurements, sampling failures, Unicode response amplification, browser/provider gaps and the decision to withhold numeric scores before public release. No model, dataset, dependency or production methodology changed. The frozen Step 8 report remains valid.


## Step 12 current records

Verify `docs/benchmarks/20261028-step12.json` after the reviewed resource/public-policy version change. The old Step 10 JSON is retained as historical evidence and does not verify against changed code. Methodology 0.3.0 retains all seventeen mechanical outcomes/relations and the same offline arithmetic; the mechanics reference's version/source bindings were intentionally refreshed only after equality checks. HTTP resource samples now all require null public scores and the normalization stress case must reject with normalized_text_limit. No new dataset, training authorization or dependency was added. See ../docs/SECURITY_AUDIT.md.
