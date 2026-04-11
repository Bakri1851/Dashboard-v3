# Graph Report - .  (2026-04-11)

## Corpus Check
- 149 files · ~130,395 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 794 nodes · 1069 edges · 67 communities detected
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 85 edges (avg confidence: 0.83)
- Token cost: 0 input · 0 output

## God Nodes (most connected - your core abstractions)
1. `Ch2 — Background and Requirements` - 22 edges
2. `Reference Index` - 15 edges
3. `Ch2 – Background and Requirements` - 15 edges
4. `_read_state_unlocked()` - 14 edges
5. `Analytics Engine` - 14 edges
6. `_lock()` - 13 edges
7. `_write_state_unlocked()` - 13 edges
8. `Student Struggle Logic` - 12 edges
9. `Report Sync` - 11 edges
10. `Chapter 2: Background and Requirements` - 11 edges

## Surprising Connections (you probably didn't know these)
- `Ch4 Implementation (Outdated - Full Rewrite Required)` --conceptually_related_to--> `Chapter 4: Implementation`  [INFERRED]
  docs/obsidian-vault/Thesis/Writing Roadmap.md → Report/main.pdf
- `Ch5 Results and Evaluation (Empty)` --conceptually_related_to--> `Chapter 5: Evaluation`  [INFERRED]
  docs/obsidian-vault/Thesis/Writing Roadmap.md → Report/main.pdf
- `API Record Structure` --implements--> `data_loader.py — API Fetch and XML Parsing`  [INFERRED]
  Report/figures/design-and-architecture/data-entry.png → code/learning_dashboard/data_loader.py
- `NumPy Library` --calls--> `bkt.py — BKT Mastery Model`  [EXTRACTED]
  docs/obsidian-vault/Code/Reference/Libraries/NumPy.md → code/learning_dashboard/models/bkt.py
- `NumPy Library` --calls--> `improved_struggle.py — Improved Struggle Model`  [EXTRACTED]
  docs/obsidian-vault/Code/Reference/Libraries/NumPy.md → code/learning_dashboard/models/improved_struggle.py

