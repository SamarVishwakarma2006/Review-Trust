# Step 10 benchmark and release decision

Measured locally on 2026-10-28. **NO TRAIN remains the decision. Public numeric scores are not approved.** Publish findings and coverage with the score withheld before any public release; Step 12 must implement and verify that release policy across API and UI. The current loopback development analyzer retains the experimental index for inspection. This step does not authorize deployment or change rt-patterns-0.2.0-experimental.

The [measurement record](benchmarks/20261028.json) contains actual samples, exact synthetic request hashes, implementation hashes, runtime versions, settings and outcome checks. The [model card](MODEL_CARD.md) and [mechanics evaluation](EVALUATION.md) describe target validity and semantic failures. No real dataset or trained model was added. Precision, recall, F1, confusion matrix, calibration and confidence remain unavailable, never zero.

## Reproduction and integrity

From the repository root, using the pinned API development environment:

```powershell
api/.venv/Scripts/python.exe -m ml.benchmark --output ml/artifacts/my-benchmark.json
api/.venv/Scripts/python.exe -m ml.benchmark --verify ml/artifacts/my-benchmark.json
api/.venv/Scripts/python.exe -m ml.benchmark --verify docs/benchmarks/20261028.json
api/.venv/Scripts/python.exe -m ml.evaluate --verify ml/fixtures/mechanics.expected.json
./scripts/check.ps1
```

Choose an unused output name: the runner permits only new files under ignored ml/artifacts/. Only the reviewed synthetic measurement record is committed under docs/benchmarks/. `--verify` checks the record checksum, current source/input hashes, arithmetic, outcomes, sampling and no-train gates. It does not replay or assert equality of host-dependent timings. The source fingerprint is checked before and after measurement so edits during a run invalidate it. Changed implementation requires a new measurement record and intentional review, rather than silently updating a baseline.

There is no previous comparable performance baseline. Regression deltas and trends are unavailable. Preserve this record as the first reference and capture a new record on unchanged hardware/runtime/settings when comparing changes. Do not compare unlike transports or interpret three samples as a production p95 or capacity estimate.

## Measurement boundary and hardware

- Windows 11, build 10.0.26300, AMD64; AMD Ryzen 7 170 with Radeon Graphics, 16 logical CPUs; 16,369,967,104 bytes physical RAM reported by local CIM. The JSON records the Python-reported processor family, rather than host names, user paths or device identifiers.
- Python 3.12.14. Exact measured package versions are in the JSON, including FastAPI 0.162.0, Pydantic 2.14.1, Starlette 1.10.0, AnyIO 4.15.1, httpx2 2.16.0, python-multipart 0.0.32 and Uvicorn 0.54.0. No dependency changed.
- Three fresh child processes per resource case. Wall time uses perf_counter; CPU uses process_time, which may report zero for a short request because of clock granularity. Timing starts after imports, workload construction, app and TestClient setup and ends after the POST returns. It includes in-process transport, bounded body handling, parsing, validation, worker dispatch, masking, analysis, evidence and response serialization. There is no socket, TLS, proxy, provider cold start or Internet latency.
- Peak RSS is each child's process-lifetime high-water mark, including imports, fixture construction and client; it is not an analysis allocation delta, private memory, an aggregate worker limit or proof of no leaks. Windows uses [GetProcessMemoryInfo](https://learn.microsoft.com/en-us/windows/win32/psapi/process-memory-usage-information) and [PeakWorkingSetSize](https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters). Linux/macOS use resource.ru_maxrss with platform-specific units; unsupported platforms return null. Windows and Unix RSS definitions are not interchangeable baselines.
- Each child has a 45-second parent process timeout for harness containment. This does not replace the application's cooperative 10-second request budget. Defaults remain 1 MiB total body, 500 rows, 5,000 code points per text, 250,000 aggregate text/title points, two admitted requests and no unbounded queue. No limit was raised on these measurements. This local machine does not establish affordable hosting capacity.

## Resource measurements

| Synthetic workload | Status | Wall median ms | Wall max ms | CPU median ms | Peak RSS max MiB |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20 distinct rows | 200 | 26.36 | 26.89 | 31.25 | 48.70 |
| 500 dense non-exact rows | 200 | 1,412.43 | 1,580.85 | 1,406.25 | 60.32 |
| 250,000 aggregate text points | 200 | 157.57 | 162.93 | 156.25 | 52.08 |
| One 5,000-point text | 200 | 6.22 | 6.38 | 0.00 | 48.80 |
| JSON exactly 1 MiB | 200 | 23.87 | 23.92 | 15.62 | 51.29 |
| 500-row Unicode CSV multipart | 200 | 200.85 | 202.10 | 203.12 | 57.69 |
| Body one byte over 1 MiB | 413 | 3.06 | 3.74 | 0.00 | 49.55 |
| Vocabulary feature overflow | 200, score withheld | 51.29 | 52.73 | 46.88 | 51.77 |
| Unicode normalization expansion | 200 | 1,520.33 | 1,540.25 | 1,515.62 | 86.89 |

Numbers are observed values rounded for display; all three unrounded samples are retained in the record. Peak memory uses MiB (1,048,576 bytes). Expected over-limit rejection is a passing boundary outcome, not a successful analysis.

