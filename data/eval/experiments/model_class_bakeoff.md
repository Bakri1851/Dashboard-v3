# Model-class bake-off results

_Ran at 2026-05-26T19:00:32.771297+00:00_

Side experiment to test whether OLS (current v2 baseline) is the best regression model class against the 4-band target, or whether regularised linear / non-linear alternatives give meaningfully better Spearman ρ. NO canonical artefacts modified.

All metrics: Spearman ρ against the LLM 4-band rating, using identical CV splits to `scripts/optimise_v2_weights.py`. Higher is better.

## Struggle (n=1306, 7 features, 5-fold GroupKFold by session)

| Model | Mean ρ | Std | Δ vs OLS |
|---|---|---|---|
| OLS (baseline) **★** | +0.573 | 0.115 | +0.000 |
| Ridge alpha=0.1 | +0.573 | 0.115 | -0.000 |
| Ridge alpha=1.0 | +0.573 | 0.115 | +0.000 |
| Ridge alpha=10.0 | +0.573 | 0.115 | +0.000 |
| Lasso alpha=0.01 | +0.574 | 0.117 | +0.001 |
| ElasticNet a=0.01 | +0.574 | 0.116 | +0.001 |
| RandomForest | +0.583 | 0.126 | +0.010 🟢 |
| GradientBoosting | +0.559 | 0.128 | -0.013 🔴 |

## Difficulty (n=72, 5 features, LOO — pooled ρ)

| Model | Pooled ρ |
|---|---|
| OLS (baseline) **★** | +0.287 (Δ +0.000) |
| Ridge alpha=0.1 | +0.287 (Δ +0.000) |
| Ridge alpha=1.0 | +0.290 (Δ +0.003) |
| Ridge alpha=10.0 | +0.279 (Δ -0.008) 🔴 |
| Lasso alpha=0.01 | +0.316 (Δ +0.029) 🟢 |
| ElasticNet a=0.01 | +0.309 (Δ +0.022) 🟢 |
| RandomForest | +0.133 (Δ -0.154) 🔴 |
| GradientBoosting | -0.024 (Δ -0.311) 🔴 |

## Improved-struggle (n=1306, 3 features, 5-fold GroupKFold by session)

| Model | Mean ρ | Std | Δ vs OLS |
|---|---|---|---|
| OLS (baseline) **★** | +0.168 | 0.132 | +0.000 |
| Ridge alpha=0.1 | +0.168 | 0.132 | +0.000 |
| Ridge alpha=1.0 | +0.168 | 0.132 | +0.000 |
| Ridge alpha=10.0 | +0.168 | 0.132 | -0.000 |
| Lasso alpha=0.01 | +0.168 | 0.131 | +0.000 |
| ElasticNet a=0.01 | +0.168 | 0.131 | -0.000 |
| RandomForest | +0.202 | 0.116 | +0.034 🟢 |
| GradientBoosting | +0.164 | 0.102 | -0.004 |

## Verdict heuristic

- **🟢** = improves ρ by > +0.005 vs the OLS baseline (i.e. measurably better)
- **🔴** = degrades ρ by > 0.005 vs OLS (worse)
- **★** = the current canonical v2 baseline (`scripts/optimise_v2_weights.py`)
- No marker = within ±0.005 of OLS (effectively tied)

Trade-off reminder for the non-linear models (RandomForest, GradientBoosting): better Spearman ρ here does NOT mean we should swap to them as the v2 model. They produce no per-feature signed weights, so the §5.4 v1↔v2 weight-comparison story cannot apply to them. Use them as a CEILING REFERENCE only — "the best non-linear model achieves X; OLS gets Y; we're within Z of the achievable ceiling".