## Hyperedges (group relationships)
- **Two-App Shared State System** — claudemd_instructor_dashboard, claudemd_lab_assistant_app, claudemd_lab_session_json, claudemd_lab_state_py, requirements_filelock [EXTRACTED 1.00]
- **Analytics Scoring Engine Pipeline** — claudemd_analytics_py, claudemd_incorrectness_scoring, claudemd_student_struggle_score, claudemd_question_difficulty_score, claudemd_collaborative_filtering, claudemd_mistake_clustering, requirements_openai, requirements_sklearn [EXTRACTED 1.00]
- **Assistant App Four-View Routing Flow** — assistant_flow_ui, assistant_flow_no_session, assistant_flow_join, assistant_flow_unassigned, assistant_flow_assigned, claudemd_aid_url_param [EXTRACTED 1.00]
- **Improved Model Pipeline (IRT + BKT + Improved Struggle)** — irt_rasch_model, bkt_algorithm, improved_struggle_model, improved_models_feature_flag, comparison_view [EXTRACTED 0.95]
- **Student Struggle Scoring System** — baseline_struggle_model, behavioral_composite, bayesian_shrinkage, struggle_thresholds, incorrectness_scoring, student_struggle_logic [EXTRACTED 0.95]
- **Data Ingestion and Filtering Pipeline** — data_loading_persistence, filter_precedence, data_pipeline, academic_calendar_module, config_runtime_paths [INFERRED 0.85]
- **Scoring Engine Library Dependencies** — module_analytics, lib_numpy, lib_openai, lib_sklearn, lib_pandas [EXTRACTED 1.00]
- **Early Warning Systems Literature Cluster** — lit_a2020_atrisk, lit_a2022_early, lit_a2023_real, concept_early_warning [INFERRED 0.85]
- **Candidate Future Libraries (Not Yet Used)** — lib_optuna, lib_mlflow, lib_polars, lib_sentencetransformers, lib_shap [EXTRACTED 0.90]
- **Student Struggle Detection — Core Papers** — dong_using_paper, estey_2017_automatically_paper, or_2024_exploring_paper, koutcheme_using_paper [EXTRACTED 0.95]
- **IRT and Difficulty Modelling Papers** — frederikbaucks_2024_gaining_paper, pankiewicz_measuring_paper, khajah_supercharging_paper [EXTRACTED 0.90]
- **Real-Time Analytics and Dashboard Design Papers** — marr_2021_what_paper, mustafaayobamiraji_2024_realtime_paper, govaerts_the_paper, klerkx_2017_learning_paper [INFERRED 0.80]
- **Thesis Writing Depends on Evidence Which Depends on Coding** — full_roadmap, evidence_bank, concept_model_comparison_view, ch4_implementation, ch5_evaluation [EXTRACTED 0.95]
- **Literature Papers Collectively Inform Ch2 Background and Requirements** — piech_modeling_piech, pitts_a_pitts, schafer_2007_collaborative_schafer, tzimas_2021_ethical_tzimas, verbert_2020_learning_verbert, vieira_2018_visual_vieira, wilson_2017_learning_wilson, ch2_background [EXTRACTED 0.97]
- **Formula Mismatch Drives Ch3 Rewrite Queue and Report Sync Corrections** — concept_formula_mismatch, concept_struggle_formula_5, concept_struggle_formula_7, rewrite_queue, report_sync [EXTRACTED 0.93]
- **Student Struggle Detection Pipeline: Data Endpoint -> Struggle Variables -> LLM Scoring -> Struggle Model** — mainpdf_data_endpoint, mainpdf_struggle_variables, mainpdf_llm_incorrectness_scoring, mainpdf_student_struggle_model [EXTRACTED 0.95]
- **Advanced Model Suite for Difficulty and Mastery: IRT, BKT, Improved Struggle, Measurement Confidence** — mainpdf_irt, mainpdf_bkt, mainpdf_improved_struggle_model, mainpdf_measurement_confidence [EXTRACTED 0.95]
- **Thesis Writing Priority Chain: Ch4 Rewrite -> Appendix B Screenshots -> Appendix C Tests -> Ch5 Evaluation** — writingroadmap_ch4_implementation, writingroadmap_appendix_b, writingroadmap_appendix_c, writingroadmap_ch5_evaluation [EXTRACTED 1.00]
- **All Project Phases in Oct 2025 Gantt Plan** — gantt_oct2025_task_research_planning, gantt_oct2025_task_literature_review, gantt_oct2025_task_model_design, gantt_oct2025_task_dashboard_design, gantt_oct2025_task_system_impl, gantt_oct2025_task_testing_eval, gantt_oct2025_task_documentation [EXTRACTED 1.00]
- **All Project Phases in Jan 2026 Gantt Plan** — gantt_jan2026_task_model_integration, gantt_jan2026_task_dashboard_refinement, gantt_jan2026_task_eval_data_collection, gantt_jan2026_task_analysis_discussion, gantt_jan2026_task_writing_revision, gantt_jan2026_task_final_review_submission [EXTRACTED 1.00]
- **All Gantt Chart Plan Versions (Oct 2025, Jan 2026, figures)** — gantt_oct2025_project_plan, gantt_jan2026_project_plan, gantt_figures_project_plan [INFERRED 0.85]
- **Key Project Milestones: Research Complete, Model Complete, Final Submission** — milestone_research_lit_review_complete, milestone_model_impl_complete, milestone_final_submission [INFERRED 0.80]
- **Existing Learning Analytics Dashboards (Requirements Research)** — attentiondashboard_radial_viz, edsight1_responsive_design, mmdashboard_engagement, piwik_student_overview [INFERRED 0.85]
- **API Record JSON Fields** — data_entry_api_record, data_entry_module_field, data_entry_question_field, data_entry_timestamp_field, data_entry_xml_field, data_entry_session_field, data_entry_user_field [EXTRACTED 1.00]
- **XML Payload Submission Structure** — data_entry_xml_payload, data_entry_submission_element, data_entry_step_element, data_entry_feedback_element [EXTRACTED 1.00]
- **AI Feedback and Submission Trigger Loop** — data_entry_ai_submission_trigger, data_entry_submission_element, data_entry_feedback_element, data_entry_step_element [EXTRACTED 0.95]
- **Instructor Dashboard Main Widget Group** — figma1_student_progress_overview_widget, figma1_question_difficulty_overview_widget, figma1_struggle_summary_counters, figma1_assistant_leaderboard_widget [EXTRACTED 1.00]
- **Lab Assistant Allocation Interaction Flow** — figma2_assign_assistant_dropdown, figma2_available_assistants_list, figma2_assign_button, figma2_currently_helping_section, concept_assistant_allocation [INFERRED 0.85]
- **Assistant Leaderboard Gamification Components** — figma3_leaderboard_rank_badges, figma3_students_helped_metric, figma3_remove_assistant_button, concept_assistant_leaderboard [EXTRACTED 0.90]
- **Struggle Classification Visual Representations Across Mockups** — figma1_color_coded_student_tiles, figma1_struggle_summary_counters, figma2_student_progress_overview_widget, concept_struggle_level_classification [INFERRED 0.85]
- **Existing Learning Analytics Dashboards Survey for Requirements** — attention_dashboard_img, edsight_dashboard_1_img, edsight_dashboard_2_img, mm_dashboard_img, piwik_analytics_img, thesis_requirements_specification [EXTRACTED 1.00]
- **Student Performance Visualisation Concepts** — concept_radar_chart, concept_stacked_bar_chart, concept_student_overview_table, concept_per_question_answer_distribution, concept_multidimensional_learning_score [INFERRED 0.80]
- **Engagement and Attention Tracking Approaches** — concept_student_attention_tracking, concept_multimodal_engagement_tracking, concept_video_sensor_analytics [INFERRED 0.75]
- **Edsight Platform Dashboard Views** — edsight_dashboard_1_img, edsight_dashboard_2_img, platform_edsight [EXTRACTED 1.00]
- **Thesis Institutional Identity** — lboro_logo_loughborough_university_logo, lboro_logo_loughborough_university, lboro_logo_title_page, lboro_logo_masters_thesis [INFERRED 0.85]

