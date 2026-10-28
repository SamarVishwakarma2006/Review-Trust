# Analysis API — Steps 4–6

Local base URL: `http://127.0.0.1:8000`. Start with `./scripts/dev-api.ps1` from the repository root. The Step 5 frontend submits directly; see [frontend usage](FRONTEND.md). This experimental API has not passed the production release gates.

## Endpoints

| Method and path | Request | Result |
| --- | --- | --- |
| GET / | None | Existing development service status |
| GET /health | None | `{"status":"ok"}` |
| POST /v1/analyze | UTF-8 application/json, canonical ReviewSubmission | AnalysisResult |
| POST /v1/analyze/csv | Multipart file and metadata fields below | Same AnalysisResult |

No accounts, saved-result retrieval, URL fetching or public sharing. Unsupported paths/methods return safe 404/405 errors; trailing-slash redirects are disabled. Interactive API docs/OpenAPI endpoints remain disabled; explicit Python contracts are in `app/schemas.py` and `app/results.py`.

JSON example (one review intentionally withholds the score):

```json
{
  "schema_version": "1",
  "category": "electronics",
  "language": "en",
  "origin": "paste",
  "reviews": [{"text": "The display is bright and easy to read."}]
}
```

CSV multipart fields:

- `file`: exactly one uploaded UTF-8 CSV, optionally with BOM. Filename is ignored. Text/csv, application/csv, text/plain, application/octet-stream and application/vnd.ms-excel MIME labels are accepted; actual CSV content is validated. Archives and nested uploads are unsupported.
- `schema_version`, `category`, `language`: required text fields (`1`, `electronics`, `en`); each at most 64 bytes.
- `mapping`: optional JSON object from source header to canonical field; at most 4,096 bytes. Example: `{"Opinion":"text","Stars":"rating"}`. Explicit mapping replaces automatic canonical-header mapping. Null and duplicate JSON keys reject.

All parts must be unique; at most five parts. Per-part headers are limited to Content-Disposition and Content-Type (two headers, 8,192 bytes per header). A complete multipart closing boundary is required. Unknown fields and extra files reject atomically. Parser callbacks retain bytes in memory and never create UploadFile/temporary files. See [input validation](INPUT_VALIDATION.md) and SPEC.md for CSV record/column/text limits.

## Results

`AnalysisResult` includes schema/methodology versions, `experimental: true`, origin, `scope: submitted_subset`, review count, score, evidence coverage, unvalidated confidence, five findings, redacted display reviews, coverage warnings and limitations. Product/source identifiers and verified-purchase values are not returned as review content. Contextual evidence may include submitted ratings and normalized UTC days; polarity is a rule-derived direction. Field presence/missing counts still include optional metadata.

Current methodology: `rt-patterns-0.3.0-experimental`. Exact/TF-IDF repetition, four incentive phrases, timing bursts, rating distribution and conservative lexicon disagreement are implemented with signal-specific evidence gates in SPEC.md. Timing, ratings and disagreement are contextual only. Each finding carries its computed fraction or null, assessment, coverage, explanation, required fields, methodology and availability reason. Supporting references resolve to returned display reviews. Repetition includes actual matching pairs with exact/tfidf method and cosine; incentive and lexicon evidence include the first matched span per listed phrase in the displayed text. Supporting references are capped at 20 and truncation is explicit.

Score is null with `status: insufficient_evidence` if fewer than 20 submitted reviews, fewer than 20 eligible text reviews, less than 80% eligible text coverage, or either scoring signal is unavailable (including similarity vocabulary over 20,000 features). A review requires at least five word tokens after placeholder exclusion; each scoring signal requires ten eligible reviews. Regardless of those gates, HTTP score.value remains null and reason_codes includes public_score_not_validated. When the sample gates pass, status is withheld; otherwise insufficient_evidence. Only the offline library computes the experimental formula in SPEC.md. Metadata cannot improve the score by being absent. A value of 100 is not verified authenticity. Confidence remains `not_validated`, with `level: null`. `score.evaluated_signal_ids` is restricted to the two scoring methods; coverage lists all available methods.

Signal value shapes: repetition/incentives/disagreement use matching_reviews, eligible_reviews and fraction. Burst adds window_start/window_end (inclusive UTC days) and observed_span_days. Rating distribution uses rated_reviews, histogram[{rating,count}], mean, low_share and high_share. Evidence optionally adds match_kind (exact/tfidf), similarity, rating, timestamp_day and polarity (positive/negative); absent values serialize as null. The browser rejects incompatible methodology versions; deploy matching API/web versions.

Availability reasons: insufficient_eligible_text, feature_limit, insufficient_dated_reviews, low_timestamp_coverage, insufficient_time_span, insufficient_rated_reviews, low_rating_coverage, insufficient_supported_polarity. Unavailable findings have null value, zero evaluated count and no supporting evidence. Available negative findings can have descriptive summaries but do not invent matching rows. Evidence is capped at ten repetition pairs or twenty single-review entries; reference truncation and full matching counts remain explicit.

