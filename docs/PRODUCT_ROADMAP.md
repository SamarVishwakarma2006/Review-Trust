# ReviewTrust product-link expansion roadmap

Planning checkpoint E00: complete. E01 feasibility: complete with explicit source-access blocker; see [SOURCE_FEASIBILITY.md](SOURCE_FEASIBILITY.md). E02: BLOCKED, no store/provider access (see [SOURCE_ACCESS.md](SOURCE_ACCESS.md)); E03: source-neutral design complete by explicit owner request; see [URL_INGESTION.md](URL_INGESTION.md). E04: authored-fixture parser complete ([SOURCE_PARSER.md](SOURCE_PARSER.md)); E05: offline safeguards implemented; BLOCKED for live acceptance ([SOURCE_COLLECTION.md](SOURCE_COLLECTION.md)). E06–E20: not started. E02 remains blocked. This document records the owner's request for a monitored, step-by-step expansion of the existing project. It does not claim any source access, trained model, dataset admission or deployed capability.

## Target and boundaries

Target experience: paste a supported electronics product link; obtain available reviews automatically; inspect review patterns and recurring product feedback; compare suitable alternatives and current offers; optionally inspect feedback across other products of the same brand.

Reuse Next.js, FastAPI, typed contracts, pure signals, masking, evidence display and offline audits. URL collection is the planned extension to v1's no-fetch boundary. Change SPEC.md and THREAT_MODEL.md deliberately before implementation. The existing API contract and numeric-withholding policy remain authoritative until reviewed changes are implemented and verified. Product quality, review manipulation, AI authorship and counterfeit authenticity are different questions. No “fully bot,” “genuine company,” “fake product” or guaranteed quality verdict is justified by text patterns alone.

The user's existing no-deployment and blank-contact preferences persist. The original Step 13 stays deferred. This expansion breaks the original optional Step 14 idea into E01–E19 for controlled local development; E20 remains separately authorized deployment. One `next` authorizes only the next eligible expansion step, with E05 still active and blocked for live acceptance. E06 is not automatically authorized while E05 is incomplete. E02 remains a live-collection gate; preparation/tests cannot establish actual source access. It does not authorize purchases, credentials disclosure, restricted-site bypass, data collection without permission, training without admitted labels or public release.

## Working agreement and Git records

For every step I inspect status/branch/recent commits, read the specification/handoff, preserve existing work and implement only that step. I record changed files, actual checks, remaining limits, status and next model recommendation. You review the result and manually commit it. Commit messages use natural, specific human wording without mandatory conventional prefixes. After each step I open the local browser and demonstrate visible behavior, explicitly identifying backend-only or still-disabled changes. I never stage, commit or push automatically.

Use PENDING, IN_PROGRESS, COMPLETE, BLOCKED or SKIPPED_WITH_REASON in the checklist. Conditional steps cannot be marked complete without their evidence. Owner explicitly authorized independent E03 design while E02 is blocked; next E04 may implement authored fixtures only, and E05 live collection remains blocked. Stop dependent live work at a failed gate; select another permitted source or continue an explicitly independent path. A mocked source proves mechanics, never live support. Deployment pending does not prevent local feature development.

At each checkpoint, I provide exact file paths and a commit message. You run `git diff`, stage only listed files, inspect `git diff --cached`, commit, and optionally push after verifying the remote/branch. GitHub Actions must be inspected on the pushed SHA; a local test pass is not remote CI evidence. Avoid mixing steps in one commit. Manual commit pending does not block verified completion, but separate commits are strongly preferred for tracking.

E01 starting Git baseline: main at ebb631b. The owner committed E00 and earlier deployment preparation together; E01 began with a clean tree. Never include .env files, credentials, real reviews, restricted fixtures or private evidence in commits. Record public or minimized evidence references rather than secrets.

## Numbered steps

### E01 — Select a feasible first source and product category

- You: choose target retailer(s), country/currency, first electronics category and maximum monthly data budget. If undecided, I compare options and record an unresolved choice rather than invent access.
- Me: inspect current official source access options, review-text coverage, prices, rights, quotas and supported regions. Recommend one workable source; distinguish metadata-only access from actual review-text access.
- Done: a dated feasibility matrix, chosen source or explicit blocker, clear first release scope. No scraping in this step.
- Commit: `Define product-link scope and source feasibility`.

### E02 — Establish permission and source access