## Communities

### Community 0 - "UI Components & Visualization"
Cohesion: 0.04
Nodes (58): _apply_leaderboard_layout(), _hex_to_rgb(), 4 metric cards for question drill-down., Small coloured dot showing mean AI confidence for this question's incorrectness, Render mistake clusters as neon-themed cards in a 2-column grid.     Each card s, Dashboard title with gradient text and subtitle., Apply shared layout to both leaderboard bar charts., Horizontal bar chart of students ranked by struggle score.     Clickable legend (+50 more)

### Community 1 - "Thesis Chapters & Theory References"
Cohesion: 0.04
Nodes (58): Abstract, Bayesian Knowledge Tracing (BKT), Chapter 2: Background and Requirements, Chapter 3: Design and Modelling, 4.6 Advanced Models (IRT, BKT, Improved Struggle), 4.5 Analytics Engine, Chapter 4: Implementation, 4.7 Instructor Application (6 Views) (+50 more)

### Community 2 - "Learning Models & Analytics Theory"
Cohesion: 0.05
Nodes (56): AI-Assisted Instructor and Student Support, BKT + IRT Combined Latent Structure, Bayesian Knowledge Tracing (BKT) Mastery, Collaborative Filtering for Personalised Learning Signals, Collaborative Filtering for Education, Consecutive Failures Threshold (4+), Course-Level Analytics and Temporal Granularity, Dashboard Affordances and Instructor Behaviour (+48 more)

