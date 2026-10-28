# Website content and owner setup — Step 11

The website content is implemented locally, with noindex retained. Public deployment is not approved. The user explicitly requested a blank contact address to edit later; this overrides the earlier requirement to supply it before Step 11 completion. A working destination remains a public-launch prerequisite.

## Routes and navigation

| Route | Purpose |
| --- | --- |
| / | Landing page, preparation guide, analyzer at #analyze and development release limits |
| /how-it-works | Paste/CSV preparation, field mapping, submission, evidence and cancel/reset |
| /methodology | Versioned signals, availability, index arithmetic, no-train decision and known limitations |
| /privacy | Current data flow, raw upload bytes, incomplete masking, memory handling and unverified infrastructure retention |
| /contact | Blank address space, honest contact unavailability and minimal-data dispute guidance |

Root layout shares primary/footer navigation and a first-focusable skip link. Each page has one h1/main, with main id=content and tabIndex=-1. The landing page stays synchronous and composes the existing client Analyzer. Native links and CSS provide navigation/layout without another package or client menu. Existing typeface, green/neutral palette, focus rings and result styling remain consistent. No image, chart, form or animation dependency is needed for these content pages.

## Fill in contact later

Edit web/lib/contact.ts:

```typescript
export const CONTACT_EMAIL: string = "";
```

Replace the empty string with your real, monitored email address, then rebuild and restart the web app. It is public contact information, never a credential. Do not insert a placeholder or test address into production.

Blank state intentionally has an empty visible address box, an accessible “No contact address configured” description and an explicit message that questions/disputes cannot be sent. It does not render mailto or offer a fake submit button. The owner edits source, not an in-browser input.

Configured state trims the address, displays it as escaped React text and constructs an encoded mailto link with a fixed question/dispute subject. Clicking opens the visitor’s email application; it does not automatically send or invoke an API. Privacy copy reads the same constant so it does not keep claiming the destination is absent after setup. Tests use an authored example.invalid address only; the repository constant stays empty.

No mailbox was supplied, contacted or verified. Before launch, configure and check the recipient, email-client behavior and mailbox access/retention practices. There is no ticket database, contact form, promised response time, automatic acknowledgement or deletion workflow. Do not claim operational support until a channel is monitored.

## Content boundaries

- Describe observable patterns in a user-supplied, unverified English/electronics subset. No authenticity authority, product-quality judgment, purchasing recommendation, validation percentage or confidence level.
- Explain all five methods, distinguishing the two development scoring signals from three contextual checks. Keep the literal phrase inventory, mention/negation limits, sample/coverage gates, max aggregation and no-train decision aligned with SPEC.md.
- Public numeric scores are not approved. Existing local development numbers are unchanged; API/UI release withholding still must be implemented and tested in Step 12 before deployment. Static explanatory copy does not enforce that policy.
- Explain that original CSV bytes, including unmapped columns, reach the API. The browser preview is headers only; discarding canonical columns is not pre-upload privacy filtering. Remove sensitive fields from the source file first.
- Privacy describes current code, not a legal certification or a verified hosted retention policy. Application-memory/no-persistence controls do not guarantee secure erasure, network anonymity or absent infrastructure logs. Recheck/update provider and mailbox practices before launch.
- Contact/dispute guidance requests methodology/finding details, a request ID if available and minimal redacted context, not full review files or reviewer identities. Request IDs do not retrieve saved analyses.

## Actual verification

`./scripts/check.ps1` passed: pip check, 187 backend tests, 28 offline tests, Python Ruff lint/format, 25 frontend tests, ESLint, route type generation/TypeScript and optimized production build. Five new content checks cover internal route/hash links, heading/main/skip structure, noindex, blank/configured email behavior and privacy/method limits. The existing input warning test now scopes its selector to the analyzer region because the landing page also discusses removal of personal details; no warning was removed.

Targeted loopback production-browser checks:

- Tab reaches Skip to content first; Return focuses main#content. The hero Analyze your reviews link focuses #analyze.
- A single authored synthetic review successfully reaches the existing API and returns insufficient evidence with unset confidence; result focus works. Reset clears input/results.
- Home and all four content routes at 320px: document client/scroll width both 305px, one main, readable wrapped navigation, no horizontal page overflow. The contact page shows blank space, unavailable text and zero mail links.
- At 1280px: document client/scroll width both 1265px; home hero has two columns (approximately 560.7px/431.3px). Screenshots inspected at mobile/desktop sizes. Temporary viewport reset afterward.
- Browser error log empty. Temporary production server, API and tab stopped/closed. No email was sent. These are targeted checks, not a comprehensive accessibility/security certification or hosted performance claim.

No backend, scoring, source admission, research fixture or dependency changed. Step 10 measurement and Step 8 mechanics records remain valid. Remote CI was not run or verified. Remaining work belongs to Steps 12–13, after the next explicit user command.


## Step 12 security update

The local audit is complete: see [SECURITY_AUDIT.md](SECURITY_AUDIT.md). Both HTTP routes and UI enforce null scores; only the offline library retains numerical arithmetic. Methodology 0.3.0 adds normalized/masked text limits and 2 MiB serialization rejection. Next pages now render dynamically with fresh script nonces, no-store and anti-framing/referrer/permissions headers; inline chart styles remain documented. Escaped evidence, cancellation/reset and intentional blank contact are preserved. Current benchmark is benchmarks/20261028-step12.json; the original Step 10 record is historical. Contact setup and actual provider TLS/proxy/logging/retention/edge/resource verification remain prerequisites to public launch. No deployment was performed.
