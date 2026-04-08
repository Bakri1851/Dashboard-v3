---
tags: [lab-app, evaluation, placeholder, meeting3]
date: 2026-04-08
status: 🔲 Placeholder — not yet implemented
source: FYP Meeting 3 — Dr. Batmaz
---

# Evaluation Strategy

> ⚠️ **Placeholder** — Not yet written or implemented.
> Recorded from Meeting 3 (2026-04-08) for planning purposes only.

## Dr. Batmaz's Requirement

The struggle detection model needs a mathematically justifiable evaluation before submission.

## Option A — Human Evaluation (not preferred)

Ask observers if struggling students were correctly identified. Subjective.

## Option B — Model Comparison (preferred, not yet done)

Define "who needs most attention" mathematically. Compare parametric model vs at least
one alternative. No human subjects — fully mathematical.

## Current Model (implemented, not yet formally evaluated)

## Candidate Alternatives (not yet selected)

- Threshold-based rule model (simple baseline)
- Collaborative filtering (approved by Dr. Batmaz)
- BKT / IRT if implemented

## Future Work — Weight Optimisation

> 💡 Currently α, β, γ, δ, η are set by trial and error due to absence of labeled ground truth.
> Once labeled data is available, weights could be trained using supervised ML rather than
> manual tuning:
> - Logistic regression over validated struggle labels
> - Gradient boosting (XGBoost / sklearn)
> - Optuna hyperparameter search over the weight space
> The absence of labeled data must be stated explicitly as a limitation in the report.

## Planned Actions (none started)

- [ ] Select alternative model to compare against
- [ ] Define evaluation criterion mathematically
- [ ] Draft Ch5 evaluation section
- [ ] Add future work paragraph on ML weight optimisation
- [ ] State labeled data absence as explicit limitation in Ch5