### Community 3 - "Data Loading & Session Persistence"
Cohesion: 0.06
Nodes (46): add_feedback_flag(), apply_saved_session_to_state(), _backup_corrupt_saved_sessions(), build_retroactive_session_record(), build_session_record_from_state(), delete_session_record(), detect_format(), _empty_saved_sessions_payload() (+38 more)

### Community 4 - "Project Architecture & Modules"
Cohesion: 0.1
Nodes (44): Academic Calendar Module, Academic Period Converter, Analytics Engine, Lab App Entrypoint, Architecture, Baseline Question Difficulty Model, Baseline Student Struggle Model, Bayesian Shrinkage for Low-Volume Students (+36 more)

### Community 5 - "Scoring Engine & State Concepts"
Cohesion: 0.07
Nodes (43): Bayesian Knowledge Tracing (BKT), Collaborative Filtering (CF), Deferred Actions Pattern, Difficulty Score, Incorrectness Score, Item Response Theory (IRT), Learning Progression Modelling, Min-Max Normalisation (+35 more)

### Community 6 - "Thesis Document Structure"
Cohesion: 0.08
Nodes (38): Ch1 – Introduction, Ch3 – Design and Modelling, Ch4 – Implementation, Ch5 – Results and Evaluation, Ch6 – Conclusion, 3-Layer System Architecture: Data Generation, Processing, Decision, 7 Thesis Objectives, Bayesian Shrinkage as Risk Mitigation for Insufficient Data (+30 more)

### Community 7 - "Lab Assistant App Flows"
Cohesion: 0.07
Nodes (31): Assistant App — Join Session Flow, Assistant App — No Active Session View, Assistant App — UI Flow Overview, Assistant App — Unassigned View Flow, Lab Assistant System Module, ?aid= URL Query Param for Assistant Identity, data_loader.py — API Fetch and Persistence, Deferred Actions Pattern (pending_* flags) (+23 more)

### Community 8 - "Analytics Engine Code"
Cohesion: 0.1
Nodes (29): apply_temporal_smoothing(), _call_openai_batch(), classify_score(), cluster_question_mistakes(), compute_cf_struggle_scores(), compute_incorrectness_column(), compute_question_difficulty_scores(), compute_recent_incorrectness() (+21 more)

### Community 9 - "Thesis Introduction & Approach"
Cohesion: 0.08
Nodes (28): Agile Incremental Development Approach, 1.3 Aims and Objectives, Chapter 1: Introduction, 1.1 Problem - Student Struggle Detection in Live Labs, 1.5 Project Approach - Agile Incremental Development, 1.2 Proposed Solution - Real-Time Learning Analytics Dashboard, 1.4 Risks and Mitigation Table, 5.2 Functional Testing (FR1-FR7) (+20 more)

### Community 10 - "Advanced Features & RAG Design"
Cohesion: 0.09
Nodes (27): Assistant App — Assigned View Flow, RAG Architecture — Hybrid SQL+ChromaDB Design, academic_calendar.py — Academic Week Labels, analytics.py — Scoring Engine, BKT Mastery Model, Collaborative Filtering for Struggle Detection, config.py — Tunable Constants, Incorrectness Scoring (OpenAI GPT-4o-mini) (+19 more)

### Community 11 - "Background & Requirements"
Cohesion: 0.09
Nodes (27): Ch2 – Background and Requirements, CF as Diagnostic Layer in Analytics Engine, Dashboard Interpretability for Instructors, Functional Requirements FR1–FR7, Graphical Model of Student Progression, Interactive Visualisation for Learning Data, k-NN Cosine Similarity Collaborative Filtering, LA in HE: Privacy, Interpretability, Scalability (+19 more)

### Community 12 - "Dashboard Views Code"
Cohesion: 0.1
Nodes (24): comparison_view(), data_analysis_view(), _format_duration(), _format_session_timestamp(), in_class_view(), previous_sessions_view(), question_detail_view(), Render ISO timestamp in a compact display format. (+16 more)

