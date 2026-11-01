# E10 catalog access preparation

2026-11-01. Status: PREPARATION COMPLETE; live access and adapters BLOCKED.
Scope: India, English headphones/earphones. Owner deferred Bright Data setup.
Account/key visibility was reported by the owner, but no sanitized Amazon.in
result, account entitlement, agreed budget or permitted-use evidence was supplied.
This is not an admitted source. No credentials, calls, purchases or data retained.

## Candidate sources and evidence

Official pages checked 2026-11-01; advertised capabilities are not measured results.

| Candidate | Documented capability | Remaining verification |
| --- | --- | --- |
| Bright Data Amazon products/discovery | Product URLs, ASIN, brand, currency, prices and availability; discovery options listed | Amazon.in coverage, actual variant/model/GTIN fields, INR offers, search limits and permissions |
| Bright Data Flipkart products/search | Keyword/category discovery; SKU, variant ID, name, brand, currency and price advertised | Actual selected schema, seller/variant association, delivery charges, rights and account entitlement |
| Amazon India Creators API | SearchItems, GetItems and GetVariations; Associates eligibility including 10 qualifying sales in 30 days | Owner eligibility, permitted comparison use, attribution and license restrictions; no review-body access established |

Evidence: [Amazon product scraper](https://brightdata.com/products/web-scraper/amazon/products),
[Flipkart catalog/search](https://brightdata.com/products/web-scraper/flipkart),
[Creators API prerequisites](https://affiliate-program.amazon.in/creatorsapi/docs/en-us/introduction).
The first two pages support only the advertised field summaries above. They do
not establish that a particular India listing contains every required field.

Conditional recommendation: validate Bright Data Amazon.in catalog first using
the owner's existing account, then Flipkart as a separately verified second site.
The owner has not selected Flipkart or approved spending; it is a proposed pilot.
One working source supports a single-site pilot, never cross-site coverage.

## Rights and operating conditions

Bright Data's [acceptable use policy](https://brightdata.com/acceptable-use-policy)
subjects usage to its Master Service Agreement. Product marketing does not grant
every downstream display, image, retention or redistribution right. The generic
terms-of-service URL was unavailable during research; the applicable account
agreement and linked MSA still need review. No legal conclusion is recorded.

Amazon's [programming practices](https://affiliate-program.amazon.in/creatorsapi/docs/en-us/concepts/best-programming-practices)
say applications must direct sales to Amazon and describe resource-specific cache
limits. This makes the official affiliate path conditional on product purpose
and applicable license review. Do not substitute these cache suggestions for
ReviewTrust's default memory-only handling or a negotiated provider policy.

Complete the existing SOURCE_ACCESS.md source card separately for each source:
automated catalog/search retrieval; analysis; public names/specification/offer
display; excerpts and review rights; images/trademarks; attribution/affiliate
disclosure; temporary retention; provider job/snapshot retention and deletion;
quota, expiry, revocation and account billing. Training remains unauthorized.
Public marketing of free credits does not establish this account's balance or
hard spend cap. Paid usage cap remains zero until the owner specifies a budget.

## Fields to verify before E11–E14

| Concern | Minimal evidence required | Unknown behavior |
| --- | --- | --- |
| Provenance | Provider/schema version, retailer, retrieval time, permitted canonical URL | Reject records lacking source identity |
| Product identity | Retailer ID, manufacturer brand/model/MPN or GTIN when supplied | Retailer IDs are site-scoped; no cross-site equality from titles alone |
| Variant | Capacity, color, connectivity, generation, pack quantity, bundle, condition | Preserve unknown; no exact-match claim |
| Offer | Seller identity, currency, decimal price, stock, observation time, location context | Unknown seller/price/stock stays unknown |
| Total cost | Shipping/tax inclusion, mandatory fees, membership/subscription/coupon conditions | No cheapest-total claim without comparable totals |
| Discovery | Query/category, order, sponsored status when supplied, returned/available counts | Selected results are not exhaustive or independently ranked |
| Review link | Exact product/variant association and review selection coverage | No reuse across listings based on similar wording/design |

Do not infer GTIN, model, price components or seller from a marketing title.
Do not fetch image URLs during this pilot. Similar appearance is only a candidate
hint; exact product identity is E11 and relevant alternatives are E12.

## Minimal verification once setup resumes

1. Owner confirms approved retailers, free-only or explicit monthly cap, current
   entitlement and applicable uses. Keep tokens out of chat/Git/browser variables.
2. Review source-specific request templates and provider origin, fixed dataset
   identifiers and credential scope under E03/E05. Provider async jobs, polling,
   result size and retention require an intentional transport/contract design;
   the current single fixed WooCommerce metadata GET cannot simply be reused.
3. Within the confirmed free/approved allowance, test one authorized known product
   per retailer and a capped discovery result. If billing/record limits cannot be
   enforced, do not run the probe. No unbounded polling, retry or fan-out.
4. Validate currency, product association, selected variant and seller; record
   status, field presence/types, counts, measured latency/bytes and credits only.
   Do not commit real bodies or identifiers requiring a separate privacy review.
5. Document permitted-use decisions and actual provider storage/deletion behavior.
   Admit each source only after these checks and E05 security verification.
6. Implement only the approved adapter with authored fixtures and contract tests.
   Preserve unknown fields, reject invalid values atomically and keep public
   scores/confidence withheld. Full live E10 acceptance needs actual availability
   evidence; a second retailer must work before cross-site comparison is promised.

## Next independent work

E11 can prepare exact-product/variant matching rules using authored examples
while access remains deferred. No real matching or recommendations should be
claimed from this plan. E09 real-data evaluation and E02/E05 live gates persist.
The current website remains the synthetic feedback demo.
