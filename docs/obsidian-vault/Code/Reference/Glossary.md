# Glossary

This glossary defines the project terms that recur across the dashboard, analytics code, and session-state model. It is intentionally practical rather than theoretical, so the definitions match how the code currently behaves.

Related: [[Student Struggle Logic]], [[Question Difficulty Logic]], [[Instructor Dashboard]], [[Lab Assistant System]]

## Terms

- `Incorrectness`: continuous score in `[0, 1]` derived from `ai_feedback` text through OpenAI; lower means more correct.
- `CORRECT_THRESHOLD`: cutoff used to treat an attempt as correct vs incorrect; currently `0.5`.
- `Struggle score`: per-student weighted aggregate used for the student leaderboard.
- `Difficulty score`: per-question weighted aggregate used for the question leaderboard.
- `A_raw`: recent incorrectness term for student struggle, using the last 5 submissions with exponential time decay.
- `d_hat`: normalized slope of a student's incorrectness over time; positive means worsening performance.
- `rep_hat`: rate at which a student exactly repeats the same answer on the same question.
- `CF`: collaborative filtering layer over normalized student-behavior features; currently shown diagnostically.
- `Live session`: instructor-started time window that begins at `session_start` and coordinates assistants through a shared code.
- `Saved session`: persisted record with a fixed `start_time` and `end_time`, reloaded from `data/saved_sessions.json`.
- `Dashboard filter state`: general UI filters such as time filter, today-only scope, and secondary module filter.
- `Live session state`: session-specific runtime keys such as `session_active`, `session_start`, and `lab_session_code`.
- `Saved session state`: keys such as `loaded_session_id`, `loaded_session_start`, and `loaded_session_end`.
- `Self-allocation`: assistant ability to claim a student without instructor assignment when enabled.
- `Session code`: 6-character code that assistants use to join the live lab session.
- `Assignment status`: either `helping` or `helped` for a student/assistant pairing in shared state.

## Thesis and requirements terms

- `V1`: proof-of-concept prototype described in the thesis implementation chapter (January 2026 milestone).
- `V2`: full implementation (Dashboard-v3) with all scoring models, lab assistant system, and advanced features.
- `Functional requirement (FR)`: system capability the dashboard must provide; FR1-FR7 defined in [[Ch2 – Background and Requirements]].
- `Non-functional requirement (NFR)`: quality attribute the system must satisfy; NFR1-NFR6 defined in [[Ch2 – Background and Requirements]].
- `MoSCoW`: prioritisation framework (Must/Should/Could/Won't) used to scope implementation phases.
- `SAM`: early learning analytics dashboard separating at-risk students by time/resource use.
- `EMODA`: emotion-aware learning dashboard using audio/video/self-reports.
- `Edsight`: responsive web-based learning analytics dashboard for educators.

## IRT and improved models

- `IRT`: Item Response Theory — probabilistic framework treating difficulty as a latent parameter estimated from response patterns.
- `Rasch model`: 1-parameter logistic IRT model estimating question difficulty and student ability jointly via MLE.
- `irt_difficulty`: IRT-estimated difficulty mapped to [0, 1] via sigmoid; alternative to baseline `difficulty_score`.
- `improved_models_enabled`: feature flag in session state gating IRT, BKT, and improved struggle models.
- `Response matrix`: binary student x question matrix used as IRT input; built from best attempt per pair.

## BKT and mastery tracking

- `BKT`: Bayesian Knowledge Tracing — HMM-based model that estimates the probability a student has learned a skill (question) from their submission history.
- `P(L)`: latent mastery probability for a student-question pair; updated after each observation via Bayes' rule + learning transition.
- `P(L_0)` / `BKT_P_INIT`: prior probability of knowing a skill before any practice (default 0.3).
- `P(T)` / `BKT_P_LEARN`: probability of learning on each attempt (default 0.1).
- `P(G)` / `BKT_P_GUESS`: probability of guessing correctly without knowing (default 0.2).
- `P(S)` / `BKT_P_SLIP`: probability of a wrong answer despite knowing (default 0.1).
- `BKT_MASTERY_THRESHOLD`: P(L) above 0.95 classifies a student-question pair as "mastered".
- `mastery_df`: per-student per-question mastery DataFrame cached in session state.
- `mastery_summary_df`: per-student aggregate mastery statistics (mean, min, mastered count).

## Code references

- `learning_dashboard/config.py`
- `learning_dashboard/analytics.py`
- `learning_dashboard/instructor_app.py`
- `learning_dashboard/lab_state.py`
- `data/saved_sessions.json`
- `data/lab_session.json`
