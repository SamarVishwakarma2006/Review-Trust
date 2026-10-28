import time

import pytest
from fastapi.testclient import TestClient

from app import main
from app.analysis import analyze
from app.ingestion import ReviewInputError, validate_submission
from app.schemas import MAX_BODY_BYTES
from app.security import Settings
from app.uploads import parse_upload


def payload(rows):
    return {
        "schema_version": "1",
        "category": "electronics",
        "language": "en",
        "origin": "paste",
        "reviews": rows,
    }


@pytest.mark.parametrize("text", ["one two three four five", "received a free product today"])
def test_json_and_csv_never_publish_numeric_scores(text):
    with TestClient(main.create_app(Settings())) as client:
        responses = [
            client.post("/v1/analyze", json=payload([{"text": text}] * 20)),
            client.post(
                "/v1/analyze/csv",
                files={"file": ("synthetic.csv", "text\n" + (text + "\n") * 20, "text/csv")},
                data={"schema_version": "1", "language": "en", "category": "electronics"},
            ),
        ]
    for response in responses:
        assert response.status_code == 200
        result = response.json()
        assert result["score"]["value"] is None
        assert result["score"]["status"] == "withheld"
        assert result["score"]["reason_codes"] == ["public_score_not_validated"]
        assert len(result["findings"]) == 5 and result["confidence"]["level"] is None
        assert (
            response.headers["content-security-policy"]
            == "default-src 'none'; frame-ancestors 'none'"
        )
        assert response.headers["referrer-policy"] == "no-referrer"


@pytest.mark.parametrize(
    "rows",
    [
        [{"text": "ﷺ" * 500}],
        [{"text": "one two three four five", "title": "ﷺ" * 100}],
        [{"text": "ﬃ " * 1250}] * 60,
    ],
)
def test_normalization_expansion_rejects_atomically_without_echoing(rows):
    app = main.create_app(Settings())
    with TestClient(app) as client:
        response = client.post("/v1/analyze", json=payload(rows))
        assert response.status_code == 413
        assert response.json()["error"]["code"] == "normalized_text_limit"
        assert "reviews" not in response.json() and "score" not in response.json()
        assert app.state.controls.active == 0


def test_serialized_response_limit_is_enforced_in_worker(monkeypatch):
    result = analyze(
        validate_submission(payload([{"text": "one two three four five"}])), time.monotonic() + 10
    )
    result.limitations.append("x" * (2 * MAX_BODY_BYTES))
    monkeypatch.setattr(main, "analyze", lambda *_: result)
    app = main.create_app(Settings())
    with TestClient(app) as client:
        response = client.post("/v1/analyze", json=payload([{"text": "one two three four five"}]))
        assert response.status_code == 413
        assert response.json()["error"]["code"] == "response_limit"
        assert len(response.content) < 1000 and app.state.controls.active == 0


def test_multipart_part_header_budget_is_checked_before_parsing_options():
    body = (
        b'--b\r\nContent-Disposition: form-data; name="' + b"x" * 9000 + b'"\r\n\r\nx\r\n--b--\r\n'
    )
    with pytest.raises(ReviewInputError) as error:
        parse_upload(body, "multipart/form-data; boundary=b", time.monotonic() + 10)
    # The installed parser already enforces max_header_size=8192 natively.
    assert error.value.code == "malformed_multipart"
    assert error.value.status_code == 400
