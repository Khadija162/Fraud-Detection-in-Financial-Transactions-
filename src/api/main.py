"""Read-only prototype inference API. No authentication; localhost only."""
import json
import os
from pathlib import Path
from functools import lru_cache
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="FraudShield API", version="0.1.0")
MODEL = Path(os.getenv("MODEL_PATH", "artifacts/fraud_model.joblib"))
METRICS = Path(os.getenv("METRICS_PATH", "artifacts/metrics.json"))


class Transaction(BaseModel):
    features: dict[str, float] = Field(description="Time, Amount and V1..V28")


@lru_cache(maxsize=1)
def load_model():
    if not MODEL.is_file():
        return None
    # joblib artifacts are executable: only load artifacts created by trusted training code.
    return joblib.load(MODEL)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
def ready():
    return {"ready": load_model() is not None}


@app.get("/metrics")
def metrics():
    if not METRICS.is_file():
        return {"available": False}
    return json.loads(METRICS.read_text())


@app.get("/gold/daily")
def daily():
    path = Path("data/gold/daily_risk.parquet")
    return {"rows": pd.read_parquet(path).to_dict(orient="records") if path.is_file() else []}


@app.post("/predict")
def predict(transaction: Transaction):
    artifact = load_model()
    if artifact is None:
        raise HTTPException(503, "Model unavailable; run training first")
    required = artifact["features"]
    if set(transaction.features) != set(required):
        raise HTTPException(422, f"Expected exactly: {required}")
    values = pd.DataFrame([transaction.features])[required]
    risk = float(artifact["model"].predict_proba(values)[0, 1])
    threshold = float(artifact["threshold"])
    return {"fraud_probability": risk, "risk_flag": risk >= threshold,
            "threshold": threshold, "notice": "Decision support only; human review required"}
