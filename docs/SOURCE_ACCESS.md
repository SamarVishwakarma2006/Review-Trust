# E02 — Permission and source access

Date: 2026-10-30 (Asia/Calcutta). Status: **BLOCKED — no actual store/provider or permission/access evidence.** The owner answered: “I have no store or provider access yet.” E01's WooCommerce merchant/headphones recommendation remains conditional. No country, currency, retailer or monthly budget has been approved.

This is an access-preparation checkpoint, not an approved source card. E02 cannot be marked complete or dependent live collection enabled from this document. No credentials, permission grant, merchant communication, product-data request, purchase, training or deployment occurred. Current v1 no-fetch behavior, NO TRAIN and public score withholding persist.

## What is established

Current official WooCommerce documentation describes merchant-generated API keys, a Read permission option and HTTPS authentication. Keys inherit the associated WordPress user's roles/capabilities. A Read key is not automatically restricted to products/reviews; the actual account can permit broader store reads. A public review page or API response does not establish the rights needed for ReviewTrust analysis or redistribution.

The following are technical observations, not permission evidence:

- Merchant documentation: [generate/manage keys](https://woocommerce.com/document/woocommerce-rest-api/).
- Developer documentation: [authentication and roles/capabilities](https://developer.woocommerce.com/docs/apis/rest-api/authentication/).
- Schema reference from E01: [product reviews](https://developer.woocommerce.com/docs/apis/rest-api/v3/product-reviews/), [products](https://developer.woocommerce.com/docs/apis/rest-api/v3/products/).

The merchant and authentication pages were read this step in the browser after the search service returned an empty error. No store endpoint was tested. No additional vendor fees, quotas or license rights were verified. Documentation examples using orders, read/write permissions, query-string secrets or HTTP are not instructions for this project: restrict planned access to approved product/review reads over verified HTTPS, keep credentials out of URLs, and resolve scope before obtaining keys.

## Unapproved source card — complete with evidence before admission

| Item | Current evidence / decision |
| --- | --- |
| Actual store/provider, authorized representative and agreement | Not supplied; keep personal contact/agreements private where appropriate |
| Approved HTTPS origin and product URLs/IDs | Not supplied; no destination is approved |
| Target market/currency and category/language | Undecided; English headphones proposed only |
| Source implementation/API version | WooCommerce v3 candidate only; actual store/version unverified |
| Review ownership, third-party/syndicated content rights | Unknown; merchant access alone may not cover syndicated content |
| Allowed automated retrieval and analysis | Unknown — not authorized by this source card |
| Public display of excerpts, attribution and source links | Unknown — no publication rights established |
| Product names/specifications, images, trademarks and offers | Unknown; review permission does not cover every catalog field |
| Temporary caching and retention/deletion requirements | Unknown; application default remains memory-only, no raw-body logs |
| Sharing/redistributing raw data or committing examples | Not approved; real reviews/private records stay out of Git |
| Model training, derived datasets and model redistribution | Not approved; separate E16 admission required |
| API key issuer, user capabilities, resource scope and revocation | Not supplied; key values must never appear in this card |
| Quotas, page/byte/time/concurrency budgets, fees and expiry | Unknown; owner must agree acceptable limits/costs |
| Available fields, sufficient sample, variants and moderation | Schema documented; actual availability and selection unverified |
| Minimal allowed GET probe | Not run — no approved destination or access |
| Source decision | NOT APPROVED; E02 blocked |

Use evidence references and dates, not bare “yes” checkmarks. Clarify whether permission covers a private development pilot or public use. If necessary, seek qualified review of rights/privacy requirements; this document is not a legal determination. Do not store a private agreement or personal information in the public repository without an explicit appropriate decision.

## Practical next actions for the owner

1. Decide whether a cooperating merchant pilot is acceptable. If Amazon/Flipkart must be first, say so: their review-text access remains unresolved and needs a specific approved provider/retailer arrangement. Do not buy catalog-only access expecting review bodies.
2. If a merchant pilot is acceptable, identify a store you own or an electronics merchant willing to cooperate. Ask its authorized representative about the narrow pilot below. No merchant has been selected or contacted by the assistant.
3. Obtain confirmation of the allowed uses in the source card, covering review rights, public excerpts if desired, retention and quotas. Share only the public origin and a non-sensitive summary/evidence reference here; keep full private records locally.
4. Once the merchant agrees, have its administrator review least-privilege access. Prefer a narrowly scoped user/endpoint arrangement, Read permissions and a revocable pilot credential. Do not hand over an administrator password or a broad manager key merely because it is marked Read. If narrow scope cannot be demonstrated, resolve it in the security design rather than accepting broad access by default.
5. Keep credentials in a secure local secret mechanism once its setup is agreed. Never paste them into this chat, commit them, send them in query strings or place them in browser-public variables. Creating new access and accepting any agreements remain owner/provider actions with applicable confirmation.

Starting a new store populated with authored reviews can support a later development demo, but provides no independent customer evidence and no Amazon/Flipkart rights. It cannot satisfy E02's real-source acceptance. If obtaining a partner is impractical, the owner may explicitly rescope development to an honestly labeled synthetic-only demonstration; do not silently mark this gate passed.

## Optional merchant message — draft only, not sent

> I am developing ReviewTrust, a tool that examines patterns and recurring feedback in electronics reviews. Would you consider a limited development pilot using a small sample of approved reviews for selected headphone products on your store?
>
> The proposed pilot would retrieve product identifiers, review text, ratings and dates through an authorized interface, exclude reviewer names/emails, and process the sample in memory. It would not modify your store or claim that reviews prove authenticity. Please confirm whether you are authorized to permit this use, whether any reviews are syndicated, and what limits, attribution and deletion requirements apply.
>
> Could we separately agree whether short supporting excerpts may be displayed publicly? Model training, raw-data redistribution, images and broader catalog/comparison use would require separate review. Please do not send an administrator password or API secret in an ordinary reply; we can agree a scoped, revocable access method after permission is established.

The owner may adapt/send this request. The assistant has not contacted anyone, promised a service or accepted terms.

## Minimal live-access verification once prerequisites exist

This is a future verification plan, not an implemented collector:

- Verify the approved origin's ownership/context, HTTPS certificate, agreed scope and quota; no arbitrary URL, private-network destination or redirect to an unapproved host. Keep all response bodies out of logs and command output.
- Make one permitted GET for one approved product and at most one approved review, using only the necessary fields. The relevant review path is `/wp-json/wc/v3/products/reviews` with product filtering; no orders/customers/write endpoint should be exercised. A response-field filter reduces exposure but is not an authorization boundary.
- Record status, field presence/types, non-sensitive counts, timestamp and outcome only. Never dump the returned review, names, email, auth header or full private URL into evidence. Check safe handling when the response unexpectedly includes sensitive fields.
- Verify product association, availability of review text, supported ratings (source may use 0; analyzer accepts 1–5), UTC-date semantics and approved moderation status. Moderation/verified-purchase fields do not prove authenticity. No review data may be relabeled as independent training ground truth.
- Record successful access, real quotas and expiry/revocation arrangements, plus the permitted-use decision. Only then can E02 be complete. A single successful request does not validate production network controls; E03/E05 must still design and verify them.

## Checkpoint result and next gate

Prepared the source card, field/use distinctions, owner actions, unsent request and future minimal probe plan. **Actual permission, live fields and working access are not verified.** E02 stays BLOCKED until the owner provides a real permitted source. E03 has not started. Checks for this documentation checkpoint: local links, tracker consistency and `git diff --check`; no application tests needed for unchanged code. No source is added to `ml/sources.json`.


India source-access update (2026-10-31): owner prioritizes real access over E09 demo expansion and confirmed India, with paid access possible but budget unspecified. Conditional first validation target: Amazon.in via Canopy cookie-free top reviews; no provider/account/rights/probe admitted. Top-review selection differs from current newest_first design and requires explicit contract/adapter work after access verification. E02 stays BLOCKED. See INDIA_SOURCE_PILOT.md.
