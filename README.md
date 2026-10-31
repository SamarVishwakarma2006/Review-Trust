# ReviewTrust

An electronics review-pattern analysis platform. It detects observable patterns, not proven deception. Proposed scores are experimental and apply only to the submitted subset.

## Current status

Steps 1–12 are complete. The Next.js interface supports editable pasted reviews, CSV header mapping, direct API submission, cancel/reset, safe errors and an evidence view with explicit coverage, prioritised navigation, accessible charts and highlighted supporting text. FastAPI provides bounded analysis with experimental scoring, masking and explicit insufficient-evidence states. Dataset audits, a synthetic labelling/split workflow, a no-train baseline evaluation and local resource/robustness benchmarks are complete. No real dataset, trained model, independent accuracy or calibration is available. Public numeric scores are not approved and withholding is now enforced in both HTTP routes and the UI. Website content is implemented; the contact address is intentionally blank at the owner’s request. The local security audit is complete; public launch remains NO GO pending owner/provider verification. Local checks pass; GitHub Actions is configured but has not been verified remotely.

Read [SPEC.md](SPEC.md), [API usage/configuration](docs/API.md), [input validation interface](docs/INPUT_VALIDATION.md), [decisions](docs/DECISIONS.md), [threat model](docs/THREAT_MODEL.md), [dataset audit](docs/DATASET_AUDIT.md), [offline workflow](ml/README.md), [model card](docs/MODEL_CARD.md), [evaluation record](docs/EVALUATION.md), [engineering guidance](AGENTS.md) and [handoff](docs/HANDOFF.md).

## Development setup

Prerequisites: Node.js 24 LTS with npm, Python 3.12 with pip/venv, and Git. Python 3.12 is the tested backend baseline; the Windows Store command alias alone is not a Python installation.

From the repository root in PowerShell:

```powershell
python -m venv api/.venv
& ./api/.venv/Scripts/python.exe -m pip install -r api/requirements-dev.txt
npm --prefix web ci
```

If this machine's `python` alias fails, the Codex bundled runtime used for local verification can create the environment:

```powershell
& "$env:USERPROFILE/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe" -m venv api/.venv
```

This fallback path is machine-specific; a normal Python 3.12 installation is preferred for independent development. Do not commit the virtual environment. No environment secrets or `.env` file are needed for the current foundation.

On macOS/Linux:

```sh
python3.12 -m venv api/.venv
api/.venv/bin/python -m pip install -r api/requirements-dev.txt
npm --prefix web ci
```

## Run locally

Open two terminals at the repository root:

```powershell
# Terminal 1: API (http://127.0.0.1:8000)
./scripts/dev-api.ps1
```

```powershell
# Terminal 2: web (http://127.0.0.1:3000)
npm --prefix web run dev
```

For macOS/Linux, run `.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log --no-proxy-headers` from `api/`. Stop either server with Ctrl+C. API `GET /` retains the development status; `GET /health` returns `{"status":"ok"}`. `POST /v1/analyze` accepts canonical JSON; `POST /v1/analyze/csv` accepts multipart CSV plus required metadata. The web page calls the API directly; confirm English reviews for one electronics product before submitting. These development apps are not approved for public deployment.

Methodology `rt-patterns-0.3.0-experimental` adds TF-IDF near repetition, timing windows, rating distributions and conservative lexicon disagreement. Only repetition and four incentive phrases affect the score; the other findings are contextual. Each signal has explicit evidence gates, and excessive similarity vocabulary withholds the score. See SPEC.md for exact rules and limitations. Public API scores are always withheld; only the offline library evaluates experimental arithmetic. Confidence remains unvalidated. Common email/phone masking is incomplete, so remove personal information before submitting.

Default API budgets: 1 MiB total request including upload envelope, two admitted requests, ten-second body/processing deadline, peer token bucket with burst two/refill ten per minute. Optional process settings are listed in [docs/API.md](docs/API.md) and `api/.env.example`; the example file is not automatically loaded. Use one API process until deployment-specific shared abuse controls are verified. Do not trust forwarded identity headers by default.

