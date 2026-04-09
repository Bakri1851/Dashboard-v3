Part of [[Lab App]] · see also [[Assistant App/Operations/Next Steps]]

# Next Steps — Lab App

Implementation specifications for the instructor dashboard phases. For assistant app phases (Phase 0d, 0e, Phase 6) see [[Assistant App/Operations/Next Steps]].

Related: [[Known Issues]], [[Instructor Dashboard]], [[Analytics Engine]], [[Coding Roadmap]]

See [[Coding Roadmap]] for a phase-by-phase status overview.

---

## Report alignment items

These are implemented features that are not yet documented in the thesis and must be added before submission:

- [ ] **Improvement trajectory** — linear regression slope over time per student. Document in Ch3/Ch4.
- [ ] **Answer repetition rate** — `rep_hat` signal in 7-component struggle model. Document in Ch3/Ch4.
- [ ] **Bayesian shrinkage** — applied to all struggle signals. Document in Ch3/Ch4.
- [ ] **Temporal smoothing** — currently stubbed out (`SMOOTHING_ENABLED = False`). Reconcile with Ch3 design section.

---

## Implementation phases

All new models live in `code/learning_dashboard/models/` behind a feature flag (`improved_models_enabled` in session state). The baseline in `analytics.py` is never modified — improved models coexist alongside it.

### Dependency graph

```
Phase 0 (bugs)        → independent, do first
Phase 1 (measurement) → independent
Phase 2 (IRT)         → independent
Phase 3 (BKT)         → independent
Phase 4 (improved)    → requires Phase 2 + Phase 3
Phase 5 (comparison)  → requires Phase 4
```

Phases 0–3 can be developed in parallel. Each phase is independently deployable.

### New files created across all phases

- `code/learning_dashboard/models/__init__.py`
- `code/learning_dashboard/models/measurement.py`
- `code/learning_dashboard/models/irt.py`
- `code/learning_dashboard/models/bkt.py`
- `code/learning_dashboard/models/improved_struggle.py`

### New dependencies

None beyond what is already installed. `scipy` is available transitively via `scikit-learn`. Add `scipy>=1.11.0` to `requirements.txt` for explicit declaration.

---

## Phase 0: Bug fixes (instructor-side)

- [x] Complete

Targeted fixes for the instructor app and analytics engine. See [[Assistant App/Operations/Next Steps]] for Phase 0d (assistant data scope) and 0e (name collision on rejoin).

### 0a. Session sound miswiring

- **File:** `code/learning_dashboard/instructor_app.py` ~lines 456–459
- **Fix:** Replace `play_selection()` with `play_session_start()` / `play_session_end()` based on whether session transitioned active→inactive or inactive→active
- **Ref:** `sound.play_session_start()` and `sound.play_session_end()` already exist in `code/learning_dashboard/sound.py`

### 0b. Analytics cache key weakness

- **File:** `code/learning_dashboard/instructor_app.py` ~line 582
- **Current key:** `(len(df), str(df["timestamp"].min()), str(df["timestamp"].max()))`
- **Problem:** If contents change while row count and timestamp range stay the same, stale results are reused
- **Fix:** Add content fingerprint to cache key, e.g. `pd.util.hash_pandas_object(df).sum()` or a column checksum

### 0c. Cluster cache key too coarse

- **File:** `code/learning_dashboard/analytics.py` ~line 605
- **Current key:** `(question_id, total_wrong)`
- **Problem:** Different wrong answers with the same count reuse stale cluster output
- **Fix:** Include a hash of the actual wrong answer content in the cache key

### Phase 0 verification (instructor-side)

- Modify data while row count stays same — verify analytics recompute (not cached)
- Trigger session start/end — verify correct sounds play (`play_session_start` / `play_session_end`)

---

## Phase 1: AI incorrectness as measurement signal

- [x] Complete

**Goal:** Add confidence metadata to incorrectness scores without changing existing values. The project already uses AI-derived incorrectness; this phase makes explicit that it is a measurement signal, not ground truth.

### New file: `code/learning_dashboard/models/measurement.py`