### Community 13 - "Instructor UI & Assignment System"
Cohesion: 0.11
Nodes (24): Lab Assistant Allocation Workflow, Assistant Leaderboard (Gamification), Question Difficulty Classification, Student Struggle Level Classification, Add Assistant Button, Assistant Leaderboard Widget (collapsed), Color-Coded Question Difficulty Tiles (Very Hard/Hard/Medium/Easy rows), Color-Coded Student Tiles (High/Medium/Low/None rows) (+16 more)

### Community 14 - "Lab Session State Manager"
Cohesion: 0.28
Nodes (22): assign_student(), _build_assistant_id(), _default_state(), end_lab_session(), generate_session_code(), get_assignment_for_assistant(), join_session(), leave_session() (+14 more)

### Community 15 - "Instructor App Entry & Routing"
Cohesion: 0.14
Nodes (21): _coerce_datetime(), _get_dataframe_window(), init_session_state(), main(), _on_dashboard_view_change(), _on_view_change(), Return min/max timestamps for the currently displayed dataframe., Return the active explicit time-filter window, if any. (+13 more)

### Community 16 - "Sound Effects System"
Cohesion: 0.16
Nodes (18): _play(), play_assignment_received(), play_assistant_join(), play_high_struggle(), play_navigation(), play_refresh(), play_selection(), play_session_end() (+10 more)

### Community 17 - "Lab Assistant App Core"
Cohesion: 0.25
Nodes (17): _clear_assistant_query_param(), _coerce_query_value(), _heading(), _leave_session(), _load_student_data(), main(), _pop_join_notice(), Fetch live data and compute struggle scores. Returns (df, struggle_df). (+9 more)

### Community 18 - "Existing LA Dashboard Survey"
Cohesion: 0.14
Nodes (18): Attention Dashboard Screenshot, Multidimensional Learning Score, Multimodal In-Class Engagement Tracking, Per-Question Answer Distribution Visualisation, Radar / Spider Chart Visualisation, Responsive Multi-Device Dashboard Design, Stacked Bar Chart for Student Performance, Student Attention Tracking (+10 more)

### Community 19 - "Project Timeline Phases"
Cohesion: 0.16
Nodes (16): Phase 4: Analysis and Discussion, Phase 2: Dashboard Refinement, Phase 3: Evaluation Design and Data Collection, Phase 6: Final Review and Submission, Phase 1: Analytical Model Integration, Phase 5: Writing and Revision, Phase 4: Dashboard Design, Phase 7: Finish Off Documentation and Submit (+8 more)

### Community 20 - "Academic Calendar Module"
Cohesion: 0.15
Nodes (12): academic_period_sorter(), add_academic_period_column(), _build_periods(), format_academic_period_window(), get_academic_period(), get_period_date_range(), Populate ACADEMIC_PERIODS from the boundary dates., Format a date window as one academic period label or a range. (+4 more)

### Community 21 - "API Data Schema & XML"
Cohesion: 0.19
Nodes (13): AI Check Triggers Submission, API Record Structure, Feedback XML Element (AI Response), Module Code Field, Question Field, Session ID Field (Time of First Submission), Step XML Element (Student Answer), Submission XML Element (+5 more)

### Community 22 - "Runtime Paths & File Layout"
Cohesion: 0.27
Nodes (11): _copy_if_missing(), _ensure_data_dir(), ensure_runtime_data_layout(), lab_session_lock_path(), lab_session_path(), Runtime path helpers for app data and backward-compatible migration., Create the runtime data directory and migrate legacy root files once., Preferred saved-sessions path, with legacy fallback if migration fails. (+3 more)

### Community 23 - "UI Theme & Styling"
Cohesion: 0.24
Nodes (10): get_google_fonts_import(), get_main_css(), get_mobile_css(), get_plotly_layout_defaults(), _hex_to_rgb(), Complete CSS string for the sci-fi neon dashboard theme., Default Plotly layout properties for consistent chart theming., Mobile-optimized CSS for lab_app.py. Designed for 375px+ phone screens. (+2 more)

