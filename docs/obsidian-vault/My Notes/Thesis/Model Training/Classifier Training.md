---
type: training-reference
covers: band-threshold (score → label classifier) training across all 6 model sets
parent: "[[00 Overview]]"
sibling-of: "[[Struggle Model Training]]"
sibling-of-2: "[[Difficulty Model Training]]"
created: 2026-05-27
---

# Classifier Training — band thresholds

The score-to-band mapping is a separate trainable component from the scoring models themselves. Each dashboard model produces a continuous score; three cutpoints `(c1, c2, c3)` then map that score to one of four ordinal band labels. The cutpoints in `code2/backend/config.py` (`STRUGGLE_THRESHOLDS`, `DIFFICULTY_THRESHOLDS`) were originally hand-set on round-number boundaries for instructor interpretability; this note covers their empirical replacement via κ-maximising grid search.

The classifier training affects **band labels only** — ranking is unchanged because thresholds don't affect score order. The improvement is in classification accuracy against the LLM rater, not in leaderboard ordering.

## §1 Six (model × score-space) combinations trained

The dashboard exposes six distinct (model × score-space) combinations through the various weight-version and model toggles. Each has its own score distribution and thus deserves its own threshold set:

| # | Model | Score domain |
|---|---|---|
| 1 | Struggle baseline composite (v1 or v2 weights) | [0, 1] |
| 2 | Struggle improved (BKT+IRT blend) | [0, 1] |
| 3 | Struggle v2 OLS (raw band-index prediction) | [0, 3] |
| 4 | Difficulty baseline composite | [0, 1] |
| 5 | Difficulty IRT Rasch (min-max scaled b_raw) | [0, 1] |
| 6 | Difficulty v2 OLS (raw band-index prediction) | [0, 3] |

## §2 Methodology

### Objective — linear-weighted Cohen's κ

For each candidate cutpoint triple `(c1, c2, c3)`, predicted bands `ŷ_i = band(score_i)` are compared to LLM ground-truth bands `y_i` via:

```
κ = 1 − Σ_{ij} W[i,j] · O[i,j] / Σ_{ij} W[i,j] · E[i,j]
W[i,j] = |i − j|                              ← linear weighting
O[i,j] = observed confusion-matrix count (truth=i, pred=j)
E[i,j] = expected count under independence = row_i · col_j / n
```