**Function:** `compute_incorrectness_with_confidence(df) -> DataFrame`
- Wraps existing `analytics.compute_incorrectness_column()`
- Adds columns:
  - `incorrectness_confidence` — heuristic float [0,1] based on feedback length + score extremity
  - `incorrectness_source` — string, always `"gpt-4o-mini"` for traceability

**Confidence heuristic (no extra API calls):**
- Empty/null feedback → confidence 0.0 (the 0.5 default is a prior, not a measurement)
- Short feedback (<20 chars) → low confidence (0.3–0.5)
- Scores near 0.0 or 1.0 → higher confidence (clearer cases)
- Scores near 0.5 → lower confidence (ambiguous)
- Formula: `confidence = base_conf * length_factor * extremity_factor`

### Config additions in `code/learning_dashboard/config.py`

```python
MEASUREMENT_CONFIDENCE_MIN_LENGTH: int = 20
MEASUREMENT_CONFIDENCE_BASE: float = 0.7
```

### Integration

- `code/learning_dashboard/instructor_app.py` ~line 594: call measurement wrapper alongside existing incorrectness computation
- `code/learning_dashboard/ui/components.py`: optionally show a confidence indicator (opacity or dot) next to incorrectness values in drill-down views
- Existing `incorrectness` column is unchanged — all downstream code is unaffected

### Verification

- Spot-check confidence values for known feedback strings (empty, short, long, clearly correct/incorrect)
- Verify existing `incorrectness` values are bit-identical to baseline output

---

## Phase 2: IRT-based difficulty model

- [x] Complete

**Goal:** Add a 1-Parameter Logistic (Rasch) IRT model that estimates question difficulty as a latent parameter, alongside the existing weighted difficulty score.

### New file: `code/learning_dashboard/models/irt.py`

Uses `scipy.optimize.minimize` (L-BFGS-B). No new pip dependencies.

**Mathematical model:**

```
P(correct | theta_j, b_i) = sigmoid(theta_j - b_i)
```

where `theta_j` is student ability and `b_i` is question difficulty. Both are latent parameters estimated jointly via maximum likelihood.

**Functions:**
- `build_response_matrix(df, correct_threshold=0.5) -> DataFrame` — student x question binary matrix. Uses the best attempt per student-question pair. Binary threshold at `config.CORRECT_THRESHOLD` (0.5).
- `fit_rasch_model(response_matrix, max_iter=100) -> dict` — joint MLE for difficulty (`b_i`) and ability (`theta_j`). Returns `{"difficulty": {qid: float}, "ability": {uid: float}, "convergence": bool, "log_likelihood": float}`.
- `compute_irt_difficulty_scores(df) -> DataFrame` — wrapper returning DataFrame compatible with baseline `difficulty_df` structure. Columns: `question`, `irt_difficulty`, `irt_difficulty_level`, `irt_difficulty_color`. Raw `b_i` on logit scale is mapped to [0,1] via sigmoid for UI compatibility.

**Edge cases:**
- Questions attempted by <2 students → fallback difficulty 0.0 (no information)
- Students who attempted <2 questions → fallback ability 0.0
- Standard errors computed from inverse Fisher information (diagonal approximation)

### Config additions in `code/learning_dashboard/config.py`

```python
IRT_MIN_ATTEMPTS_PER_QUESTION: int = 2
IRT_MIN_ATTEMPTS_PER_STUDENT: int = 2
IRT_MAX_ITER: int = 100
IRT_DIFFICULTY_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.00, 0.35, "Easy",      "#00ff88"),
    (0.35, 0.50, "Medium",    "#ffcc00"),
    (0.50, 0.75, "Hard",      "#ff6600"),
    (0.75, 1.00, "Very Hard", "#ff2d55"),
]
```

### Integration

- Computed in `code/learning_dashboard/instructor_app.py` behind a feature flag (`improved_models_enabled`)
- Stored in `st.session_state["_irt_difficulty_df"]`
- Consumed by Phase 4 (improved struggle) and Phase 5 (comparison UI)

### Verification

