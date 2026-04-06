# Next Steps

The project already has a working baseline system. This includes:

- a live instructor dashboard
- a mobile lab assistant app
- live and saved session support
- assistant assignment / self-claim / helped-state flows
- a baseline student struggle model
- a baseline task difficulty model
- AI-derived incorrectness scoring
- collaborative filtering
- mistake clustering

The next phase is therefore **not** about building these from scratch. It is about adding the new modelling concepts now reflected in the report, while keeping the current system as the baseline for comparison.

Related: [[Known Issues]], [[Instructor Dashboard]], [[Lab Assistant System]], [[Analytics Engine]]

---

## Implementation phases

All new models live in `learning_dashboard/models/` behind a feature flag (`improved_models_enabled` in session state). The baseline in `analytics.py` is never modified — improved models coexist alongside it.

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

- `learning_dashboard/models/__init__.py`
- `learning_dashboard/models/measurement.py`
- `learning_dashboard/models/irt.py`
- `learning_dashboard/models/bkt.py`
- `learning_dashboard/models/improved_struggle.py`

### New dependencies

None beyond what is already installed. `scipy` is available transitively via `scikit-learn`. Add `scipy>=1.11.0` to `requirements.txt` for explicit declaration.

---

## Phase 0: Bug fixes (from Known Issues)

- [x] Complete

5 targeted fixes, no architectural changes. All issues are documented in [[Known Issues]].

### 0a. Session sound miswiring

- **File:** `learning_dashboard/instructor_app.py` ~lines 456–459
- **Fix:** Replace `play_selection()` with `play_session_start()` / `play_session_end()` based on whether session transitioned active→inactive or inactive→active
- **Ref:** `sound.play_session_start()` and `sound.play_session_end()` already exist in `learning_dashboard/sound.py`

### 0b. Analytics cache key weakness

- **File:** `learning_dashboard/instructor_app.py` ~line 582
- **Current key:** `(len(df), str(df["timestamp"].min()), str(df["timestamp"].max()))`
- **Problem:** If contents change while row count and timestamp range stay the same, stale results are reused
- **Fix:** Add content fingerprint to cache key, e.g. `pd.util.hash_pandas_object(df).sum()` or a column checksum

### 0c. Cluster cache key too coarse

- **File:** `learning_dashboard/analytics.py` ~line 605
- **Current key:** `(question_id, total_wrong)`
- **Problem:** Different wrong answers with the same count reuse stale cluster output
- **Fix:** Include a hash of the actual wrong answer content in the cache key

### 0d. Assistant data scope mismatch

- **File:** `learning_dashboard/assistant_app.py` ~lines 19–25
- **Problem:** `_load_student_data()` calls `data_loader.load_data()` without applying the instructor's active live-session window. Assistants can see students outside the instructor's current teaching scope.
- **Fix:** Add a `session_start` ISO timestamp field to `lab_session.json` (set in `start_lab_session()`). In the assistant app, read this from lab state and filter the DataFrame to only include submissions after `session_start` before computing struggle scores.
- **Also touches:** `learning_dashboard/lab_state.py` — add `session_start` to `_default_state()` and `start_lab_session()`

### 0e. Name collision on rejoin

- **File:** `learning_dashboard/lab_state.py` ~lines 192–195
- **Problem:** When a name matches an existing assistant case-insensitively, `join_session()` returns the old `assistant_id` with potentially stale `assigned_student` state
- **Fix:** When returning an existing assistant_id on name match, clear `assigned_student` to `None` so the rejoining assistant starts fresh

### Verification

- Start session, join as assistant, leave, rejoin with same name — verify fresh state (no inherited assignment)
- Trigger session start/end — verify correct sounds play (`play_session_start` / `play_session_end`)
- Modify data while row count stays same — verify analytics recompute (not cached)
- Check assistant app shows only students within instructor's session window

---

## Phase 1: AI incorrectness as measurement signal

- [x] Complete

**Goal:** Add confidence metadata to incorrectness scores without changing existing values. The project already uses AI-derived incorrectness; this phase makes explicit that it is a measurement signal, not ground truth.

