# Student Struggle Logic

Student struggle is a weighted score built from submission volume, time activity, incorrectness, retry behavior, recent trend, trajectory, and exact-answer repetition. The score is continuous, shrinkage-adjusted, and then classified into the labels shown across the instructor and assistant experiences.

Related: [[Analytics Engine]], [[Instructor Dashboard]], [[Dashboard Pages and UI Flow]], [[Question Difficulty Logic]], [[Glossary]]

## Foundation: incorrectness

- Every submission is first assigned an `incorrectness` value in `[0, 1]`.
- That value comes from `ai_feedback` text scored by OpenAI, with a fallback of `0.5` when feedback is empty or the API fails.
- The struggle model aggregates those incorrectness values locally; the dashboard does not classify struggle directly from raw feedback text.

## Formula

`S = 0.10*n_hat + 0.10*t_hat + 0.20*i_hat + 0.10*r_hat + 0.38*A_raw + 0.05*d_hat + 0.07*rep_hat`

## Component meanings

- `n_hat`: min-max normalized submission count.
- `t_hat`: min-max normalized minutes between first and last submission.
- `i_hat`: mean incorrectness across all submissions.
- `r_hat`: retry rate, derived from repeated attempts on already-seen questions.
- `A_raw`: recent incorrectness over the last 5 submissions with exponential time decay.
- `d_hat`: min-max normalized slope of incorrectness over submission order; positive means the student is getting worse.
- `rep_hat`: exact-answer repetition rate on the same question.

## Shrinkage and labels

- Raw scores are shrunk toward the class mean using `w_n = n / (n + 5)`.
- Low-volume students are therefore treated more conservatively.
- Label thresholds are:
  - `0.00-0.20`: On Track
  - `0.20-0.35`: Minor Issues
  - `0.35-0.50`: Struggling
  - `0.50-1.00`: Needs Help

## Where the score is used

- Student leaderboard ranking in `In Class View`.
- Student detail header and summary metrics.
- Assistant assignment eligibility in the instructor sidebar.
- Available-student list in the assistant waiting view.

## Improved model

Phase 4 adds an improved struggle model that incorporates BKT mastery and IRT difficulty alongside behavioral signals. See [[Improved Struggle Logic]] for full details. The baseline model documented here remains unchanged and available for comparison.

## Design rationale

The weighted parametric model was chosen over collaborative filtering as the primary approach for three reasons: (1) it produces scores immediately with no minimum class size, avoiding the cold-start problem where CF requires k+1 active students; (2) it is interpretable — each weight has a clear meaning; (3) it runs in O(n) per update versus O(n^2) for CF's pairwise similarity matrix. See [[Ch3 – Design and Modelling]] for the thesis comparison table.

The thesis design chapter defines a 5-component struggle formula (n, t, e, f, A_raw). The V2 implementation extends this to 7 components, adding retry rate (r_hat), trajectory slope (d_hat), and exact-answer repetition (rep_hat). The thesis also proposes temporal smoothing via exponential smoothing, but this is not active in V2 (`SMOOTHING_ENABLED = False`). These divergences are tracked in [[Report Sync]].

Academic foundations: [[dong_using|Dong et al.]] (session-level struggle detection), [[estey_2017_automatically|Estey et al.]] (trajectory metric reducing false-positive rate), [[piech_modeling|Piech et al.]] (progression path modelling), [[or_2024_exploring|Or]] (consecutive failure threshold), and LLM-based answer quality assessment ([[koutcheme_using|Koutcheme et al.]], [[pitts_a|Pitts et al.]]). See [[Ch2 – Background and Requirements]] for the full literature review.

## Collaborative filtering note

- Collaborative filtering is computed from struggle-model features, but the current UI treats it as a separate diagnostic layer.
- It does not rewrite `struggle_level` or change assistant assignment eligibility in the present implementation.

## Code references

- `code/learning_dashboard/analytics.py`: `compute_incorrectness_column()`
- `code/learning_dashboard/analytics.py`: `compute_recent_incorrectness()`, `_compute_slope()`
- `code/learning_dashboard/analytics.py`: `compute_student_struggle_scores()`, `classify_score()`
- `code/learning_dashboard/config.py`: struggle weights and thresholds
- `code/learning_dashboard/instructor_app.py`: `_render_lab_assignment_panel()`
- `code/learning_dashboard/assistant_app.py`: `render_unassigned_view()`
