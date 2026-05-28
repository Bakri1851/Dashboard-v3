---
type: training-reference
covers: v2 OLS weight training for struggle-baseline + improved-struggle
parent: "[[00 Overview]]"
sibling-of: "[[Difficulty Model Training]]"
sibling-of-2: "[[Classifier Training]]"
created: 2026-05-27
---

# Struggle Model Training

Two distinct models share the "struggle" namespace, both trained under the same CV regime:

1. **Baseline composite** — weighted sum of 7 behavioural signals. The deployed default.
2. **Improved (BKT + IRT blend)** — weighted sum of 3 derived components (behavioural composite, mastery gap, difficulty-adjusted exposure). Available via the `struggle_model: baseline | improved` toggle in Settings.

Both are trained against the same target (4-band LLM rating, integer 0–3) using the same OLS regression machinery; the difference is the input feature set.

## §1 Baseline composite — 7 signals

### Features

| Signal | What it measures |
|---|---|
| `n_hat` | Normalised submission count |
| `t_hat` | Normalised time-active |
| `i_norm` | Mean incorrectness (LLM-judged or 0.5 fallback) |
| `r_norm` | Recent-incorrectness EWMA |
| `A_norm` | Normalised attempt-gap distribution |
| `d_hat` | IRT-derived difficulty-adjusted exposure |
| `rep_norm` | Repeat-rate per question |

Features are normalised to [0, 1] at extraction time (see `code2/backend/analytics.py`). The OLS weights are then signed coefficients applied to the normalised features; the output is interpreted as a band-index prediction in approximately [0, 3].

### Target

`STRUGGLE_BAND_INDEX = {"On Track": 0, "Minor Issues": 1, "Struggling": 2, "Needs Help": 3}` — integer 0–3 cast to float for OLS.

LLM labels from `data/eval/llm_struggle_labels.json` (gpt-4o rater, upgraded from gpt-4o-mini 2026-05-26).

### Cross-validation

- **Scheme**: `GroupKFold(5)` grouped by `session_id` — prevents same-session snapshots leaking across folds.
- **n_samples**: 1306 matched snapshots (snapshots with both `v1_features` and an LLM band label).
- **Optimisation**: `sklearn.LinearRegression` (plain OLS, no regularisation, no inner CV). Per fold: `StandardScaler` fit on train → fit OLS → predict on held-out.

The model-class bake-off (`scripts/experiments/model_class_bakeoff.py`, see `data/eval/experiments/DECISION.md`) confirmed OLS is the right choice — Ridge / Lasso / ElasticNet all sit within ±0.003 ρ of OLS, RandomForest gives +0.010 ρ at the cost of losing per-feature signed weights, and the interpretable weights are load-bearing for the §5.4.9 narrative.

### Results — under gpt-4o labels

| Metric | Value (CV pooled) |
|---|---|
| Spearman ρ | **+0.588** [+0.490, +0.686] |
| Linear-weighted Cohen's κ | +0.483 (with constrained-trained thresholds; +0.380 with natural-rounding) |
| MAE | ~0.74 band units |
| Per-fold ρ std | < 0.05 across all 5 folds |

The v2 baseline ρ = +0.471 for reference (same CV scheme, hand-set weights). Δρ = +0.117 from training.

### v1 vs v2 weights — sign-flip diagnostic

Two features sign-flip between v1 and v2 (negative weight under trained → positive under hand-set or vice-versa). The §5.4.9 prose discusses which features lose their hand-set sign and why; lift the canonical values from `data/eval/optimised_struggle_weights_v2.json` rather than memoising them here.

## §2 Improved (BKT + IRT) — 3 components

### Components

| Component | What it measures |
|---|---|
| `behavioural_composite` | The 7-signal baseline composite output (recursive use) |
| `mastery_gap` | `1 − BKT(student, module)` — Bayesian Knowledge Tracing inferred unmastery |
| `difficulty_adjusted_score` | IRT-2PL response-pattern adjusted exposure score |

