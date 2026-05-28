---
type: training-reference
covers: v2 OLS weight training for difficulty-baseline + IRT alternative
parent: "[[00 Overview]]"
sibling-of: "[[Struggle Model Training]]"
sibling-of-2: "[[Classifier Training]]"
created: 2026-05-27
---

# Difficulty Model Training

One trained model + one alternative considered:

1. **Baseline composite** — weighted sum of 5 question-level signals. The deployed default.
2. **IRT Rasch 1PL alternative** — fit on the full deployed submission stream (`data/eval/submissions.parquet`); NOT trained against the LLM rater. Toggle-available in Settings.

The training programme covers only the baseline composite. The IRT model has its own internal fit (maximum-likelihood on response patterns) and is included in the dashboard as a reference alternative; its alignment with the LLM rater is evaluated in [[Classifier Training]] and surfaces a substantive anti-result (see §3 below).

## §1 Baseline composite — 5 signals

### Features

| Signal | What it measures |
|---|---|
| `c_norm` | Cohort-normalised incorrectness rate per question |
| `t_tilde` | Median-normalised time-to-correct |
| `a_tilde` | Normalised attempt count per question |
| `f_norm` | Cohort-normalised final-incorrectness rate |
| `p_norm` | Normalised plateau-flag rate (repeated wrong attempts) |

All normalised at extraction time (see `code2/backend/analytics.py`). The OLS weights are signed coefficients applied to the normalised features.

### Target

`DIFFICULTY_BAND_INDEX = {"Easy": 0, "Medium": 1, "Hard": 2, "Very Hard": 3}` — integer 0–3 cast to float for OLS.

LLM labels from `data/eval/llm_difficulty_labels.json` (gpt-4o rater, upgraded from gpt-4o-mini 2026-05-26).

### Cross-validation

- **Scheme**: `LeaveOneOut` — required by the small sample size; no useful grouping available.
- **n_samples**: 72 matched questions (questions with both `v1_features` and an LLM band label).
- **Optimisation**: `sklearn.LinearRegression` (plain OLS, no regularisation). Per fold: `StandardScaler` fit on the 71 train samples → fit OLS → predict on the held-out 1.

The model-class bake-off (`scripts/experiments/model_class_bakeoff.py`) tested Lasso (α=0.01), Ridge (α∈{0.1, 1, 10}), ElasticNet, RandomForest, GradientBoosting. Most interesting finding: **Lasso α=0.01** gives +0.029 ρ over OLS on this n=72 / 5-feature setting (regularisation has measurable purchase at small N + small feature space). RandomForest gives +0.010 ρ (within noise). GradientBoosting catastrophically overfits (Δρ = −0.024, literally worse than the OLS baseline).

OLS was retained for **consistency** with the struggle model class — switching difficulty alone to Lasso would make the §5.1.5 methodology preamble harder to defend ("we used OLS everywhere except difficulty, because..."). The +0.029 ρ gain doesn't change the headline narrative either way; difficulty's absolute ρ is modest under any model.

### Results — under gpt-4o labels

| Metric | Value (CV pooled) |
|---|---|
| Spearman ρ | **+0.468** (LOO pooled) |
| Linear-weighted Cohen's κ | +0.436 (with constrained-trained thresholds; +0.225 with natural-rounding) |
| MAE | ~0.50 band units |

Under gpt-4o-mini labels (pre-relabel) the same training produced ρ = +0.287. The +0.181 ρ gain from the rater upgrade alone is the largest single-source improvement in the v2 pipeline — see `[[v2 Relabel Handoff]]` for the relabel-pass methodology and findings.

The v1 difficulty baseline ρ is near-flat (close to zero); the v2 +0.468 is a substantial improvement, but the absolute value is still "moderate positive correlation" rather than "strong" by Landis–Koch convention. The N=72 sample size and the heavily skewed cohort (72% Very Hard) both constrain the achievable ceiling.

### Per-fold weight stability

LOO produces 72 per-fold weight vectors. The per-fold std is small (typically < 0.05 per weight component), confirming the small-N fit isn't producing wildly different weights per held-out question. The trained weight vector is essentially deterministic for this cohort.

