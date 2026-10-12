# Public data provenance

Primary dataset: **PaySim synthetic financial datasets for fraud detection** (Lopez-Rojas, Elmir, Axelsson, 2016):
https://www.kaggle.com/datasets/ealaxi/paysim1

Kaggle lists the PaySim public distribution as CC BY-SA 4.0. Credit the authors and check source terms if publishing derived data. The full ~6.36-million-row CSV is NOT committed to Git. Download it from Kaggle into `data/raw/`, then pass its filename via `--csv`.

Expected fields: `step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud`.

The script intentionally uses only numeric and transaction type features for inference; source account identifiers are not needed by the deployed API. GitHub CI uses unit tests that do not download the data.

Sample metrics are not advertised as real until you run training locally on the genuine PaySim dataset.
