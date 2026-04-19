# Graph Report - .  (2026-04-19)

## Corpus Check
- 105 files · ~297,824 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1815 nodes · 4791 edges · 62 communities detected
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `As()` - 129 edges
2. `K()` - 103 edges
3. `i()` - 101 edges
4. `a()` - 93 edges
5. `p()` - 77 edges
6. `b()` - 77 edges
7. `R()` - 73 edges
8. `w()` - 72 edges
9. `Ox()` - 70 edges
10. `g()` - 60 edges

## Surprising Connections (you probably didn't know these)
- `Sessions router — GET list, POST save (retroactive), DELETE by id.  `POST /api/s` --uses--> `SavedSession`  [INFERRED]
  code2\backend\routers\sessions.py → code2\backend\schemas.py
- `Retroactive save — builds a record from the frontend's current filter     window` --uses--> `SavedSession`  [INFERRED]
  code2\backend\routers\sessions.py → code2\backend\schemas.py
- `GET /api/rag/student/{id} and /api/rag/question/{id} — coaching suggestions.` --uses--> `RagSuggestions`  [INFERRED]
  code2\backend\routers\rag.py → code2\backend\schemas.py
- `Send a batch of feedback texts to OpenAI and return incorrectness scores.      R` --rationale_for--> `_call_openai_batch()`  [EXTRACTED]
  code\learning_dashboard\analytics.py → code2\learning_dashboard\analytics.py
- `Score all ai_feedback values via OpenAI, batched for efficiency.     Successful` --rationale_for--> `compute_incorrectness_column()`  [EXTRACTED]
  code\learning_dashboard\analytics.py → code2\learning_dashboard\analytics.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.0
Nodes (19): BG(), Dbe(), dq(), EF(), hF(), Hje(), hV(), IL() (+11 more)

### Community 1 - "Community 1"
Cohesion: 0.04
Nodes (183): ae(), age(), aj(), Ame(), aX(), bge(), bj(), bk() (+175 more)

