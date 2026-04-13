# Algorithms

Reference for every algorithm in the scoring system — inputs, outputs, steps, and key parameters. For the raw formulas see [[Formulae and Equations]]. For per-topic design rationale see the individual Logic notes.

Related: [[Formulae and Equations]], [[Analytics Engine]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[IRT Difficulty Logic]], [[BKT Mastery Logic]], [[Improved Struggle Logic]], [[Glossary]]

---

## 1. LLM Incorrectness Scoring

Converts free-text AI tutor feedback into a continuous `incorrectness` value.

**Input:** `ai_feedback` string per submission  
**Output:** `incorrectness ∈ [0.0, 1.0]` per submission

**Steps:**
1. Collect all submissions lacking an `incorrectness` value in the current batch.
2. Send `ai_feedback` text to OpenAI API in batch; ask for a score in `[0, 1]`.
3. Cache result in `_incorrectness_cache` (process-local) keyed by feedback text — identical feedback strings reuse the cached value without a second API call.
4. If the API call fails or feedback is empty, assign the fallback `0.5`.

**Key parameters:**
- `CORRECT_THRESHOLD = 0.5` — anything below this is treated as "correct" by downstream models
- Fallback: `0.5` (neutral, not biased toward correct or incorrect)

**Code references:**
- `code/learning_dashboard/analytics.py` — `compute_incorrectness_column()`
- `code/learning_dashboard/config.py` — `CORRECT_THRESHOLD`

---

## 2. Baseline Student Struggle Pipeline

Produces a per-student struggle score from behavioral aggregates over the current session.

**Input:** filtered submissions DataFrame (one row per submission)  
**Output:** `struggle_df` — one row per student with `struggle_score`, `struggle_level`, `struggle_color`

**Steps:**
1. For each student, aggregate all their submissions:
   - Count submissions → `n`
   - Compute session duration (minutes, first to last) → `t`
   - Compute mean incorrectness → `i_hat`
   - Compute retry rate (fraction of attempts on already-seen questions) → `r_hat`
   - Compute recent incorrectness with exponential time decay over last 5 submissions → `A_raw`
   - Compute incorrectness trajectory slope over submission order → `d`
   - Compute exact-answer repetition rate on same question → `rep_hat`
2. Min-max normalise `n`, `t`, `d` across the student population → `n_hat`, `t_hat`, `d_hat`.
3. Apply weighted sum: `S_raw = 0.10*n_hat + 0.10*t_hat + 0.20*i_hat + 0.10*r_hat + 0.38*A_raw + 0.05*d_hat + 0.07*rep_hat`
4. Apply Bayesian shrinkage: `S_final = w_n * S_raw + (1 - w_n) * mean(S_raw)` where `w_n = n / (n + 5)`
5. Classify via `STRUGGLE_THRESHOLDS` → `struggle_level` and `struggle_color`.

**Key parameters:** `STRUGGLE_WEIGHTS`, `SHRINKAGE_K = 5`, `RECENT_SUBMISSION_COUNT`, `STRUGGLE_THRESHOLDS`

**Code references:**
- `code/learning_dashboard/analytics.py` — `compute_student_struggle_scores()`, `compute_recent_incorrectness()`, `_compute_slope()`, `classify_score()`
- `code/learning_dashboard/config.py` — `STRUGGLE_WEIGHTS`, `SHRINKAGE_K`, `STRUGGLE_THRESHOLDS`

---

## 3. Baseline Question Difficulty Pipeline

Produces a per-question difficulty score from attempt aggregates.

**Input:** filtered submissions DataFrame  
**Output:** `difficulty_df` — one row per question with `difficulty_score`, `difficulty_level`, `difficulty_color`

**Steps:**
1. For each question, aggregate all attempts:
   - Incorrect rate across all attempts → `c_tilde`
   - Average time per student → `t` (then min-max normalised → `t_tilde`)
   - Average attempts per student → `a` (then min-max normalised → `a_tilde`)
   - Average incorrectness across all attempts → `f_tilde`
   - First-attempt failure rate across students → `p_tilde`
2. Apply weighted sum: `D = 0.28*c_tilde + 0.12*t_tilde + 0.20*a_tilde + 0.20*f_tilde + 0.20*p_tilde`
3. Classify via `DIFFICULTY_THRESHOLDS` → `difficulty_level` and `difficulty_color`.