### New file: `learning_dashboard/models/measurement.py`

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

### Config additions in `learning_dashboard/config.py`

```python
MEASUREMENT_CONFIDENCE_MIN_LENGTH: int = 20
MEASUREMENT_CONFIDENCE_BASE: float = 0.7
```

### Integration

- `learning_dashboard/instructor_app.py` ~line 594: call measurement wrapper alongside existing incorrectness computation
- `learning_dashboard/ui/components.py`: optionally show a confidence indicator (opacity or dot) next to incorrectness values in drill-down views
- Existing `incorrectness` column is unchanged — all downstream code is unaffected

### Verification

- Spot-check confidence values for known feedback strings (empty, short, long, clearly correct/incorrect)
- Verify existing `incorrectness` values are bit-identical to baseline output

---

## Phase 2: IRT-based difficulty model

- [x] Complete

**Goal:** Add a 1-Parameter Logistic (Rasch) IRT model that estimates question difficulty as a latent parameter, alongside the existing weighted difficulty score.

### New file: `learning_dashboard/models/irt.py`

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

### Config additions in `learning_dashboard/config.py`

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

- Computed in `learning_dashboard/instructor_app.py` behind a feature flag (`improved_models_enabled`)
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

### New file: `learning_dashboard/models/bkt.py`

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

### Config additions in `learning_dashboard/config.py`

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

- [ ] Complete

**Goal:** Struggle score that incorporates IRT difficulty and BKT mastery alongside behavioral signals from the baseline. Requires Phase 2 (IRT) and Phase 3 (BKT).

### New file: `learning_dashboard/models/improved_struggle.py`

**Function:** `compute_improved_struggle_scores(df, mastery_summary=None, irt_difficulty=None) -> DataFrame`

**Three signal groups with weights:**

1. **Behavioral (0.45):** baseline behavioral composite — the live-session signals (A_raw weighted recent incorrectness, r_hat retry rate, d_hat trajectory, rep_hat repetition). These are recomputed internally, not imported from the baseline function.
2. **Mastery gap (0.30):** `mean_mastery - recent_performance`. A large positive gap means the student is performing below their demonstrated ability — a strong struggle signal. A negative gap means performing above demonstrated ability (not struggling).
3. **Difficulty-adjusted (0.25):** `recent_incorrectness * (1 - normalized_irt_difficulty)` averaged across recent questions. Failing easy questions (low IRT difficulty) is more concerning than failing hard questions.

**Graceful degradation:** If BKT mastery is unavailable (too few submissions or feature disabled), the mastery_gap weight is redistributed to behavioral. If IRT difficulty is unavailable, the difficulty-adjusted weight is redistributed. At the extreme of no additional data, the model collapses to a behavioral-only model.

### Config additions in `learning_dashboard/config.py`

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

- `learning_dashboard/ui/views.py` — add `comparison_view()` function
- `learning_dashboard/ui/components.py` — add comparison-specific components
- `learning_dashboard/instructor_app.py` — add "Model Comparison" to view routing radio + settings toggle for improved models

### New components in `learning_dashboard/ui/components.py`

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

- instructor app: `learning_dashboard/instructor_app.py`
- assistant app: `learning_dashboard/assistant_app.py`
- lab session state: `learning_dashboard/lab_state.py`
- analytics engine: `learning_dashboard/analytics.py`
- baseline struggle model: `analytics.compute_student_struggle_scores()` (lines 181–290)
- baseline difficulty model: `analytics.compute_question_difficulty_scores()` (lines 437–528)
- AI-derived incorrectness scoring: `analytics.compute_incorrectness_column()` (lines 68–85)
- collaborative filtering: `analytics.compute_cf_struggle_scores()` (lines 300–384)
- mistake clustering: `analytics.cluster_question_mistakes()` (lines 580–706)
- future IRT-based difficulty: `models/irt.py` (Phase 2)
- future mastery-aware struggle: `models/improved_struggle.py` (Phase 4)
- future BKT mastery tracking: `models/bkt.py` (Phase 3)
- future measurement layer: `models/measurement.py` (Phase 1)