### Community 2 - "Community 2"
Cohesion: 0.07
Nodes (147): a(), ab(), abe(), AF(), ah(), ak(), ao(), aq() (+139 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (106): _activity_by_week(), get_analysis(), GET /api/analysis — aggregate stats for the Data Analysis view., Counts keyed by (academic period label, day-of-week) — feeds a heatmap., Hourly counts for the last 24h → (buckets, peak_hour_of_day, peak_count)., _timeline_24h(), _top_questions(), _user_activity() (+98 more)

### Community 4 - "Community 4"
Cohesion: 0.04
Nodes (93): ac(), ad(), ai(), As(), bd(), bi(), cc(), cd() (+85 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (74): ar(), at(), AU(), be(), br(), bt(), BU(), ct() (+66 more)

### Community 6 - "Community 6"
Cohesion: 0.04
Nodes (67): add_feedback_flag(), apply_saved_session_to_state(), _backup_corrupt_saved_sessions(), build_retroactive_session_record(), build_session_record_from_state(), delete_session_record(), detect_format(), _empty_saved_sessions_payload() (+59 more)

### Community 7 - "Community 7"
Cohesion: 0.07
Nodes (7): Compatibility wrapper for the instructor Streamlit app., ApiError, lifespan(), FastAPI entry point for the code2 alternative frontend.  Launch with:     uvi, Pre-warm the analytics cache in the background so the first user     request do, isoToDate(), openSaveDialog()

### Community 8 - "Community 8"
Cohesion: 0.04
Nodes (60): _apply_leaderboard_layout(), _hex_to_rgb(), Convert '#rrggbb' to 'r, g, b' string for rgba()., 4 metric cards for question drill-down., Small coloured dot showing mean AI confidence for this question's incorrectness, Render mistake clusters as neon-themed cards in a 2-column grid.     Each card, Dashboard title with gradient text and subtitle., Apply shared layout to both leaderboard bar charts. (+52 more)

### Community 9 - "Community 9"
Cohesion: 0.06
Nodes (46): apply_temporal_smoothing(), _call_openai_batch(), classify_score(), cluster_question_mistakes(), compute_cf_struggle_scores(), compute_incorrectness_column(), compute_question_difficulty_scores(), compute_recent_incorrectness() (+38 more)

### Community 10 - "Community 10"
Cohesion: 0.09
Nodes (31): bq(), BW(), cw(), DV(), dw(), Eq(), Fq(), fw() (+23 more)

### Community 11 - "Community 11"
Cohesion: 0.12
Nodes (27): ctx(), _play(), play_assignment_received(), play_assistant_join(), play_high_struggle(), play_navigation(), play_refresh(), play_selection() (+19 more)

### Community 12 - "Community 12"
Cohesion: 0.1
Nodes (24): comparison_view(), data_analysis_view(), _format_duration(), _format_session_timestamp(), in_class_view(), previous_sessions_view(), question_detail_view(), Render ISO timestamp in a compact display format. (+16 more)

### Community 13 - "Community 13"
Cohesion: 0.13
Nodes (23): _coerce_datetime(), _get_dataframe_window(), init_session_state(), main(), _on_dashboard_view_change(), _on_view_change(), Return min/max timestamps for the currently displayed dataframe., Combine the Custom date_range + time_start/end widgets into a datetime window. (+15 more)

### Community 14 - "Community 14"
Cohesion: 0.28
Nodes (22): assign_student(), _build_assistant_id(), _default_state(), end_lab_session(), generate_session_code(), get_assignment_for_assistant(), join_session(), leave_session() (+14 more)

### Community 15 - "Community 15"
Cohesion: 0.23
Nodes (19): _clear_assistant_query_param(), _coerce_query_value(), _heading(), _leave_session(), _load_student_data(), main(), _pop_join_notice(), Fetch live data and compute struggle scores. Returns (df, struggle_df). (+11 more)

### Community 16 - "Community 16"
Cohesion: 0.15
Nodes (18): build_rag_collection(), clear_cluster_suggestion_cache(), clear_suggestion_cache(), _extract_bullets(), generate_assistant_suggestions(), generate_cluster_suggestions(), _lazy_import(), question_suggestions() (+10 more)

### Community 17 - "Community 17"
Cohesion: 0.13
Nodes (19): aN(), bN(), fN(), Fve(), gN(), hN(), jN(), KN() (+11 more)

### Community 18 - "Community 18"
Cohesion: 0.15
Nodes (18): BL(), cL(), EL(), FL(), GL(), jL(), kL(), lL() (+10 more)

### Community 19 - "Community 19"
Cohesion: 0.16
Nodes (15): bkt_update(), _build_sequences(), compute_all_mastery(), compute_student_mastery(), compute_student_mastery_summary(), fit_bkt_parameters(), Phase 3 — Bayesian Knowledge Tracing (BKT) mastery estimation.  Standard BKT w, Per-(user, question) binary correctness sequences, in temporal order.      Use (+7 more)

### Community 20 - "Community 20"
Cohesion: 0.13
Nodes (14): academic_period_sorter(), add_academic_period_column(), _build_periods(), format_academic_period_window(), get_academic_period(), get_academic_week_window(), get_period_date_range(), Populate ACADEMIC_PERIODS from the boundary dates. (+6 more)

### Community 21 - "Community 21"
Cohesion: 0.23
Nodes (13): _copy_if_missing(), _ensure_data_dir(), ensure_runtime_data_layout(), lab_session_lock_path(), lab_session_path(), rag_chroma_dir(), Runtime path helpers for app data and backward-compatible migration., Create the runtime data directory and migrate legacy root files once. (+5 more)

### Community 22 - "Community 22"
Cohesion: 0.14
Nodes (0): 

### Community 23 - "Community 23"
Cohesion: 0.24
Nodes (14): am(), BM(), cm(), dm(), im(), JM(), lm(), nm() (+6 more)

### Community 24 - "Community 24"
Cohesion: 0.23
Nodes (12): filter_df(), invalidate(), load_dataframe(), load_difficulty_df(), load_struggle_df(), TTL-cached data + analytics loader for the FastAPI path.  The raw DataFrame is f, Compute + cache the struggle leaderboard for the given window., Compute + cache the difficulty leaderboard for the given window. (+4 more)

### Community 25 - "Community 25"
Cohesion: 0.27
Nodes (10): assign(), end(), get_state(), leave(), mark_helped(), remove_assistant(), self_claim(), start() (+2 more)

### Community 26 - "Community 26"
Cohesion: 0.18
Nodes (13): aa(), Ba(), Ca(), ea(), Fa(), Ha(), kA(), La() (+5 more)

### Community 27 - "Community 27"
Cohesion: 0.24
Nodes (6): beep(), playNav(), playRefresh(), playSelect(), playSessionEnd(), playSessionStart()

### Community 28 - "Community 28"
Cohesion: 0.24
Nodes (10): get_google_fonts_import(), get_main_css(), get_mobile_css(), get_plotly_layout_defaults(), _hex_to_rgb(), Complete CSS string for the sci-fi neon dashboard theme., Default Plotly layout properties for consistent chart theming., Mobile-optimized CSS for lab_app.py. Designed for 375px+ phone screens. (+2 more)

### Community 29 - "Community 29"
Cohesion: 0.2
Nodes (0): 

### Community 30 - "Community 30"
Cohesion: 0.28
Nodes (6): defaults(), Process-local mutable settings — powers the live Settings view.  Mirrors Streaml, Merge `partial` into the live config. Unknown keys are ignored., reset(), RuntimeConfig, update()

### Community 31 - "Community 31"
Cohesion: 0.32
Nodes (7): build_response_matrix(), compute_irt_difficulty_scores(), fit_rasch_model(), Phase 2 — 1-Parameter Logistic (Rasch) IRT difficulty estimation., Compute IRT-based difficulty scores for all questions.      Returns a DataFram, Build a binary student x question response matrix.      For each student-quest, Fit a Rasch (1PL) model via joint MLE.      Parameters     ----------     re

### Community 32 - "Community 32"
Cohesion: 0.29
Nodes (7): BEe(), Ev(), Fee(), MEe(), Nee(), Ov(), sV()

### Community 33 - "Community 33"
Cohesion: 0.38
Nodes (7): fb(), gb(), ib(), lb(), pb(), ub(), vB()

### Community 34 - "Community 34"
Cohesion: 0.4
Nodes (5): _compute_difficulty_adjusted(), compute_improved_struggle_scores(), Phase 4 — Improved struggle model (mastery-aware, difficulty-adjusted).  Combi, Per-student difficulty-adjusted score from recent submissions.      For each s, Return a struggle DataFrame compatible with the baseline schema.      Extra di

### Community 35 - "Community 35"
Cohesion: 0.33
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 0.33
Nodes (6): pz(), rZ(), sZ(), TZ(), wZ(), xZ()

### Community 37 - "Community 37"
Cohesion: 0.4
Nodes (6): BF(), cF(), iF(), MF(), nF(), sF()

### Community 38 - "Community 38"
Cohesion: 0.5
Nodes (3): compute_incorrectness_with_confidence(), Phase 1 — Measurement confidence for AI-derived incorrectness scores., Wrap analytics.compute_incorrectness_column() and add confidence metadata.

### Community 39 - "Community 39"
Cohesion: 0.83
Nodes (4): fV(), gV(), lV(), uV()

### Community 40 - "Community 40"
Cohesion: 0.67
Nodes (3): _guess_ext(), main(), Decompress the mockup bundle into plain-text source files.  The mockup at C:\\

### Community 41 - "Community 41"
Cohesion: 0.67
Nodes (3): AP(), CP(), hP()

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (3): Vje(), Wje(), zje()

### Community 43 - "Community 43"
Cohesion: 0.67
Nodes (3): Gpe(), qpe(), Vpe()

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Compatibility wrapper for the assistant Streamlit app.

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): UI subpackage for dashboard presentation modules.

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (0): 

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (2): Vee(), wee()

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (2): Vwe(), Wwe()

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (2): Gje(), rwe()

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (2): cge(), pge()

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (2): qee(), uee()

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (2): Qfe(), Zfe()

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (2): kP(), tP()

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (2): Cv(), kv()

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (2): jF(), wF()

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (2): oP(), SP()

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (2): gz(), NZ()

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (2): due(), Iue()

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): ui/theme.py — Theme and CSS

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (0): 

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (0): 

