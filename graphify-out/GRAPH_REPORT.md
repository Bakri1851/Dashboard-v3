# Graph Report - .  (2026-04-16)

## Corpus Check
- 23 files · ~151,995 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 340 nodes · 489 edges · 21 communities detected
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `_read_state_unlocked()` - 14 edges
2. `_lock()` - 13 edges
3. `_write_state_unlocked()` - 13 edges
4. `_play()` - 10 edges
5. `main()` - 9 edges
6. `render_unassigned_view()` - 8 edges
7. `render_assigned_view()` - 8 edges
8. `_now_iso()` - 8 edges
9. `compute_student_struggle_scores()` - 7 edges
10. `load_data()` - 7 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities

### Community 0 - "Community 0"
Cohesion: 0.04
Nodes (60): _apply_leaderboard_layout(), _hex_to_rgb(), Convert '#rrggbb' to 'r, g, b' string for rgba()., 4 metric cards for question drill-down., Small coloured dot showing mean AI confidence for this question's incorrectness, Render mistake clusters as neon-themed cards in a 2-column grid.     Each card s, Dashboard title with gradient text and subtitle., Apply shared layout to both leaderboard bar charts. (+52 more)

### Community 1 - "Community 1"
Cohesion: 0.06
Nodes (46): add_feedback_flag(), apply_saved_session_to_state(), _backup_corrupt_saved_sessions(), build_retroactive_session_record(), build_session_record_from_state(), delete_session_record(), detect_format(), _empty_saved_sessions_payload() (+38 more)

### Community 2 - "Community 2"
Cohesion: 0.09
Nodes (31): apply_temporal_smoothing(), _call_openai_batch(), classify_score(), cluster_question_mistakes(), compute_cf_struggle_scores(), compute_incorrectness_column(), compute_question_difficulty_scores(), compute_recent_incorrectness() (+23 more)

### Community 3 - "Community 3"
Cohesion: 0.09
Nodes (26): comparison_view(), data_analysis_view(), _format_duration(), _format_session_timestamp(), in_class_view(), previous_sessions_view(), question_detail_view(), Render ISO timestamp in a compact display format. (+18 more)

### Community 4 - "Community 4"
Cohesion: 0.13
Nodes (23): _coerce_datetime(), _get_dataframe_window(), init_session_state(), main(), _on_dashboard_view_change(), _on_view_change(), Return min/max timestamps for the currently displayed dataframe., Combine the Custom date_range + time_start/end widgets into a datetime window. (+15 more)

### Community 5 - "Community 5"
Cohesion: 0.28
Nodes (22): assign_student(), _build_assistant_id(), _default_state(), end_lab_session(), generate_session_code(), get_assignment_for_assistant(), join_session(), leave_session() (+14 more)

### Community 6 - "Community 6"
Cohesion: 0.23
Nodes (19): _clear_assistant_query_param(), _coerce_query_value(), _heading(), _leave_session(), _load_student_data(), main(), _pop_join_notice(), Fetch live data and compute struggle scores. Returns (df, struggle_df). (+11 more)

### Community 7 - "Community 7"
Cohesion: 0.16
Nodes (18): _play(), play_assignment_received(), play_assistant_join(), play_high_struggle(), play_navigation(), play_refresh(), play_selection(), play_session_end() (+10 more)

### Community 8 - "Community 8"
Cohesion: 0.16
Nodes (15): bkt_update(), _build_sequences(), compute_all_mastery(), compute_student_mastery(), compute_student_mastery_summary(), fit_bkt_parameters(), Phase 3 — Bayesian Knowledge Tracing (BKT) mastery estimation.  Standard BKT wit, Per-(user, question) binary correctness sequences, in temporal order.      Uses (+7 more)

### Community 9 - "Community 9"
Cohesion: 0.13
Nodes (14): academic_period_sorter(), add_academic_period_column(), _build_periods(), format_academic_period_window(), get_academic_period(), get_academic_week_window(), get_period_date_range(), Populate ACADEMIC_PERIODS from the boundary dates. (+6 more)

