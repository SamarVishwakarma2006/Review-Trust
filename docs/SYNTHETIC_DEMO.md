# End-to-end synthetic demo

Owner explicitly authorized the E07/E08 demo scope on 2026-10-31. COMPLETE for that scope; actual live source collection remains blocked.

Run scripts/dev-api.ps1 and npm --prefix web run dev, then open http://127.0.0.1:3000/#demo. Choose patterns, partial or empty. API POST /v2/demo/analyze accepts exactly an example enum. It never accepts/fetches a product URL. Fixed authored headphone text is generated in memory, passed through the source parser/sample assembler and fixture analyzer, and returned with authored_fixture provenance. The patterns example intentionally contains ten repeated reviews and ten incentive mentions. These counts demonstrate mechanics, not accuracy.

Demo route shares rate/admission/deadline/worker cleanup with v1; 8 KiB actual input and 2 MiB output caps apply. Browser uses the trusted configured API origin with no credentials, AbortController and request-identity guards. Selection changes/cancel/reset discard stale results. Consumed response fields and fixture origin/null score are validated. React escapes strings. No persistence, new dependency or contact change. Numeric score/confidence remain withheld. Original paste/CSV remains available; live product endpoint remains fail-closed.

Verification: 433 backend, 28 offline, 30 frontend tests; lint, dependency consistency, typecheck and production build pass. Four new API cases and three frontend tests cover examples, forbidden extra URL input, admission/body caps, request construction, reset/cancel late responses and invalid provenance/score. Existing analyzer test was scoped to its own region after adding a second status region. Browser verified actual API success for complete, empty and partial examples and synthetic disclosures. A page text encoding issue caught visually was corrected. Current benchmark docs/benchmarks/20261031-e08-demo.json verifies; mechanics unchanged. No remote CI/provider verification claimed.

Remaining: permitted source access and E05 network controls, real collected-source integration, actual product URL entry and provider-specific proof. This demo does not satisfy those gates. No deployment or model training.
