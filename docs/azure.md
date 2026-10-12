# Azure deployment plan

This repository includes Terraform templates for Azure ADLS Gen2, ACR and a Container Apps environment. **No cloud resources have been deployed.** The Terraform currently provisions foundational resources, not a running API app.

## Deployment stages

1. Set an Azure spending budget; review privacy, RBAC and region.
2. Provision foundations: `cd infra/terraform && terraform init && terraform plan`.
3. Train the model on approved data locally or in a controlled job. Save artifact in a private artifact store.
4. Build and scan Docker image; push to ACR via federated GitHub Actions/Azure identity.
5. Deploy the API to Azure Container Apps with internal ingress, managed identity and secrets from Key Vault.
6. Publish the analyst dashboard behind Microsoft Entra ID authentication and HTTPS.
7. Store Parquet snapshots in ADLS Gen2, add Delta Lake and orchestration via Databricks as a future extension.
8. Add alerts and monitoring through Azure Monitor / Application Insights, load tests and drift evaluation.

## Security

Do not deploy the sample unauthenticated API to the public internet. Never embed Azure credentials, registry passwords or customer records in source control. Limit PII and apply appropriate licenses/terms to public data.