The improved model blends these three into a single struggle score via OLS-trained weights `(w_B, w_M, w_D)`.

### Training

Same CV regime (`GroupKFold(5)` by `session_id`), same target (4-band integer 0–3), same OLS optimiser. Only the input feature dimensionality differs (3 vs 7).

### Results — under gpt-4o labels

| Metric | Value (CV pooled) |
|---|---|
| Spearman ρ | **+0.201** [+0.047, +0.356] |
| Linear-weighted Cohen's κ | +0.134 (with trained thresholds; +0.105 with hand-set) |

The v1 improved baseline ρ ≈ +0.168 (same CV, hand-set weights — `w_B=0.45, w_M=0.30, w_D=0.25`). Δρ = +0.033 from training.

### Substantive finding: negative w_M and w_D

The trained weights assign **negative** coefficients to `w_M` (mastery-gap) and `w_D` (difficulty-adjusted score). This means: under the trained model, students with HIGHER mastery-gap and HIGHER difficulty-adjusted exposure score LOWER on struggle — the opposite of the v1 hand-set assumption.

This is interpretable: the LLM rater appears to treat BKT-inferred unmastery and IRT-adjusted exposure as orthogonal-to-or-anti-correlated-with the immediate behavioural-signal evidence of struggle. The trained model effectively says "the behavioural composite is what matters; BKT and IRT components add noise". Consistent with the model-class bake-off finding that RandomForest only beats OLS by +0.05 ρ here — the underlying signal is just weak, regardless of model family.

§5.4.9 in the report frames this as a negative finding for the improved-struggle hypothesis.

### Caveat — improved-struggle is weaker than baseline

Under matched CV, baseline-composite struggle (ρ = +0.588) outperforms improved-struggle (ρ = +0.201) by a wide margin. The improved model is retained in the dashboard as a toggle for transparency and reproducibility of the §5.4.9 finding, but instructors who want best rank quality should leave the struggle model toggle on `baseline`.

## §3 Canonical artefacts

| Path | Contents |
|---|---|
| `data/eval/optimised_struggle_weights_v2.json` | Baseline OLS weights, per-fold std, ρ/κ/MAE |
| `data/eval/optimised_improved_weights_v2.json` | Improved-blend OLS weights, per-fold std, ρ/κ/MAE |
| `data/eval/snapshots.json` (`struggle_snapshots`) | Per-snapshot features + LLM bands + v1 + improved component scores |
| `data/eval/pooled_predictions_v2.json` | Per-snapshot pooled v1 + v2 predictions (used by the rank-shift + score-delta cells in `eval_main.ipynb`) |
| `data/eval/figures/weights_struggle_v1_vs_v2.png` | Headline weight comparison bar chart |
| `data/eval/figures/per_fold_rho_struggle.png` | Per-fold ρ stability for the baseline composite |
| `data/eval/figures/weight_heatmap_struggle.png` | Per-fold weight stability heatmap |

## §4 Scripts

- `scripts/optimise_v2_weights.py --kind struggle` — re-fits baseline composite
- `scripts/optimise_v2_weights.py --kind improved` — re-fits improved blend
- `scripts/experiments/model_class_bakeoff.py` — 8-model-class comparison (run once; decision in `data/eval/experiments/DECISION.md`)

Both `scripts/optimise_v2_weights.py` invocations write to `data/eval/optimised_*_weights_v2.json` in place. Re-running is idempotent; safe to run after a relabel.

## §5 Cross-references

- [[Difficulty Model Training]] — sibling for difficulty
- [[Classifier Training]] — covers the band-threshold mapping applied AFTER the OLS score
- `[[v2 Relabel Handoff]]` — covers the gpt-4o label upgrade that lifted ρ from +0.573 to +0.588
- `[[v2 Target-Swap Handoff]]` — covers the swap from binary intervene to 4-band target that necessitated the OLS training in the first place