**Key parameters:** `DIFFICULTY_WEIGHTS`, `DIFFICULTY_THRESHOLDS`, `CORRECT_THRESHOLD`

**Code references:**
- `code/learning_dashboard/analytics.py` — `compute_question_difficulty_scores()`
- `code/learning_dashboard/config.py` — `DIFFICULTY_WEIGHTS`, `DIFFICULTY_THRESHOLDS`

---

## 4. Collaborative Filtering (CF)

Identifies students who are similar to a given student based on normalized behavioral features. Diagnostic only — does not overwrite `struggle_level` or affect assistant assignment.

**Input:** per-student feature vectors (normalized struggle components)  
**Output:** per-student list of k nearest neighbours with cosine similarity scores

**Steps:**
1. Build a feature matrix: one row per student, columns are normalized struggle features (`n_hat`, `t_hat`, `i_hat`, `r_hat`, `A_raw`, `d_hat`, `rep_hat`).
2. Compute pairwise cosine similarity across all student pairs.
3. For each student, rank other students by similarity descending.
4. Return top k=3 most similar students.

**Constraint:** requires k+1 active students minimum (cold-start: returns empty with fewer students).

**Code references:**
- `code/learning_dashboard/analytics.py` — `compute_cf_struggle_scores()`, `get_similar_students()`
- `code/learning_dashboard/config.py` — `CF_N_NEIGHBOURS`

---

## 5. Mistake Clustering

Groups incorrect answers for a single question into thematic clusters and labels each cluster with a short conceptual description.

**Input:** all submissions for one question  
**Output:** list of clusters, each with a label and representative example answers

**Steps:**
1. Filter to incorrect submissions only (`incorrectness >= CORRECT_THRESHOLD`).
2. Remove blank answer strings.
3. Deduplicate exact answer text (keeps one copy of each unique wrong answer).
4. Vectorise unique answers using TF-IDF (scikit-learn `TfidfVectorizer`).
5. Sweep `k` from 2 to `MAX_CLUSTERS`; fit K-means for each `k`; compute silhouette score.
6. Select `k` with the highest silhouette score.
7. For each cluster centroid, pick the answer with highest cosine similarity to the centroid as the representative example.
8. Send representative examples to OpenAI with a prompt requesting short conceptual cluster labels.
9. Cache result in `_cluster_cache` keyed by question ID.

**Edge cases:** if fewer than 2 unique incorrect answers exist, clustering is skipped. If OpenAI labelling fails, generic labels ("Cluster 1", "Cluster 2", …) are used.

**Key parameters:** `MAX_CLUSTERS`, `CORRECT_THRESHOLD`

**Code references:**
- `code/learning_dashboard/analytics.py` — `cluster_question_mistakes()`, `_label_clusters_with_openai()`
- `code/learning_dashboard/config.py` — `MAX_CLUSTERS`, `CORRECT_THRESHOLD`

---

## 6. IRT Estimation — Rasch 1PL

Estimates latent question difficulty (`b_i`) and latent student ability (`θ_j`) jointly from binary response data.

**Input:** filtered submissions DataFrame  
**Output:** per-question `irt_difficulty ∈ [0, 1]` with level and color columns

**Steps:**
1. **Build response matrix:** for each student-question pair, select the best attempt (lowest `incorrectness`). Code as `1` (correct) if `incorrectness < CORRECT_THRESHOLD`, else `0`.
2. **Filter sparse data:** drop questions with fewer than `IRT_MIN_ATTEMPTS_PER_QUESTION` responding students; drop students with fewer than `IRT_MIN_ATTEMPTS_PER_STUDENT` attempted questions.
3. **Initialise parameters:** set all `θ_j = 0`, all `b_i = 0`.
4. **Optimise via L-BFGS-B:** maximise the log-likelihood of observed correct/incorrect responses under the Rasch model `P(correct) = sigmoid(θ_j − b_i)`.
5. **Identifiability:** pin `mean(θ) = 0` after each optimisation step.
6. **Map output:** apply `sigmoid(b_i)` then min-max normalise across questions to get `irt_difficulty ∈ [0, 1]`.
7. Classify using `DIFFICULTY_THRESHOLDS` (same labels as baseline).

**Key parameters:** `IRT_MIN_ATTEMPTS_PER_QUESTION`, `IRT_MIN_ATTEMPTS_PER_STUDENT`, `IRT_MAX_ITER`

