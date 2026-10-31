"""Fail-closed v2 ingress. No collector, fixture loader or live-source activation."""

from typing import Literal

from fastapi import Request
from pydantic import ValidationError

from app.analysis import check_deadline
from app.ingestion import ReviewInputError, decode_json
from app.schemas import InputModel
from app.security import run_worker
from app.source_collection import product_request
from app.uploads import content_type

PRODUCT_PATH = "/v2/products/analyze"


class ProductRequest(InputModel):
    schema_version: Literal["2"]
    category: Literal["electronics"]
    language: Literal["en"]
    product_url: str


async def product_analysis(request: Request):
    data, deadline = request.state.body, request.state.deadline
    header = request.headers.get("content-type", "")

    def work():
        check_deadline(deadline)
        media, _ = content_type(header)
        if media != b"application/json":
            raise ReviewInputError("media_type", "Use application/json for product links.", 415)
        try:
            payload = ProductRequest.model_validate(decode_json(data))
        except ValidationError:
            raise ReviewInputError(
                "invalid_request", "Correct the product request format."
            ) from None
        product_request(payload.product_url)
        # Even a future registry entry cannot activate an unverified collection path.
        raise ReviewInputError("source_not_ready", "Product collection is not available.", 503)

    return await run_worker(request, work)
