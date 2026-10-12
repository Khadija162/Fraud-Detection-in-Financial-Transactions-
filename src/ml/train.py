"""Temporal holdout and validation-threshold model training."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, precision_score, recall_score, f1_score, roc_auc_score

ARTIFACTS = Path("artifacts")
FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]


def choose_threshold(y, scores):
    thresholds = np.linspace(0.05, 0.95, 19)
    return float(max(thresholds, key=lambda t: f1_score(y, scores >= t, zero_division=0)))


def train(path=Path("data/silver/transactions.parquet")):
    frame = pd.read_parquet(path).sort_values("Time").reset_index(drop=True)
    n = len(frame)
    if n < 100 or frame["Class"].nunique() != 2:
        raise ValueError("Insufficient training data or only one class")
    # Chronological split: 60% train, 20% validation, 20% test.
    a, b = int(n * 0.6), int(n * 0.8)
    train_df, val_df, test_df = frame.iloc[:a], frame.iloc[a:b], frame.iloc[b:]
    if any(x["Class"].nunique() != 2 for x in (train_df, val_df, test_df)):
        raise ValueError("Each chronological split must include both classes")
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(class_weight="balanced", max_iter=1500, random_state=42),
    )
    model.fit(train_df[FEATURES], train_df["Class"])
    val_scores = model.predict_proba(val_df[FEATURES])[:, 1]
    threshold = choose_threshold(val_df["Class"], val_scores)
    scores = model.predict_proba(test_df[FEATURES])[:, 1]
    predictions = scores >= threshold
    y = test_df["Class"]
    metrics = {
        "test_rows": int(len(y)),
        "test_fraud_rate": float(y.mean()),
        "average_precision": float(average_precision_score(y, scores)),
        "roc_auc": float(roc_auc_score(y, scores)),
        "precision": float(precision_score(y, predictions, zero_division=0)),
        "recall": float(recall_score(y, predictions, zero_division=0)),
        "f1": float(f1_score(y, predictions, zero_division=0)),
        "threshold": threshold,
        "split": "chronological 60/20/20",
        "warning": "Interpret as a proof-of-concept; ULB dataset spans only two days."
    }
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "threshold": threshold},
                ARTIFACTS / "fraud_model.joblib")
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps(metrics, indent=2))
    return metrics


if __name__ == "__main__":
    train()
