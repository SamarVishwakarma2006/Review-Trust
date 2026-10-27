# ReviewTrust

An electronics review-pattern analysis platform. It detects observable patterns, not proven deception. Proposed scores are experimental and apply only to the submitted subset.

## Current status

Steps 1 and 2 are complete. The development-only Next.js page and FastAPI application start successfully; pinned dependencies, smoke tests, static checks and the production frontend build were verified locally. Review submission, scoring, datasets and deployment remain future work. GitHub Actions has been configured but has not yet been verified remotely.

Read [SPEC.md](SPEC.md), [decisions](docs/DECISIONS.md), [threat model](docs/THREAT_MODEL.md), [engineering guidance](AGENTS.md) and [handoff](docs/HANDOFF.md).

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

This fallback path is machine-specific; a normal Python 3.12 installation is preferred for independent development. Do not commit the virtual environment. No environment secrets or `.env` file are needed for Step 2.

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

For macOS/Linux, run `.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload --no-access-log` from `api/`. Stop either server with Ctrl+C. API `GET /` returns only a development status. The web page does not call the API yet. `/health` and analysis endpoints belong to Step 4; ingestion schemas belong to Step 3. These development apps are not approved for public deployment.

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
- [ ] Step 3 — Schemas and Review Validation
- [ ] Step 4 — FastAPI Analysis Foundation
- [ ] Step 5 — Functional Next.js Application
- [ ] Step 6 — Explainable Detection Signals
- [ ] Step 7 — Dataset Audit and Labelling System
- [ ] Step 8 — ML Baseline and Evaluation (document no-train decision if labels unsupported)
- [ ] Step 9 — Final Trust Score and Evidence UI
- [ ] Step 10 — Benchmark and Model Report
- [ ] Step 11 — Public Website and Product Content
- [ ] Step 12 — Pre-Deployment Security Audit
- [ ] Step 13 — Deployment and Production Verification
- [ ] Step 14 — OPTIONAL URL Input (not authorized)

One approved step per message. Next: Step 3 with GPT-6.1 Sol, Medium reasoning, after user says `next`.

## Git

Repository: `https://github.com/SamarVishwakarma2006/Review-Trust.git`, remote `origin`, branch `main`. The previously committed README merge markers were removed in Step 2. Commits and pushes are manual; the assistant provides commands after each step and does not stage or commit automatically.
