# Question Difficulty Logic

Question difficulty is a weighted score over correctness, time cost, attempt volume, average incorrectness, and first-attempt failure. It produces the ranked question leaderboard and also gates the mistake-clustering feature in the question drill-down view.

Related: [[Analytics Engine]], [[Student Struggle Logic]], [[Dashboard Pages and UI Flow]], [[Glossary]]

## Foundation: incorrectness

- Question difficulty is built on the same OpenAI-derived incorrectness values used by the student struggle model.
- A submission is treated as correct when `incorrectness < 0.5` and incorrect otherwise.

## Formula

`D = 0.28*c_tilde + 0.12*t_tilde + 0.20*a_tilde + 0.20*f_tilde + 0.20*p_tilde`

## Component meanings

- `c_tilde`: incorrect rate across all attempts.
- `t_tilde`: min-max normalized average time per student.
- `a_tilde`: min-max normalized average attempts per student.
- `f_tilde`: average incorrectness across all attempts.
- `p_tilde`: first-attempt failure rate across students.

## Labels

- `0.00-0.35`: Easy
- `0.35-0.50`: Medium
- `0.50-0.75`: Hard
- `0.75-1.00`: Very Hard

## Mistake clustering

- Runs only in `question_detail_view()`.
- Filters the question's submissions to incorrect answers only.
- Removes blank answers and deduplicates exact answer text.
- Vectorizes unique answers with TF-IDF.
- Chooses `k` with silhouette scoring, then runs K-means.
- Picks representative examples by cosine similarity to cluster centroids.
- Sends those representatives to OpenAI for short conceptual labels.

## UI impact

- Difficulty scores drive the question leaderboard and question header card.
- Question drill-down also shows attempt counts, student counts, incorrect rate, mistake clusters, a student table, and an attempt timeline.

## Code references

- `learning_dashboard/analytics.py`: `compute_question_difficulty_scores()`
- `learning_dashboard/analytics.py`: `cluster_question_mistakes()`, `_label_clusters_with_openai()`
- `learning_dashboard/config.py`: difficulty weights, thresholds, `CORRECT_THRESHOLD`, cluster limits
- `learning_dashboard/ui/views.py`: `question_detail_view()`