- Synthetic test: questions with 90% correct rate should get low difficulty; 10% correct should get high difficulty
- Verify difficulty ordering aligns with baseline difficulty ordering on real data
- Test convergence with small datasets (5 students, 3 questions)

---

## Phase 3: BKT-based mastery tracking

- [x] Complete

**Goal:** Add per-student per-question mastery tracking via Bayesian Knowledge Tracing. Mastery is explicitly distinct from live struggle — it represents accumulated knowledge over time.

### New file: `code/learning_dashboard/models/bkt.py`

Pure numpy computation. No new pip dependencies.

**Mathematical model — standard BKT with 4 parameters per skill:**

```
P(L_0)  = prior probability of knowing skill before any practice
P(T)    = probability of learning skill on each opportunity
P(G)    = probability of guessing correctly without knowing
P(S)    = probability of slipping (wrong despite knowing)
```

Update rule after observation:
```
P(L_t | correct) = P(L_t) * (1 - P(S)) / P(correct)
P(L_t | wrong)   = P(L_t) * P(S) / P(wrong)
P(L_{t+1})       = P(L_t | obs) + (1 - P(L_t | obs)) * P(T)
```

Each question is treated as a skill (simplest mapping). Observations derived from `incorrectness` column: `correct = (incorrectness < CORRECT_THRESHOLD)`. Submissions processed chronologically per student per question.

**Functions:**
- `bkt_update(p_mastery, correct, params) -> float` — single HMM update step
- `compute_student_mastery(student_df, params) -> dict[str, float]` — replay one student's submission history chronologically, return `{question_id: P(L_final)}`
- `compute_all_mastery(df) -> DataFrame` — all students, all questions. Columns: `user`, `question`, `mastery`, `n_attempts`
- `compute_student_mastery_summary(df) -> DataFrame` — per-student aggregate. Columns: `user`, `mean_mastery`, `min_mastery`, `mastered_count`, `total_questions`

### Config additions in `code/learning_dashboard/config.py`

```python
BKT_P_INIT: float = 0.3      # prior probability of knowing
BKT_P_LEARN: float = 0.1     # probability of learning per opportunity
BKT_P_GUESS: float = 0.2     # guess rate
BKT_P_SLIP: float = 0.1      # slip rate
BKT_MASTERY_THRESHOLD: float = 0.95  # P(L) above this = "mastered"
```

### Integration

- Computed behind same feature flag as IRT (`improved_models_enabled`)
- Stored in `st.session_state["_mastery_df"]` and `st.session_state["_mastery_summary_df"]`
- Consumed by Phase 4 (improved struggle model)

### Verification

- 5 consecutive correct answers → mastery approaches 1.0
- Alternating correct/wrong → mastery plateaus at moderate level
- Empty data → empty DataFrame (no crash)

---

## Phase 4: Improved struggle model (mastery-aware)

- [x] Complete

**Goal:** Struggle score that incorporates IRT difficulty and BKT mastery alongside behavioral signals from the baseline. Requires Phase 2 (IRT) and Phase 3 (BKT).

### New file: `code/learning_dashboard/models/improved_struggle.py`

**Function:** `compute_improved_struggle_scores(df, mastery_summary=None, irt_difficulty=None) -> DataFrame`

**Three signal groups with weights:**

1. **Behavioral (0.45):** baseline behavioral composite — the live-session signals (A_raw weighted recent incorrectness, r_hat retry rate, d_hat trajectory, rep_hat repetition). These are recomputed internally, not imported from the baseline function.
2. **Mastery gap (0.30):** `mean_mastery - recent_performance`. A large positive gap means the student is performing below their demonstrated ability — a strong struggle signal. A negative gap means performing above demonstrated ability (not struggling).
3. **Difficulty-adjusted (0.25):** `recent_incorrectness * (1 - normalized_irt_difficulty)` averaged across recent questions. Failing easy questions (low IRT difficulty) is more concerning than failing hard questions.

**Graceful degradation:** If BKT mastery is unavailable (too few submissions or feature disabled), the mastery_gap weight is redistributed to behavioral. If IRT difficulty is unavailable, the difficulty-adjusted weight is redistributed. At the extreme of no additional data, the model collapses to a behavioral-only model.

