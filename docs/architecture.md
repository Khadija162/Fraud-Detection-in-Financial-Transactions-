# Fraud detection platform architecture

## Implemented locally

- Public PaySim CSV acquisition by the developer (dataset not rehosted).
- Chunked Pandas -> Bronze raw Parquet -> Silver validated Parquet -> Gold DuckDB aggregation.
- Scikit-learn time-ordered baseline with fraud average precision and ROC-AUC.
- FastAPI model serving and Streamlit UI.
- Optional Kafka-compatible Redpanda producer/consumer for streaming scoring.
- Docker Compose for API/UI and optional event broker; GitHub Actions testing and Docker build.

## Advanced engineering extensions (not yet deployed)

- Replace local Parquet batch ETL with Spark + Delta Lake MERGE, watermarks, late events and exactly-once semantics.
- Azure Event Hubs / ADLS Gen2 / Databricks jobs, Azure PostgreSQL, Azure Monitor and App Insights.
- Feature store, model monitoring (drift/PR-AUC with delayed labels), model registry and shadow deployments.
- Managed identity, Entra auth, private networking and Key Vault.
- A read-only Llama/LLM fraud-operations assistant grounded in stored incident metrics; no automatic fraud or account action.

## Evaluation cautions

Time-based split rather than random split. PaySim contains synthetic transactions, so real-world generalization is unproven. Monitor false positives and recall at realistic review capacity. The baseline excludes `isFraud` and `isFlaggedFraud` as predictors. This demo should never autonomously block customer accounts.
