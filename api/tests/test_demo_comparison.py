import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.mark.parametrize(
    "example,count", [("compare", 3), ("compare_gaps", 3), ("compare_empty", 1)]
)
def test_bounded_comparison_and_missing_evidence(example, count):
    with TestClient(create_app()) as client:
        response = client.post("/v2/demo/analyze", json={"example": example})
    assert response.status_code == 200
    assert len(response.content) < 2097152
    result = response.json()
    assert result["evidence_origin"] == "authored_fixture"
    assert len(result["products"]) == count
    for i, product in enumerate(result["products"]):
        report = product["report"]
        assert product["role"] == ("original" if i == 0 else "alternative")
        assert report["evidence_origin"] == "authored_fixture"
        if report["analysis"]:
            assert report["analysis"]["score"]["value"] is None
        offers = product["offers"]
        if example == "compare_gaps" and i:
            assert not offers["comparison_complete"]
            assert offers["lowest_total_refs"] == []
            assert all(o["total"] is None for o in offers["decisions"])
        else:
            assert offers["lowest_total_refs"] == ["o1", "o2"]
    if example == "compare_gaps":
        assert result["products"][1]["report"]["status"] == "partial"
        assert result["products"][2]["report"]["analysis"] is None
    if example == "compare":
        assert [p["report"]["analyzed_reviews"] for p in result["products"]] == [20, 8, 12]
