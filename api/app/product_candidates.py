"""Bounded offline selection from explicitly authored candidate catalogs."""

from typing import Literal

from pydantic import Field

from app.analysis import check_deadline
from app.ingestion import ReviewInputError
from app.product_identity import IdentityMatch, ProductIdentity, match_products
from app.schemas import InputModel


class AuthoredCandidate(InputModel):
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"
    identity: ProductIdentity
    category: Literal["headphones", "earphones", "speakers", "accessory"] | None = None
    form_factor: Literal["over_ear", "on_ear", "in_ear", "open_ear"] | None = None
    microphone: bool | None = None


class CandidatePreferences(InputModel):
    category: Literal["headphones", "earphones"]
    form_factor: Literal["over_ear", "on_ear", "in_ear", "open_ear"]
    connectivity: Literal["wired", "wireless"]
    microphone_required: bool = False


class CandidateDecision(InputModel):
    ref: str
    status: Literal["candidate", "same_product", "incompatible", "unresolved"]
    reasons: tuple[str, ...]
    identity_match: IdentityMatch


class CandidateSelection(InputModel):
    version: Literal["rt-candidates-0.1.0"] = "rt-candidates-0.1.0"
    evidence_origin: Literal["authored_fixture"] = "authored_fixture"
    supplied_count: int
    duplicate_count: int
    decisions: tuple[CandidateDecision, ...]
    selected_refs: tuple[str, ...]
    omitted_eligible_count: int


class CandidateRequest(InputModel):
    target: AuthoredCandidate
    candidates: tuple[AuthoredCandidate, ...] = Field(max_length=50)
    preferences: CandidatePreferences


def select_candidates(request: CandidateRequest, deadline: float) -> CandidateSelection:
    """Return up to five eligible references in input order, not a quality ranking.

    Duplicate source/listing records collapse only when every supplied field agrees.
    Conflicts reject atomically. Input references remain c1..cN after deduplication.
    """
    check_deadline(deadline)
    target, preferences = request.target, request.preferences
    target_key = target.identity.source, target.identity.listing_id
    seen = {}
    decisions = []
    duplicates = 0
    selected = []
    eligible = 0
    for i, row in enumerate(request.candidates, 1):
        check_deadline(deadline)
        key = row.identity.source, row.identity.listing_id
        if key == target_key and row != target:
            raise ReviewInputError("candidate_conflict", "Catalog identity conflicts.")
        if key in seen:
            if row != seen[key]:
                raise ReviewInputError("candidate_conflict", "Catalog identity conflicts.")
            duplicates += 1
            continue
        seen[key] = row
        identity = match_products(target.identity, row.identity)
        requirements = {
            "category": (row.category, preferences.category),
            "form_factor": (row.form_factor, preferences.form_factor),
            "connectivity": (row.identity.connectivity, preferences.connectivity),
        }
        if preferences.microphone_required:
            requirements["microphone"] = (row.microphone, True)
        wrong = tuple(
            k
            for k, (actual, wanted) in requirements.items()
            if actual is not None and actual != wanted
        )
        missing = tuple(k for k, (actual, _) in requirements.items() if actual is None)
        missing_identity = any(
            value is None
            for value in (
                target.identity.brand,
                target.identity.model,
                row.identity.brand,
                row.identity.model,
            )
        )
        if wrong:
            status, reasons = "incompatible", wrong
        elif (
            key == (target.identity.source, target.identity.listing_id)
            or identity.status == "same_variant"
        ):
            status, reasons = "same_product", ("same_product",)
        elif missing or missing_identity or identity.status == "unresolved":
            status, reasons = (
                "unresolved",
                missing
                + (("identity",) if missing_identity or identity.status == "unresolved" else ()),
            )
        else:
            status, reasons = "candidate", tuple(requirements)
        ref = f"c{i}"
        decisions.append(
            CandidateDecision(ref=ref, status=status, reasons=reasons, identity_match=identity)
        )
        if status == "candidate":
            eligible += 1
            if len(selected) < 5:
                selected.append(ref)
    check_deadline(deadline)
    return CandidateSelection(
        supplied_count=len(request.candidates),
        duplicate_count=duplicates,
        decisions=tuple(decisions),
        selected_refs=tuple(selected),
        omitted_eligible_count=eligible - len(selected),
    )