- You: obtain necessary provider approval/account/access, choose any paid plan yourself within the agreed budget, and supply credentials through local secrets configuration. Obtain qualified legal advice where required; I cannot certify legal permission.
- Me: document allowed collection, display, attribution, caching, retention, training and redistribution separately; verify accessible fields with a minimal permitted request when access exists. Robots rules alone do not establish legal permission. Stop if access is unavailable; no CAPTCHA/paywall/login bypass.
- Done: reviewed source card and allowed-use decision, permission evidence and working permitted access. This is a hard gate for live collection.
- Commit: `Record approved source access and data-use boundaries`.

### E03 — Specify URL ingestion and its security boundaries

- You: review supported URL examples, sample coverage expectations and any operational tradeoffs.
- Me: update SPEC/THREAT_MODEL/DECISIONS with product identity, variants, collection status, evidence provenance, error schemas, cost/byte/page/time budgets and cancellation. Design destination allowlisting, DNS/IP checks including IPv6, redirect validation, network egress isolation and secret/log handling. Choose synchronous work only if measured budgets fit; justify a queue before adding one.
- Done: explicit contracts and network design covering blocked/private destinations, DNS rebinding, unsupported sources and partial extraction. Existing analysis limits stay enforced.
- Commit: `Specify bounded product-link ingestion and threat controls`.

### E04 — Implement the first source parser using authored fixtures

- You: inspect representative product and review fields for the intended experience.
- Me: implement source-specific extraction against synthetic, provider-shaped responses; validate fields, variants, ratings, dates and product IDs; omit reviewer names and unsafe HTML. Reuse existing parsing conventions.
- Done: deterministic tests cover valid, malformed, missing, changed and empty source responses. No fixture implies permission or live availability.
- Commit: `Parse the first supported product source`.

### E05 — Implement controlled collection

- You: make the approved source's credentials available locally; confirm any unavoidable request costs before they are incurred.
- Me: implement the E03 network boundary with fixed permitted endpoints/product IDs where possible, bounded retries, timeout/byte limits, quota handling and safe errors. Keep fetching isolated from arbitrary user destinations; use mocked network tests and approved live probes.
- Done: redirects/private targets/oversized bodies/timeouts are safely handled, secrets stay server-side, quotas and real provider access are verified. Security work cannot be waived for a demo.
- Commit for the current partial checkpoint: `Add safeguards before collecting product reviews`. A later completion commit must describe actual verified collection.

### E06 — Normalize review samples and disclose coverage

- You: review the sample-selection policy and how incomplete retrieval is explained.
- Me: bound pagination, track exact product/variant, source/time/sort order and stop reason, and map records into canonical input. Distinguish provider overlap from legitimate repeated reviews; preserve auditability and avoid silently dropping invalid records. Provider fetch limits must be disclosed separately from analyzer limits.
- Done: deterministic pagination/overlap/limit tests, no invented “all reviews” coverage, clear unavailable and partial states, no persisted raw uploads.
- Commit: `Normalize collected reviews with sampling provenance`.

### E07 — Connect product analysis to FastAPI

- You: inspect example success, unsupported-link and unavailable-review responses.
- Me: implement the versioned product endpoint, run the existing analyzer on the validated sample, retain public score withholding, and return typed source/product/coverage metadata. Preserve admission, rate, timeout and worker cleanup controls across collection and analysis.
- Done: API integration tests verify complete/partial/empty/error cases, bounded work and cancellation, with no unsupported authenticity claim. Review intentional source-bound benchmark changes.
- Commit: `Analyze supported product links through the API`.

### E08 — Make product links the primary website input

- You: try the local flow and review wording. Decide whether paste/CSV remains visible under an advanced option; URL input is the intended primary path.
- Me: build the URL form and real request/loading/cancel/reset/error states, update browser response validation, and show product identity, source and coverage beside existing evidence. No simulated collection success in the real flow.
- Done: keyboard/mobile and actual API-shaped interaction checks pass; stale responses are discarded and source failures are understandable.
- Commit: `Add the product-link analysis experience`.

### E09 — Add evidence-backed product feedback summaries

- You: identify useful aspects for the chosen category, such as battery, comfort, durability or audio.
- Me: define versioned aspect extraction and aggregate praise/complaints with excerpts, denominators and abstention for negation/ambiguity. Start with a small transparent method; benchmark before adding a model. Distinguish mentions from supported positive/negative assessments.
- Done: labeled authored cases and a permitted human-reviewed evaluation sample verify attribution and limits. Show recurring reported experiences without asserting physical product quality or authenticity.
- Commit: `Summarize product feedback with supporting evidence`.

