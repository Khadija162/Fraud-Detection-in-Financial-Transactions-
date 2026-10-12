"""Time-ordered offline fraud model evaluation, with no label leakage in features."""
import argparse
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import average_precision_score, classification_report, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from .features import FEATURES, NUMERICS, prepare_features


def train(csv_file: str, output: str = "models/fraud_pipeline.joblib", max_rows: int = 500_000):
    cols = FEATURES + ["isFraud"]
    frame = pd.read_csv(csv_file, usecols=cols, nrows=max_rows).sort_values("step")
    frame = frame[frame["isFraud"].isin([0, 1])].reset_index(drop=True)
    cut = int(len(frame) * 0.8)
    if cut < 20 or cut >= len(frame):
        raise ValueError("Need at least 25 valid records")
    train_df, test_df = frame.iloc[:cut], frame.iloc[cut:]
    y_train = train_df["isFraud"].astype(int)
    y_test = test_df["isFraud"].astype(int)
    if y_train.nunique() < 2 or y_test.nunique() < 2:
        raise ValueError("Both chronological train and test must contain both classes; increase --max-rows")
    pre = ColumnTransformer([
        ("numeric", SimpleImputer(strategy="median", add_indicator=True), NUMERICS),
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), ["type"]),
    ])
    model = Pipeline([("preprocess", pre), ("classifier", HistGradientBoostingClassifier(max_iter=120, learning_rate=0.08, random_state=42))])
    model.fit(prepare_features(train_df), y_train)
    scores = model.predict_proba(prepare_features(test_df))[:, 1]
    predictions = (scores >= 0.5).astype(int)
    results = {"rows_train": len(train_df), "rows_test": len(test_df), "fraud_rate_test": float(y_test.mean()), "average_precision": float(average_precision_score(y_test, scores)), "roc_auc": float(roc_auc_score(y_test, scores)), "classification_report": classification_report(y_test, predictions, output_dict=True, zero_division=0)}
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    path.with_suffix(".metrics.json").write_text(json.dumps(results, indent=2))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output", default="models/fraud_pipeline.joblib")
    parser.add_argument("--max-rows", type=int, default=500_000)
    a = parser.parse_args()
    print(json.dumps(train(a.csv, a.output, a.max_rows), indent=2))