### Community 24 - "BKT Mastery Model"
Cohesion: 0.24
Nodes (9): bkt_update(), compute_all_mastery(), compute_student_mastery(), compute_student_mastery_summary(), Phase 3 — Bayesian Knowledge Tracing (BKT) mastery estimation.  Standard BKT wit, Per-student aggregate mastery statistics.      Accepts the output of ``compute_a, Single BKT HMM update step.  Returns P(L_{t+1})., Replay one student's chronological submissions and return final mastery per ques (+1 more)

### Community 25 - "IRT Difficulty Model"
Cohesion: 0.32
Nodes (7): build_response_matrix(), compute_irt_difficulty_scores(), fit_rasch_model(), Phase 2 — 1-Parameter Logistic (Rasch) IRT difficulty estimation., Compute IRT-based difficulty scores for all questions.      Returns a DataFrame, Build a binary student x question response matrix.      For each student-questio, Fit a Rasch (1PL) model via joint MLE.      Parameters     ----------     respon

### Community 26 - "Improved Struggle Model"
Cohesion: 0.4
Nodes (5): _compute_difficulty_adjusted(), compute_improved_struggle_scores(), Phase 4 — Improved struggle model (mastery-aware, difficulty-adjusted).  Combine, Per-student difficulty-adjusted score from recent submissions.      For each stu, Return a struggle DataFrame compatible with the baseline schema.      Extra diag

### Community 27 - "Edsight Dashboard Features"
Cohesion: 0.33
Nodes (6): Edsight Progress Tracking Charts, Edsight Responsive Dashboard Design, Edsight Question-Level Analytics, Stacked Bar Charts Per Question, Colored Progress Bar Indicators, Piwik Student Overview Table

### Community 28 - "Measurement Confidence"
Cohesion: 0.5
Nodes (3): compute_incorrectness_with_confidence(), Phase 1 — Measurement confidence for AI-derived incorrectness scores., Wrap analytics.compute_incorrectness_column() and add confidence metadata.

### Community 29 - "Documentation Index Notes"
Cohesion: 0.5
Nodes (4): Assistant App Index Note, Code Index — Master Index Note, Obsidian Vault Home — Master Map, Lab App Index Note

### Community 30 - "Early Warning Literature"
Cohesion: 1.0
Nodes (4): Early Warning Systems, Anon. — At-Risk Student Identification (2020), Anon. — Early Warning Systems for Student Performance (2022), Anon. — Real-Time Early Warning Framework (2023)

### Community 31 - "Multimodal Engagement Research"
Cohesion: 0.5
Nodes (4): Knowledge-Force-Help Dimensions, Radial Attention Visualization, MM Dashboard Classroom Engagement Metrics, Video Feed Integration

### Community 32 - "Institutional Identity"
Cohesion: 0.67
Nodes (4): Loughborough University, Loughborough University Logo, Master's Thesis, Thesis Title Page

### Community 33 - "Project Gantt Charts"
Cohesion: 0.67
Nodes (3): Project Gantt Chart (Report Figures Version - condensed), Project Gantt Chart (Jan 2026 Version), Project Gantt Chart (Oct 2025 Version)

### Community 34 - "Gamification & Leaderboard UI"
Cohesion: 0.67
Nodes (3): Add Assistant Action, Assistant Leaderboard UI, Gamification Badges (Gold/Silver/Bronze)

### Community 35 - "Instructor App Wrapper"
Cohesion: 1.0
Nodes (1): Compatibility wrapper for the instructor Streamlit app.

### Community 36 - "Lab App Wrapper"
Cohesion: 1.0
Nodes (1): Compatibility wrapper for the assistant Streamlit app.

### Community 37 - "UI Subpackage Init"
Cohesion: 1.0
Nodes (1): UI subpackage for dashboard presentation modules.

### Community 38 - "UI Theme Module"
Cohesion: 1.0
Nodes (2): Assistant App — UI System Module, ui/theme.py — CSS and Plotly Theme

