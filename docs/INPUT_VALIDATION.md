# Input validation interface

Step 3 provides the shared backend library functions. Step 4 now exposes them through the bounded endpoints in [API.md](API.md). SPEC.md section 3 owns the complete contract and limits.

From `api/`:

```python
from app.ingestion import parse_csv, parse_json, ReviewInputError

json_result = parse_json(
    b'{"schema_version":"1","category":"electronics","language":"en",'
    b'"origin":"paste","reviews":[{"text":"The screen is bright."}]}'
)

csv_result = parse_csv(
    b'Opinion,Stars,ReviewerName\nThe screen is bright.,4,Example Name\n',
    category="electronics",
    language="en",
    mapping={"Opinion": "text", "Stars": "rating"},
)
```

Examples are synthetic. Each result contains:

- `submission`: canonical `ReviewSubmission`, with validated `ReviewInput` records and source origin. Optional missing fields are null. Library records contain raw review text; they must not be logged or returned directly. The analysis layer applies conservative email/phone masking before output, without claiming complete anonymization.
- `review_refs`: ordered tuple `r1`, `r2`, etc.; the same duplicate text in two records retains two references.
- `warnings`: `unverified_subset` always; `mixed_product_coverage` when only some rows have a product ID; `unmapped_columns` with column positions when CSV fields were discarded. These are coverage warnings, not suspicious-pattern findings.

`validate_submission(payload)` is for already-decoded trusted adapter input; it enforces canonical rules but cannot enforce serialized byte limits. API requests must go through the bounded byte adapters plus transport checks. CSV mapping keys are trimmed source headers; matching is case-sensitive. Explicit mappings select only the mapped fields, even when other canonical headers exist.

Catch `ReviewInputError` to render its safe message, status/code, `fields` and `total_errors`. Each field issue has row, canonical field and code. Do not expose underlying Pydantic errors, raw payloads, invalid values, arbitrary unknown keys, parser traces or exception context. Step 4 adds request IDs and the public error envelope. Structural CSV errors fail fast; row validation errors show up to 20 issues plus their full count.

Byte adapters operate in memory, with no file persistence or external requests. The API boundary enforces streaming/multipart limits and releases request state after completion; library callers still own their buffers. CSV input does not execute spreadsheet formulas, scripts or prompt-like text. The analysis layer masks common email/phone patterns; safe UI rendering remains Step 5 work and production release gates remain pending.

Run the complete backend suite from `api/`:

```powershell
& ./.venv/Scripts/python.exe -m pytest
& ./.venv/Scripts/python.exe -m ruff check .
& ./.venv/Scripts/python.exe -m ruff format --check .
```
