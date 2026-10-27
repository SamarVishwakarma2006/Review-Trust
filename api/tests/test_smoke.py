from fastapi.testclient import TestClient

from app.main import app


def test_development_app_starts_and_returns_minimal_status():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"service": "ReviewTrust API", "status": "development"}
    assert response.headers["cache-control"] == "no-store"


def test_empty_review_submission_is_rejected():
    with TestClient(app) as client:
        response = client.post("/v1/analyze", json={})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "invalid_submission"
