# ReviewTrust engineering guidance

Build an evidence-based electronics review-pattern analyzer, never an authenticity authority. Stack: Next.js App Router/React/TypeScript/Tailwind and Python FastAPI/Pydantic/Uvicorn. Offline ML only when justified; no database, accounts, paid LLM, URL fetching or browser extension in v1.

Read this file, SPEC.md, README.md roadmap and docs/HANDOFF.md before each step; inspect Git status/branch/recent commits and relevant files. Preserve existing user work. Implement exactly one approved roadmap step per user message. Current completed design: Step 1; next pending: Step 2. Do not start until user says `next`.

SPEC.md owns contracts, scoring, evidence definitions and acceptance criteria. docs/THREAT_MODEL.md owns proposed controls. docs/DECISIONS.md records tradeoffs. Numeric scoring is experimental; missing evidence is never low risk; no confidence level without validation. No review names, raw-body logs or persisted uploads. Treat all input as untrusted.

Prefer small pure analysis functions, explicit typed API contracts, deterministic evidence and native/standard-library features. Server limits and validation are authoritative. Add dependencies only for concrete needs. Review methodology changes with a version bump and regression fixtures.

Verification currently: documentation inspection only; no runnable application exists. Step 2 must establish exact backend pytest and frontend test/lint/typecheck/build commands and CI, then record them here and in README. Never report nonexistent checks as passed.

After each step: run relevant checks, fix failures, update README checklist and handoff, and update guidance when meaningful. User override: do not stage or commit automatically. Provide exact commands for the user to review, stage all step-related files, commit with a descriptive message, and inspect the commit. Provide initialization commands if Git is absent. Manual commit pending does not block an otherwise verified step. Never push without explicit user permission; provide a push command only when the remote and branch are verified. If tests fail, mark the step BLOCKED and stop. Never invent remote/branch/hash or claim a manual commit succeeded without verification.

Every step ends with the REVIEWTRUST STEP HANDOFF (step/status, changes/files, actual verification, Git, manual TODO) and ACTION REQUIRED — CODEX MODEL FOR NEXT STEP (current/next step, current recommendation, switch/keep, exact next model/effort, rationale, fallback, complexity, next scope/testing/escalation). User manually switches; never claim a switch. Stop until `next`.

Model recommendations from user's roadmap: Step 1 and 12 Astra High; Steps 2–5, 9, 13 Sol Medium; Steps 6–8 Sol High; Step 10 Sol Medium/High; Step 11 Luna Medium (Sol Medium for complex work); optional Step 14 Astra High and separate approval. Exact names: GPT-6 Astra, GPT-6.1 Sol, GPT-6 Luna. Fallbacks if selectable: Astra -> GPT-6.1 Sol High; Sol -> GPT-5.6 Sol same effort; Luna -> GPT-5.6 Luna same effort. Availability must not be assumed. Request manual escalation on a concrete blocker.
