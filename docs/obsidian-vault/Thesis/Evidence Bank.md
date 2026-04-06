# Evidence Bank

Tracks what evidence exists for thesis claims and what still needs to be created. Each entry notes where it would be used in the report.

Related: [[Report Sync]], [[Rewrite Queue]], [[Figures and Tables]], [[Setup and Runbook]]

---

## Screenshots — Status: None captured

All screenshots need to be captured from the running V2 dashboard. Target: Appendix B and inline in Ch4/Ch5.

| Screenshot | Description | Supports | Status |
|-----------|-------------|----------|--------|
| In Class view | Leaderboards, summary cards, score distributions | Ch4, Ch5 FR4/FR5, replaces Fig 8 | Needed |
| Student detail view | Drill-down metrics, submission timeline, retry trend | Ch4, Ch5 FR2 | Needed |
| Question detail view | Mistake clusters, student table, attempt timeline | Ch4, Ch5 FR3 | Needed |
| Data analysis view | Module usage, top questions, activity timeline | Ch4, Ch5 FR5 | Needed |
| Settings page | Model toggles, CF threshold, auto-refresh | Ch4, NFR6 | Needed |
| Previous sessions view | Saved session list, academic period filter | Ch4 | Needed |
| Lab assistant: join screen | Session code entry | Ch4, FR7 (partial) | Needed |
| Lab assistant: assigned view | Student card, mark-helped button | Ch4, FR4 | Needed |
| Lab assistant: waiting view | Available students list | Ch4 | Needed |
| CF diagnostic panel | Elevated students, neighbour details | Ch4, Ch5 | Needed |
| Instructor sidebar: live session | Session code, assistants, assignments | Ch4 | Needed |

---

## Implementation evidence — Status: Exists in code

Evidence that features are built. Code references documented in vault notes.

| Feature | Code location | Documented in vault? |
|---------|--------------|---------------------|
| 7-signal struggle model | `analytics.py:compute_student_struggle_scores()` | Yes — [[Student Struggle Logic]] |
| 5-signal difficulty model | `analytics.py:compute_question_difficulty_scores()` | Yes — [[Question Difficulty Logic]] |
| OpenAI incorrectness scoring | `analytics.py:compute_incorrectness_column()` | Yes — [[Analytics Engine]] |
| Collaborative filtering | `analytics.py:compute_cf_struggle_scores()` | Yes — [[Analytics Engine]] |
| Mistake clustering | `analytics.py:cluster_question_mistakes()` | Yes — [[Analytics Engine]] |
| IRT difficulty (Rasch 1PL) | `models/irt.py:compute_irt_difficulty_scores()` | Yes — [[IRT Difficulty Logic]] |
| BKT mastery tracking | `models/bkt.py:compute_all_mastery()` | Yes — [[BKT Mastery Logic]] |
| Improved struggle model | `models/improved_struggle.py:compute_improved_struggle_scores()` | Yes — [[Improved Struggle Logic]] |
| Measurement confidence | `models/measurement.py:compute_incorrectness_with_confidence()` | Yes — [[Analytics Engine]] |
| Lab assistant system | `lab_state.py`, `assistant_app.py` | Yes — [[Lab Assistant System]] |
| Saved sessions | `data_loader.py:save_session_record()` etc. | Yes — [[Data Loading and Session Persistence]] |
| Academic calendar | `academic_calendar.py` | Yes — [[Academic Period Converter]] |
| Config-driven thresholds | `config.py` | Yes — [[Configuration and Runtime Paths]] |

---

## Model evidence — Status: Needs creation

Comparative data showing model behavior. Target: Ch5 Results.

| Evidence | Description | How to generate | Status |
|----------|-------------|-----------------|--------|
| Baseline vs IRT difficulty | Side-by-side difficulty scores for same questions | Run dashboard with both models enabled, compare outputs | Needed |
| Baseline vs improved struggle | Side-by-side struggle scores for same students | Run dashboard with both models enabled, compare outputs | Needed |
| CF elevation examples | Students elevated by CF that baseline missed | Enable CF, capture diagnostic panel with elevated students | Needed |
| Mistake cluster examples | Cluster labels and representative answers for a question | Run dashboard on session with enough incorrect answers (>3) | Needed |
| BKT mastery evolution | How mastery changes with successive attempts | Extract from `mastery_df` session state for a student | Needed |
| Score distributions | Histograms of struggle/difficulty scores across a real session | Screenshot from In Class view | Needed |

---

## Testing evidence — Status: Needs creation

Manual testing results. Target: Ch5 and Appendix C.

| Test | What to verify | Status |
|------|---------------|--------|
| FR1: Data loads from endpoint | Dashboard shows data after launch | Needs documenting |
| FR2: Struggle scores compute | Leaderboard shows scored students with labels | Needs documenting |
| FR3: Difficulty scores compute | Question leaderboard shows scored questions | Needs documenting |
| FR4: Prioritisation works | Students sorted by score, colors match thresholds | Needs documenting |
| FR5: Analytics presented | All 6 views render correctly | Needs documenting |
| FR6: Smart devices | NOT IMPLEMENTED | N/A |
| FR7: Assistant ranking | Helped count visible in lab state | Needs documenting |
| NFR1: Performance | Measure refresh cycle time | Needs measuring |
| NFR2: Interpretability | Walkthrough showing no specialist knowledge needed | Needs documenting |
| NFR3: Robustness | Test with empty data, single student, no feedback | Needs testing |
| NFR4: Scalability | Test with varying class sizes | Needs testing |
| NFR5: Privacy | Confirm read-only API, no PII stored | Needs documenting |
| NFR6: Extensibility | Demonstrate model toggles, config-driven thresholds | Needs documenting |

Existing test resource: smoke test checklist in [[Setup and Runbook]].

---

## What is completely missing

- No automated test suite
- No evaluation metrics or scripts
- No user studies or feedback
- No benchmark datasets
- No performance profiling data
- No accessibility testing
