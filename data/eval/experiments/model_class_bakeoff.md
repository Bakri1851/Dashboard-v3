# Model-class bake-off results

_Ran at 2026-05-26T22:27:29.370858+00:00_

Side experiment to test whether OLS (current v2 baseline) is the best regression model class against the 4-band target, or whether regularised linear / non-linear alternatives give meaningfully better Spearman ρ. NO canonical artefacts modified.

All metrics: Spearman ρ against the LLM 4-band rating, using identical CV splits to `scripts/optimise_v2_weights.py`. Higher is better.

## Struggle (n=1306, 7 features, 5-fold GroupKFold by session)

| Model | Mean ρ | Std | Δ vs OLS |
|---|---|---|---|
| OLS (baseline) **★** | +0.588 | 0.079 | +0.000 |
| Ridge alpha=0.1 | +0.588 | 0.079 | +0.000 |
| Ridge alpha=1.0 | +0.588 | 0.079 | +0.000 |
| Ridge alpha=10.0 | +0.589 | 0.079 | +0.000 |
| Lasso alpha=0.01 | +0.586 | 0.080 | -0.003 |
| ElasticNet a=0.01 | +0.587 | 0.080 | -0.001 |
| RandomForest | +0.565 | 0.080 | -0.023 🔴 |
| GradientBoosting | +0.552 | 0.102 | -0.036 🔴 |

## Difficulty (n=72, 5 features, LOO — pooled ρ)

| Model | Pooled ρ |
|---|---|
| OLS (baseline) **★** | +0.468 (Δ +0.000) |
| Ridge alpha=0.1 | +0.468 (Δ +0.000) |
| Ridge alpha=1.0 | +0.470 (Δ +0.001) |
| Ridge alpha=10.0 | +0.471 (Δ +0.003) |
| Lasso alpha=0.01 | +0.456 (Δ -0.013) 🔴 |
| ElasticNet a=0.01 | +0.466 (Δ -0.003) |
| RandomForest | +0.479 (Δ +0.010) 🟢 |
| GradientBoosting | +0.436 (Δ -0.032) 🔴 |

## Improved-struggle (n=1306, 3 features, 5-fold GroupKFold by session)

| Model | Mean ρ | Std | Δ vs OLS |
|---|---|---|---|
| OLS (baseline) **★** | +0.201 | 0.124 | +0.000 |
| Ridge alpha=0.1 | +0.201 | 0.124 | +0.000 |
| Ridge alpha=1.0 | +0.201 | 0.124 | -0.000 |
| Ridge alpha=10.0 | +0.201 | 0.124 | -0.000 |
| Lasso alpha=0.01 | +0.197 | 0.120 | -0.004 |
| ElasticNet a=0.01 | +0.200 | 0.121 | -0.002 |
| RandomForest | +0.250 | 0.136 | +0.048 🟢 |
| GradientBoosting | +0.221 | 0.111 | +0.020 🟢 |

## Verdict heuristic

- **🟢** = improves ρ by > +0.005 vs the OLS baseline (i.e. measurably better)
- **🔴** = degrades ρ by > 0.005 vs OLS (worse)
- **★** = the current canonical v2 baseline (`scripts/optimise_v2_weights.py`)
- No marker = within ±0.005 of OLS (effectively tied)

Trade-off reminder for the non-linear models (RandomForest, GradientBoosting): better Spearman ρ here does NOT mean we should swap to them as the v2 model. They produce no per-feature signed weights, so the §5.4 v1↔v2 weight-comparison story cannot apply to them. Use them as a CEILING REFERENCE only — "the best non-linear model achieves X; OLS gets Y; we're within Z of the achievable ceiling".