Browser configuration: the default API origin is `http://127.0.0.1:8000`. To change it, copy `web/.env.example` to `web/.env.local` and set `NEXT_PUBLIC_API_URL` to the trusted API origin (no path, credentials, query or fragment). Restart development or rebuild: Next.js embeds this public value at build time. Match the browser origin in the API CORS settings. Never put secrets in this variable. See [frontend usage](docs/FRONTEND.md).

Production frontend smoke check, after building: `npm --prefix web run start`.

## Verification

Run all current checks on Windows from the repository root:

```powershell
./scripts/check.ps1
```

Equivalent individual commands:

```powershell
Push-Location api
& ./.venv/Scripts/python.exe -m pytest
& ./.venv/Scripts/python.exe -m ruff check .
& ./.venv/Scripts/python.exe -m ruff format --check .
Pop-Location
& ./api/.venv/Scripts/python.exe -m unittest discover -s ml/tests -v
& ./api/.venv/Scripts/python.exe -m ruff check ml --config api/pyproject.toml
& ./api/.venv/Scripts/python.exe -m ruff format --check ml --config api/pyproject.toml
npm --prefix web run test
npm --prefix web run lint
npm --prefix web run typecheck
npm --prefix web run build
```

On macOS/Linux substitute `.venv/bin/python` for `.venv/Scripts/python.exe`, and run the backend checks inside `api/`. CI runs the same checks plus `pip check` on Python 3.12 and Node 24 under Ubuntu. The workflow runs after a manual push or pull request; adding it does not mean a remote run has passed.

Runtime and development Python requirements are separately pinned, including transitive packages. npm uses exact direct versions and `web/package-lock.json`; use `npm ci` for reproducible installs. Dependency updates require rerunning checks. No ML dependencies are installed yet.

Known tooling limitation: ESLint 9 is deprecated upstream but remains required by the current Next.js React/import/accessibility lint plugins. It is pinned for peer compatibility; see D15 in the decisions log. This must be revisited during maintenance and the pre-deployment audit.

## Roadmap

- [x] Step 1 — Architecture, Scoring Definition and Threat Model
- [x] Step 2 — Repository and Development Foundation
- [x] Step 3 — Schemas and Review Validation
- [x] Step 4 — FastAPI Analysis Foundation
- [x] Step 5 — Functional Next.js Application
- [x] Step 6 — Explainable Detection Signals
- [x] Step 7 — Dataset Audit and Labelling System
- [x] Step 8 — ML Baseline and Evaluation (no-train decision and mechanical evaluation)
- [x] Step 9 — Final Trust Score and Evidence UI
- [x] Step 10 — Benchmark and Model Report
- [x] Step 11 — Public Website and Product Content
- [x] Step 12 — Pre-Deployment Security Audit
- [ ] Step 13 — Deployment and Production Verification (preparation complete; deployment deferred by owner)
- [ ] Step 14 — URL expansion (planned as E01–E19; implementation pending)

The next active development roadmap is [PRODUCT_ROADMAP.md](docs/PRODUCT_ROADMAP.md): E00 planning and E01 feasibility are complete; [source findings and access blockers](docs/SOURCE_FEASIBILITY.md) are recorded. E02 permission/access is [BLOCKED](docs/SOURCE_ACCESS.md): the owner has no store/provider access yet. An access checklist and unsent merchant request are prepared; no live source is approved. E03 [URL-ingestion/security design](docs/URL_INGESTION.md) is complete by explicit owner request; E04 [offline source parsing](docs/SOURCE_PARSER.md) is complete with 57 authored-fixture cases; E05 [collection safeguards](docs/SOURCE_COLLECTION.md) and an unwired [bounded metadata transport](docs/SOURCE_TRANSPORT.md) have synthetic tests; full E05 remains BLOCKED on source access, resolver/egress and API integration evidence. E06 has not started. Execute one expansion step per `next`, with acceptance checks and manual Git checkpoints. Original Step 13 and E20 deployment stay deferred; contact stays blank. E01–E03 review source access and network security before live collection; training remains conditional on admitted data. Existing v1 runtime behavior is unchanged.

