# irt.py

**Path:** `code/learning_dashboard/models/irt.py`
**Folder:** [[models]]

> 1-Parameter Logistic (Rasch) IRT model for question difficulty. Estimates per-question difficulty and per-student ability jointly from the binary response matrix.

## Responsibilities

- Build a students × questions response matrix from the submissions DataFrame using the `CORRECT_THRESHOLD` on incorrectness.
- Filter students and questions to those with at least `IRT_MIN_ATTEMPTS_PER_*` responses, iterating until stable.
- Fit the 1-PL Rasch model via joint MLE using iterative alternating updates, capped at `IRT_MAX_ITER`.
- Map fitted difficulty parameters to `[0, 1]` and classify with `IRT_DIFFICULTY_THRESHOLDS` from [[config]].

## Key functions / classes

- `build_response_matrix(df, correct_threshold)` → matrix, student index, question index.
- `fit_rasch_model(matrix, max_iter=...)` → `(abilities, difficulties)`.
- `compute_irt_difficulty_scores(df)` → DataFrame with `question`, `irt_difficulty`, `irt_difficulty_level`, `irt_difficulty_color`, `n_responses`.

## Dependencies

- `numpy`, `pandas`.
- Reads [[config]]: `CORRECT_THRESHOLD`, `IRT_MIN_ATTEMPTS_PER_QUESTION`, `IRT_MIN_ATTEMPTS_PER_STUDENT`, `IRT_MAX_ITER`, `IRT_DIFFICULTY_THRESHOLDS`.

## Related notes

- [[IRT Difficulty Logic]] (thematic, canonical)
- [[Formulae and Equations]] · [[Algorithms]]
