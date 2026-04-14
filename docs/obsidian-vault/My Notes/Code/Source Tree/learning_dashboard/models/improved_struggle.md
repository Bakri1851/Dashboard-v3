# improved_struggle.py

**Path:** `code/learning_dashboard/models/improved_struggle.py`
**Folder:** [[models]]

> Difficulty-adjusted struggle model. Blends the baseline behavioural composite with a BKT mastery gap and an IRT-based penalty for failing questions the student *should* have handled easily.

## Responsibilities

- Compute a composite improved-struggle score per student as a weighted sum of three components (weights from [[config]]):
  - **Behavioural (`0.45`)** — the baseline struggle score from [[analytics]].
  - **Mastery gap (`0.30`)** — `1 - mean_mastery` from [[bkt]], reflecting recent performance.
  - **Difficulty adjustment (`0.25`)** — penalty for failing easy questions as ranked by [[irt]].
- Redistribute weights when either [[bkt]] or [[irt]] outputs are unavailable, so the model still produces a useful score.
- Classify using the standard `STRUGGLE_THRESHOLDS` so the downstream UI is compatible with the baseline.

## Key functions / classes

- `compute_improved_struggle_scores(df, baseline_struggle_df, mastery_summary_df=None, irt_difficulty_df=None)` → DataFrame with improved score, level, color.
- `_compute_difficulty_adjusted(df, irt_difficulty_df, correct_threshold)` — the per-student easy-question-failure penalty.

## Dependencies

- `pandas`, `numpy`.
- Reads [[config]]: `IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL`, `IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP`, `IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ`, `STRUGGLE_THRESHOLDS`, `CORRECT_THRESHOLD`.
- Depends on [[bkt]] output (optional) and [[irt]] output (optional).

## Related notes

- [[Improved Struggle Logic]] (thematic, canonical)
- [[Formulae and Equations]]
