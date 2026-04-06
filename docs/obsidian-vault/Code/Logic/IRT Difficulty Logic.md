# IRT Difficulty Logic

IRT (Item Response Theory) provides an alternative difficulty estimate that treats question difficulty as a latent parameter, estimated jointly with student ability via maximum likelihood. It runs alongside the baseline weighted difficulty model and does not replace it.

Related: [[Question Difficulty Logic]], [[Analytics Engine]], [[Next Steps]], [[Glossary]]

## Relationship to baseline

The baseline difficulty model in `analytics.py` uses a weighted sum of five observable metrics (incorrect rate, time, attempts, mean incorrectness, first-attempt failure). IRT instead models difficulty as an unobserved property inferred from the pattern of correct and incorrect responses across all students. Both models are available when `improved_models_enabled` is toggled on in Settings.

## Mathematical model (Rasch / 1PL)

```
P(correct | theta_j, b_i) = sigmoid(theta_j - b_i)
```

- `theta_j` = latent ability of student j
- `b_i` = latent difficulty of question i
- Both estimated jointly via maximum likelihood (L-BFGS-B)
- Mean ability is pinned to 0 for identifiability

## Input: response matrix

A binary student x question matrix is built from the data:

- For each student-question pair, the best attempt (lowest incorrectness) is selected.
- An attempt is coded as correct when `incorrectness < CORRECT_THRESHOLD` (0.5).
- Questions with fewer than 2 responding students are dropped.
- Students with fewer than 2 attempted questions are dropped.

## Output

Raw logit-scale difficulty (`b_i`) is mapped to [0, 1] via the sigmoid function for UI compatibility. The same threshold labels as the baseline are used:

- `0.00-0.35`: Easy
- `0.35-0.50`: Medium
- `0.50-0.75`: Hard
- `0.75-1.00`: Very Hard

Output columns: `question`, `irt_difficulty`, `irt_difficulty_level`, `irt_difficulty_color`.

## Edge cases

- Questions attempted by fewer than 2 students are excluded (insufficient information).
- Students who attempted fewer than 2 questions are excluded.
- If no valid data remains after filtering, an empty DataFrame is returned.
- The model degrades gracefully with small datasets but may not converge.

## Leaderboard integration

When the "Use IRT / BKT models" toggle is active in the In Class View, IRT difficulty powers the question leaderboard:

- Raw `irt_difficulty` values (sigmoid of logit-scale `b_i`) are **min-max normalized** (`analytics.min_max_normalize`) before classification. Without normalization, sigmoid maps all large positive `b_i` values to near 1.0, making every question appear "Very Hard".
- Classification uses the standard `DIFFICULTY_THRESHOLDS`.

Raw IRT values are preserved in session state for Phase 4 and Phase 5.

## Settings integration

IRT computation is gated by `improved_models_enabled` in session state (toggled in Settings). When enabled, results are cached in `st.session_state["_irt_difficulty_df"]`. When disabled, the cache is cleared. The active difficulty model is selected via the **Question Difficulty Model** selectbox in Settings ("Baseline" or "IRT"). IRT difficulty also feeds into the improved struggle model's difficulty-adjusted signal group.

## Code references

- `learning_dashboard/models/irt.py`: `build_response_matrix()`, `fit_rasch_model()`, `compute_irt_difficulty_scores()`
- `learning_dashboard/config.py`: `IRT_MIN_ATTEMPTS_PER_QUESTION`, `IRT_MIN_ATTEMPTS_PER_STUDENT`, `IRT_MAX_ITER`, `IRT_DIFFICULTY_THRESHOLDS`
- `learning_dashboard/instructor_app.py`: feature-flag integration (~line 680)
- `learning_dashboard/ui/views.py`: leaderboard toggle and normalization (~line 115)