### Community 39 - "Config Module"
Cohesion: 1.0
Nodes (0): 

### Community 40 - "Report TOC"
Cohesion: 1.0
Nodes (0): 

### Community 41 - "Dashboard Project Overview"
Cohesion: 1.0
Nodes (1): Dashboard v3 Project

### Community 42 - "UI Components Module"
Cohesion: 1.0
Nodes (1): ui/components.py — Reusable UI Blocks

### Community 43 - "Two-App Architecture"
Cohesion: 1.0
Nodes (1): Two-App Streamlit System Architecture

### Community 44 - "Scoring Models Overview"
Cohesion: 1.0
Nodes (1): Scoring Models Overview

### Community 45 - "Live Session Lifecycle"
Cohesion: 1.0
Nodes (1): Live Session Lifecycle

### Community 46 - "Assistant App Entrypoint"
Cohesion: 1.0
Nodes (1): Assistant App — App Entrypoint Module

### Community 47 - "Assistant Known Issues"
Cohesion: 1.0
Nodes (1): Assistant App — Known Issues

### Community 48 - "Assistant Next Steps"
Cohesion: 1.0
Nodes (1): Assistant App — Next Steps

### Community 49 - "Live Session Concept"
Cohesion: 1.0
Nodes (1): Live Session

### Community 50 - "Saved Session Concept"
Cohesion: 1.0
Nodes (1): Saved Session

### Community 51 - "LA Dashboard Design"
Cohesion: 1.0
Nodes (1): Learning Analytics Dashboard Design

### Community 52 - "FR1 Live Data Ingestion"
Cohesion: 1.0
Nodes (1): FR1: Live Data Ingestion (Implemented)

### Community 53 - "Appendix References"
Cohesion: 1.0
Nodes (1): Appendix D References (Done)

### Community 54 - "CF Evaluation Subsection"
Cohesion: 1.0
Nodes (1): Ch5 CF Evaluation Subsection (Missing)

### Community 55 - "Rewrite Queue Link"
Cohesion: 1.0
Nodes (1): Rewrite Queue (Linked Note)

### Community 56 - "Evidence Bank Link"
Cohesion: 1.0
Nodes (1): Evidence Bank (Linked Note)

### Community 57 - "Figures & Tables Link"
Cohesion: 1.0
Nodes (1): Figures and Tables (Linked Note)

### Community 58 - "Thesis Overview Link"
Cohesion: 1.0
Nodes (1): Thesis Overview (Linked Note)

### Community 59 - "Polish & LaTeX Compile"
Cohesion: 1.0
Nodes (1): Polish Pass - Terminology and LaTeX Compile

### Community 60 - "Technology Stack Section"
Cohesion: 1.0
Nodes (1): 4.2 Technology Stack and Software Selection

### Community 61 - "Data Pipeline Section"
Cohesion: 1.0
Nodes (1): 4.3 Data Pipeline

### Community 62 - "Session Management Section"
Cohesion: 1.0
Nodes (1): 4.4 Session Management

### Community 63 - "UI Design Section"
Cohesion: 1.0
Nodes (1): 4.9 User Interface and Interaction Design

### Community 64 - "Non-Functional Testing"
Cohesion: 1.0
Nodes (1): 5.3 Non-Functional Testing

### Community 65 - "Model Comparison Results"
Cohesion: 1.0
Nodes (1): 5.4 Results (Baseline, Advanced Model Comparison)

### Community 66 - "Loughborough University"
Cohesion: 1.0
Nodes (1): Loughborough University

