"""Stable, inference-safe PaySim features. No target or post-transaction flags."""
import pandas as pd
FEATURES = ["step", "type", "amount", "oldbalanceOrg", "newbalanceOrig", "oldbalanceDest", "newbalanceDest"]
NUMERICS = [c for c in FEATURES if c != "type"]


def prepare_features(frame: pd.DataFrame) -> pd.DataFrame:
    missing = set(FEATURES) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing PaySim columns: {sorted(missing)}")
    x = frame[FEATURES].copy()
    for column in NUMERICS:
        x[column] = pd.to_numeric(x[column], errors="coerce")
    x["type"] = x["type"].fillna("UNKNOWN").astype(str)
    return x