### Community 10 - "Community 10"
Cohesion: 0.18
Nodes (14): build_rag_collection(), clear_cluster_suggestion_cache(), clear_suggestion_cache(), _extract_bullets(), generate_assistant_suggestions(), generate_cluster_suggestions(), _lazy_import(), Pull a list of short strings out of whatever shape OpenAI returned.      `respon (+6 more)

### Community 11 - "Community 11"
Cohesion: 0.23
Nodes (13): _copy_if_missing(), _ensure_data_dir(), ensure_runtime_data_layout(), lab_session_lock_path(), lab_session_path(), rag_chroma_dir(), Runtime path helpers for app data and backward-compatible migration., Create the runtime data directory and migrate legacy root files once. (+5 more)

### Community 12 - "Community 12"
Cohesion: 0.32
Nodes (7): build_response_matrix(), compute_irt_difficulty_scores(), fit_rasch_model(), Phase 2 — 1-Parameter Logistic (Rasch) IRT difficulty estimation., Compute IRT-based difficulty scores for all questions.      Returns a DataFrame, Build a binary student x question response matrix.      For each student-questio, Fit a Rasch (1PL) model via joint MLE.      Parameters     ----------     respon

### Community 13 - "Community 13"
Cohesion: 0.4
Nodes (5): _compute_difficulty_adjusted(), compute_improved_struggle_scores(), Phase 4 — Improved struggle model (mastery-aware, difficulty-adjusted).  Combine, Per-student difficulty-adjusted score from recent submissions.      For each stu, Return a struggle DataFrame compatible with the baseline schema.      Extra diag

### Community 14 - "Community 14"
Cohesion: 0.5
Nodes (3): compute_incorrectness_with_confidence(), Phase 1 — Measurement confidence for AI-derived incorrectness scores., Wrap analytics.compute_incorrectness_column() and add confidence metadata.

### Community 15 - "Community 15"
Cohesion: 1.0
Nodes (1): Compatibility wrapper for the instructor Streamlit app.

### Community 16 - "Community 16"
Cohesion: 1.0
Nodes (1): Compatibility wrapper for the assistant Streamlit app.

### Community 17 - "Community 17"
Cohesion: 1.0
Nodes (1): UI subpackage for dashboard presentation modules.

### Community 18 - "Community 18"
Cohesion: 1.0
Nodes (0): 

### Community 19 - "Community 19"
Cohesion: 1.0
Nodes (1): ui/theme.py — Theme and CSS

### Community 20 - "Community 20"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **142 isolated node(s):** `Compatibility wrapper for the instructor Streamlit app.`, `Compatibility wrapper for the assistant Streamlit app.`, `Populate ACADEMIC_PERIODS from the boundary dates.`, `Return (start_date, end_date) inclusive for a period label, or None.`, `Map a date to a 2025/26 academic period label.` (+137 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 15`** (2 nodes): `app.py`, `Compatibility wrapper for the instructor Streamlit app.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 16`** (2 nodes): `lab_app.py`, `Compatibility wrapper for the assistant Streamlit app.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 17`** (2 nodes): `__init__.py`, `UI subpackage for dashboard presentation modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 18`** (1 nodes): `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 19`** (1 nodes): `ui/theme.py — Theme and CSS`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 20`** (1 nodes): `main.toc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What connects `Compatibility wrapper for the instructor Streamlit app.`, `Compatibility wrapper for the assistant Streamlit app.`, `Populate ACADEMIC_PERIODS from the boundary dates.` to the rest of the system?**
  _142 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Community 3` be split into smaller, more focused modules?**
  _Cohesion score 0.09 - nodes in this community are weakly interconnected._
- **Should `Community 4` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._
- **Should `Community 9` be split into smaller, more focused modules?**
  _Cohesion score 0.13 - nodes in this community are weakly interconnected._