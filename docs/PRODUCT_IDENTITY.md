# E11 offline product identity

2026-11-01: authored offline matcher implemented in api/app/product_identity.py,
version rt-identity-0.1.0. Live catalog admission/integration remains pending.

ProductIdentity validates bounded strict fields; unknown values are null. Compare
brand, model, region, color, connectivity, capacity, bundle, quantity and condition.
All must be present and exactly equal after outer whitespace trimming for
same_variant. No case folding, punctuation removal, alias inference or fuzzy
title/image match. Model means a manufacturer model identifier, never a guessed
marketing title. A source adapter must establish those semantics before use.
Explicit not_applicable may represent capacity only when supported by source
semantics, never as a substitute for missing data. Opaque bundle descriptions
must be mapped to a reviewed common vocabulary before cross-source use.

Known differing fields return different. Missing fields return unresolved when
there are no known differences. Conflicting descriptions of the same source and
listing return unresolved. Returned reason_fields name differences or missing
fields in fixed order. Seller identity is separate: same/different only when
both seller IDs are present under the same source; otherwise unknown.

same_variant means matching supplied declarations, not verified authenticity.
Retailer IDs are site-scoped; no review pooling or offer deduplication is performed.
GTIN validation, manufacturer alias maps and actual adapter field mappings are
deferred until there is source evidence. No public endpoint or UI calls this
module. Existing demo remains unchanged. Twenty authored cases pass, including
missing fields, wrong model/region/capacity/bundle/quantity/condition, source-scoped
sellers and invalid inputs. Ruff passes; no full-suite or live-evaluation claim.

Next: integrate only against admitted catalog adapters, or continue E12 with
explicitly authored candidates. Provider setup and live E10 remain blocked.