Step 10: [benchmark and release report](docs/BENCHMARK.md), [measured synthetic record](docs/benchmarks/20261028.json) and [model card](docs/MODEL_CARD.md). Reproduce with `api/.venv/Scripts/python.exe -m ml.benchmark --output ml/artifacts/my-benchmark.json`; verify the committed record with `--verify docs/benchmarks/20261028-step12.json`. No independent accuracy/calibration is available. Public numeric scores are not approved: enforce findings/coverage with score withheld before deployment, subject to Step 12 review. Only the offline research library retains the experimental index. Provider/browser performance and Unicode response amplification remain release gates.

## Website content and contact setup

The landing page keeps the analyzer at `/#analyze`. Public information routes: `/how-it-works`, `/methodology`, `/privacy` and `/contact`. See [content and owner setup](docs/CONTENT.md). These are local development pages; indexing and public deployment remain disabled/pending review.

To add your contact address later, edit `CONTACT_EMAIL` in [web/lib/contact.ts](web/lib/contact.ts), replacing the empty string with a real monitored email, then rebuild/restart the web app. Until then, the address space is blank and the page clearly states contact/dispute submission is unavailable. There is no contact form, message storage, automatic sending or invented address. The privacy page follows the same setting. Verify the configured email application/recipient and mailbox privacy practices before launch.

## Git

Repository: `https://github.com/SamarVishwakarma2006/Review-Trust.git`, remote `origin`, branch `main`. The previously committed README merge markers were removed in Step 2. Commits and pushes are manual; the assistant provides commands after each step and does not stage or commit automatically.

Benchmark CI repair (2026-10-28): isolated the worker test's subprocess mock so Linux processor detection can run independently. The regression and full local checks pass; the frozen benchmark record remains unchanged. See [repair details](docs/BENCHMARK.md#ci-test-repair--2026-10-28). Remote CI rerun remains unverified.


## Step 12 security audit

See [audit findings and launch gates](docs/SECURITY_AUDIT.md), [dependency query evidence](docs/security/dependencies-20261028.json) and [current measurement record](docs/benchmarks/20261028-step12.json). Both HTTP routes return null scores. Normalized/masked display limits and a 2 MiB serialized-response cap reject atomically. Methodology 0.3.0 supersedes 0.2.0; pair/phrase arithmetic is unchanged offline. The Step 10 record is historical; current integrity tests use the new Step 12 record.

Next now renders pages dynamically for fresh CSP script nonces; page HTML is no-store. Production scripts have no unsafe-inline/eval exception; bounded chart styles retain inline styles. No new dependency or distributed infrastructure was added. All local checks pass, including 194 backend, 28 offline and 27 frontend tests. Remote CI and hosting readiness are not claimed. Configure monitored contact and verify actual HTTPS origins, one-process edge/proxy limits, resource/timeouts and provider logging/retention before public launch. Step 13 must resolve these gates; Step 12 did not deploy anything.


### E06 fixture-only sample assembly

- [x] E06 authored synthetic sample normalization and coverage mechanics, explicitly authorized independently of blocked E05. See [SOURCE_SAMPLE.md](docs/SOURCE_SAMPLE.md).
- [ ] E02/E05 permitted live source and network verification remain blocked; E07 API integration is pending.

The website still accepts paste/CSV. No product URL is collected or analyzed by these offline components.


- [ ] E07 — [Fail-closed product API ingress](docs/PRODUCT_API.md) implemented; full analysis integration remains blocked. No live collection or URL UI is enabled.


E07 continuation: authored samples can now be analyzed offline with explicit fixture provenance and withheld scores. Production product ingress remains fail-closed; E07 is partial, E08 pending. See [PRODUCT_API.md](docs/PRODUCT_API.md).


E07 now includes validated collected-source result contracts and authored contract examples. Production ingress remains fail-closed; successful collected analysis and frontend integration are pending. See [PRODUCT_API.md](docs/PRODUCT_API.md).
