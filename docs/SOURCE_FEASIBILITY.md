# E01 — Product-link source feasibility

Research date: 2026-10-30 (Asia/Calcutta). Status: **E01 COMPLETE — feasibility report delivered; live source selection/access unresolved.** Baseline: main at ebb631b, clean tree at start. No product reviews were collected, accounts created, credentials used, source access purchased, model trained or service deployed.

## Decision

Recommend a first pilot with **one cooperating electronics merchant using WooCommerce, one approved HTTPS store origin, English-language headphones reviews and one market/currency**. This is a technical recommendation conditional on merchant cooperation and rights, not an assertion that such a merchant has been found. Country/currency, retailer preference and maximum monthly data spend remain owner choices; no paid access is authorized. Headphones is a proposed manageable category with concrete comparison attributes, not an owner-approved selection.

The actual first live source is **NOT SELECTED**. Blocker: no approved merchant, review-data agreement, provider access or budget has been supplied or verified. If the owner requires Amazon/Flipkart links, do not silently substitute a WooCommerce demo or claim those retailers are supported. Seek a source-approved review-text arrangement for those retailers or report the access blocker.

The useful distinction is review-text access versus aggregate ratings/catalog access. The existing analyzer requires actual review text; a product's average stars and review count cannot supply repetition evidence, incentive spans or recurring complaint excerpts.

## Dated feasibility matrix

All entries are documentation-level observations. No successful authenticated data request or complete permitted-use review has been performed. “Documented” does not mean admitted, purchased or approved for ReviewTrust.

| Candidate | Individual review text | Catalog / price coverage | Access / cost / quota / region | E01 disposition |
| --- | --- | --- | --- | --- |
| Merchant-authorized WooCommerce REST API v3 | Documented review content, product ID, rating, date and verified flag; product-filtered paginated GET. Responses may contain reviewer name/email, which must be excluded immediately. | Products document permalink, SKU, current/regular/sale prices and stock status. Actual variants, currency, market and completeness depend on merchant configuration. | Requires an actual store and appropriate owner-issued access. No universal hosted service quota, data license or monthly price was established from these docs; merchant/host controls and any fees must be agreed. No global retailer coverage. | **Recommended conditional pilot route.** No cooperating merchant or credentials currently verified. |
| Amazon Creators API | Individual review-body retrieval was not established by the reviewed introduction/GetItems documentation; do not treat catalog access as review access. | SearchItems, GetItems, GetVariations and catalog/OffersV2 resources documented. Locale support and parameter behavior vary. | Current introduction requires target-market Associates enrollment, qualifying sales and credentials; it states 10 qualifying sales in the past 30 days for the described access. Account eligibility, exact quotas, fees and analytical-use rights remain unverified. | Candidate for later catalog/offers subject to terms. **Not established as the review-text source.** Do not implement deprecated PA-API 5. |
| Best Buy Products / Recommendations APIs | Reviewed docs show customerReviewAverage/customerReviewCount or customerReviews.averageScore/count. Individual review-body access was not established in this API documentation. | Product catalog, prices, categories and recommendation operations documented. Treat US/USD as a proposed target only; confirm actual account/market terms in E02. | API key required. Product docs restrict caching to temporary use and describe expiring response links. Current account quotas, fees and permitted independent analysis/display remain unverified. | Potential catalog/offer candidate; aggregate ratings alone cannot run the text analyzer. |
| Bazaarvoice Conversations API | Overview explicitly documents retrieval of ratings/reviews, with product catalog/statistics. Per-client review schema/coverage and enabled locales need verification. | Product/catalog data documented; current retailer offer/price coverage not established by the reviewed overview. | Overview states Enterprise package required and access for Bazaarvoice Conversations clients. No numeric price, quota or usable client agreement established. | Possible commercial/merchant-partner review source if budget and rights fit. **Not verified as a free public review API.** |
| Flipkart affiliate material | No individual review-text endpoint or entitlement verified in this review. | Affiliate FAQ describes referral links/tools; it does not establish the needed review schema. | The visited /api-docs/ landing returned Page Not Found; FAQ says affiliate membership has no joining cost. That does not prove current API onboarding, quotas, review access or analytics rights. India/INR suitability needs specific source evidence. | **Unresolved.** A broken documentation URL is not proof that an API does not exist. Do not infer review access or permission to scrape. |

Prices and quotas above are deliberately unknown where account-specific/current evidence was unavailable. Free program membership, a reachable endpoint or a vendor's collection capability does not establish free operational access or rights to use retailer reviews. No third-party scraper has been vetted as a substitute.

## First-release scope proposed for E02/E03 review

