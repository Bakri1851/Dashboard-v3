# Analytics Engine

`analytics.py` is the core scoring module for the project. It converts AI tutor feedback into incorrectness values, rolls those values up into student and question scores, adds a collaborative-filtering diagnostic layer, and clusters wrong answers for question drill-downs.

Related: [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Instructor Dashboard]], [[UI System]], [[Known Issues]], [[BKT Mastery Logic]], [[IRT Difficulty Logic]], [[Improved Struggle Logic]], [[Scikit-learn]], [[OpenAI]]

## Responsibilities

- Score `ai_feedback` text into continuous incorrectness values in `[0, 1]`.
- Compute per-student struggle scores from behavioral aggregates.
- Compute per-question difficulty scores from attempt aggregates.
- Compute collaborative-filtering similarity diagnostics over normalized student features.
- Cluster incorrect answers for a single question and label those clusters.

## Key Algorithms

- Incorrectness measurement: [[OpenAI]] converts `ai_feedback` text into continuous incorrectness values used throughout the baseline scoring pipeline.
- Baseline student struggle: a weighted behavioral score over normalized activity and incorrectness features; see [[Student Struggle Logic]].
- Baseline question difficulty: a weighted aggregate of incorrect rate, time cost, attempts, mean incorrectness, and first-attempt failure; see [[Question Difficulty Logic]].
- Collaborative filtering: cosine similarity over normalized student features powers the diagnostic CF layer and similar-student lookups; see [[Scikit-learn]] and [[Student Struggle Logic]].
- Mistake clustering: TF-IDF text features, K-means clustering, silhouette-based cluster-count selection, and centroid-similarity example picking drive the question drill-down clusters; see [[Scikit-learn]] and [[Question Difficulty Logic]].
- Improved models: the alternative measurement, IRT, BKT, and mastery-aware struggle pipeline live in `models/`; see [[IRT Difficulty Logic]], [[BKT Mastery Logic]], and [[Improved Struggle Logic]].

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

## Improved models (`code/learning_dashboard/models/`)

Alternative and enhanced models live in the `models/` package, gated by the `improved_models_enabled` feature flag in Settings. These never replace the baseline — they provide a second estimate for comparison.

- `measurement.py` (Phase 1): adds confidence metadata to incorrectness scores.
- `irt.py` (Phase 2): Rasch IRT difficulty estimation as an alternative to the baseline weighted score. See [[IRT Difficulty Logic]].
- `bkt.py` (Phase 3): Bayesian Knowledge Tracing for per-student per-question mastery estimation. See [[BKT Mastery Logic]].
- `improved_struggle.py` (Phase 4): mastery-aware, difficulty-adjusted struggle model combining behavioral signals with BKT and IRT outputs. See [[Improved Struggle Logic]].
- Phase 5 (Comparison UI): each sub-model is gated individually in `instructor_app.py` via session state toggles (`irt_enabled`, `bkt_enabled`, `improved_struggle_enabled`). `_improved_models_settings_key` fingerprints all toggle + BKT param state so any slider or toggle change triggers automatic recomputation without a manual refresh. The comparison view is in `ui/views.py` `comparison_view()`. See [[UI System]].

## Code references

- `code/learning_dashboard/analytics.py`: `compute_incorrectness_column()`
- `code/learning_dashboard/analytics.py`: `compute_student_struggle_scores()`
- `code/learning_dashboard/analytics.py`: `compute_question_difficulty_scores()`
- `code/learning_dashboard/analytics.py`: `compute_cf_struggle_scores()`, `get_similar_students()`
- `code/learning_dashboard/analytics.py`: `cluster_question_mistakes()`
- `code/learning_dashboard/config.py`: `IMPROVED_MODELS_ENABLED_DEFAULT`, `IRT_ENABLED_DEFAULT`, `BKT_ENABLED_DEFAULT`, `IMPROVED_STRUGGLE_ENABLED_DEFAULT`
