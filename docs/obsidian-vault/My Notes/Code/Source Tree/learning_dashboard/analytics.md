# analytics.py

**Path:** `code/learning_dashboard/analytics.py`
**Folder:** [[learning_dashboard]]

> Baseline scoring engine — converts AI feedback into incorrectness values and rolls them up into per-student struggle scores, per-question difficulty scores, collaborative-filtering diagnostics, and mistake clusters.

## Responsibilities

- Call OpenAI in batches to convert free-text `ai_feedback` into continuous incorrectness values in `[0, 1]`, with fallback to `0.5` on error and an in-process `_incorrectness_cache`.
- Compute per-student struggle as a 7-component weighted score (submission count, active time, mean incorrectness, retry rate, recent incorrectness with exponential time decay, improvement slope, answer repetition) with Bayesian shrinkage for low-volume students.
- Compute per-question difficulty as a 5-component weighted score (incorrect rate, avg time, avg attempts, mean incorrectness, first-attempt failure rate).
- Expose a collaborative-filtering layer (cosine similarity over normalised student features) for the diagnostic CF panel and `get_similar_students`.
- Cluster wrong answers for a single question via TF-IDF + K-means with silhouette-based `k`-selection, label clusters via OpenAI, and cache the result in `_cluster_cache`.
- Provide `min_max_normalize`, `classify_score`, and `apply_temporal_smoothing` as shared helpers.

## Key functions / classes

- `estimate_incorrectness(feedback)` · `compute_incorrectness_column(df)`
- `compute_student_struggle_scores(df)` — returns `struggle_df` with per-student aggregates, components, and the composite score.
- `compute_question_difficulty_scores(df)` — returns `difficulty_df`.
- `compute_cf_struggle_scores(df, struggle_df)` · `get_similar_students(...)`
- `cluster_question_mistakes(df, question_id)` + `_label_clusters_with_openai(...)`
- `classify_score(score, thresholds)` · `min_max_normalize(series)` · `apply_temporal_smoothing(...)`
- `compute_recent_incorrectness(student_submissions)` — 30-min half-life exponential decay.

## Dependencies

- `openai`, `scikit-learn` (TfidfVectorizer, KMeans, silhouette_score, cosine_similarity), `numpy`, `pandas`.
- Imports [[config]] for every weight and threshold.
- Consumed by [[instructor_app]] (via [[views]] and [[components]]) and by [[assistant_app]] (`_load_student_data`).

## Related notes

- [[Analytics Engine]] (thematic, canonical)
- [[Student Struggle Logic]] · [[Question Difficulty Logic]] · [[Formulae and Equations]]
- [[Algorithms]] — algorithms reference
- [[models]] — advanced models that layer on top
