import time

import pytest
from pydantic import ValidationError

from app.ingestion import ReviewInputError
from app.product_candidates import (
    AuthoredCandidate,
    CandidatePreferences,
    CandidateRequest,
    select_candidates,
)
from app.product_identity import ProductIdentity


def candidate(number=0, **changes):
    return AuthoredCandidate(
        identity=ProductIdentity(
            source="authored",
            listing_id=str(number),
            brand="Example",
            model=f"H{number}",
            connectivity="wired",
            region="IN",
            color="black",
            capacity="not_applicable",
            bundle="headphones_only",
            quantity=1,
            condition="new",
        ),
        category="headphones",
        form_factor="over_ear",
        microphone=True,
    ).model_copy(update=changes)


def request(*rows, microphone_required=False):
    return CandidateRequest(
        target=candidate(),
        candidates=rows,
        preferences=CandidatePreferences(
            category="headphones",
            form_factor="over_ear",
            connectivity="wired",
            microphone_required=microphone_required,
        ),
    )


def run(req):
    return select_candidates(req, time.monotonic() + 5)


def test_shortlist_has_stable_cap_and_duplicate_accounting():
    result = run(request(candidate(1), candidate(1), *(candidate(n) for n in range(2, 8))))
    assert result.selected_refs == ("c1", "c3", "c4", "c5", "c6")
    assert result.omitted_eligible_count == 2 and result.duplicate_count == 1
    assert len(result.decisions) + result.duplicate_count == result.supplied_count


@pytest.mark.parametrize(
    "changes,status",
    [
        ({"category": "accessory"}, "incompatible"),
        ({"form_factor": "in_ear"}, "incompatible"),
        ({"category": None}, "unresolved"),
        ({"microphone": None}, "unresolved"),
        ({"microphone": False}, "incompatible"),
    ],
)
def test_required_features(changes, status):
    result = run(request(candidate(1, **changes), microphone_required=True))
    assert not result.selected_refs and result.decisions[0].status == status


def test_exact_variant_self_missing_identity_and_empty():
    target = candidate()
    same = candidate(1, identity=target.identity.model_copy(update={"listing_id": "other"}))
    unknown = candidate(2, identity=candidate(2).identity.model_copy(update={"brand": None}))
    result = run(request(target, same, unknown))
    assert [d.status for d in result.decisions] == ["same_product", "same_product", "unresolved"]
    assert not result.selected_refs
    assert not run(request()).selected_refs
    assert run(request(target, target)).duplicate_count == 1


def test_conflicts_limits_origin_and_deadline():
    with pytest.raises(ReviewInputError, match="Catalog identity conflicts"):
        run(request(candidate(1), candidate(1, microphone=False)))
    with pytest.raises(ValidationError):
        request(*(candidate(i) for i in range(51)))
    with pytest.raises(ValidationError):
        AuthoredCandidate(identity=candidate().identity, evidence_origin="collected")
    with pytest.raises(ReviewInputError):
        select_candidates(request(), 0)
