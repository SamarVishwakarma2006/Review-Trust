# Frontend usage — Step 5

Start both services using README.md. The synchronous page renders a client Analyzer; the browser calls FastAPI directly, without a Next.js proxy.

## Input

- Paste: one editable review per entry. Add/remove entries and check the entry count before submission. Empty entries reject; duplicates remain. Optional rating/date/title/ID/verified-purchase fields can be supplied through CSV. Bulk splitting is optional and not implemented.
- CSV: choose one nonempty UTF-8 file (optional BOM), then map headers to canonical fields. Exact canonical headers are preselected. Map text once and each optional field at most once. Unmapped columns are discarded by the server; mapping replaces automatic selection. Header preview supports quoted commas, newlines and escaped quotes. The browser reads at most 1 MiB into memory, decodes strictly, and previews only headers; it does not parse or validate data rows. The server remains authoritative.
- Confirm English reviews for a single electronics product. Declarations and subset representativeness remain unverified. Remove all personal information first; masking is incomplete.
- Pasted convenience limits: 500 entries, 5,000 Unicode code points each, 250,000 combined, and 1 MiB encoded JSON. CSV file size is checked before reading; multipart overhead may still trigger a server 413. Neither adapter silently truncates input.
- CSV filenames are replaced with reviews.csv during upload. The original filename is not sent. CSV error rows include the header as logical record 1; JSON rows start at review 1.

## Configuration and lifecycle

`web/.env.example` documents NEXT_PUBLIC_API_URL. Copy to `web/.env.local` if an override is needed. Default: http://127.0.0.1:8000. Only an HTTP(S) origin is accepted; no credentials, path, query or fragment. This trusted build setting selects the recipient of review data. It is not a user-entered import URL. Next.js embeds it into browser code at build time; restart dev or rebuild after changes. Configure API exact-origin CORS separately. HTTPS/provider auditing remains a production gate.

Fetch uses credentials omit, cache no-store and redirect error. Native FormData sets the multipart boundary. No automatic retries, analytics, localStorage, result persistence or user-data logs. Browser input, File objects and results remain in memory until replaced/reset/unmount; memory cleanup is not secure erasure.

Inputs are disabled during submission; Cancel and Reset remain available. AbortController stops client waiting and generation guards discard stale results from requests and file reads. A 35-second client deadline bounds waiting, distinct from the API's ten-second default processing budget (configurable up to 30 seconds). Cancel does not promise immediate server cancellation: server admission remains held until bounded work completes. Reset clears entries, selected file, mapping, confirmation, errors and results. Editing clears prior results. Failures retain input for correction; successful responses do not silently clear it.

Errors use fixed HTTP-status explanations and safe structured row/field details, capped at 20. Rate-limit Retry-After seconds and server request IDs are shown when valid. Raw error messages/HTML and network exception details are not rendered. Consumed success fields are checked before rendering; incompatible results show no score.

## Results and accessibility

Results show experimental or insufficient-evidence score, withholding reasons, unvalidated confidence, field and signal coverage with denominators, unavailable reasons, warnings, limitations and methodology version. Collapsible evidence displays actual returned reference pairs and escaped review text; phrase offsets are zero-based Unicode code points with an exclusive end. No HTML interpretation, risk bands or authenticity claims. Step 9 adds the presentation and navigation described below.

Native controls have labels, fieldsets and visible keyboard focus. Results/errors receive focus; loading/cancel/reset use a status region and failures use an alert. Responsive CSS was checked at 320px without horizontal page overflow. This is targeted verification, not a complete accessibility audit.

Tests: `npm --prefix web run test`. The suite covers canonical submission, duplicate preservation, declaration, reset/cancel/unmount/deadline, stale file reads, network retry, CSV mapping, Unicode/byte limits, malformed headers, safe errors, escaped text and response validation. Tests use synthetic data only.

## Step 6 signals

