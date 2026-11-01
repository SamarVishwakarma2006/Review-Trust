# E13 authored prices and freshness

2026-11-01: offline `rt-offers-0.1.0` implemented in product_offers.py. No live
offer retrieval, caching, affiliate links or website integration is enabled.

## Contract

AuthoredOffer includes E11 identity (with seller and condition), INR/USD/EUR
currency, timezone-aware observed_at, opaque delivery_context, known/unknown
availability, purchase terms and four nullable monetary components: price,
shipping, tax and mandatory_fees. All four refer to the complete listed
bundle/quantity. Explicit zero means included or free; null means unknown.
Adapters must establish whether tax/fees are included to avoid double counting.
Do not infer free shipping, known tax, stock or ordinary purchase terms.

Money accepts only bounded nonnegative decimal strings (up to nine integer and
two fractional digits). Reject floats, booleans, signs, exponent syntax, NaN,
infinity and excessive precision. Convert to Decimal and sum with local precision
28; serialize totals as two-decimal strings. No binary float, FX conversion,
rounding of overprecise inputs, unit-price inference or inferred discount.
Supported currencies use this narrow two-decimal prototype contract; others
need an intentional extension rather than automatic acceptance.

OfferRequest has a target identity, comparison currency (default INR), opaque
delivery context, explicit aware now, required max_age_seconds (1–86400) and up to
50 offers. Freshness is caller policy, not a claim about provider accuracy. The
authored tests use 3600 seconds. Age exactly equal to the cap is eligible; future
observations and older observations are unavailable. Compare aware instants.
Opaque delivery context avoids storing a personal address but requires a future
adapter to establish consistent shipping/tax assumptions across sources.

## Eligibility and result

An offer is comparable only when all of these hold:

- E11 resolves same_variant against the target, including quantity/bundle/condition.
- Seller is identified, currency and delivery context match the request.
- Observation is within the explicit freshness window and availability is true.
- Purchase terms are explicitly unconditional (subscriptions, membership, coupon
  and unknown conditions are excluded).
- All four monetary components are known.

Return an original-position reference (`o1`, etc.), comparable/unavailable,
fixed reason codes, observation time, currency and nullable total for every
offer. Multiple failures are retained. Unknown or unusable offers have no total.
Only if every supplied offer is comparable and the input is nonempty is
comparison_complete true and lowest_total_refs populated. Ties return all tied
references in input order. This is lowest among supplied authored offers only;
it does not imply cheapest available online. No deduplication or seller ranking
is performed. Comparison eligibility does not establish authenticity or quality.

The internal typed API is not a public JSON decoder. Use normal safe ingestion
and error handling if a public contract is added. Keep model validation errors
out of HTTP output. The function checks its cooperative deadline before work,
per offer and before returning. The 50-record limit bounds comparisons.

## Verification and next step

24 authored tests cover exact decimal sums, ties, empty results, stale/future
observations and freshness boundary, subscriptions/membership/coupons, missing
charges, stock, currencies, delivery context, variant/seller evidence, malformed
amounts, naive dates, input count/provenance and expired deadlines.

E14 can now compose E09 feedback, E11 identity, E12 candidates and E13 offers in
an explicitly synthetic comparison experience. The owner still needs to review
comparison priorities. Provider setup, source rights, live field verification,
currency/location-specific pricing semantics and real data evaluation remain
pending. No model training or public numeric score is justified by these tests.
