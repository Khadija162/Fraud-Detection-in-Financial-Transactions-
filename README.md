# Financial Transaction Fraud Detection — Data Engineering + AI + Azure

A full-stack **fraud detection engineering prototype** using the publicly available **PaySim synthetic mobile-money dataset**. Includes repeatable lakehouse-style ETL, offline ML training and evaluation, HTTP inference, dashboard, Kafka-compatible streaming demo, Docker, GitHub Actions and starter Azure infrastructure.

> **Status:** Working code scaffold committed; not yet validated against the full public dataset or deployed to Azure. The model and operational risk controls require independent evaluation before any real-world use.

## Architecture

```text
[Public PaySim CSV] ----> [Bronze Parquet] ---> [Validated Silver Parquet] ---> [Gold DuckDB metrics]
      |                                  |
      v                                  v
[Chronological ML training] ---> [Trained scikit-learn model] ---> [FastAPI /predict]
                                     |                           |
                                     v                           v
                            [Redpanda consumer]             [Streamlit UI]
                                     ^
                                     |
                           [Kafka event producer]

GitHub Actions -> Python unit tests + Docker image build
Terraform example -> Azure Resource Group + ADLS Gen2 (NOT deployed)
```

## Dataset — open/public source

**PaySim**: https://www.kaggle.com/datasets/ealaxi/paysim1 . This dataset is simulated financial activity, not real banking customer transactions; Kaggle lists **CC BY-SA 4.0**. Credit: E. A. Lopez-Rojas, A. Elmir & S. Axelsson, *PaySim: A financial mobile money simulator for fraud detection* (2016). Download the CSV yourself and place it in `data/raw/` (excluded from Git).

The dataset contains roughly 6.36 million synthetic transactions, so the full file should not be committed. See [data provenance](docs/data.md).

## Quick start — Windows PowerShell

```powershell
git clone https://github.com/Khadija162/Fraud-Detection-in-Financial-Transactions-.git
cd Fraud-Detection-in-Financial-Transactions-
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Download PaySim CSV from Kaggle; substitute the actual filename:

```powershell
.\.venv\Scripts\python.exe -m fraud.etl --csv "data/raw/PS_20174392719_1491204439457_log.csv"
.\.venv\Scripts\python.exe -m fraud.train --csv "data/raw/PS_20174392719_1491204439457_log.csv" --max-rows 1000000
.\.venv\Scripts\python.exe -m pytest -q
```

If the training split has no fraud examples in both partitions, increase `--max-rows` or use the full dataset. Time-ordered metrics may be much lower than random-split results; that is expected and more defensible.

Start the API and UI in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --reload
.\.venv\Scripts\python.exe -m streamlit run dashboard/app.py
```

Then visit http://127.0.0.1:8000/docs and http://localhost:8501.

## Docker deployment — local only

After training so `models/fraud_pipeline.joblib` exists:

```powershell
docker compose up --build
```

API: http://localhost:8000/docs · UI: http://localhost:8501

Optional Redpanda Kafka-compatible broker:

```powershell
docker compose --profile streaming up -d redpanda
.\.venv\Scripts\python.exe -m streaming.producer --csv "data/raw/PS_20174392719_1491204439457_log.csv" --rows 200
.\.venv\Scripts\python.exe -m streaming.consumer
```

Kafka events are demo messages; the consumer logs scores and commits offsets and does **not** implement full production-grade exactly-once semantics.

## Code layout

- `fraud/etl.py` — chunked CSV -> Bronze/Silver Parquet -> Gold DuckDB analytics
- `fraud/train.py` — baseline supervised ML, chronological evaluation, artifact output
- `fraud/features.py` — centralized inference-time feature contract
- `api/main.py` — FastAPI prediction endpoint
- `dashboard/app.py` — Streamlit scoring interface
- `streaming/` — Redpanda/Kafka example producers and consumers
- `tests/` — automated unit tests
- `infra/terraform/` — Azure ADLS proof-of-concept infrastructure
- `.github/workflows/ci.yml` — automated tests + image build
- `docs/` — data lineage and cloud architecture notes

## Production and cloud roadmap

Azure Event Hubs -> Azure Databricks Spark / Delta Lake -> ADLS Gen2 -> fraud feature store / registry -> Azure Container Apps model serving -> Azure Monitor / dashboard -> optional Llama operational assistant. These components are **not deployed yet**. Terraform currently provisions only a resource group and storage account when explicitly applied.

Security before public deployment: authenticated API, authorization, private networking, Key Vault/managed identity, encrypted storage, audit logs, risk monitoring, human review, threshold tuning and evaluation for bias and false positives. Predictions are research signals, **not automated account-blocking decisions**.

## License and source attribution

Software code in this repository is original demo code. The external PaySim dataset has its own CC BY-SA licensing and attribution obligations and is not redistributed here.