The input subset and its declared electronics/English scope remain unverified. Common email/phone masking is conservative and incomplete; names and other personal details can remain in text. Users must remove personal information before upload. Review text is untrusted inert content; the frontend renders it as escaped text.

## Errors and response headers

```json
{
  "error": {
    "code": "invalid_submission",
    "message": "Correct the indicated fields.",
    "fields": [{"row": 1, "field": "text", "code": "missing"}],
    "total_errors": 1,
    "request_id": "server_generated_id"
  }
}
```

Validation details never include submitted values or arbitrary unknown keys. At most 20 field issues are returned, with total count. JSON row numbering starts at review 1; CSV logical records count the header as 1. Structural errors can fail fast. A failed or timed-out analysis returns no partial score.

400 malformed request; 403 disallowed Origin; 404/405 path/method; 413 limits; 415 content type/charset/compression; 422 invalid metadata/review values; 429 rate/capacity limit; 503 analysis busy or deadline; 500 generic internal failure. Rate responses include Retry-After. Error request IDs match X-Request-ID and are always server-generated. Responses use Cache-Control: no-store and X-Content-Type-Options: nosniff.

Allowed CORS preflights follow Starlette's protocol response format (short text), including rejected methods/headers. Actual endpoint errors use the JSON envelope. CORS permits exact configured origins without credentials and exposes X-Request-ID/Retry-After. It is not authentication. Requests without Origin may use the API; disallowed declared origins are rejected before processing.

## Limits and configuration

Defaults: 1 MiB total HTTP body including multipart envelope; at most two admitted analyses; ten-second body/processing budget; token bucket capacity two, refilling ten tokens/minute per peer. Invalid analysis requests consume rate budget. A bucket can initially accept two requests, then one approximately every six seconds; this is a sustained-rate policy, not an exact rolling-window count.

Actual streamed bytes are counted even without Content-Length; duplicate/mismatched/oversized lengths reject. Compressed bodies reject. HTTP request headers are capped at 64 / 8,192 combined bytes. Empty/malformed bodies produce safe errors. Upload reads time out. Parsing and analysis run on bounded worker admission with cooperative deadline checks; bounded JSON/CSV library calls cannot be preempted in the middle. Expiry returns 503 when control reaches the next check. Cancellation keeps the admission slot occupied until worker completion; CPU work is not abandoned in an untracked timeout thread. Client delivery time is not an inference-confidence measure or a performance guarantee.

Set optional process environment variables; `api/.env.example` is documentation, not automatically loaded:

| Variable | Default | Accepted range |
| --- | --- | --- |
| REVIEWTRUST_ALLOWED_ORIGINS | http://127.0.0.1:3000,http://localhost:3000 | At most ten comma-separated exact HTTP(S) origins, or empty to disable browser origins |
| REVIEWTRUST_RATE_PER_MINUTE | 10 | 1–600 |
| REVIEWTRUST_RATE_BURST | 2 | 1–100, no greater than refill rate |
| REVIEWTRUST_LIMITER_CAPACITY | 10000 | 1–10000 peer keys |
| REVIEWTRUST_MAX_CONCURRENT | 2 | 1–2 |
| REVIEWTRUST_TIMEOUT_SECONDS | 10 | 0.01–30 |

Limiter keys are scoped HMACs under a random process-only key; idle entries expire after 60 seconds and the table fails closed for new peers at capacity. No raw IP is retained in this table. Process restart resets the limiter. Only one process/instance is supported until shared edge enforcement is verified. Proxy peers can share a budget; forwarded headers must not be treated as trusted user identity. The development script disables Uvicorn proxy-header handling. Deployment-specific proxy trust, host connection/write limits, HTTPS and provider logs remain release-review work.

The application creates no persistent review/file history and performs no outbound fetching/model calls. Unexpected failures log only a fixed error code and random request ID, without exceptions, input or client identity. Disable body capture/tracing and access logs in any hosting layer; application tests do not certify provider retention behavior.


## Step 12 enforced public policy

Both analysis routes withhold numeric scores unconditionally, including loopback development. No request/config flag bypass exists. Findings, context, evaluated IDs and coverage remain available. API and finding methodology are rt-patterns-0.3.0-experimental; deploy the matching web version. Post-NFKC/masking text/title/aggregate limits are 5,000/300/250,000 code points. Overflow returns 413 normalized_text_limit without partial results. Serialized UTF-8 output is capped at 2 MiB inside the admitted worker (413 response_limit); the processing deadline is checked after serialization. Errors/JSON also carry default-src none/frame-ancestors none CSP and no-referrer, alongside no-store/nosniff. These limits do not certify provider sockets, buffers, logs or sustained capacity. See SECURITY_AUDIT.md for required actual-host verification before release.
