# bkt.py

**Path:** `code/learning_dashboard/models/bkt.py`
**Folder:** [[models]]

> Bayesian Knowledge Tracing — a hidden Markov model for per-question mastery. Replays each student's submissions in chronological order to track `P(mastery)` as they attempt the question repeatedly.

## Responsibilities

- Apply the BKT update rule given observed correctness, using the four parameters from [[config]]: `P_INIT`, `P_LEARN`, `P_GUESS`, `P_SLIP`.
- Compute per-student, per-question mastery trajectories from chronological submissions.
- Roll up to a per-student summary — mean mastery, count of questions mastered above `BKT_MASTERY_THRESHOLD` (0.95).
- Produce the all-students × all-questions mastery table used by the Comparison view and [[improved_struggle]].
- **Fit the four parameters by MLE on the current dataset** via `fit_bkt_parameters()`, so the defaults in [[config]] are a starting point rather than a commitment. See [[BKT Mastery Logic#Parameter fitting (MLE)]].

## Key functions / classes

- `bkt_update(prior, correct, p_learn, p_guess, p_slip)` → posterior mastery.
- `compute_student_mastery(student_df, question_id)` → per-attempt mastery trace.
- `compute_all_mastery(df)` → DataFrame with `user`, `question`, `final_mastery`, `n_attempts`, `mastered`.
- `compute_student_mastery_summary(df)` → per-student summary with `mean_mastery`, `n_mastered`, `n_total`.
- `fit_bkt_parameters(df)` → dict with fitted `p_init, p_learn, p_guess, p_slip`, `log_likelihood`, next-attempt `auc`, `convergence`, `n_observations`. Forward-algorithm MLE with L-BFGS-B and bounds `[(0,1), (0,1), (0,0.5), (0,0.5)]`. Refuses to fit on fewer than `BKT_FIT_MIN_OBSERVATIONS` attempts.
- `_build_sequences(df)` → list of per-(user, question) 0/1 arrays in deterministic `[timestamp, question]` order (internal helper; same ordering as `compute_all_mastery`).
- `_walk_and_score(sequences, p_init, p_learn, p_guess, p_slip)` → `(log_likelihood, predictions, actuals)`; single pass used as both the MLE objective and the AUC scorer.

## Dependencies

- `numpy`, `pandas`, `scipy.optimize.minimize` (L-BFGS-B), `sklearn.metrics.roc_auc_score`.
- Reads [[config]]: `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD`, `CORRECT_THRESHOLD`, `BKT_FIT_MIN_OBSERVATIONS`, `BKT_FIT_MAX_ITER`.
- Consumed by [[improved_struggle]] and the Comparison view in [[views]]. `fit_bkt_parameters` is called from [[views]]`._render_bkt_fit_controls()` behind the **Fit from data** button in Settings.

## Related notes

- [[BKT Mastery Logic]] (thematic, canonical)
- [[Formulae and Equations]] · [[Algorithms]]