## Knowledge Gaps
- **204 isolated node(s):** `Compatibility wrapper for the instructor Streamlit app.`, `Compatibility wrapper for the assistant Streamlit app.`, `Populate ACADEMIC_PERIODS from the boundary dates.`, `Return (start_date, end_date) inclusive for a period label, or None.`, `Map a date to a 2025/26 academic period label.` (+199 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 44`** (2 nodes): `lab_app.py`, `Compatibility wrapper for the assistant Streamlit app.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (2 nodes): `__init__.py`, `UI subpackage for dashboard presentation modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (2 nodes): `config.py`, `eslint.config.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (2 nodes): `Vee()`, `wee()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (2 nodes): `Vwe()`, `Wwe()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (2 nodes): `Gje()`, `rwe()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (2 nodes): `cge()`, `pge()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (2 nodes): `qee()`, `uee()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (2 nodes): `Qfe()`, `Zfe()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (2 nodes): `kP()`, `tP()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (2 nodes): `Cv()`, `kv()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (2 nodes): `jF()`, `wF()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (2 nodes): `oP()`, `SP()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (2 nodes): `gz()`, `NZ()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (2 nodes): `due()`, `Iue()`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `ui/theme.py — Theme and CSS`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `vite.config.ts`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `5e0dbd7d-1f61-49cc-91d7-7e00b9851399.js`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `As()` connect `Community 4` to `Community 0`, `Community 1`, `Community 2`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **Why does `RagSuggestions` connect `Community 3` to `Community 16`?**
  _High betweenness centrality (0.002) - this node is a cross-community bridge._
- **Why does `GET /api/rag/student/{id} and /api/rag/question/{id} — coaching suggestions.` connect `Community 16` to `Community 3`?**
  _High betweenness centrality (0.001) - this node is a cross-community bridge._
- **What connects `Compatibility wrapper for the instructor Streamlit app.`, `Compatibility wrapper for the assistant Streamlit app.`, `Populate ACADEMIC_PERIODS from the boundary dates.` to the rest of the system?**
  _204 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Community 0` be split into smaller, more focused modules?**
  _Cohesion score 0.0 - nodes in this community are weakly interconnected._
- **Should `Community 1` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Community 2` be split into smaller, more focused modules?**
  _Cohesion score 0.07 - nodes in this community are weakly interconnected._