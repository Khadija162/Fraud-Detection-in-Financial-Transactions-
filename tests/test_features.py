import pandas as pd
import pytest
from fraud.features import prepare_features
from fastapi.testclient import TestClient
from api.main import app


def test_features_no_target_leakage():
    row = {"step": 1, "type": "TRANSFER", "amount": 100, "oldbalanceOrg": 150, "newbalanceOrig": 50, "oldbalanceDest": 0, "newbalanceDest": 100, "isFraud": 1}
    x = prepare_features(pd.DataFrame([row]))
    assert "isFraud" not in x.columns
    assert x.shape == (1, 7)


def test_missing_feature():
    with pytest.raises(ValueError, match="Missing"):
        prepare_features(pd.DataFrame([{"step": 1}]))


def test_api_health():
    assert TestClient(app).get("/health").status_code == 200


def test_predict_without_model(monkeypatch, tmp_path):
    from api.main import load_model
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "missing.joblib"))
    load_model.cache_clear()
    assert TestClient(app).post("/predict", json={"step":1,"type":"TRANSFER","amount":10,"oldbalanceOrg":10,"newbalanceOrig":0,"oldbalanceDest":0,"newbalanceDest":10}).status_code == 503
    load_model.cache_clear()
