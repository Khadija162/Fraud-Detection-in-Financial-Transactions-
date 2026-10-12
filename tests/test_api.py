from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_health():
    assert client.get("/health").json()["status"] == "ok"


def test_prediction_missing_model_returns_error_or_valid_prediction():
    result = client.post("/predict", json={"features": {}})
    assert result.status_code in (422, 503)
