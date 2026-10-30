# E04 — Offline source-response parser

Status: COMPLETE for authored-fixture mechanics only. Date: 2026-10-31. Adapter version: `rt-woocommerce-parser-0.1.0`. No live WooCommerce merchant, retailer or review dataset is admitted. E02 remains blocked; no network requests, HTTP routes or UI were added.

## Implemented scope

`api/app/source_parser.py` exposes two pure, in-memory functions:

- `parse_product(data: bytes, expected_slug=...)` returns a frozen SourceProduct with source ID, plain title, exact slug, simple/variable kind and variant IDs. Product identity must match the caller's resolved slug. IDs are positive integers (not booleans), capped at 2^53−1; title follows existing 300-character canonical validation. Slugs are lowercase ASCII letter/digit segments separated by hyphens, max 100 characters. Variations are unique IDs, at most 100, not the parent ID; simple products cannot claim child variants. Missing parent_id means zero; supplied values must be integer zero. Variation/bundle/unsupported types reject. No inference that a variable product's reviews refer to a specific child variant.
- `parse_review_page(data: bytes, product_id=..., today=...)` returns a tuple of SourceReview records containing source ID and existing canonical ReviewInput. It accepts an empty page, but never silently skips malformed rows. Caller supplies the UTC date explicitly for deterministic future-date validation. Product IDs and approved status must match; raw source dates use only `date_created_gmt` in YYYY-MM-DDTHH:MM:SS form, interpreted as UTC by this source-field convention. No fallback to naive local timestamps. Missing/null optional rating/date/verified values stay null; supplied values use existing strict canonical validation (finite ratings 1–5, strict booleans and valid dates). Zero ratings and malformed metadata reject the page.

Required source fields are explicit; unrelated fields are ignored and never retained in output. Upstream errors/HTML challenge pages or changed required schemas reject with fixed `source_data_invalid`/502. Existing strict JSON decoding rejects duplicate keys, malformed UTF-8, nonfinite constants and excessive nesting without exposing parser details. Body/page/aggregate ceilings reject with `source_limit`/502.

HTMLParser from the standard library extracts inert text, preserves paragraph/line/list boundaries, decodes character references, and omits comments plus script/style/template/iframe/object contents. No URL, image, attribute, script or external entity resource is fetched or executed. HTML extraction is not a browser-grade sanitizer: decoded tag-looking prose can remain plain text, so future UI consumers must preserve React escaping. Malformed declaration errors are translated into safe source errors. Blank extracted content rejects.

Bounds: 256 KiB per response, 100 reviews/page, 20,000 raw HTML characters per selected name/review field before extraction, canonical text 5,000/title 300 and aggregate page text 250,000 points. Larger content is rejected, not sliced. Cross-page 500-row/aggregate/byte limits and deadline checks remain E05/E06 integration work; these standalone parsers do not enforce transport, admission or whole-request budgets.

Review IDs are retained only for future request-local pagination overlap checks. Duplicate IDs within a page reject, including identical records, while equal text from distinct IDs is preserved. Cross-page overlap/conflicts are E06 work. Source-product `permalink`, images, reviewer names/emails and unknown fields are not retained. Returned text/title are internal canonical data and may still contain personal details in prose; existing masking and post-normalization limits must run before signals/output. Repr suppresses IDs and content, but this is not permission to log or serialize these internal records publicly.

## Authored fixtures and verification

`api/tests/fixtures/source_product.json` and `source_reviews.json` were authored for this project. All products, review prose, sentinel names and .example/.invalid domains are synthetic. They are not scraped examples, independent deception labels, evidence of provider access or a training dataset.

`api/tests/test_source_parser.py` has 57 parametrized cases covering product/variant identity, Unicode/entity/block text, hidden content, UTC versus local dates, null/missing optional fields, duplicate text/IDs, malformed/changed/empty schemas, zero/bool/out-of-range ratings, future/invalid dates, PII-field removal and fixed safe errors, body/page/aggregate limits and required fields. Run from api/:

```powershell
./.venv/Scripts/python.exe -m pytest tests/test_source_parser.py
./.venv/Scripts/python.exe -m ruff check .
./.venv/Scripts/python.exe -m ruff format --check .
```

Full checks are recorded in HANDOFF.md. Existing v1 API, pure signals, methodology, public score policy, real-data admission and benchmark records remain unchanged. These parsers are not wired into the serving application. E05 cannot claim live collection complete until E02 permitted access and the E03 transport/security requirements are satisfied. No synthetic parser result may be presented as a live collected product report.
