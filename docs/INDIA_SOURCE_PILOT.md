# India retailer/provider pilot recommendation

Research: 2026-10-31. Owner confirmed India; paid access may be possible but no monthly budget has been specified. No purchase, account, credential, provider probe or source admission occurred. E02 remains BLOCKED pending permission/access verification. E09 demo work is paused in favor of real access.

## Recommended first validation target

Amazon.in through Canopy, restricted to its top-reviews endpoint, English electronics/headphones as a proposed initial category. This is a conditional feasibility recommendation, not verified live support. Canopy documents IN marketplace support, review bodies, 100 free monthly requests, then $0.01/request. Its top-review route is documented as API-key-only outside the US; paginated reviews require a signed-in Amazon cookie. Do not collect or transmit session cookies for this pilot. Confirm current India functionality and applicable analysis/display/retention rights before use. [Provider documentation](https://www.canopyapi.co/amazon-reviews-api).

Top reviews are a selected subset, not all reviews or newest-first. Dates/order/count can be missing, and small samples may leave existing methods unavailable. Do not change thresholds to make this pilot look successful. A provider summary is not raw review text. Never label unavailable reviews empty or genuine.

## Other candidates

- Bright Data advertises an Amazon Reviews scraper and 5,000 free records/month without a card. The reviewed page did not establish India review-specific coverage, sample limits or our allowed use. Keep as backup pending written clarification. [Official product page](https://brightdata.com/products/web-scraper/amazon).
- Rainforest documents reviews_v2 deprecation and loss of most-recent reviews; top reviews remain described under product data. Not the first choice for a new review-centric integration. [Official changelog](https://docs.trajectdata.com/rainforestapi/product-updates).
- Amazon Creators API documents catalog operations and Associates access prerequisites. The reviewed introduction does not establish bulk review-body access; do not buy/build around an assumption that catalog access includes reviews. [Official introduction](https://affiliate-program.amazon.com/creatorsapi/docs/en-us/introduction).
- Flipkart has no verified review-text provider in this checkpoint. WooCommerce remains the earlier conditional partner-store option, but the owner has no partner access.

## Concrete validation before implementation

Owner: specify a maximum monthly INR budget; review/create the chosen provider account and its terms, confirm automated analysis and excerpt-display rights, and keep API credentials local (never chat/Git/browser-public variables). Do not subscribe or enable overage until budget approval. No outreach has been sent.

Ask provider: Does cookie-free IN top-reviews work now for headphone ASINs? Which review fields and dates are returned? How many reviews, how selected, how fresh? What are rate, latency, failed-request billing and hard spending-cap rules? Is temporary analysis and display of short attributed excerpts permitted, and what deletion/retention rules apply?

After permitted access exists: use one owner-approved Amazon.in product in a bounded probe; record status/field-presence/count/latency only, no raw reviews or identities in logs/Git. Confirm product/variant association and nonempty bodies, quota accounting and no cookie requirement. A successful request does not itself establish use rights.

Engineering impact: current WooCommerce adapter cannot parse this provider. Add a provider-specific adapter, fixed provider-origin requests and secret handling only after access is verified. Version collection ordering from newest_first to a source-selected/top-review policy; keep partial/source_window and unknown totals. Existing four-second collection limit may not fit provider latency and requires measured review, not silent expansion. Preserve DNS/TLS/egress/admission/deadline controls, score withholding, NO TRAIN and deployment deferral.

Outcome: first validation target identified; E02 not complete, no supported retailer claimed. Documentation-only checkpoint; application tests not rerun because runtime unchanged.
