"""Acquire authorized public data or generate OFFLINE synthetic smoke-test data."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

RAW = Path("data/raw/creditcard.csv")
FEATURES = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]


def synthetic(n=2000, seed=42):
    rng = np.random.default_rng(seed)
    data = {f"V{i}": rng.normal(size=n) for i in range(1, 29)}
    data["Time"] = np.sort(rng.uniform(0, 172800, n))
    data["Amount"] = np.round(rng.lognormal(3, 1, size=n), 2)
    # Predictable signal for pipeline smoke testing, NOT real fraud evidence.
    score = 2.2 * data["V1"] - 1.5 * data["V3"] + rng.normal(size=n)
    data["Class"] = (score > np.quantile(score, 0.98)).astype(int)
    return pd.DataFrame(data)[FEATURES]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", choices=["openml", "synthetic"], required=True)
    args = parser.parse_args()
    RAW.parent.mkdir(parents=True, exist_ok=True)
    if args.source == "synthetic":
        df = synthetic()
    else:
        from sklearn.datasets import fetch_openml
        df = fetch_openml("creditcard", version=1, as_frame=True).frame
        df.columns = [str(col) for col in df.columns]
        if "Class" not in df:
            raise ValueError("OpenML dataset missing Class; download official CSV manually")
        df["Class"] = pd.to_numeric(df["Class"], errors="raise").astype(int)
        df = df[FEATURES]
    df.to_csv(RAW, index=False)
    print(f"Saved {len(df)} records to {RAW}; source={args.source}")
if __name__ == "__main__":
    main()
