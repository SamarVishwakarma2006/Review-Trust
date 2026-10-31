"""Authored E06 mechanics; no provider access or dataset admission."""

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from app.ingestion import ReviewInputError
from app.source_parser import parse_product
from app.source_sample import assemble_fixture_sample

FIXTURES = Path(__file__).parent / "fixtures"
PRODUCT = parse_product(
    (FIXTURES / "source_product.json").read_bytes(), expected_slug="example-headphones"
)
NOW = datetime(2026, 10, 31, tzinfo=UTC)


def row(identity=1, **changes):
    return {
        "id": identity,
        "product_id": 101,
        "status": "approved",
        "review": "Authored clear sound.",
        **changes,
    }


def sample(*pages, exhausted=False, **changes):
    arguments = dict(
        product=PRODUCT, window_started_at=NOW, window_finished_at=NOW, exhausted=exhausted
    )
    return assemble_fixture_sample(
        tuple(json.dumps(page).encode() for page in pages), **(arguments | changes)
    )


def test_identical_overlap_collapses_but_distinct_ids_with_equal_text_remain():
    result = sample([row()], [row(), row(2)], exhausted=True)
    assert result.status == "complete" and result.stop_reason == "exhausted"
    assert len(result.reviews) == 2 and result.fetched_records == 3
    assert result.overlap_records == 1 and result.pages_fetched == 2
    assert result.available_reviews is None and result.count_scope == "unknown"
    assert result.variant_scope == "combined" and result.evidence_origin == "authored_fixture"
    assert all(review.source_id is None and review.product_id == "101" for review in result.reviews)
    assert "Authored" not in repr(result)
    assert result == sample([row()], [row(), row(2)], exhausted=True)


@pytest.mark.parametrize("change", [{"review": "changed"}, {"rating": 4}, {"verified": True}])
def test_conflicting_ids_reject_atomically(change):
    with pytest.raises(ReviewInputError, match="Source data"):
        sample([row()], [row(**change)])


@pytest.mark.parametrize(
    "exhausted,status,reason", [(True, "empty", "empty"), (False, "partial", "source_window")]
)
def test_empty_requires_explicit_exhaustion(exhausted, status, reason):
    result = sample([], exhausted=exhausted)
    assert (result.status, result.stop_reason, result.reviews) == (status, reason, ())


def test_short_page_never_proves_exhaustion_and_nulls_remain_unknown():
    result = sample([row()])
    assert result.status == "partial" and result.stop_reason == "source_window"
    assert result.reviews[0].rating is None and result.reviews[0].timestamp is None


def test_page_and_row_limits_are_disclosed_without_extra_page_or_truncation():
    result = sample(*[[row(i)] for i in range(1, 6)])
    assert result.stop_reason == "page_limit"
    pages = [[row(page * 100 + i + 1) for i in range(100)] for page in range(5)]
    assert sample(*pages).stop_reason == "row_limit"
    assert sample(*pages, exhausted=True).status == "complete"
    with pytest.raises(ReviewInputError):
        sample(*pages, [])


def test_newest_first_dates_checked_across_pages_with_overlap():
    newer = row(date_created_gmt="2025-02-02T00:00:00")
    older = row(2, date_created_gmt="2025-02-01T00:00:00")
    assert len(sample([newer], [newer, older]).reviews) == 2
    with pytest.raises(ReviewInputError):
        sample([older], [newer])


@pytest.mark.parametrize(
    "pages", [([], [row()]), ([row(), row()],), ([row(product_id=102)],), ([row(rating=0)],)]
)
def test_invalid_pages_and_product_association_never_silently_drop_rows(pages):
    with pytest.raises(ReviewInputError):
        sample(*pages)


def test_masking_nfkc_and_utc_window_do_not_change_identity_or_invent_variant():
    result = sample(
        [row(review="Ｆｉｔ authored@example.invalid +1 202 555 0123")],
        window_started_at=NOW.astimezone(timedelta_timezone()),
    )
    assert result.window_started_at == NOW and result.window_started_at.tzinfo == UTC
    assert result.reviews[0].text == "Fit [EMAIL_REDACTED] [PHONE_REDACTED]"
    assert result.reviews[0].verified_purchase is None


def timedelta_timezone():
    from datetime import timezone

    return timezone(timedelta(hours=5, minutes=30))


@pytest.mark.parametrize(
    "changes",
    [
        {"window_started_at": NOW.replace(tzinfo=None)},
        {"window_finished_at": NOW - timedelta(seconds=1)},
        {"exhausted": 1},
    ],
)
def test_invalid_provenance_rejects(changes):
    with pytest.raises(ReviewInputError):
        sample([row()], **changes)


def test_normalization_amplification_and_cross_page_text_caps_reject():
    with pytest.raises(ReviewInputError) as error:
        sample([row(review="\ufdfa" * 300)])
    assert error.value.code == "source_limit"
    with pytest.raises(ReviewInputError) as error:
        sample(
            [row(i, review="x" * 3000) for i in range(1, 51)],
            [row(i, review="x" * 3000) for i in range(51, 101)],
        )
    assert error.value.code == "source_limit"


def test_aggregate_raw_bytes_cap_precedes_parsing():
    with pytest.raises(ReviewInputError) as error:
        assemble_fixture_sample(
            (b" " * 262145,) * 4,
            product=PRODUCT,
            window_started_at=NOW,
            window_finished_at=NOW,
            exhausted=False,
        )
    assert error.value.code == "source_limit"