The dense case contains 500 distinct rows with many shared features, exercising 124,750 comparisons without overflowing the feature vocabulary. Rare distinguishing terms keep its score at 100; a 100 here is only a mechanical index outcome. The aggregate case is exactly 500 rows × 500 code points. The single-row case reaches 5,000 points and correctly withholds its score for insufficient evidence. The JSON case is padded with legal whitespace to exactly 1,048,576 bytes; one more byte rejects with body_limit. The CSV case contains 500 rows/250,000 points and 946,830 bytes including multipart overhead. Feature overflow returns findings with the scoring method unavailable and score withheld, rather than a partial numeric result.

## Admission, rate, timeout and cancellation

Two dense requests run in the same process after a controlled receive barrier occupies both admission slots. Rate is explicitly raised to 600/minute with burst 100 for this probe so rate rejection does not conceal admission rejection. A third request receives 503 analysis_busy in 0.25 ms while health remains 200 in 1.54 ms. Both workers complete in 4.30 seconds and active slots return to zero. Their elapsed times include the barrier and overlap; these are not pure CPU timings or steady-state throughput. Python worker threads do not imply a twofold CPU throughput improvement. See the JSON for exact values.

Separate default settings return 200, 200, 429 for three immediate small requests from one synthetic peer. A delayed receive (30 ms) under a deliberately shortened 10 ms budget returns 503 request_timeout and releases admission. Timer scheduling has finite resolution; this verifies safe termination/status and cleanup, not millisecond deadline precision.

The existing backend cancellation regression holds a real worker behind a threading event, cancels the request task and checks that its admission slot stays occupied until the worker exits. Existing CPU deadline and streaming/false-Content-Length regressions also remain required. These controlled tests do not establish production disconnect semantics, socket timeouts or multi-process abuse protection. Provider/proxy behavior, worker sizing and memory limits must be measured under Steps 12–13.

## Robustness and error analysis

The original 17 authored mechanics cases still pass unchanged. They exercise exact/near repetition, negated and quoted incentives, missed paraphrases, short/small/low-coverage samples, normalization, masking collisions, legitimate launch/rating context, metadata removal, sarcasm/negation, feature withholding and prompt-like text. Fixture agreement measures implementation behavior, not deception accuracy.

Six additional sampling observations use one fixed 40-row synthetic batch (20 repeated templates plus 20 distinct controls):

| Selection | Rows | Experimental index |
| --- | ---: | ---: |
| Entire batch | 40 | 50 |
| First half | 20 | 0 |
| Last half | 20 | 100 |
| Fixed random sample, seed 20261028 | 20 | 45 |
| Distinct control reduced to 19 | 19 | Withheld |
| 20 distinct controls plus six short rows | 26 | Withheld |

No seed was rerolled for balance. This demonstrates sensitivity to user selection, not sampling uncertainty bounds. TF-IDF also depends on the submitted vocabulary; there is no independent corpus calibration. Removing metadata preserves the score in the frozen mechanics case; timing and rating concentration remain context only.

Observed failure modes and implications:

- Legitimate supplied templates or duplicate ingestion can produce index 0. Negated/quoted incentive language also incurs the literal-mention penalty; unlisted paraphrases can retain 100. These are interpretation and recall limits, not measured real-world false-positive/negative rates.
- The U+FDFA normalization stress input is declared English but contains Arabic presentation characters. The service trusts the declared language; it does not detect or validate it. A numeric result for this case does not establish supported multilingual behavior. Mixed language and natural review distributions remain unvalidated.
- The 756,092-byte normalization input produces an **8,275,593-byte response**, because NFKC expands each submitted presentation character. It exercises 250,000 raw text points within existing limits. Peak RSS and latency are measured in the table above; a byte-limited upload does not imply a similarly sized response. Step 12 must review normalization/response amplification and browser rendering/memory under production budgets; no larger limits are justified. Changing normalization, evidence or scoring semantics requires a methodology revision and fixtures.
- Masking can collapse contact differences into repetition and still misses names and other personal information. The fixture outputs are synthetic; this report makes no privacy certification claim.
- No independent admitted deception target exists. The index has no validated probabilistic, purchasing or authenticity interpretation. Confidence stays unset regardless of resource speed or fixture pass counts.

## Browser and deployment gaps

The existing production frontend opened successfully on loopback. The available browser tool's read-only evaluation scope did not expose performance.getEntriesByType, so TTFB, FCP, LCP, DOM/load times and network transfer totals are **N/A**, with no performance grade. Do not substitute the server's ready message or a guessed zero. No new browser timing baseline or regression is claimed. Existing Step 9 keyboard/mobile interaction checks remain separate from performance evidence.

The local Next production build contained 594,365 bytes of .js files and 10,331 bytes of .css under .next/static at inspection. This is a disk inventory of all emitted chunks, not initial-route transfer, compressed payload, cache behavior or a Core Web Vitals budget result. Hosting/browser instrumentation and worst-case result rendering still require deployment-target measurement. Temporary production server/tab were stopped/closed after inspection.

## Release conclusion

Resource checks complete this local benchmark step, with explicit limitations. They neither validate authenticity nor approve hosting. **Withhold the numeric score for public release; retain transparent findings/coverage.** Enforce that policy before deployment and audit it in Step 12. Reopening numeric publication or training requires new permitted in-domain target evidence, a frozen independent evaluation plan and reviewed methodology. Outstanding browser/provider measurements and Unicode amplification must be resolved or explicitly bounded before production approval. No push, deployment or public release was performed.

Tooling note: the optional gstack helper was unavailable, so its measurement/baseline principles were applied using the repository harness. `/gstack-upgrade` can restore that helper separately. Starlette's pinned TestClient uses httpx2; query the installed distribution by that name when recording versions. No helper installation or telemetry was performed.
