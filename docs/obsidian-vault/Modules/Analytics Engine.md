# Analytics Engine

`analytics.py` is the core scoring module for the project. It converts AI tutor feedback into incorrectness values, rolls those values up into student and question scores, adds a collaborative-filtering diagnostic layer, and clusters wrong answers for question drill-downs.

Related: [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Instructor Dashboard]], [[UI System]], [[Known Issues]]

## Responsibilities

- Score `ai_feedback` text into continuous incorrectness values in `[0, 1]`.
- Compute per-student struggle scores from behavioral aggregates.
- Compute per-question difficulty scores from attempt aggregates.
- Compute collaborative-filtering similarity diagnostics over normalized student features.
- Cluster incorrect answers for a single question and label those clusters.

## Important implementation details

- OpenAI calls are batched for incorrectness scoring and reused through `_incorrectness_cache`.
- Wrong-answer clusters are cached through `_cluster_cache`.
- If OpenAI calls fail, incorrectness falls back to `0.5` and cluster labels fall back to generic names.
- The module is UI-independent in structure, but it still depends on secrets and external services for some outputs.

## Outputs used elsewhere

- `struggle_df` powers leaderboards, summary cards, drill-down headers, and assistant assignment eligibility.
- `difficulty_df` powers the question leaderboard and question drill-down metrics.
- Mistake clusters only appear in question detail views.
- Collaborative filtering is currently shown as a diagnostic panel rather than rewriting the main struggle labels.

## Improved models (`learning_dashboard/models/`)

Alternative and enhanced models live in the `models/` package, gated by the `improved_models_enabled` feature flag in Settings. These never replace the baseline — they provide a second estimate for comparison.

- `measurement.py` (Phase 1): adds confidence metadata to incorrectness scores.
- `irt.py` (Phase 2): Rasch IRT difficulty estimation as an alternative to the baseline weighted score. See [[IRT Difficulty Logic]].
- `bkt.py` (Phase 3): Bayesian Knowledge Tracing for per-student per-question mastery estimation. See [[BKT Mastery Logic]].

## Code references

- `learning_dashboard/analytics.py`: `compute_incorrectness_column()`
- `learning_dashboard/analytics.py`: `compute_student_struggle_scores()`
- `learning_dashboard/analytics.py`: `compute_question_difficulty_scores()`
- `learning_dashboard/analytics.py`: `compute_cf_struggle_scores()`, `get_similar_students()`
- `learning_dashboard/analytics.py`: `cluster_question_mistakes()`
