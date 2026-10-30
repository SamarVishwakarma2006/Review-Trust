# Step 13 — deployment preparation

Status: **PREPARATION COMPLETE; NOT DEPLOYED OR PRODUCTION-VERIFIED.** On 2026-10-28 the owner explicitly requested “prepare only, keep contact blank.” Step 13 remains unchecked. No provider project, domain, paid plan, email destination or public release is configured by this document. Application baseline: commit `987dd2e`, methodology `rt-patterns-0.3.0-experimental`.

## Before creating services

Resume only when the owner requests deployment. Record the selected Render/Vercel projects, owner, plan/region, actual HTTPS origins, release commit and CI run URL. Verify both CI jobs on that exact commit. A local passing suite is not remote CI evidence. Keep preview/production access restricted until the [security audit launch gates](SECURITY_AUDIT.md#required-before-public-launch--ownerprovider-gates) are closed. `noindex` and CORS do not restrict public access; protecting Vercel alone does not protect Render.

Configure a real monitored `CONTACT_EMAIL` in `web/lib/contact.ts` and verify mailbox operation/retention before public launch. It remains blank now. Never put provider credentials in source or `NEXT_PUBLIC_*` variables. No database, persistent disk, analytics, log drain, ML dependency, custom Docker image or additional proxy is needed for the current application.

## Render API settings to enter later

Use the existing repository `https://github.com/SamarVishwakarma2006/Review-Trust.git`, branch `main`, with a manually selected verified release commit. Disable automatic deployment during initial verification. Service creation can immediately expose an onrender.com endpoint: establish the actual access controls first, or defer creation.

| Setting | Prepared value |
| --- | --- |
| Service / runtime | Web Service / Python 3 |
| Root directory | `api` |
| Build command | `python -m pip install -r requirements.txt` |
| Start command | `python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1 --no-access-log --no-proxy-headers --timeout-keep-alive 5 --timeout-graceful-shutdown 15` |
| Health check path | `/health` |
| Instances | One; no autoscaling or extra workers |
| Persistent disk | None |
| PYTHON_VERSION | `3.12.14` (tested local patch; verify availability when creating service) |
| REVIEWTRUST_ALLOWED_ORIGINS | Actual exact HTTPS web origin, without trailing slash; no wildcard or loopback |
| REVIEWTRUST_RATE_PER_MINUTE | `10` |
| REVIEWTRUST_RATE_BURST | `2` |
| REVIEWTRUST_LIMITER_CAPACITY | `10000` |
| REVIEWTRUST_MAX_CONCURRENT | `2` |
| REVIEWTRUST_TIMEOUT_SECONDS | `10` |

`$PORT` above is Render's shell variable, not a PowerShell substitution. Commands run relative to `api`; install runtime requirements only. Environment variables must be configured in the provider; `.env.example` is not loaded. The application retains its 1 MiB request, 500-row, normalized text and 2 MiB response ceilings.

The start command is a conservative candidate, not proof of production capacity. With proxy headers disabled, users behind one provider peer can share the same rate bucket. Do not “fix” this with `--forwarded-allow-ips '*'`. Establish trusted hops, spoof resistance and native edge quotas before changing identity handling. One instance can still overlap old/new processes during rollout; verify how deployment overlap affects limits. Five-second keep-alive does not impose header/body/write timeouts. Document actual edge connection/header/body/write budgets, buffering, CPU/RAM and behavior under controlled load before public use.

Sources: [Render FastAPI deployment](https://render.com/docs/deploy-fastapi), [root directory behavior](https://render.com/docs/monorepo-support), [Python version selection](https://render.com/docs/python-version). Uvicorn flags were checked against the installed pinned runtime's `python -m uvicorn --help`.

## Vercel web settings to enter later

| Setting | Prepared value |
| --- | --- |
| Repository / production branch | Same repository / `main` |
| Framework preset | Next.js |
| Root directory | `web` |
| Node version | `24.x`, matching package engines |
| Install command | `npm ci` |
| Build command | `npm run build` |
| Output directory | Framework default; no static export |
| NEXT_PUBLIC_API_URL | Actual HTTPS Render API origin, no path/query/credentials/trailing slash |
| NEXT_TELEMETRY_DISABLED | `1` |

Keep native Next hosting: do not use the local loopback `npm start` command as a custom Vercel server. Configure the API URL before building; changing it requires a fresh build. Configure each enabled deployment environment explicitly. Do not allow arbitrary preview domains in API CORS: use a fixed approved preview origin or keep analysis disabled there. Inspect native [deployment protection](https://vercel.com/docs/deployment-protection) scope for every enabled URL; do not assume a protected preview means the production alias is protected. See [Vercel monorepo setup](https://vercel.com/docs/monorepos).

Retain dynamic rendering, fresh CSP nonces, no-store HTML and noindex. Do not add CDN caching to HTML or replace the application's CSP with a static nonce. Native fingerprinted asset caching is allowed. Verify Node/Next compatibility on the actual provider build; local compilation does not establish it.

## Release and smoke verification

1. Run `./scripts/check.ps1`; verify current mechanical and benchmark records using the commands in [BENCHMARK.md](BENCHMARK.md). Repeat the dependency checks in [SECURITY_AUDIT.md](SECURITY_AUDIT.md). Review and manually commit/publish the release; record passing remote CI for the exact SHA.
2. Establish both providers' restricted access, actual plan, owner, resource budgets and logging/privacy settings before testing. Confirm request bodies, uploads, APM breadcrumbs and crash dumps are not captured; record access/deploy log fields, retention, access and deletion policy. [Render retention depends on the plan](https://render.com/docs/logging); app access-log suppression does not disable provider logs.
3. Deploy the API release with exact origins; health must return 200 and `{"status":"ok"}`. Deploy the same web release with the actual API origin embedded. Record service/deployment IDs and URLs. Test from the real browser origin, not only a command-line client.
4. Verify HTTPS certificates, HTTP-to-HTTPS behavior and HSTS on both actual origins. Check home, four information routes and 404: fresh CSP nonce on successive requests, matching script nonces, no production script unsafe-inline/eval, no-store HTML, nosniff, anti-framing and referrer policy. Confirm no cached HTML/nonce and successful hydration.
5. Use only authored synthetic input. Submit 20 copies of “The screen and battery work in this synthetic example” through JSON and through a UTF-8 CSV with a `text` header. Both must return 200, methodology 0.3.0, `score.value: null`, reason `public_score_not_validated`, `confidence.level: null`, and 20 reviews. The UI must show findings/coverage and Score withheld, never a number. Allow rate tokens to refill between probes; record genuine 429s rather than disabling limits.
6. Check allowed-origin preflight and exact Access-Control-Allow-Origin, no credentials; unapproved-origin POST must be 403 and have no permissive CORS header. CORS preflight failures may be short text. Missing Origin is not authentication and is not expected to be blocked. Confirm invalid JSON 400, semantic input 422, unsupported media 415, over-limit body 413, and trailing-slash analysis path 404 without redirect. Endpoint errors must be safe, no-store and contain no submitted text.
7. On the restricted test service, verify 429/Retry-After, controlled admission/503, health during analysis, cancellation/slot recovery, timeouts, maximum accepted input and normalization rejection. Schedule load probes with the owner; do not run an uncontrolled production flood. Record measured memory/latency and provider logs without review bodies. Distinguish provider-generated errors from application JSON; UI must fail safely for either. The offline benchmark's ASGI probes do not replace these hosted checks.
8. In a real browser test paste, CSV mapping, cancel/reset, stale responses, keyboard navigation, 320px layout, contact state and safe evidence rendering. Confirm no mixed-content/CSP/CORS console failures, persistence or raw-data logging. Keep release NO GO until all gates have recorded evidence and the owner approves public exposure.

## Rollback and evidence

Before exposure, record the previous compatible API/web deployment pair and environment values (no secrets). On failed health, unsafe scores, body logging, CSP/CORS breakage or resource exhaustion: restrict/suspend exposure, stop promotion, restore the last verified compatible pair and repeat smoke checks. Do not roll back to methodology 0.2.0: it predates enforced HTTP score withholding. If no compatible pair exists, keep services unavailable until repaired. Rebuild when reverting the embedded API origin. Keep auto-deployment disabled until an explicitly approved release workflow exists.

Record evidence in this document when deployment resumes: exact SHA and CI URL; provider projects/plans/region; HTTPS origins; deployment IDs; contact/privacy verification; edge/proxy/timeouts/resource measurements; log retention/access; smoke dates/results; rollback pair; release decision and owner. All are currently **unverified/not configured**, not silently passed. Optional Step 14 remains out of scope.