## §2 Cohort skew — the dominant caveat

The 72-question difficulty cohort has the following LLM band distribution:

```
Easy      (band 0):   0 questions
Medium    (band 1):   3 questions  (4.2%)
Hard      (band 2):  17 questions  (23.6%)
Very Hard (band 3):  52 questions  (72.2%)
```

The cohort is dominated by Very-Hard questions; Easy is empty. This has two methodological consequences:

1. **Constrained absolute ρ ceiling**: with 72% of the cohort in one band, there's limited room for rank discrimination. The +0.468 ρ is close to the achievable ceiling on this cohort, not a sign that the OLS model is undertrained.

2. **Hand-set thresholds were wrong**: the hand-set DIFFICULTY_THRESHOLDS = (0.35, 0.5, 0.75) were designed for a balanced 4-band cohort that doesn't exist in this deployment. CV-trained thresholds for the difficulty baseline composite drop the Hard/Very-Hard boundary from 0.75 to ~0.59, recovering substantial κ. See [[Classifier Training]] §2.

Cohort-balanced re-evaluation (a follow-up semester with more uniformly-distributed difficulty) is flagged as Ch6 future work.

## §3 The IRT-difficulty alternative — substantive anti-result

The dashboard supports a `difficulty_model: irt` toggle that switches the difficulty source from the OLS-trained composite to the IRT-Rasch 1PL `b_raw` parameter (min-max scaled to [0, 1] for threshold mapping).

The IRT model is **NOT** trained against the LLM rater — it has its own internal MLE fit on response patterns. The κ evaluation against the LLM bands (covered in [[Classifier Training]] §3) surfaces a clean anti-result:

- Hand-set thresholds: κ = −0.016
- Constrained CV-trained thresholds: κ = −0.024
- Spearman ρ(IRT, baseline composite) = +0.345
- Top-10-hardest overlap = 1/10

The IRT model is fitting **item-response-pattern difficulty** (probability a student of given ability gets the question right) rather than the **pedagogical difficulty** the LLM rater judges (curricular position, prerequisite load, cognitive demand). The two are conceptually distinct and empirically uncorrelated on this cohort.

§5.6.x in the report frames this as a model–rater mismatch limitation, not a failure of either the IRT model or the LLM rater individually.

## §4 Canonical artefacts

| Path | Contents |
|---|---|
| `data/eval/optimised_difficulty_weights_v2.json` | OLS weights, per-fold std, ρ/κ/MAE, pooled predictions + pooled_y |
| `data/eval/snapshots.json` (`difficulty_questions`) | Per-question features + LLM band + v1 difficulty score |
| `data/eval/comparison_difficulty_pairs.csv` | Per-question baseline-vs-IRT pairs (written by `model_comparison.ipynb`) |
| `data/eval/figures/negative_findings.png` | Side-by-side v1 vs v2 weight bar charts for difficulty + improved-struggle |
| `data/eval/figures/comparison_difficulty_scatter.png` | Baseline vs IRT scatter (continuous scores, coloured by LLM band) |
| `data/eval/figures/comparison_difficulty_top10.png` | Top-10 hardest leaderboards side-by-side |

## §5 Scripts

- `scripts/optimise_v2_weights.py --kind difficulty` — re-fits the baseline composite (LOO over 72 questions, ~30 s wall-clock)
- `scripts/experiments/model_class_bakeoff.py` — 8-model-class comparison (run once; decision in `data/eval/experiments/DECISION.md`)
- `notebooks/model_comparison.ipynb` — generates the baseline-vs-IRT comparison artefacts; reruns the full IRT 2PL fit on `submissions.parquet`

## §6 Cross-references

- [[Struggle Model Training]] — sibling for struggle
- [[Classifier Training]] — covers the band-threshold mapping; surfaces the IRT anti-result in §3
- `[[v2 Relabel Handoff]]` — covers the gpt-4o label upgrade that lifted difficulty ρ from +0.287 to +0.468 (the single largest pipeline improvement)
- `[[v2 Target-Swap Handoff]]` — covers the swap from binary intervene to 4-band target
