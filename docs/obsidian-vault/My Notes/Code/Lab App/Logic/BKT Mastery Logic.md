# BKT Mastery Logic

Bayesian Knowledge Tracing (BKT) estimates per-student, per-question mastery as a latent probability that evolves with each submission. It runs alongside the baseline struggle model and does not replace it. Mastery represents accumulated knowledge over time, which is explicitly distinct from live-session struggle.

Related: [[Student Struggle Logic]], [[IRT Difficulty Logic]], [[Analytics Engine]], [[Next Steps]], [[Glossary]]

Academic foundations: BKT originates with [[corbett_1995_knowledge|Corbett & Anderson 1995]]; per-student parameterisation is in [[yudelson_2013_individualized|Yudelson, Koedinger & Gordon 2013]]; deep-learning alternatives (DKT) surveyed in [[piech_2015_deep|Piech et al. 2015]] — BKT is preferred here for interpretability and low-data tractability. Prior uses in the struggle-detection literature: [[khajah_supercharging|Khajah et al.]] (BKT + IRT-like structure), [[kim_knowledge|Kim et al.]] (knowledge tracing with auto-extracted skills). See [[Ch2 – Background and Requirements]] §2.1.4.

## Relationship to baseline

The baseline struggle model in `analytics.py` captures current-session behavioral signals (recent incorrectness, retry rate, trajectory). BKT adds a longitudinal dimension: how much evidence exists that a student has learned each question's skill, regardless of how they are performing right now. Both are available when `improved_models_enabled` is toggled on in Settings.

## Mathematical model (standard BKT)

Each question is treated as a single skill. The hidden state is binary: "learned" (L) vs "not learned" (~L). Four parameters govern the model. The values below are textbook defaults (Corbett & Anderson); the Settings panel exposes a **Fit from data** action (see [[#Parameter fitting (MLE)]]) that replaces them with MLE estimates from the current filtered submissions.

```
P(L_0) = 0.3    prior probability of knowing the skill     (default)
P(T)   = 0.1    probability of learning on each opportunity (default)
P(G)   = 0.2    probability of guessing correctly without knowing (default)
P(S)   = 0.1    probability of slipping (wrong despite knowing)   (default)
```

### Update rule

After each observation (correct or wrong), the posterior is computed via Bayes' rule, then the learning transition is applied:

```
P(L | correct) = P(L) * (1-S) / [P(L)*(1-S) + (1-P(L))*G]
P(L | wrong)   = P(L) * S     / [P(L)*S     + (1-P(L))*(1-G)]
P(L_next)      = P(L|obs)     + (1 - P(L|obs)) * P(T)
```

Submissions are processed chronologically per student per question. A submission is coded as correct when `incorrectness < CORRECT_THRESHOLD` (0.5).

## Parameter fitting (MLE)

The four BKT parameters are no longer tied to textbook defaults. `fit_bkt_parameters(df)` maximises the forward-algorithm log-likelihood of the observed submission sequences over `(P(L_0), P(T), P(G), P(S))` using `scipy.optimize.minimize` with L-BFGS-B and bounds `[(0,1), (0,1), (0,0.5), (0,0.5)]`. The upper bounds on P(G) and P(S) enforce the standard BKT identifiability constraint `P(G) + P(S) < 1` — without them the likelihood surface has degenerate "flipped" maxima where guessing and slipping swap roles.

The fit uses the same `[timestamp, question]` mergesort ordering as `compute_all_mastery()`, so the parameters fitted by MLE and the mastery values produced at inference are consistent — both replay the identical sequences.

### Fit quality diagnostic — next-attempt AUC

For each attempt `t` in a student-question sequence, the model's predicted `P(correct)` *before* the attempt is observed is

```
P(correct) = mastery_t * (1 - P(S)) + (1 - mastery_t) * P(G)
```

These predictions paired with actual correctness give a ROC-AUC via `sklearn.metrics.roc_auc_score`. KT-literature convention: **AUC > 0.70** means the model explains next-attempt correctness well enough to be useful; **AUC ≈ 0.5** means the parameters are no better than chance.

### UI entry point

Settings → Model Toggle → *(struggle_model = Improved)* → **Fit from data** button, directly under the four BKT sliders. On click: the fitter runs on the currently-filtered DataFrame, sliders snap to the fitted values, a caption shows `n_observations`, AUC, and log-likelihood, and the Improved Struggle leaderboard recomputes on the next rerun via the existing `_improved_settings_key` cache invalidation.

### Honest framing (for Ch5 §5.5)

MLE fitting is the standard unsupervised approach in the KT literature; it replaces arbitrary defaults with values grounded in this cohort's data. But it maximises **next-attempt correctness prediction**, not "struggle identification":

- BKT estimates `P(knows skill)`, one input to struggle — not struggle itself.
- BKT assumes one skill per question, monotonic learning, and independent questions. Real learning violates all three.
- The `incorrectness` labels come from the OpenAI grader, not humans — parameter fit quality is upper-bounded by grader accuracy.
- Defensible claim: *"BKT parameters fitted by MLE on submission sequences, validated via next-attempt correctness AUC."* Not *"the dashboard accurately identifies struggling students."*

This also gives **Meeting 4 action item "IRT/BKT disagreement (Ch5 §5.5)"** a concrete angle: the ~0% agreement between improved and baseline models partly reflected using textbook BKT defaults that didn't match the dataset. Re-running comparison with fitted parameters is the cleanest thing to report alongside the disagreement paragraph.

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

- `code/learning_dashboard/models/bkt.py`: `bkt_update()`, `compute_student_mastery()`, `compute_all_mastery()`, `compute_student_mastery_summary()`, `fit_bkt_parameters()`, `_build_sequences()`, `_walk_and_score()`
- `code/learning_dashboard/config.py`: `BKT_P_INIT`, `BKT_P_LEARN`, `BKT_P_GUESS`, `BKT_P_SLIP`, `BKT_MASTERY_THRESHOLD`, `BKT_FIT_MIN_OBSERVATIONS`, `BKT_FIT_MAX_ITER`
- `code/learning_dashboard/instructor_app.py`: feature-flag integration (~line 680)
- `code/learning_dashboard/ui/views.py`: leaderboard toggle and normalization (~line 115); `_render_bkt_fit_controls()` + **Fit from data** button in `settings_view()`