- One merchant-approved HTTPS source origin; exact product URLs map to source product IDs. No arbitrary-web crawler, multi-site promise or CAPTCHA/login bypass.
- English headphones reviews, one product/variant per analysis; retain existing 500-row, text/body/output limits. Collection gets separate page/byte/time/request budgets and explicit stop/coverage metadata in E03.
- Source, retrieval time, selected sort order, available versus analyzed count, variant scope and incomplete/empty/unavailable states must be visible. Public scores/confidence stay withheld as currently specified.
- First URL milestone is E08: automatically obtain an allowed sample and display existing evidence. No user CSV requirement in this primary flow; original manual tools can remain a development fallback pending UI review.
- Product aspects are later E09; alternatives/catalog, identity, offers and comparison E10–E14; brand view E15. A single merchant cannot substantiate cross-website comparison. Stock/price freshness must be measured when those steps run.
- Real review ingestion permission and model-training permission are separate. Nothing here changes the existing NO TRAIN decision or admits a research dataset. Human authorship, favorable stars or verified purchase are not genuine-review labels.
- If no permitted live source is obtained, disclose that as blocked; synthetic source fixtures can establish mechanics only and cannot count as a live product-link feature.

## E02 owner inputs and evidence needed

1. Target country/currency and first category; accept headphones or choose another electronics category.
2. Required retailers: is a cooperating merchant pilot acceptable, or must Amazon/Flipkart be supported first?
3. Maximum monthly data budget, including whether only free access is acceptable. No purchase/subscription is authorized by a budget discussion alone.
4. A cooperating store/provider project or a plan to obtain access. Use normal provider sign-in and local secrets configuration; do not put keys or passwords in chat/Git. Do not reuse credentials copied from another site's frontend.
5. Review allowed collection, automated analysis, display/excerpts, attribution, retention/deletion and any training/redistribution separately. Obtain qualified advice when rights are unclear; these docs are not legal certification. Prefer least-privilege read access and minimize personal fields; some merchant keys can expose broader store data, so E03 must address scope.

E02 can start its permission/access review on `next`, but cannot finish its live-access acceptance or proceed to dependent live collection until the relevant evidence exists. No new agreement or request to a third party has been sent in E01.

## Official evidence inspected

The web-search tool returned empty errors twice, so primary documentation was read in the browser. Legacy URLs redirected or failed as noted. No product page or customer-review payload was scraped. Descriptions above are paraphrases, not complete terms reviews.

- [WooCommerce REST API overview](https://developer.woocommerce.com/docs/apis/rest-api/): authentication, API keys and pagination; legacy GitHub docs redirected here.
- [WooCommerce v3 product reviews](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-reviews/): GET review/list endpoints; product filtering and review content schema (including PII and rating 0–5). ReviewTrust accepts 1–5: E03/E04 must explicitly handle 0 rather than coerce it into a star or silently omit it. Review moderation status is not a deception label.
- [WooCommerce v3 products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/): permalink, SKU, price/regular_price/sale_price and stock fields.
- [Amazon PA-API deprecation notice](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/paapiv5-deprecation): legacy PA-API docs redirect here; Creators API is the supported successor.
- [Amazon Creators API introduction](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction): catalog operations and prerequisites; [GetItems reference](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/api-reference/operations/get-items): supported high-level resources and locale-dependent parameters.
- [Best Buy API documentation](https://bestbuyapis.github.io/api-documentation/#user-guide): Search on Reviews, customer rating/count fields, catalog/offer/recommendations and temporary caching statement; reached from the [official developer portal](https://developer.bestbuy.com/).
- [Bazaarvoice Conversations API overview](https://developers.bazaarvoice.com/v1.0-ConversationsAPI/docs/home): review retrieval, client prerequisites and Enterprise package requirement. A guessed legacy reviews page returned 404; conclusions rely on the successfully opened overview, not that failed page.
- [Flipkart affiliate FAQs](https://affiliate.flipkart.com/faqs): affiliate purpose and joining-cost statement. The [API docs landing](https://affiliate.flipkart.com/api-docs/) returned Page Not Found on this research date; schema/access not verified.

## Acceptance and verification

E01's acceptance allows a chosen source **or an explicit blocker**. Delivered: dated source matrix, recommended conditional route, defined pilot scope, unresolved owner choices and E02 handover. This completes feasibility research without claiming approved access. Current runtime and data admission policies are unchanged. Only documentation links, roadmap consistency and Git whitespace checks are appropriate here; no application code/tests, dependency installs, live-data probes or model measurements were introduced. Revalidate source terms/eligibility during E02 rather than treating this point-in-time review as permanent.