Implemented manually as `fast_kappa()` in the search scripts to avoid sklearn dispatch overhead during fold-level grid search (300K+ calls per training run; the manual version is ~50× faster and runs successfully under Windows memory pressure where sklearn's lazy DLL loads would otherwise fail).

### Search algorithm — two-stage brute force

For each candidate cutpoint triple in an ordered Cartesian grid `c1 < c2 < c3`:

1. **Coarse pass**: grid step 0.025 over [0, 1] for normalised scores, step 0.05 over [0, 3] for v2 OLS band-index outputs. ~10 K valid combinations per pass.
2. **Fine refinement**: grid step = coarse / 5, restricted to a ±1.5× window around the coarse argmax.

No regularisation, no order penalty beyond the strict `c1 < c2 < c3` ordering — the constraint is enforced as a skip-filter, not a Lagrangian penalty.

### Cross-validation — matched to each model's training scheme

- **Struggle models** (n=1306): `GroupKFold(5)` by `session_id`. Same scheme as `scripts/optimise_v2_weights.py` for struggle.
- **Difficulty models** (n=72): `LeaveOneOut`. Same scheme as `scripts/optimise_v2_weights.py` for difficulty.

Trained cutpoints fit on each fold's training set, applied to the held-out fold, predictions pooled across all folds for the final κ.

### Constraints — applied per fold (constrained variant only)

Two guardrails added to prevent cohort-overfit degeneracies:

- **`c1 ≥ train-fold P5`**: lowest cutpoint at or above the 5th percentile of the training-fold score distribution. Forces the lowest band to capture roughly ≥5% of the population.
- **`(c2 − c1) ≥ min_width`** AND **`(c3 − c2) ≥ min_width`** AND **`(score_max − c3) ≥ min_width`**: every band wider than 10% of score range (0.10 in [0,1], 0.30 in [0,3]).

The constrained variant trades raw κ (typically loses 10–50% of the unconstrained gain) for deployment-defensibility — cutpoints that survive a new cohort rather than fitting this cohort's specific class imbalance.

## §3 Headline results — all 6 sets

| Model | Hand-set κ | Unconstrained CV κ | **Constrained CV κ (ship)** | Constrained Δ |
|---|---|---|---|---|
| Struggle baseline composite | +0.303 | +0.402 | **+0.390** | **+0.087** ✓ ship |
| Struggle improved (BKT+IRT) | +0.105 | +0.134 | +0.103 | −0.002 ✗ retain hand-set |
| Struggle v2 OLS [0,3] | +0.380 | +0.483 | **+0.456** | **+0.076** ✓ ship |
| Difficulty baseline composite | +0.065 | +0.465 | **+0.239** | **+0.175** ✓ ship |
| Difficulty IRT Rasch (scaled) | −0.016 | −0.069 | −0.024 | −0.007 ✗ retain hand-set |
| Difficulty v2 OLS [0,3] | +0.225 | +0.436 | **+0.393** | **+0.168** ✓ ship |

**Production cutpoints shipped (constrained CV, mean across folds)**:

```python
STRUGGLE_THRESHOLDS = (0.000, 0.315, 0.505, 0.605, 1.000)  # On Track / Minor Issues / Struggling / Needs Help
DIFFICULTY_THRESHOLDS = (0.000, 0.363, 0.463, 0.588, 1.000)  # Easy / Medium / Hard / Very Hard
# v2 OLS band-index rounding cutpoints (used in confusion-matrix evaluation):
#   struggle:   c1=1.22, c2=1.78, c3=2.09
#   difficulty: c1=1.88, c2=2.19, c3=2.69
```

Per-fold std on every shipped cutpoint is ≤ 0.03 — the optima are essentially deterministic across folds, not noise.

## §4 The IRT-difficulty anti-result

The IRT Rasch 1PL model produced **negative** κ against the LLM rater both at hand-set thresholds (−0.016) and at constrained CV-trained cutpoints (−0.024). The constrained search reduced the unconstrained overfitting damage (−0.069 → −0.024) but the absolute κ remains negative.

The interpretation is not "the IRT model is broken" — it is "the IRT model is measuring a different latent quantity than the LLM rater is judging". IRT fits **item-response-pattern difficulty** (probability a student of given ability gets the question right); the LLM rates **pedagogical difficulty** (curricular position, prerequisite load, cognitive demand). The two are conceptually distinct and empirically uncorrelated on this cohort (Spearman ρ = +0.345, top-10-hardest overlap = 1/10).

Threshold training cannot rescue a model–rater mismatch — only ratter-anchoring or model-target re-alignment would. The IRT toggle is retained in the dashboard for transparency; the baseline composite is the recommended production default for difficulty ranking on this cohort.

§5.6.x in the report frames this as a substantive limitation, not a failure.

## §5 The improved-struggle marginal result

The improved-struggle model (BKT + IRT blend) saw a constrained gain of −0.002 — indistinguishable from noise. The underlying model's absolute κ stays around +0.10 to +0.13 regardless of threshold choice. The signal is weak enough that no threshold scheme rescues it.

Decision: retain hand-set thresholds for improved-struggle. No code change needed for this model.

The §5.4.9 report narrative already covers the improved-struggle weakness (negative `w_M` and `w_D`, weaker than baseline by a wide margin). The threshold-training non-result simply confirms it.

## §6 The cohort-empty-band phenomenon

In the unconstrained CV search, three of the four winning sets place `c1 = 0` — collapsing the lowest band ("On Track" or "Easy") to empty. This is the κ-maximising response to a cohort where the lowest band is sparsely or never labelled:

- Difficulty cohort: 0 Easy-labelled questions out of 72
- Struggle cohort: 76 On-Track snapshots out of 1306 (5.8%)

The κ-optimiser correctly recognises that predicting "Easy" or "On Track" is never the right answer often enough to help κ, and pushes `c1` to zero.

The **constrained** search prevents this with the `c1 ≥ train-fold P5` floor, producing properly populated 4-band cutpoint sets. The constrained gain is smaller (e.g. difficulty baseline +0.175 vs unconstrained +0.400) but the cutpoints are deployment-defensible: a future cohort with even one Easy question won't break the scheme.

Both variants are reported in §5.4.11 for transparency.

## §7 Decision — default-only promotion

Trained thresholds are **promoted to production defaults** (no Settings UI toggle). Rationale:

1. The Model Comparison dashboard view was removed this same session for being "evaluation, not production". Adding a threshold-comparison toggle would repeat the same anti-pattern.
2. Thresholds are a downstream label-display calibration, not a modelling choice — flipping them doesn't represent a different *modelling decision* the way flipping weights or hyperparams does.
3. Rollback path is `git revert` on the config commit + a notebook rerun — same friction as any other backend default change.

The implementation pass is covered by `[[v2 Threshold Promotion Handoff]]`.

## §8 What CHANGES vs DOESN'T after promotion

### Doesn't change (no regeneration needed)
- All Spearman ρ values (ranking unchanged)
- All weight tables + weight-comparison bar charts
- OLS residuals, per-fold ρ stability, weight-stability heatmap
- Predicted-vs-observed scatter (continuous predictions + LLM band integer)
- Score-delta + rank-shift histograms (score-based, no thresholds)
- IRT discrimination, incorrectness distribution
- Optuna hyperparam plots, κ inter-rater (label-only)
- Baseline-vs-alternative comparison scatter plots
- Top-10 leaderboard ORDERING (band-label columns will refresh, but the sort order is unchanged)

### Does change (regenerate from notebook re-run)
- `data/eval/figures/confusion_bands.png` — directly threshold-dependent
- `data/eval/figures/model_disagreement.png` — derived from band classification
- `data/eval/figures/cohort_distributions.png` — if it re-bins under new thresholds
- Band-label columns in `comparison_struggle_top10.png` / `comparison_difficulty_top10.png` + the pairs CSVs
- A few narrative numbers in `data/eval/results.md` (exact-band agreement %, model-disagreement counts)

## §9 Canonical artefacts

| Path | Contents |
|---|---|
| `data/eval/experiments/threshold_search_cv.json` | All 12 entries (6 unconstrained + 6 constrained) — full per-fold cutpoints + κ |
| `scripts/experiments/threshold_search_constrained.py` | The script that generated the shipped values |
| `scripts/experiments/threshold_search_cv.py` | Unconstrained reference variant |
| `scripts/experiments/threshold_search.py` | Original in-sample (overfit) variant — kept for the overfitting diagnostic |
| `scripts/experiments/threshold_search_per_model.py` | Intermediate variant that added the improved-struggle and IRT-difficulty cases |

All four scripts are delete-safe in `scripts/experiments/`; the canonical values land in `code2/backend/config.py` after promotion.

## §10 Cross-references

- [[Struggle Model Training]] — the upstream weight training for the 3 struggle models
- [[Difficulty Model Training]] — the upstream weight training for the 1 difficulty model + the IRT alternative
- [[00 Overview]] — index + the three-component model-training arc
- `[[v2 Threshold Promotion Handoff]]` — the implementation handoff for the shipping pass
- `[[v2 Threshold Training Handoff]]` — the writing-chat brief for §5.4.11 + §5.6.x prose