**Code references:**
- `code/learning_dashboard/models/irt.py` — `build_response_matrix()`, `fit_rasch_model()`, `compute_irt_difficulty_scores()`
- `code/learning_dashboard/config.py` — `IRT_MIN_ATTEMPTS_PER_QUESTION`, `IRT_MIN_ATTEMPTS_PER_STUDENT`, `IRT_MAX_ITER`

---

## 7. BKT Mastery Tracing

Estimates per-student, per-question mastery as a latent probability that updates with each submission.

**Input:** filtered submissions DataFrame with `incorrectness` column  
**Output:** per-student-question mastery table + per-student summary table

**Steps (per student per question):**
1. Sort all submissions for this student-question pair chronologically.
2. Initialise: `P(L) = P(L_0) = 0.3`
3. For each submission in order:
   a. Classify as correct (`incorrectness < 0.5`) or wrong.
   b. Apply Bayes update: `P(L | obs)` using slip and guess parameters.
   c. Apply learning transition: `P(L_next) = P(L|obs) + (1 − P(L|obs)) * P(T)`.
   d. Clip result to `[0, 1]`.
4. Record final `P(L)` as `mastery` for this student-question pair.

**Per-student summary:** compute `mean_mastery`, `min_mastery`, `mastered_count` (mastery >= `BKT_MASTERY_THRESHOLD`), `total_questions` across all attempted questions.

**Convergence reference:** 5 consecutive correct answers → mastery > 0.99. All wrong → mastery ≈ 0.11 after 5 attempts.

**Key parameters:** `BKT_P_INIT = 0.3`, `BKT_P_LEARN = 0.1`, `BKT_P_GUESS = 0.2`, `BKT_P_SLIP = 0.1`, `BKT_MASTERY_THRESHOLD = 0.95`

**Code references:**
- `code/learning_dashboard/models/bkt.py` — `bkt_update()`, `compute_student_mastery()`, `compute_all_mastery()`, `compute_student_mastery_summary()`
- `code/learning_dashboard/config.py` — `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD`

---

## 8. Improved Struggle Assembly (Phase 4)

Combines behavioral signals, BKT mastery gap, and IRT difficulty-adjusted incorrectness into a richer struggle estimate.

**Input:** `struggle_df` (baseline behavioral components), `_mastery_summary_df` (BKT), IRT difficulty values  
**Output:** `_improved_struggle_df` — same schema as `struggle_df` plus `behavioral_composite`, `mastery_gap`, `difficulty_adjusted_score`

**Steps:**
1. **Behavioral composite:** `(A_raw + r_hat + d_hat + rep_hat) / 4`
2. **Mastery gap:** `max(0, mean_mastery − (1 − A_raw))`  
   - If BKT unavailable, redistribute `w_mg = 0.30` to `w_beh`.
3. **Difficulty-adjusted incorrectness:** `mean(incorrectness_i × (1 − irt_difficulty_i))` over last `RECENT_SUBMISSION_COUNT` submissions.  
   - Questions without IRT data use neutral difficulty `0.5`.  
   - If IRT unavailable, redistribute `w_da = 0.25` to `w_beh`.
4. **Assembly:** `S = w_beh * behavioral + w_mg * mastery_gap + w_da * difficulty_adjusted`
5. **Shrinkage:** `S_final = w_n * S + (1 − w_n) * mean(S)` where `w_n = n / (n + K)`
6. Clip to `[0, 1]`. Classify using `STRUGGLE_THRESHOLDS`.

**Key parameters:** `IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL = 0.45`, `IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP = 0.30`, `IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ = 0.25`, `SHRINKAGE_K`, `RECENT_SUBMISSION_COUNT`

**Code references:**
- `code/learning_dashboard/models/improved_struggle.py` — `compute_improved_struggle_scores()`
- `code/learning_dashboard/config.py` — `IMPROVED_STRUGGLE_WEIGHT_*`, `SHRINKAGE_K`

---

## 9. Measurement Confidence (Phase 1)

Adds confidence metadata to each incorrectness score, flagging how reliable the OpenAI-derived value is.

**Input:** per-submission `incorrectness` values + `ai_feedback` text  
**Output:** additional `confidence` column on the incorrectness DataFrame

Confidence is low when: feedback text is very short, the OpenAI score is near the `0.5` threshold, or the fallback value was used. High confidence when feedback is detailed and the score is clearly above or below `0.5`.

**Code references:**
- `code/learning_dashboard/models/measurement.py`
