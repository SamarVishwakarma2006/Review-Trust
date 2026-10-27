# ReviewTrust

An electronics review-pattern analysis platform. It detects observable patterns, not proven deception. Proposed scores are experimental and apply only to the submitted subset.

## Current status

Steps 1–7 are complete. The Next.js interface supports editable pasted reviews, CSV header mapping, direct API submission, cancel/reset, safe errors and initial evidence results. FastAPI provides bounded analysis with experimental scoring, masking and explicit insufficient-evidence states. Backend/API tests, frontend interaction tests, static checks and the production frontend build pass locally. Dataset candidate audits and a reproducible synthetic labelling/split workflow are complete. No real dataset is admitted; model/evaluation and production release work remain pending. GitHub Actions is configured but has not yet been verified remotely.

Read [SPEC.md](SPEC.md), [API usage/configuration](docs/API.md), [input validation interface](docs/INPUT_VALIDATION.md), [decisions](docs/DECISIONS.md), [threat model](docs/THREAT_MODEL.md), [dataset audit](docs/DATASET_AUDIT.md), [offline workflow](ml/README.md), [engineering guidance](AGENTS.md) and [handoff](docs/HANDOFF.md).

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

Methodology `rt-patterns-0.2.0-experimental` adds TF-IDF near repetition, timing windows, rating distributions and conservative lexicon disagreement. Only repetition and four incentive phrases affect the score; the other findings are contextual. Each signal has explicit evidence gates, and excessive similarity vocabulary withholds the score. See SPEC.md for exact rules and limitations. Scores are withheld below evidence gates; confidence remains unvalidated. Common email/phone masking is incomplete, so remove personal information before submitting.

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
- [ ] Step 8 — ML Baseline and Evaluation (document no-train decision if labels unsupported)
- [ ] Step 9 — Final Trust Score and Evidence UI
- [ ] Step 10 — Benchmark and Model Report
- [ ] Step 11 — Public Website and Product Content
- [ ] Step 12 — Pre-Deployment Security Audit
- [ ] Step 13 — Deployment and Production Verification
- [ ] Step 14 — OPTIONAL URL Input (not authorized)

One approved step per message. Next: Step 8 with GPT-6.1 Sol, High reasoning, after user says `next`.

## Git

Repository: `https://github.com/SamarVishwakarma2006/Review-Trust.git`, remote `origin`, branch `main`. The previously committed README merge markers were removed in Step 2. Commits and pushes are manual; the assistant provides commands after each step and does not stage or commit automatically.
