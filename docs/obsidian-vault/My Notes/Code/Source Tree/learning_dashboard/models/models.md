# models/

**Path:** `code/learning_dashboard/models/`
**Parent:** [[learning_dashboard]]

> Advanced and alternative scoring models. All four are optional — enabled by `improved_models_enabled` in Settings, with per-model sub-toggles. They never replace the baseline models in [[analytics]]; they run in parallel and feed the Comparison view.

## Contents

| File | Summary |
|------|---------|
| [[measurement]] | Attaches a confidence score (`0-1`) to each AI-estimated incorrectness value. |
| [[irt]] | 1-PL (Rasch) Item Response Theory — data-driven question difficulty by joint MLE. |
| [[bkt]] | Bayesian Knowledge Tracing — HMM per-question mastery from chronological replays. |
| [[improved_struggle]] | Difficulty-adjusted struggle: behavioural + mastery gap + difficulty adjustment. |

## Purpose

Each model addresses a weakness of the baseline:

- **Measurement confidence** exposes uncertainty in the LLM-scored incorrectness.
- **IRT** produces difficulty values driven by the actual response matrix, not fixed weights.
- **BKT** moves from point-in-time incorrectness to a per-student mastery estimate that evolves over attempts.
- **Improved struggle** combines the behavioural composite with mastery gap and a penalty for failing *easy* questions.

All four are headless (no Streamlit imports) and gracefully degrade when dependencies (e.g., IRT/BKT outputs) are missing — weights are redistributed rather than raising.

## Related notes

- [[BKT Mastery Logic]] · [[IRT Difficulty Logic]] · [[Improved Struggle Logic]] (thematic)
- [[Formulae and Equations]] · [[Algorithms]]
- [[Improved Model Pipeline (IRT + BKT + Improved Struggle)]] (hyperedge)
