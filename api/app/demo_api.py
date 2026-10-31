"""Explicit synthetic demo endpoint. Fixed authored content; no network or user URLs."""

import json
from datetime import UTC, datetime
from typing import Literal

from fastapi import Request, Response
from pydantic import ValidationError

from app.fixture_analysis import analyze_fixture_sample
from app.ingestion import ReviewInputError, decode_json
from app.schemas import InputModel
from app.security import run_worker
from app.source_parser import parse_product
from app.source_sample import assemble_fixture_sample
from app.uploads import content_type


class DemoRequest(InputModel):
    example: Literal["patterns", "partial", "empty"]


async def demo_analysis(request: Request):
    data, deadline = request.state.body, request.state.deadline
    header = request.headers.get("content-type", "")

    def work():
        if content_type(header)[0] != b"application/json":
            raise ReviewInputError("media_type", "Use application/json.", 415)
        try:
            example = DemoRequest.model_validate(decode_json(data)).example
        except ValidationError:
            raise ReviewInputError(
                "invalid_request", "Choose an available synthetic example."
            ) from None
        now = datetime.now(UTC)
        product = parse_product(
            json.dumps(
                dict(
                    id=101,
                    slug="demo-headphones",
                    name="Synthetic Demo Headphones",
                    type="simple",
                    variations=[],
                )
            ).encode(),
            expected_slug="demo-headphones",
        )
        rows = (
            []
            if example == "empty"
            else [
                dict(
                    id=i + 1,
                    product_id=101,
                    status="approved",
                    review=(
                        "These authored headphones have clear sound and comfortable ear cushions."
                        if i < 10
                        else (
                            f"Authored sample {i}: received this product for free. "
                            "Battery lasted through an example listening session."
                        )
                    ),
                    rating=4 if i % 2 else 3,
                )
                for i in range(20)
            ]
        )
        sample = assemble_fixture_sample(
            (json.dumps(rows).encode(),),
            product=product,
            window_started_at=now,
            window_finished_at=now,
            exhausted=example != "partial",
        )
        return Response(analyze_fixture_sample(sample, deadline), media_type="application/json")

    return await run_worker(request, work)
