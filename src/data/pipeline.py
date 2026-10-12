"""Bronze/Silver/Gold local lakehouse snapshot pipeline."""
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd

ROOT = Path("data")
REQUIRED = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount", "Class"]


def validate(df):
    missing = sorted(set(REQUIRED) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    d = df[REQUIRED].copy()
    for col in REQUIRED:
        d[col] = pd.to_numeric(d[col], errors="coerce")
    good = d.notna().all(axis=1) & d["Class"].isin([0, 1]) & (d["Amount"] >= 0)
    return d.loc[good].copy(), d.loc[~good].copy()


def replace_parquet(df, path):
    """Atomic file replace for one local writer; not distributed transactional storage."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp.parquet")
    df.to_parquet(temporary, index=False)
    temporary.replace(path)


def run(raw=ROOT / "raw" / "creditcard.csv"):
    df = pd.read_csv(raw)
    silver, rejected = validate(df)
    bronze = df.copy()
    bronze["ingested_at_utc"] = datetime.now(timezone.utc).isoformat()
    replace_parquet(bronze, ROOT / "bronze" / "transactions.parquet")
    replace_parquet(silver, ROOT / "silver" / "transactions.parquet")
    if len(rejected):
        replace_parquet(rejected, ROOT / "quarantine" / "rejected.parquet")
    else:
        (ROOT / "quarantine" / "rejected.parquet").unlink(missing_ok=True)
    silver["day_index"] = (silver["Time"] // 86400).astype(int)
    gold = silver.groupby("day_index", as_index=False).agg(
        transactions=("Class", "size"),
        frauds=("Class", "sum"),
        total_amount=("Amount", "sum"),
    )
    gold["fraud_rate"] = gold["frauds"] / gold["transactions"]
    replace_parquet(gold, ROOT / "gold" / "daily_risk.parquet")
    result = {"source_rows": int(len(df)), "valid_rows": int(len(silver)),
              "rejected_rows": int(len(rejected)), "gold_rows": int(len(gold))}
    (ROOT / "gold" / "manifest.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    run()
