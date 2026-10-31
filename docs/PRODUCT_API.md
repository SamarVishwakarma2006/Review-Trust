# E07 — Fail-closed product API ingress

Date: 2026-10-31. Status: PARTIAL / BLOCKED for complete analysis integration.

POST /v2/products/analyze now accepts only schema_version="2", category="electronics", language="en" and product_url. The request uses strict JSON decoding and exact typed keys, existing product URL validation, application/json, no compression and an 8 KiB body cap enforced while reading. Unknown sources return unsupported_source/422; invalid URLs return invalid_product_url/422. Malformed JSON returns the existing 400 errors. Validation never returns raw submitted keys, values or parser errors.

The route shares v1's token bucket, two-slot admission, request deadline, worker cancellation retention and safe error/security headers. Even an injected registry entry ends in source_not_ready/503. It imports no transport, credentials or fixture loader and cannot fetch. No successful product-analysis response, collected origin, fabricated reviews or v1-origin substitution exists.

This is a reviewable E07 component, not E07 completion. Complete/partial/empty analysis envelopes, versioned canonical analysis inputs, source provenance, worker/cancellation integration and response bounds remain to implement and verify. Live access additionally requires E02 and E05 permission/network evidence. E08 has not started. Website remains paste/CSV; numeric scores withheld, NO TRAIN, contact blank and deployment deferred.

Fourteen API cases cover strict requests, decoder errors, body/media caps, safe responses, shared rate/admission controls and registry activation refusal. Existing v1 analysis is unchanged. HTTP source bindings changed, requiring an intentional new synthetic benchmark record; historical records are retained. No provider access, classifier accuracy or remote CI is claimed.
