# FraudShield — Financial Transaction Fraud Detection Platform

An Azure-ready, end-to-end **data engineering + machine learning + API + dashboard** portfolio project built around the publicly available **ULB/Worldline Credit Card Fraud Detection dataset**.

**Status:** runnable local reference stack and deployment templates; **not yet deployed to Azure**. Source data is downloaded independently, not redistributed. No production accuracy or latency benchmarks are claimed.

## Architecture

```text
OpenML / ULB creditcard.csv
    -> validation + Bronze Parquet -> Silver Parquet -> Gold daily risk metrics
                                     -> temporal train/test -> sklearn fraud classifier
                                     -> model artifact (joblib)
                                     -> FastAPI /predict + /health
                                     -> Streamlit analyst dashboard
Docker Compose: api + dashboard
GitHub Actions: lint/smoke unit tests + Docker build
Azure deployment template: ACR + Container Apps + ADLS Gen2 (Terraform)
Optional Spark and Kafka adapters in pipeline extras.
```

## Public dataset

**ULB/Worldline credit-card fraud benchmark** (284,807 transactions; 492 frauds; two days; anonymized PCA components). Source: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud . Dataset access/usage is subject to the publisher's terms. Do not commit `creditcard.csv` to Git.

Get it either by:
- Download `creditcard.csv` manually and save as `data/raw/creditcard.csv`; or
- `python -m src.data.download --source openml` (OpenML availability and terms may vary).

For an **offline smoke test only**: `python -m src.data.download --source synthetic`. Synthetic scores are not legitimate benchmark results.

## Quick start — Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.data.download --source synthetic
.\.venv\Scripts\python.exe -m src.data.pipeline
.\.venv\Scripts\python.exe -m src.ml.train
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload
```

Open http://localhost:8000/docs . In a second terminal: `streamlit run dashboard/app.py` (http://localhost:8501).

For **real benchmark training**, replace the synthetic raw file with the real ULB `creditcard.csv`, rerun pipeline and training, and inspect `artifacts/metrics.json`. This repo intentionally does not publish unverified evaluation numbers.

## Docker

After preparing the data and model locally:
```bash
docker compose up --build
```
The API runs at http://localhost:8000 and dashboard at http://localhost:8501. Containers load the local model via a volume. If there is no trained artifact, the readiness endpoint reports unavailable and prediction returns HTTP 503.

## API contract

- `GET /health`: liveness
- `GET /ready`: model availability
- `GET /metrics`: training evaluation report, if generated
- `POST /predict`: JSON `{"features":{"Time":0,"V1":0,...,"V28":0,"Amount":25}}`; response includes risk score and threshold decision
- `GET /gold/daily`: aggregate reporting data (if generated)

The API is a demo, unauthenticated, and must **not** be publicly exposed without security controls. Fraud predictions are not financial decisions; human review is required.

## Data engineering characteristics

- Explicit source column validation and null quarantine counts
- Bronze/Silver/Gold Parquet layers with run manifests
- Idempotent snapshot refresh using temp directories + swap (local demo only; no cross-process concurrency safety)
- Leakage-aware chronological holdout and PR-AUC evaluation
- Class imbalance handled with class-weighted logistic regression
- Threshold selection on validation data, untouched test evaluation
- Feature schema validation at inference
- Optional PySpark aggregation and Kafka event producer templates

## Azure

See [Azure deployment guide](docs/azure.md) and `infra/terraform/`. Terraform creates a resource group, storage account/ADLS, container registry, and Container Apps environment + API app. It **does not** automatically build or push images, or train a model. Review access/networking, identities, costs and auth before deploying.

## Repository structure

```text
src/data/        source ingestion, Bronze/Silver/Gold
src/ml/          model training, evaluation, inference
src/api/         FastAPI application
src/streaming/   optional Kafka adapter
spark/           optional PySpark analytics
dashboard/       Streamlit UI
tests/           offline tests
infra/terraform/ Azure infrastructure templates
.github/workflows/ CI checks
```

## Data privacy

Use approved public anonymized data or synthetic transactions. No account numbers, PII, API keys, Kaggle credentials, raw CSV exports, model artifacts or cloud state files should be committed.