### Config additions in `code/learning_dashboard/config.py`

```python
IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL: float = 0.45
IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP: float = 0.30
IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ: float = 0.25
```

### Output

- Compatible with baseline `struggle_df` structure (same columns: `user`, `struggle_score`, `struggle_level`, `struggle_color`)
- Additional diagnostic columns: `mastery_gap`, `difficulty_adjusted_score`
- Uses the same `STRUGGLE_THRESHOLDS` from config for level classification

### Verification

- High-mastery student suddenly failing → higher improved score than baseline (mastery gap signal fires)
- Low-mastery student failing hard questions → lower improved score than baseline (expected difficulty, not surprising)
- Graceful degradation: run with `mastery_summary=None`, with `irt_difficulty=None`, with both `None`

---

## Phase 5: Comparison UI

- [ ] Complete

**Goal:** Side-by-side view of baseline vs improved model results, enabling instructors to see where models agree and disagree.

### Modified files

- `code/learning_dashboard/ui/views.py` — add `comparison_view()` function
- `code/learning_dashboard/ui/components.py` — add comparison-specific components
- `code/learning_dashboard/instructor_app.py` — add "Model Comparison" to view routing radio + settings toggle for improved models

### New components in `code/learning_dashboard/ui/components.py`

- `render_comparison_scatter(baseline_scores, improved_scores, labels, title)` — scatter plot with baseline on x-axis, improved on y-axis, diagonal reference line. Points above the line: improved model rates higher struggle/difficulty.
- `render_comparison_table(baseline_df, improved_df, entity_col, score_cols, level_cols)` — table sorted by absolute delta (biggest disagreements first). Columns: Entity, Baseline Score, Baseline Level, Improved Score, Improved Level, Delta.
- `render_agreement_summary(baseline_levels, improved_levels)` — summary cards showing total agreement %, level-change counts, biggest disagreements.

### View layout

1. Toggle between "Student Struggle Comparison" and "Question Difficulty Comparison"
2. Agreement summary cards at top
3. Scatter plot (baseline vs improved)
4. Table of biggest disagreements with expandable detail

### Settings additions in `settings_view`

- Toggle: "Enable Improved Models" (default off) — this is the `improved_models_enabled` feature flag
- When enabled, sub-toggles for IRT, BKT, Improved Struggle
- BKT parameter sliders for experimentation (P_init, P_learn, P_guess, P_slip)

### Verification

- Improved models disabled → comparison view shows informative message ("Enable improved models in Settings to use this view")
- Improved models enabled → renders correctly with various data sizes
- Click-through from comparison table to student/question detail still works

---

## Conceptual additions that should now be reflected in the project

### Student struggle

The project already implements a baseline struggle score (Phase 0 preserves it). Phase 4 adds the improved concept so that struggle is treated more explicitly as:
- temporal (exponential time decay in A_raw)
- behavioural (retry rate, answer repetition, trajectory)
- live-session based (recent submissions weighted heavily)
- distinct from overall student ability (mastery gap separates knowledge from current performance)
- potentially informed by partially latent state (BKT mastery as hidden state)

### Task difficulty

