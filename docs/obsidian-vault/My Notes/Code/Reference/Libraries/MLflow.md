---
tags: [library, experiment-tracking, placeholder, unused]
status: 🔲 Not yet used
---

# MLflow

> ⚠️ Not currently used. Candidate for experiment tracking during weight optimisation.

## What it is

Open-source ML lifecycle platform: experiment tracking, parameter logging,
metric comparison, and model registry across runs.

## Potential use in this project

Log each Optuna trial — recording weight values (α, β, γ, δ, η), loss, and evaluation
metrics (precision@k, RMSE against proxy ground truth). Makes the optimisation
process reproducible and auditable for the dissertation.

```python
# Sketch — not implemented
import mlflow

with mlflow.start_run():
    mlflow.log_params({"alpha": 0.10, "beta": 0.10})
    mlflow.log_metric("loss", 0.23)
```

## Relevant to report

Future work / methodology: experiment tracking for weight optimisation.
Demonstrates awareness of production ML practices.