## Knowledge Gaps
- **292 isolated node(s):** `Compatibility wrapper for the instructor Streamlit app.`, `Compatibility wrapper for the assistant Streamlit app.`, `Populate ACADEMIC_PERIODS from the boundary dates.`, `Return (start_date, end_date) inclusive for a period label, or None.`, `Map a date to a 2025/26 academic period label.` (+287 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Instructor App Wrapper`** (2 nodes): `app.py`, `Compatibility wrapper for the instructor Streamlit app.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Lab App Wrapper`** (2 nodes): `lab_app.py`, `Compatibility wrapper for the assistant Streamlit app.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Subpackage Init`** (2 nodes): `__init__.py`, `UI subpackage for dashboard presentation modules.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Theme Module`** (2 nodes): `Assistant App — UI System Module`, `ui/theme.py — CSS and Plotly Theme`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Config Module`** (1 nodes): `config.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Report TOC`** (1 nodes): `main.toc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Dashboard Project Overview`** (1 nodes): `Dashboard v3 Project`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Components Module`** (1 nodes): `ui/components.py — Reusable UI Blocks`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Two-App Architecture`** (1 nodes): `Two-App Streamlit System Architecture`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Scoring Models Overview`** (1 nodes): `Scoring Models Overview`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Live Session Lifecycle`** (1 nodes): `Live Session Lifecycle`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Assistant App Entrypoint`** (1 nodes): `Assistant App — App Entrypoint Module`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Assistant Known Issues`** (1 nodes): `Assistant App — Known Issues`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Assistant Next Steps`** (1 nodes): `Assistant App — Next Steps`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Live Session Concept`** (1 nodes): `Live Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Saved Session Concept`** (1 nodes): `Saved Session`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `LA Dashboard Design`** (1 nodes): `Learning Analytics Dashboard Design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `FR1 Live Data Ingestion`** (1 nodes): `FR1: Live Data Ingestion (Implemented)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Appendix References`** (1 nodes): `Appendix D References (Done)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `CF Evaluation Subsection`** (1 nodes): `Ch5 CF Evaluation Subsection (Missing)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Rewrite Queue Link`** (1 nodes): `Rewrite Queue (Linked Note)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Evidence Bank Link`** (1 nodes): `Evidence Bank (Linked Note)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Figures & Tables Link`** (1 nodes): `Figures and Tables (Linked Note)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Thesis Overview Link`** (1 nodes): `Thesis Overview (Linked Note)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Polish & LaTeX Compile`** (1 nodes): `Polish Pass - Terminology and LaTeX Compile`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Technology Stack Section`** (1 nodes): `4.2 Technology Stack and Software Selection`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Data Pipeline Section`** (1 nodes): `4.3 Data Pipeline`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Session Management Section`** (1 nodes): `4.4 Session Management`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `UI Design Section`** (1 nodes): `4.9 User Interface and Interaction Design`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Non-Functional Testing`** (1 nodes): `5.3 Non-Functional Testing`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Model Comparison Results`** (1 nodes): `5.4 Results (Baseline, Advanced Model Comparison)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Loughborough University`** (1 nodes): `Loughborough University`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Chapter 2: Background and Requirements` connect `Thesis Chapters & Theory References` to `Thesis Introduction & Approach`?**
  _High betweenness centrality (0.007) - this node is a cross-community bridge._
- **Why does `Koutcheme et al. — Using LLMs for Answer Quality Assessment` connect `Learning Models & Analytics Theory` to `Scoring Engine & State Concepts`?**
  _High betweenness centrality (0.006) - this node is a cross-community bridge._
- **What connects `Compatibility wrapper for the instructor Streamlit app.`, `Compatibility wrapper for the assistant Streamlit app.`, `Populate ACADEMIC_PERIODS from the boundary dates.` to the rest of the system?**
  _292 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `UI Components & Visualization` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Thesis Chapters & Theory References` be split into smaller, more focused modules?**
  _Cohesion score 0.04 - nodes in this community are weakly interconnected._
- **Should `Learning Models & Analytics Theory` be split into smaller, more focused modules?**
  _Cohesion score 0.05 - nodes in this community are weakly interconnected._
- **Should `Data Loading & Session Persistence` be split into smaller, more focused modules?**
  _Cohesion score 0.06 - nodes in this community are weakly interconnected._