### E10 — Establish catalog access for alternatives and cross-site offers

- You: choose additional comparison retailers and access/budget options.
- Me: audit catalog/search/offer permissions and fields, then implement only approved source adapters with fixture and approved integration checks. Reuse collector controls; block unapproved sources.
- Done: actual candidate/offer availability documented, second-site access verified if cross-site comparison is promised. One retailer alone cannot be described as cross-site coverage.
- Commit: `Connect approved alternative-product catalog sources`.

### E11 — Match exact products, variants and sellers

- You: inspect difficult examples of variants, bundles and similar-looking listings.
- Me: match manufacturer/model and reliable identifiers, separate variant/bundle/condition/seller, and represent ambiguous matches as unresolved. Keep same-product offers separate from merely similar products.
- Done: tests reject wrong model/storage/region/bundle merges; uncertain matches cannot contaminate price or review comparisons.
- Commit: `Resolve product identity across approved sources`.

### E12 — Retrieve relevant alternative products

- You: set comparison preferences: purpose, budget and essential specifications.
- Me: implement bounded candidate retrieval/filtering for the chosen category and transparent similarity reasons. “Same design” initially means declared form factor/features; visual resemblance is not proof of identical manufacture. Image matching requires separate evidence and scope if later needed.
- Done: reviewed relevance examples cover useful matches, incompatible products and no-results cases. No custom recommender training is required initially.
- Commit: `Find relevant product alternatives`.

### E13 — Normalize prices and offer freshness

- You: confirm country/currency and how taxes, shipping and availability should be displayed.
- Me: track seller/condition/currency, retrieval time, discount conditions and shipping/tax unknowns. Compare like-for-like offers, handle stale/unavailable values, and disclose affiliation if applicable. Add caching only when allowed and concretely needed, with reviewed retention.
- Done: price tests cover stale offers, currency differences, subscriptions, missing charges and variant mismatches. Unknown total cost cannot become a cheapest-total claim.
- Commit: `Compare dated product offers and price coverage`.

### E14 — Build explainable alternative recommendations

- You: review comparison priorities and example recommendations.
- Me: analyze available alternative review samples through the same pipeline; show specifications, offers, recurring feedback, review coverage and reasons. Use transparent preference rules, expose missing evidence and disclose any ranking weights. Measure bounded fan-out latency/cost.
- Done: side-by-side UI and ranking checks handle no candidates, missing reviews/prices, different sample sizes and ties without treating missing evidence as a good result.
- Commit: `Compare alternatives using feedback and current offers`.

### E15 — Add a bounded brand feedback view

- You: approve how products are selected and what company-level language is acceptable.
- Me: resolve brand versus seller versus manufacturer, sample other eligible products with coverage/date disclosure, keep duplicate groups and product identities distinct, and summarize repeated reported issues. Expose selection bias; avoid pooling incomparable ratings into an unsupported company verdict.
- Done: a bounded, traceable cross-product view with explicit insufficient evidence and no blanket “genuine company” conclusion.
- Commit: `Summarize feedback across identified brand products`.

### E16 — Decide whether a real training dataset is admissible

- You: obtain data-use permissions, independent evidence and suitable annotators/domain reviewers; approve retention arrangements and any annotation budget.
- Me: audit target definition and sources, distinguish manipulation/AI authorship/sentiment, design an unknown/disagreement rubric, and extend the existing audit only through reviewed admission changes. If feasible, create consented/allowed minimized examples, annotate independently, group products/duplicates and freeze train/validation/test partitions. Include source/time separation and representative negative examples where evidence supports them. Never label genuine from stars or verified-purchase status.
- Done: either a rights-reviewed, independently supported dataset with documented label limits and frozen partitions, or a NO TRAIN report. Synthetic examples test software only. No arbitrary minimum row count substitutes for target validity and coverage.
- Commit: `Record dataset admission and training feasibility`.

### E17 — Conditional baseline training code and experiment

- You: authorize the specific admitted training target and approved local data, if E16 supports it.
- Me: provide runnable offline training/evaluation code and instructions, beginning with TF-IDF plus a simple linear classifier. Fit all learned preprocessing on training data, tune only on validation and bind outputs to manifests/code/seeds. Compare with existing heuristics. Store raw data/model artifacts outside Git under reviewed controls.
- Done: reproducible measured results and known limitations, or SKIPPED_WITH_REASON when E16 says NO TRAIN. No LLM training by default. An LLM experiment needs a concrete baseline gap, permitted data, cost/hardware decision and separate scoped approval.
- Commit if implemented: `Train and reproduce the admitted review baseline`; otherwise a documented no-train checkpoint.

