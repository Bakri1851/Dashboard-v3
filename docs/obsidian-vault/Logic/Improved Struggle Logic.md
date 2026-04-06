# Improved Struggle Logic

The improved struggle model (Phase 4) combines behavioral signals with BKT mastery and IRT difficulty to produce a richer struggle estimate. It runs alongside the baseline struggle model and does not replace it.

Related: [[Student Struggle Logic]], [[BKT Mastery Logic]], [[IRT Difficulty Logic]], [[Analytics Engine]], [[Next Steps]]

## Relationship to baseline

The baseline model in `analytics.py` uses seven weighted behavioral signals to produce a struggle score. The improved model reduces the behavioral component to four signals and adds two new signal groups: mastery gap (from BKT) and difficulty-adjusted incorrectness (from IRT). This addresses the known issue where using `1 - mean_mastery` alone caused scores to cluster near 1.0, because mastery is now one signal rather than the sole metric.

## Three signal groups

### 1. Behavioral composite (weight 0.45)

Four sub-signals, equally weighted:
- `A_raw`: recent incorrectness with exponential time decay (reuses `analytics.compute_recent_incorrectness()`)
- `r_hat`: retry rate (fraction of repeated question attempts)
- `d_hat`: min-max normalized improvement trajectory slope (reuses `analytics._compute_slope()`)
- `rep_hat`: exact-answer repetition rate

`behavioral = (A_raw + r_hat + d_hat + rep_hat) / 4`

### 2. Mastery gap (weight 0.30)

Compares BKT-estimated mastery with current-session performance:

```
recent_performance = 1 - A_raw
mastery_gap = max(0, mean_mastery - recent_performance)
```

A large positive gap means the student is performing below their demonstrated ability — a strong struggle signal. A negative gap (performing above mastery) is clamped to zero because that is not a struggle indicator.

This metric has naturally higher variance than raw mastery because it depends on the difference between two independent signals: longitudinal mastery (BKT) and current-session behavior (recent incorrectness).

### 3. Difficulty-adjusted (weight 0.25)

Weights incorrectness by how easy the question is:

```
difficulty_adjusted = mean(incorrectness_i * (1 - normalized_irt_difficulty_i))
```

Computed over the student's last `RECENT_SUBMISSION_COUNT` submissions. Failing easy questions (low IRT difficulty) produces a higher score than failing hard questions. Questions without IRT data use a neutral difficulty of 0.5.

## Graceful degradation

If BKT mastery is unavailable (too few submissions or feature disabled), the mastery gap weight (0.30) is redistributed to the behavioral composite. If IRT difficulty is unavailable, the difficulty-adjusted weight (0.25) is redistributed similarly. At the extreme, the model collapses to a behavioral-only model with weight 1.0.

## Final assembly

```
struggle_score = w_beh * behavioral + w_mg * mastery_gap + w_da * difficulty_adjusted
```

Bayesian shrinkage is applied: `w_n = n / (n + SHRINKAGE_K)`, pulling low-submission students toward the class mean. Scores are clipped to [0, 1] and classified using the standard `STRUGGLE_THRESHOLDS`.

## Output

Compatible with the baseline `struggle_df` schema:

| Column | Type | Description |
|---|---|---|
| `user` | str | Student identifier |
| `struggle_score` | float | Weighted composite score [0, 1] |
| `struggle_level` | str | On Track / Minor Issues / Struggling / Needs Help |
| `struggle_color` | str | Hex color for the level |
| `behavioral_composite` | float | Behavioral sub-score [0, 1] |
| `mastery_gap` | float | BKT mastery gap [0, 1] |
| `difficulty_adjusted_score` | float | IRT-adjusted score [0, 1] |

## Settings integration

Computed behind `improved_models_enabled` in session state (toggled in Settings). When enabled, results are cached in `st.session_state["_improved_struggle_df"]`.

The active struggle model is selected via the **Student Struggle Model** selectbox in Settings ("Baseline" or "Improved"). When "Improved" is selected, the In Class View automatically uses `_improved_struggle_df` for the student leaderboard. Similarly, the **Question Difficulty Model** selectbox ("Baseline" or "IRT") controls the question leaderboard. There is no separate toggle on the dashboard itself — model selection is centralized in Settings.

## Code references

- `learning_dashboard/models/improved_struggle.py`: `compute_improved_struggle_scores()`
- `learning_dashboard/config.py`: `IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL`, `IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP`, `IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ`
- `learning_dashboard/instructor_app.py`: feature-flag integration (~line 695)
- `learning_dashboard/ui/views.py`: leaderboard toggle (~line 94)