The project already implements a baseline difficulty score (Phase 0 preserves it). Phase 2 adds the improved concept so that task difficulty is treated more explicitly as:
- separate from student struggle (IRT difficulty is a question-level parameter)
- question-level (estimated per question)
- class-level (estimated from all students' responses)
- a latent property (IRT treats difficulty as unobserved, estimated via MLE)

### AI-derived correctness / incorrectness

The project already uses AI-derived incorrectness. Phase 1 adds the measurement concept so the project reflects more clearly that this is:
- semantically useful (feeds both struggle and difficulty models)
- informative for both struggle and difficulty
- imperfect (confidence metadata makes uncertainty explicit)
- a measurement layer rather than unquestioned truth (source tracking, confidence heuristic)

### Knowledge tracing / BKT

Phase 3 adds BKT so the project reflects that:
- mastery evolves over time (BKT update rule applied chronologically)
- mastery is useful (feeds into improved struggle model)
- mastery is not the same thing as live struggle (mastery is accumulated knowledge; struggle is current-session behavior)

### Item Response Theory

Phase 2 adds IRT so the project reflects that:
- question difficulty moves beyond raw weighted counts (latent parameter estimation via MLE)
- difficulty is treated as a latent property of the task (Rasch model)

### Collaborative filtering

Collaborative filtering is already present. It remains:
- an alternative method (not integrated into main struggle score)
- a secondary signal (diagnostic panel only)
- not the main modelling core (baseline + improved models are the conceptual backbone)

---

## Phase 10: In-app Help system

- [ ] Complete

**Goal:** Add a Help area under the existing Settings section of the instructor dashboard. The Help area serves two distinct purposes: (1) explain how to operate the dashboard in practice, and (2) explain the metrics and methodology in an interpretable way. Content should be written to accommodate a dashboard that is still evolving — avoid hardcoding implementation details that may change.

### Modified/new files

- `code/learning_dashboard/ui/views.py` — add `help_view()` function
- `code/learning_dashboard/ui/components.py` — add Help-specific components (tour step renderer, metric card, layered-maths block, tooltip wrapper, reliability badge)
- `code/learning_dashboard/instructor_app.py` — add "Help" option to the Settings navigation (or as a sidebar/settings sub-panel depending on UI structure at time of implementation)
- `code/learning_dashboard/ui/theme.py` — any CSS additions needed for Help UI; must match the existing sci-fi neon theme

---

### Sub-task 1: Add Help area under Settings

- [ ] Add a "Help" tab or expandable section within the Settings page in `instructor_app.py` / `views.py`
- [ ] Decide on UI structure at implementation time: full page, sidebar section, or expandable panel — document the decision
- [ ] Ensure the Help entry point does not appear in the main view routing radio (it should be accessed via Settings, not as a top-level page)

---

### Sub-task 2: Quick Tour / onboarding walkthrough

- [ ] Add a collapsible or step-through "Quick Tour" component to `help_view()` that walks a first-time user through the dashboard
- [ ] Tour steps should cover: joining/starting a session, reading the main in-class view, using filters, navigating to student and question detail, and accessing Settings
- [ ] Keep tour steps short (1–2 sentences each) and anchored to current UI labels — update tour text if UI labels change
- [ ] Consider whether to show the tour automatically on first load (using session_state flag) or only on demand — decide at implementation time and document
- [ ] Acceptance criterion: a new user with no prior context can complete the tour and understand the main workflow

---

### Sub-task 3: Help Centre — practical usage guidance

Add a "Help Centre" sub-section within `help_view()` with clearly labelled how-to content. Use expandable `st.expander` blocks or tabs to avoid overwhelming the page. Content to include:

- [ ] **Starting and ending a session** — how to generate a session code, what happens when a session starts/ends, how to find the session code for assistants
- [ ] **Switching between views** — in-class overview, student detail, question detail, data analysis; how to navigate back
- [ ] **How filtering works** — module filter, time window filter, live session start filter, saved session window; explain the filter application order
- [ ] **Refresh, save, and previous sessions** — how auto-refresh works (TTL), how to save a snapshot, how to load a previous session and what data is shown
- [ ] **Reading top summary metrics** — what the headline cards (struggle counts, difficulty counts) represent; how leaderboard rankings are determined
- [ ] **Reading leaderboards and charts** — how to click through from a leaderboard entry to a detail view
- [ ] Acceptance criterion: each item can be read and understood in under 60 seconds by an instructor unfamiliar with the codebase

---

### Sub-task 4: Model Guide — methodology and metrics

Add a "Model Guide" sub-section within `help_view()` explaining the analytical models. Use layered depth (see Sub-task 6 below for the maths layer). Content to include:

- [ ] **Student struggle metric** — what it measures (current-session distress, not overall ability), which signals feed into it, how the score maps to colour bands
- [ ] **Question difficulty metric** — what it measures (class-level question hardness), which signals feed into it, how IRT difficulty differs from the raw weighted score
- [ ] **Why recent submissions matter more** — explain exponential time-decay weighting and the recency bias; use plain language (e.g. "a mistake made 5 minutes ago counts more than one made an hour ago")
- [ ] **What smoothing does** — explain the temporal smoothing stub (`SMOOTHING_ENABLED`); note its current status and what activating it would change
- [ ] **Thresholds and colour bands** — how the four levels (On Track / Minor Issues / Struggling / Needs Help) are defined; that they are configurable thresholds, not fixed rules
- [ ] **Limitations in low-data or early-session settings** — minimum submission counts, what happens with 1–2 submissions, why scores become more reliable over time
- [ ] Acceptance criterion: a non-technical instructor can read the plain-English layer and understand what a score means without reading the code

---

### Sub-task 5: Contextual explanations in the live dashboard

These are inline explanations tied to data currently on screen, not generic documentation. Add alongside existing UI components in `components.py` and the relevant `views.py` sections.

- [ ] **Metric tooltips** — add `help=` parameter (Streamlit native) or a small `ℹ` icon with `st.tooltip`-style popover to key metrics: struggle score, incorrectness %, difficulty score, mastery level, confidence indicator. Tooltip text should be 1–2 sentences max.
- [ ] **"Why was this flagged?" — student card** — when a student is shown as Struggling or Needs Help, add an expandable explanation block showing which signals contributed (e.g. high recent incorrectness, high retry rate). Pull from the computed struggle score components already in the DataFrame.
- [ ] **"Why was this flagged?" — question card** — when a question is flagged as Hard or Very Hard, show which inputs drove the rating (e.g. low class-correct rate, high IRT difficulty estimate).
- [ ] **Mini explanations for current data** — in the data analysis view, add short contextual notes near charts explaining what the chart shows in the context of the current session (e.g. "Most students are on question 3 — difficulty is rated Medium based on X attempts so far")
- [ ] Acceptance criterion: a user hovering over or expanding any flagged metric can understand why it was flagged without leaving the page

---

### Sub-task 6: Layered maths documentation

Add a "Methodology" or "Under the Hood" expandable block within the Model Guide for each metric. Use three nested layers so users can engage at their preferred depth.

For each metric (struggle, difficulty, incorrectness, mastery):

- [ ] **Layer 1 — Plain English** — 2–4 sentences describing what the model does and why, with no symbols
- [ ] **Layer 2 — Formula summary** — simplified pseudocode or informal notation showing the key inputs and how they combine (e.g. `struggle ≈ 0.38 × recent_incorrectness + 0.20 × mean_incorrectness + …`)
- [ ] **Layer 3 — Full notation** — proper mathematical notation with variable definitions; can be rendered as LaTeX via `st.latex()` or as a styled code block if LaTeX is not available in the current Streamlit version
- [ ] Each layer should be in a collapsible section so the page is not overwhelming by default
- [ ] Acceptance criterion: a reader who only expands Layer 1 still gets a useful, accurate description; a reader who expands all three layers gets enough detail to reproduce the model

---

### Sub-task 7: Reliability and transparency indicators

Add lightweight in-UI signals that make uncertainty and data limitations visible. Implement in `components.py` as reusable badge/indicator components.

- [ ] **Early session indicator** — show a "Early Session" badge or note when fewer than N submissions exist for a student or question (threshold configurable in `config.py`; suggest `HELP_EARLY_SESSION_MIN_SUBMISSIONS = 5`). Shown on student cards and question cards.
- [ ] **Limited data warning** — when a metric is computed from a very small sample (e.g. 1–2 students attempted a question for difficulty, or 1–2 submissions for a student's struggle), show a muted "(limited data)" label alongside the metric value
- [ ] **Confidence indicator** — surface the existing `incorrectness_confidence` value (from `models/measurement.py`, Phase 1) in the UI where incorrectness is displayed. Use a dot or opacity scale rather than a raw number.
- [ ] **Experimental signal label** — if improved models are enabled (IRT, BKT, improved struggle), label those metrics clearly as "Experimental" in the UI so instructors know they are newer, less validated models
- [ ] Acceptance criterion: an instructor can see at a glance whether a metric is reliable or should be treated with caution

---

### Sub-task 8: Troubleshooting and help content for confusing states

Add a "Troubleshooting" sub-section in `help_view()` covering states that may confuse users. Use expandable blocks.

- [ ] **No data showing** — what to check (API endpoint, session active, time window filter applied too narrowly, no submissions yet)
- [ ] **Struggle scores not updating** — cache TTL explanation (`@st.cache_data(ttl=10)`), how to force a refresh
- [ ] **Lab assistant not appearing in instructor sidebar** — session code mismatch, app not running on port 8502
- [ ] **Previous session data missing** — where saved sessions are stored, what file format they use, what happens if the file is missing
- [ ] **All students showing "On Track"** — explain that early in a session this is expected; note minimum submission thresholds
- [ ] **Improved models toggle has no visible effect** — explain that comparison view must be opened separately; note data volume requirements for IRT/BKT
- [ ] Acceptance criterion: the most common support questions can be answered by the troubleshooting section without needing to read the code

---

### Sub-task 9: Design and UI consistency

- [ ] Review Help UI against the existing sci-fi neon theme (`ui/theme.py`) before finalising — target the instructor dashboard CSS, not the mobile assistant CSS
- [ ] Help content must not intrude on the live teaching workflow — it should only appear when the user navigates to Settings → Help
- [ ] Text contrast, font size, and expandable panel styling should match the rest of the dashboard
- [ ] If any new icons or visual elements are added for tooltips or reliability badges, ensure they are consistent with existing icon usage in `components.py`
- [ ] Acceptance criterion: a screenshot of the Help view is visually consistent with a screenshot of the in-class view

---

### Phase 10 verification

- Navigate to Settings → confirm Help area is accessible
- Open Quick Tour → confirm each step renders and makes sense without prior dashboard knowledge
- Open Help Centre → confirm each how-to section is present and readable
- Open Model Guide → confirm all three maths layers render for at least the struggle metric
- Hover over / expand a flagged student card → confirm "Why was this flagged?" block appears with signal breakdown
- Toggle improved models on → confirm "Experimental" labels appear on relevant metrics
- Syntax check: `python -m py_compile code/learning_dashboard/ui/views.py code/learning_dashboard/ui/components.py code/learning_dashboard/instructor_app.py`

---

## Documentation follow-up

- update vault notes so they clearly mark what is already implemented vs what is being added next
- keep the vault aligned with the report's newer conceptual direction
- make sure the vault clearly distinguishes:
  - baseline struggle model (in `analytics.py`, unchanged)
  - improved struggle concept (in `models/improved_struggle.py`, Phase 4)
  - baseline difficulty model (in `analytics.py`, unchanged)
  - improved difficulty concept (in `models/irt.py`, Phase 2)
  - AI-derived measurement (in `models/measurement.py`, Phase 1)
  - BKT / knowledge tracing (in `models/bkt.py`, Phase 3)
  - IRT (in `models/irt.py`, Phase 2)
  - collaborative filtering as an alternative method (in `analytics.py`, unchanged)

## Code references

- instructor app: `code/learning_dashboard/instructor_app.py`
- assistant app: `code/learning_dashboard/assistant_app.py`
- lab session state: `code/learning_dashboard/lab_state.py`
- analytics engine: `code/learning_dashboard/analytics.py`
- baseline struggle model: `analytics.compute_student_struggle_scores()` (lines 181–290)
- baseline difficulty model: `analytics.compute_question_difficulty_scores()` (lines 437–528)
- AI-derived incorrectness scoring: `analytics.compute_incorrectness_column()` (lines 68–85)
- collaborative filtering: `analytics.compute_cf_struggle_scores()` (lines 300–384)
- mistake clustering: `analytics.cluster_question_mistakes()` (lines 580–706)
- future IRT-based difficulty: `code/learning_dashboard/models/irt.py` (Phase 2)
- future mastery-aware struggle: `code/learning_dashboard/models/improved_struggle.py` (Phase 4)
- future BKT mastery tracking: `code/learning_dashboard/models/bkt.py` (Phase 3)
- future measurement layer: `code/learning_dashboard/models/measurement.py` (Phase 1)