### E18 — Conditional independent model evaluation and integration decision

- You: review error examples and acceptable false-accusation risk with qualified domain reviewers.
- Me: evaluate once against the frozen independent test, report precision/recall/F1/support/confusion matrix, uncertainty and source/time/product shifts. Validate calibration separately before probabilities. Keep unknown/abstention, avoid test-driven tuning, and integrate only if predeclared acceptance passes. A useful classifier result still does not prove product authenticity. If training was skipped, document continuing with evidence-only output.
- Done: explicit adopt/reject/no-model decision and model card; any accepted public integration gets versioned contracts, UI and regression checks. Numeric scores remain withheld unless a separate validation decision justifies them.
- Commit: `Evaluate review model and record integration decision` (or a no-model decision checkpoint).

### E19 — Validate the complete local product

- You: perform acceptance walkthroughs on permitted representative products and review the report language.
- Me: audit the expanded fetching, privacy, contracts, source permissions and recommendation paths; run full checks and bounded concurrent/cancellation/resource benchmarks. Verify local URL-to-report-to-alternatives behavior, provenance, keyboard/mobile access and safe failures. Update methodology/source-bound records intentionally.
- Done: reproducible local release-candidate report, supported-source matrix, actual measurements and no unresolved critical issue. Local success cannot mark hosted checks passed.
- Commit: `Verify the product-link comparison release candidate`.

### E20 — Deferred deployment and production verification

- You: explicitly request deployment, choose provider plans/accounts/domains, configure monitored contact, review provider retention and approve public release when ready. Purchases and access grants need their applicable authorization.
- Me: adapt docs/DEPLOYMENT.md to the expanded architecture, verify remote CI, deploy an approved compatible release and run actual HTTPS/CORS/CSP/egress/limit/privacy/resource/browser checks with rollback evidence.
- Done: actual hosted evidence and owner launch decision. Until requested, mark DEFERRED rather than complete. This resumes original Step 13; no duplicate deployment step is needed.
- Commit: `Record verified production deployment and rollback`.

## Tracker

- [x] E00 — Record expansion roadmap (documentation only)
- [x] E01 — Source and category feasibility (report complete; source access unresolved)
- [ ] E02 — Permission and access (BLOCKED: no store/provider access; preparation documented)
- [x] E03 — Contracts and network threat model (design only; E02/live access still blocked)
- [x] E04 — Source parser and authored fixtures (offline only; no source admitted)
- [ ] E05 — Controlled collection (offline safeguards tested; BLOCKED for source/transport evidence)
- [ ] E06 — Sample normalization and provenance
- [ ] E07 — Product analysis API
- [ ] E08 — Product-link website input
- [ ] E09 — Product feedback summaries
- [ ] E10 — Alternative catalog/source access
- [ ] E11 — Exact product matching
- [ ] E12 — Relevant alternative candidates
- [ ] E13 — Prices and freshness
- [ ] E14 — Comparison and recommendations
- [ ] E15 — Cross-product brand feedback
- [ ] E16 — Dataset admission/no-train decision
- [ ] E17 — Conditional baseline training
- [ ] E18 — Conditional model evaluation/integration decision
- [ ] E19 — Full local verification
- [ ] E20 — Deployment (DEFERRED by owner)

First useful URL-only milestone: E08. Quality and comparison milestone: E14. Brand view: E15. Learned prediction remains conditional E16–E18. Source access may block these milestones; no milestone promises universal retailer support.

## Model recommendations

These are recommendations for manual selection, not claims of availability or automatic switches. E00–E02 and E16: GPT-6.1 Sol High for scope/evidence review; E03 and E19: GPT-6 Astra High for security review; E04–E08 and E10–E15: GPT-6.1 Sol High for implementation; E09, E17–E18: GPT-6.1 Sol High for evidence/ML work; E20: GPT-6.1 Sol Medium unless concrete security blockers require Astra High. Fallbacks: Astra -> GPT-6.1 Sol High; Sol -> GPT-5.6 Sol at the same effort, if selectable. Keep Ponytail full: reuse native features, add infrastructure and dependencies only for measured needs.
