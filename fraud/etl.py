"""Bronze/Silver/Gold local lakehouse: chunked PaySim CSV to Parquet and DuckDB metrics."""
import argparse
from pathlib import Path
import duckdb
import pandas as pd

REQUIRED = {"step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig", "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud"}


def run(csv_file: str, output: str = "data") -> dict:
    source = Path(csv_file)
    if not source.is_file():
        raise FileNotFoundError(f"Download PaySim CSV and specify --csv: {source}")
    base = Path(output)
    bronze = base / "bronze"
    silver = base / "silver"
    gold = base / "gold"
    for directory in (bronze, silver, gold):
        directory.mkdir(parents=True, exist_ok=True)
    n_raw = n_valid = n_rejected = 0
    for i, part in enumerate(pd.read_csv(source, chunksize=100_000)):
        missing = REQUIRED - set(part.columns)
        if missing:
            raise ValueError(f"Missing PaySim columns: {sorted(missing)}")
        n_raw += len(part)
        part.to_parquet(bronze / f"part-{i:05d}.parquet", index=False)
        valid = part["amount"].notna() & (part["amount"] >= 0) & part["step"].notna() & part["isFraud"].isin([0, 1]) & part["type"].notna()
        n_valid += int(valid.sum())
        n_rejected += int((~valid).sum())
        part.loc[valid].to_parquet(silver / f"part-{i:05d}.parquet", index=False)
    if n_valid == 0:
        raise ValueError("No valid records; cannot create Gold metrics")
    conn = duckdb.connect()
    try:
        silver_glob = (silver / "*.parquet").as_posix()
        metrics = conn.execute("""
            SELECT type, COUNT(*) AS transactions, SUM(CAST(isFraud AS BIGINT)) AS frauds,
                   SUM(amount) AS total_amount,
                   AVG(CAST(isFraud AS DOUBLE)) AS fraud_rate
            FROM read_parquet(?) GROUP BY type ORDER BY type
        """, [silver_glob]).df()
        metrics.to_parquet(gold / "fraud_by_type.parquet", index=False)
    finally:
        conn.close()
    return {"raw": n_raw, "valid": n_valid, "rejected": n_rejected, "gold_rows": len(metrics)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--output", default="data")
    args = parser.parse_args()
    print(run(args.csv, args.output))
