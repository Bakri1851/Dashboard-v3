---
tags: [library, optimisation, placeholder, unused]
status: 🔲 Not yet used
---

# Optuna

> ⚠️ Not currently used. Candidate for future weight optimisation.

## What it is

Hyperparameter optimisation framework using Tree-structured Parzen Estimator.
Runs trials, prunes unpromising ones early, finds optimal parameter values automatically.

## Potential use in this project

Optimise struggle score weights (α, β, γ, δ, η) once labeled ground-truth data is available.
Define an objective function that takes a weight vector, computes struggle scores,
and returns a loss against ground-truth labels. Optuna searches the weight space.

```python
# Sketch — not implemented
import optuna

def objective(trial):
    alpha = trial.suggest_float("alpha", 0.0, 1.0)
    beta  = trial.suggest_float("beta",  0.0, 1.0)
    # ... remaining weights, compute scores, return loss vs ground truth
    return loss

study = optuna.create_study(direction="minimize")
study.optimize(objective, n_trials=100)
```

## Relevant to report

Future work: ML-based weight optimisation once labeled data is available.
Pair with MLflow for experiment tracking across trials.