The browser now accepts rt-patterns-0.2.0-experimental and validates the new value/evidence fields it displays. Results include TF-IDF pair method/similarity, exact rating histogram/mean/shares, UTC timing window and submitted rating/lexicon direction. Contextual findings are labelled as not affecting the score. Supporting dates/ratings may be returned in evidence; IDs remain omitted. Similarity values are not authenticity probabilities. Old methodology responses are rejected rather than rendered under new rules. API/web builds must match. See SPEC.md for the complete algorithm, eligibility gates, feature limit and frozen word inventory.

## Step 9 presentation

The overview places the experimental score or explicit insufficient-evidence state beside submitted/eligible counts, available method counts and unvalidated confidence. Withholding reasons are readable requirements; zero remains a numeric result, never a stand-in for unavailable. All score values use the same neutral styling. There are no traffic-light risk bands, authenticity probabilities or trained-model claims.

The first three findings are navigation links, ordered by observed, unavailable, then not_observed; scoring methods come first within each state, followed by source order. The view discloses the rule and says it is not a severity rating. Links focus the matching full finding heading. All findings remain visible; missing evidence is not hidden because other signals were observed.

Coverage is a native keyboard-operable eligible/evaluated radio selector with five returned method counts, denominator text and explicit gaps. Eligibility means usable method inputs; sample/coverage gates may still prevent evaluation. Bars are decorative to assistive technology and the text list carries the values. Field presence/missing counts are in a separate disclosure. Available rating distributions show exact-value bins and counts with the mean/extreme shares; unavailable methods do not show invented charts. UTC windows remain textual because the API does not provide a full time series.

Supporting evidence uses native disclosures, actual returned pairs/references and truncation notes. Text and titles remain React text nodes. Returned single-review match spans use mark elements after code-point-aware splitting; overlapping spans merge, and the response boundary rejects reversed or out-of-range spans. Context stays visible, with a warning that highlighted wording does not establish conduct. Pair cosines remain distinct from authenticity probabilities.

Targeted checks cover zero/withheld/100 presentation, priority stability, charts/text, missing methods, escaped HTML-like titles, emoji offsets, malformed spans and all original form/network/cancel/reset states. Live local JSON/CSV, keyboard chart/anchor/disclosure controls and responsive widths 320/1280 were checked. This is targeted accessibility verification, not a full audit. Exports/sharing/history are deferred; no dependency, scoring or model change was required.

## Step 11 — Website content

The synchronous home page keeps Analyzer at #analyze and adds an educational landing page. Shared layout navigation/footer link /how-it-works, /methodology, /privacy and /contact. Each page has one main/h1 and a focusable #content target for the keyboard skip link. Native links and responsive CSS require no new package. Static metadata provides route titles; noindex remains in force during development.

User override: the contact destination is intentionally blank for later editing, so this does not block Step 11 completion. Edit CONTACT_EMAIL in web/lib/contact.ts and rebuild/restart when a real monitored address is available. Blank state leaves an empty address box with accessible and visible unavailability, no mailto and no fake form. Configured state creates only an explicit encoded mailto link; privacy text reads the same constant. Tests use synthetic addresses, never a real message. Contact is not operational until owner setup; a working destination remains required before public launch.

See [content and owner setup](CONTENT.md) for routes, privacy/claim boundaries, actual checks and launch prerequisites. Five content tests complement the existing analyzer/result checks. API/methodology/contracts and the frozen research records are unchanged. Public numeric withholding, production retention/provider budgets and security/deployment approval remain later gates; copy does not enforce them.


## Step 12 security update

The local audit is complete: see [SECURITY_AUDIT.md](SECURITY_AUDIT.md). Both HTTP routes and UI enforce null scores; only the offline library retains numerical arithmetic. Methodology 0.3.0 adds normalized/masked text limits and 2 MiB serialization rejection. Next pages now render dynamically with fresh script nonces, no-store and anti-framing/referrer/permissions headers; inline chart styles remain documented. Escaped evidence, cancellation/reset and intentional blank contact are preserved. Current benchmark is benchmarks/20261028-step12.json; the original Step 10 record is historical. Contact setup and actual provider TLS/proxy/logging/retention/edge/resource verification remain prerequisites to public launch. No deployment was performed.
