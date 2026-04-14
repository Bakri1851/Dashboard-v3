# bkt.py

**Path:** `code/learning_dashboard/models/bkt.py`
**Folder:** [[models]]

> Bayesian Knowledge Tracing — a hidden Markov model for per-question mastery. Replays each student's submissions in chronological order to track `P(mastery)` as they attempt the question repeatedly.

## Responsibilities

- Apply the BKT update rule given observed correctness, using the four parameters from [[config]]: `P_INIT`, `P_LEARN`, `P_GUESS`, `P_SLIP`.
- Compute per-student, per-question mastery trajectories from chronological submissions.
- Roll up to a per-student summary — mean mastery, count of questions mastered above `BKT_MASTERY_THRESHOLD` (0.95).
- Produce the all-students × all-questions mastery table used by the Comparison view and [[improved_struggle]].

## Key functions / classes

- `bkt_update(prior, correct, p_learn, p_guess, p_slip)` → posterior mastery.
- `compute_student_mastery(student_df, question_id)` → per-attempt mastery trace.
- `compute_all_mastery(df)` → DataFrame with `user`, `question`, `final_mastery`, `n_attempts`, `mastered`.
- `compute_student_mastery_summary(df)` → per-student summary with `mean_mastery`, `n_mastered`, `n_total`.

## Dependencies

- `numpy`, `pandas`.
- Reads [[config]]: `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD`, `CORRECT_THRESHOLD`.
- Consumed by [[improved_struggle]] and the Comparison view in [[views]].

## Related notes

- [[BKT Mastery Logic]] (thematic, canonical)
- [[Formulae and Equations]] · [[Algorithms]]
