"""Fixed, bounded authored comparison; never a catalog or network fetch."""

import json
from datetime import UTC, datetime
from typing import Literal

from pydantic import Field

from app.analysis import check_deadline
from app.fixture_analysis import FixtureReport, analyze_fixture_sample
from app.ingestion import ReviewInputError
from app.product_candidates import (
    AuthoredCandidate,
    CandidatePreferences,
    CandidateRequest,
    select_candidates,
)
from app.product_identity import ProductIdentity
from app.product_offers import AuthoredOffer, OfferComparison, OfferRequest, compare_offers
from app.results import ResultModel
from app.source_parser import parse_product
from app.source_sample import assemble_fixture_sample


class ComparedProduct(ResultModel):
    role: Literal["original", "alternative"]
    report: FixtureReport
    offers: OfferComparison


class ComparisonReport(ResultModel):
    version: Literal["rt-comparison-0.1.0"] = "rt-comparison-0.1.0"
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"
    products: list[ComparedProduct] = Field(min_length=1, max_length=3)
    brand: Literal["Example (authored brand)"] | None = None


def compare_demo(example: str, deadline: float) -> bytes:
    brand_view = example in ("brand", "brand_gaps")
    if brand_view:
        example = "compare_gaps" if example == "brand_gaps" else "compare"
    now = datetime.now(UTC)
    candidates = [
        AuthoredCandidate(
            identity=ProductIdentity(
                source="authored",
                listing_id=str(i),
                brand="Example",
                model=f"H{i}",
                region="IN",
                color="black",
                connectivity="wireless",
                capacity="not_applicable",
                bundle="headphones",
                quantity=1,
                condition="new",
                seller_id="example-seller",
            ),
            category="headphones",
            form_factor="over_ear",
            microphone=True,
        )
        for i in range(3)
    ]
    selection = select_candidates(
        CandidateRequest(
            target=candidates[0],
            candidates=tuple(candidates[1:]) if example != "compare_empty" else (),
            preferences=CandidatePreferences(
                category="headphones",
                form_factor="over_ear",
                connectivity="wireless",
                microphone_required=True,
            ),
        ),
        deadline,
    )
    products = []
    for index in [0, *[int(ref[1:]) for ref in selection.selected_refs]]:
        check_deadline(deadline)
        identity = candidates[index].identity
        product = parse_product(
            json.dumps(
                dict(
                    id=101 + index,
                    slug=f"demo-{index}",
                    name=f"Synthetic Headphones H{index}",
                    type="simple",
                    variations=[],
                )
            ).encode(),
            expected_slug=f"demo-{index}",
        )
        count = 0 if example == "compare_gaps" and index == 2 else (20, 8, 12)[index]
        rows = [
            dict(
                id=i + 1,
                product_id=101 + index,
                status="approved",
                rating=3,
                review="The sound is good. The battery is bad."
                if i % 2
                else "These headphones are comfortable. Battery included.",
            )
            for i in range(count)
        ]
        sample = assemble_fixture_sample(
            (json.dumps(rows).encode(),),
            product=product,
            window_started_at=now,
            window_finished_at=now,
            exhausted=not (example == "compare_gaps" and index == 1),
        )
        report = FixtureReport.model_validate_json(analyze_fixture_sample(sample, deadline))
        offers = tuple(
            AuthoredOffer(
                identity=identity,
                currency="INR",
                observed_at=now,
                delivery_context="demo_IN",
                available=True,
                purchase_terms="unconditional",
                price=str(2000 + index * 500),
                shipping="0",
                tax="0",
                mandatory_fees=None if example == "compare_gaps" and index else "0",
            )
            for _ in range(2)
        )
        compared = compare_offers(
            OfferRequest(
                target=identity,
                currency="INR",
                delivery_context="demo_IN",
                now=now,
                max_age_seconds=86400,
                offers=offers,
            ),
            deadline,
        )
        products.append(
            ComparedProduct(
                role="original" if index == 0 else "alternative", report=report, offers=compared
            )
        )
    # This fixed catalog explicitly declares one brand and three distinct models.
    # Seller IDs are never used to infer brand; manufacturer is not declared.
    data = (
        ComparisonReport(
            products=products, brand="Example (authored brand)" if brand_view else None
        )
        .model_dump_json()
        .encode()
    )
    if len(data) > 2097152:
        raise ReviewInputError("response_limit", "Comparison exceeds the response limit.", 413)
    check_deadline(deadline)
    return data
