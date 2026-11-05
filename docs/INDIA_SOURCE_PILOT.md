# India retailer/provider pilot recommendation

## Current status — 2026-11-05

The owner reports a Bright Data login and API-key visibility. No key was shared
with the assistant. This supersedes the earlier statement that no provider
account exists, but it does not establish Amazon.in entitlement, permitted use,
review or catalog fields, pricing/limits, or working API access. E02 remains
BLOCKED and no live request or source admission is authorized by account
visibility alone.

Current first validation target: use the Bright Data control panel to inspect
the Amazon product-discovery and review scrapers for Amazon.in. Confirm whether
product search can return a small set of comparable candidates and whether the
review scraper can retrieve a bounded sample for the exact product/variant.
Record only schema/field presence, counts, latency and displayed quota or cost;
do not add real review bodies or identifiers to Git. Do not enable paid overage
or run the probe until the account's applicable terms and a hard spend limit are
understood. The product/review integration remains blocked until those checks
and E03/E05 security gates pass.

Historical research snapshot (2026-10-31): the owner confirmed India; paid access may be possible but no monthly budget was specified. At that time no account, purchase, credential, provider probe or source admission was reported. The current account report and remaining E02 gates are recorded above.

## Earlier candidate: Canopy

The earlier conditional recommendation was Amazon.in through Canopy, restricted to its top-reviews endpoint. It is no longer the first provider to validate because the owner now reports Bright Data account access. Canopy remains only an alternative; its functionality, terms and costs must be freshly checked before use. Never collect or transmit signed-in Amazon session cookies.

Top reviews are a selected subset, not all reviews or newest-first. Dates/order/count can be missing, and small samples may leave existing methods unavailable. Do not change thresholds to make this pilot look successful. A provider summary is not raw review text. Never label unavailable reviews empty or genuine.

## Other candidates and official catalog access

- Bright Data advertises separate Amazon product and review scrapers, including product discovery, price/currency/availability fields and review data. Public feature descriptions do not establish this account's Amazon.in coverage, result schema, review selection, applicable terms or actual quota/cost. Verify those in the signed-in account before use. [Amazon products](https://brightdata.com/products/web-scraper/amazon/products), [Amazon scraper overview](https://brightdata.com/products/web-scraper/amazon).
- Rainforest documents reviews_v2 deprecation and loss of most-recent reviews; top reviews remain described under product data. Not the first choice for a new review-centric integration. [Official changelog](https://docs.trajectdata.com/rainforestapi/product-updates).
- Amazon Creators API documents catalog operations and Associates access prerequisites. The reviewed introduction does not establish bulk review-body access; do not buy/build around an assumption that catalog access includes reviews. [Official introduction](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction).
- Flipkart has no verified review-text provider in this checkpoint. WooCommerce remains the earlier conditional partner-store option, but the owner has no partner access.

## Concrete validation before implementation

Owner: specify whether the pilot must be free-only or set a maximum monthly INR budget; review the existing Bright Data account's applicable agreement, product entitlement and spend controls; confirm automated analysis and excerpt-display rights; keep API credentials local (never chat/Git/browser-public variables). Do not subscribe or enable overage until budget approval. No outreach has been sent.

Verify with Bright Data: Does the account's Amazon.in product scraper support keyword/category discovery and exact product lookup? Does the review scraper accept the resulting product URL/ID and return review text, rating and date? How many records are returned and how are they selected? What are rate, latency, failed-request billing and hard spending-cap rules? Is temporary analysis and display of short attributed excerpts permitted, and what deletion/retention rules apply?

After permitted access and a hard limit are confirmed: use one owner-approved Amazon.in product and a capped discovery query in a bounded probe; record status/field-presence/count/latency/credits only, no raw reviews or identities in logs/Git. Confirm product/variant association, nonempty bodies, quota accounting and cookie-free operation. A successful request does not itself establish use rights.

Engineering impact: current WooCommerce parser/transport cannot call or parse Bright Data. First capture a sanitized schema description, then design a provider-specific bounded adapter and fixed provider-origin request/job contract under E03/E05. Do not invent field mappings or activate credentials before access is verified. Keep partial/source_window and unknown totals; record the provider's actual selection policy instead of claiming newest-first. Existing four-second collection limit may not fit provider latency and requires measured review, not silent expansion. Preserve DNS/TLS/egress/admission/deadline controls, score withholding, NO TRAIN and deployment deferral.

Outcome: Bright Data Amazon.in product discovery plus review retrieval is the current conditional validation target. No provider schema, permitted use, hard cost cap or live access has been verified; E02 remains BLOCKED and no retailer is supported. Documentation-only checkpoint; application tests are not rerun because runtime is unchanged.
