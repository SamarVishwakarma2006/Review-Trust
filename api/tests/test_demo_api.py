import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.security import Settings


@pytest.mark.parametrize(
    "example,status,count",
    [("patterns", "complete", 20), ("partial", "partial", 20), ("empty", "empty", 0)],
)
def test_demo_runs_authored_analysis(example, status, count):
    with TestClient(create_app()) as client:
        response = client.post("/v2/demo/analyze", json={"example": example})
        assert response.status_code == 200
        result = response.json()
        assert result["evidence_origin"] == "authored_fixture"
        assert result["status"] == status and result["analyzed_reviews"] == count
        if count:
            assert result["analysis"]["score"]["value"] is None
            assert result["analysis"]["origin"] == "authored_fixture"
            assert any(f["assessment"] == "observed" for f in result["analysis"]["findings"])
        else:
            assert result["analysis"] is None
        assert client.app.state.controls.active == 0


def test_demo_rejects_urls_and_shares_limits():
    with TestClient(create_app(Settings(rate_burst=100, rate_per_minute=600))) as client:
        assert (
            client.post(
                "/v2/demo/analyze", json={"example": "patterns", "url": "https://secret.example"}
            ).status_code
            == 422
        )
        assert client.post("/v2/demo/analyze", content=b"x" * 8193).status_code == 413
        assert client.post("/v2/demo/analyze", json={"example": "unknown"}).status_code == 422
        client.app.state.controls.active = 2
        assert client.post("/v2/demo/analyze", json={"example": "empty"}).status_code == 503
        client.app.state.controls.active = 0
