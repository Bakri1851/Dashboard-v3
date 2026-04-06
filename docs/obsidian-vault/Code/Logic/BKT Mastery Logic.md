# BKT Mastery Logic

Bayesian Knowledge Tracing (BKT) estimates per-student, per-question mastery as a latent probability that evolves with each submission. It runs alongside the baseline struggle model and does not replace it. Mastery represents accumulated knowledge over time, which is explicitly distinct from live-session struggle.

Related: [[Student Struggle Logic]], [[IRT Difficulty Logic]], [[Analytics Engine]], [[Next Steps]], [[Glossary]]

## Relationship to baseline

The baseline struggle model in `analytics.py` captures current-session behavioral signals (recent incorrectness, retry rate, trajectory). BKT adds a longitudinal dimension: how much evidence exists that a student has learned each question's skill, regardless of how they are performing right now. Both are available when `improved_models_enabled` is toggled on in Settings.

## Mathematical model (standard BKT)

Each question is treated as a single skill. The hidden state is binary: "learned" (L) vs "not learned" (~L). Four parameters govern the model:

```
P(L_0) = 0.3    prior probability of knowing the skill
P(T)   = 0.1    probability of learning on each opportunity
P(G)   = 0.2    probability of guessing correctly without knowing
P(S)   = 0.1    probability of slipping (wrong despite knowing)
```

### Update rule

After each observation (correct or wrong), the posterior is computed via Bayes' rule, then the learning transition is applied:

```
P(L | correct) = P(L) * (1-S) / [P(L)*(1-S) + (1-P(L))*G]
P(L | wrong)   = P(L) * S     / [P(L)*S     + (1-P(L))*(1-G)]
P(L_next)      = P(L|obs)     + (1 - P(L|obs)) * P(T)
```

Submissions are processed chronologically per student per question. A submission is coded as correct when `incorrectness < CORRECT_THRESHOLD` (0.5).

## Output

Two DataFrames are produced:

**Per-question mastery** (`_mastery_df`):

| Column | Type | Description |
|---|---|---|
| `user` | str | Student identifier |
| `question` | str | Question identifier |
| `mastery` | float | Final P(L) after replaying all submissions |
| `n_attempts` | int | Number of submissions for this student-question pair |

**Per-student summary** (`_mastery_summary_df`):

| Column | Type | Description |
|---|---|---|
| `user` | str | Student identifier |
| `mean_mastery` | float | Average mastery across all attempted questions |
| `min_mastery` | float | Lowest mastery across all attempted questions |
| `mastered_count` | int | Questions with mastery >= 0.95 |
| `total_questions` | int | Number of distinct questions attempted |

## Convergence behavior

- 5 consecutive correct answers drives mastery above 0.99.
- Alternating correct/wrong oscillates around 0.29-0.69 without reaching mastery.
- All wrong answers drive mastery down to approximately 0.11 after 5 attempts.
- A student who has never submitted for a question has no mastery entry (not zero).

## Edge cases

- Empty DataFrame or missing `incorrectness` column returns empty output with correct column schemas.
- Division-by-zero guards (denominator clamped to 1e-12) handle degenerate parameter combinations.
- Result is always clipped to [0, 1].

## Leaderboard integration

When the "Use Improved Models" toggle is active in the In Class View, BKT mastery feeds into the improved struggle model (Phase 4) via the mastery gap signal. The previous approach of using `1 - mean_mastery` directly as a struggle proxy caused scores to cluster near 1.0 because BKT `mean_mastery` values had very low variance across students. The improved model resolves this by using mastery as one of three signal groups rather than the sole metric. See [[Improved Struggle Logic]].

Raw mastery values are preserved in session state for the improved struggle model and future comparison UI.

## Settings integration

BKT computation is gated by `improved_models_enabled` in session state (toggled in Settings). When enabled, results are cached in `st.session_state["_mastery_df"]` and `st.session_state["_mastery_summary_df"]`. When disabled, both caches are cleared. BKT mastery is consumed by the improved struggle model when the **Student Struggle Model** is set to "Improved" in Settings.

## Code references

- `learning_dashboard/models/bkt.py`: `bkt_update()`, `compute_student_mastery()`, `compute_all_mastery()`, `compute_student_mastery_summary()`
- `learning_dashboard/config.py`: `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD`
- `learning_dashboard/instructor_app.py`: feature-flag integration (~line 680)
- `learning_dashboard/ui/views.py`: leaderboard toggle and normalization (~line 115)
