# E12 authored alternative candidates

2026-11-01. Offline selection implemented, version `rt-candidates-0.1.0`.
Live discovery and website integration remain pending. No source is admitted.

## Input and selection

`CandidateRequest` contains one authored target, at most 50 authored candidate
records and explicit preferences: headphones/earphones category, declared form
factor, wired/wireless connection, and optional microphone requirement. Nested
identity uses E11 `ProductIdentity`. Extra fields, coercion and collected origin
are rejected by the strict models. This is an internal typed interface, not a
public bytes parser. Do not expose raw validation errors over HTTP.

Preferences are caller supplied, not guessed from review sentiment or product
titles. The authored tests choose wired over-ear headphones; that is not an owner
purchasing preference. Price/budget filtering awaits E13's dated offer semantics
and explicit caller budget. There is no claim of affordability or offer availability.

Each candidate is checked in this order:

1. Reject conflicting records for a source/listing key, including contradictions
   with the target. Collapse identical repeated candidate records; count them.
2. A known mismatch with a required category/form/connection/microphone produces
   `incompatible`, with the mismatched field names. Known mismatch takes priority
   over other missing fields.
3. The target listing or an E11 `same_variant` result produces `same_product`.
   These remain separate from alternatives, even if sold by another seller.
4. Missing required specifications, missing target/candidate brand/model, or an
   E11 unresolved identity produces `unresolved`. Unknown never satisfies a rule.
5. Otherwise return `candidate`, naming the matching required fields as reasons.

Differences in model, color, region, bundle or condition can establish a different
variant under E11; relevance here checks only the explicitly listed preferences.
The caller must inspect the retained identity result and original record before
offering comparisons. This selector does not promise region/warranty/bundle/price
equivalence, physical quality, identical manufacture or visual resemblance.

## Output and limits

Return the first five eligible references in input order, an omitted eligible
count, supplied count, duplicate count and a decision for every unique record.
References use original positions (`c1`, `c2`, ...), so duplicate removal can
leave gaps. Each decision includes the E11 identity result and seller relation.
Every output explicitly carries `authored_fixture` origin and its version.

There is no quality ranking, similarity score, review aggregation, URL fetching,
image matching, price or recommendation model. An empty shortlist can mean all
records were incompatible, the same product or unresolved; inspect the decisions.
No-results is not proof that alternatives do not exist. Selected order is source
input order and can inherit source selection bias. Distinct listings of the same
candidate variant remain separate; only identical source/listing duplicates
collapse. Downstream E14 must avoid presenting those as diverse recommendations.

Work is bounded by 50 records with E11's bounded identity strings. Existing
cooperative deadline checks occur before work, for every input and before return.
Input overflow or conflicts reject atomically, never silently truncate the catalog.
The five-result preview limit is disclosed through omitted_eligible_count.

## Verification and next integration

Eight authored tests cover useful alternatives, stable selection caps, duplicate
accounting, incompatible/unknown required features, exact variants and target
exclusion, missing identity, empty catalogs, contradictory records, input limits,
provenance and expired deadlines. These verify software mechanics only.

Next E13 can normalize authored offer prices and freshness. E14 can then compose
identity, candidate and offer evidence in an explicitly synthetic comparison UI.
Live retrieval requires E10 source approval plus E02/E05 access/network evidence;
actual relevance and coverage require reviewed permitted examples. Preserve
NO TRAIN, withheld scores and deployment deferral.
