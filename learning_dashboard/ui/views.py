# views.py — Page-level view layouts
from datetime import datetime

import pandas as pd
import streamlit as st

from learning_dashboard import analytics, config, data_loader
from learning_dashboard.ui import components


def _format_session_timestamp(raw_value: str) -> str:
    """Render ISO timestamp in a compact display format."""
    if not raw_value:
        return "-"
    try:
        return datetime.fromisoformat(raw_value).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return raw_value


def _format_duration(seconds: int) -> str:
    """Render seconds as HH:MM:SS."""
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


# In Class View (default)

def in_class_view(df: pd.DataFrame, struggle_df: pd.DataFrame, difficulty_df: pd.DataFrame) -> None:
    """Main leaderboard view with summary cards, leaderboards, and distributions."""
    load_warning = st.session_state.get("session_load_warning")
    if load_warning:
        st.warning(load_warning)
        st.session_state["session_load_warning"] = None

    components.render_info_bar(
        view_name="In Class View",
        total_submissions=len(df),
        unique_students=df["user"].nunique() if not df.empty else 0,
        unique_questions=df["question"].nunique() if not df.empty else 0,
    )

    # Scope toggle — only shown when no session/time filter is controlling the data
    _session_controlled = (
        st.session_state.get("time_filter_enabled")
        or st.session_state.get("session_active")
        or st.session_state.get("loaded_session_id") is not None
    )
    if not _session_controlled:
        today_only = st.session_state.get("today_filter_only", True)
        no_today_data = not st.session_state.get("_today_has_data", True)
        _scope_cols = st.columns([7, 3])
        with _scope_cols[1]:
            if today_only:
                if no_today_data:
                    st.caption("No data for today — showing all")
                elif st.button("View All Data →", use_container_width=True, key="scope_all"):
                    st.session_state["today_filter_only"] = False
                    st.rerun()
            else:
                if st.button("← Today Only", use_container_width=True, key="scope_today"):
                    st.session_state["today_filter_only"] = True
                    st.rerun()

    # Secondary module filter (in main content area, NOT sidebar)
    modules = ["All Modules"] + sorted(df["module"].unique().tolist()) if not df.empty else ["All Modules"]
    secondary_module = st.selectbox(
        "Filter by Module",
        modules,
        key="secondary_module_filter",
    )
    view_df = data_loader.filter_by_module(df, secondary_module)

    if view_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # When a secondary module filter is active, scores must be relative to that
    # subset — but only recompute when the filter or underlying data changes.
    if secondary_module != "All Modules":
        _sec_key = (st.session_state.get("_analytics_key"), secondary_module)
        if st.session_state.get("_sec_analytics_key") != _sec_key:
            struggle_df = analytics.compute_student_struggle_scores(view_df)
            difficulty_df = analytics.compute_question_difficulty_scores(view_df)
            st.session_state["_sec_struggle_df"] = struggle_df
            st.session_state["_sec_difficulty_df"] = difficulty_df
            st.session_state["_sec_analytics_key"] = _sec_key
        else:
            struggle_df = st.session_state["_sec_struggle_df"]
            difficulty_df = st.session_state["_sec_difficulty_df"]

    # --- Model toggle ---
    # When improved models are enabled and have data, allow switching the
    # leaderboards between baseline scores and IRT/BKT scores.
    _improved_on = st.session_state.get("improved_models_enabled", False)
    _irt_df = st.session_state.get("_irt_difficulty_df")
    _mastery_summary = st.session_state.get("_mastery_summary_df")
    _can_switch = (
        _improved_on
        and _irt_df is not None and not _irt_df.empty
        and _mastery_summary is not None and not _mastery_summary.empty
    )

    use_improved = False
    if _can_switch:
        use_improved = st.toggle(
            "Use IRT / BKT models",
            value=st.session_state.get("_use_improved_leaderboards", False),
            key="_use_improved_leaderboards",
            help="Switch leaderboards to IRT difficulty and BKT mastery-gap scores.",
        )

    if use_improved and _can_switch:
        # Adapt IRT difficulty → question leaderboard format
        # Min-max normalize so scores spread across threshold ranges
        difficulty_df = _irt_df.copy()
        difficulty_df["difficulty_score"] = analytics.min_max_normalize(
            difficulty_df["irt_difficulty"]
        )
        _d_classified = difficulty_df["difficulty_score"].apply(
            lambda s: analytics.classify_score(s, config.DIFFICULTY_THRESHOLDS)
        )
        difficulty_df["difficulty_level"] = _d_classified.str[0]
        difficulty_df["difficulty_color"] = _d_classified.str[1]

        # Adapt BKT mastery summary → student leaderboard format
        # Low mastery ≈ high struggle, so score = 1 - mean_mastery
        # Min-max normalize so scores spread across threshold ranges
        _ms = _mastery_summary.copy()
        _ms["struggle_score"] = analytics.min_max_normalize(
            1.0 - _ms["mean_mastery"]
        )
        _ms = _ms.sort_values("struggle_score", ascending=False).reset_index(drop=True)
        _s_classified = _ms["struggle_score"].apply(
            lambda s: analytics.classify_score(s, config.STRUGGLE_THRESHOLDS)
        )
        _ms["struggle_level"] = _s_classified.str[0]
        _ms["struggle_color"] = _s_classified.str[1]
        struggle_df = _ms[["user", "struggle_score", "struggle_level", "struggle_color"]]

    # Summary cards
    components.render_summary_cards(struggle_df)

    st.markdown("---")

    # Side-by-side leaderboards
    left_col, right_col = st.columns(2, gap="large")

    with left_col:
        selected_student = components.render_student_leaderboard(struggle_df)
        if selected_student is not None:
            st.session_state["selected_student"] = selected_student
            st.rerun()

    with right_col:
        selected_question = components.render_question_leaderboard(difficulty_df)
        if selected_question is not None:
            st.session_state["selected_question"] = selected_question
            st.rerun()

    st.markdown("---")

    # --- Collaborative Filtering Panel ---
    if st.session_state.get("cf_enabled", False):
        try:
            cf_threshold = st.session_state.get("cf_threshold", 0.6)
            _cf_scores, cf_diag = analytics.compute_cf_struggle_scores(
                struggle_df, threshold=cf_threshold,
            )

            if cf_diag.get("fallback", False):
                reason = cf_diag.get("error") or cf_diag.get("reason", "unknown")
                st.warning(f"Collaborative Filtering could not run: {reason}")
            else:
                st.markdown(
                    f'<h3 style="color:{config.COLORS["purple"]}; font-family:{config.FONT_HEADING}; '
                    f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">'
                    f'Collaborative Filtering</h3>',
                    unsafe_allow_html=True,
                )

                cf_c1, cf_c2, cf_c3 = st.columns(3)
                with cf_c1:
                    components.render_metric_card(
                        "CF Elevated", cf_diag["n_elevated_cf"], config.COLORS["purple"],
                    )
                with cf_c2:
                    components.render_metric_card(
                        "Parametric Flagged", cf_diag["n_flagged_parametric"], config.COLORS["orange"],
                    )
                with cf_c3:
                    components.render_metric_card(
                        "Threshold (τ)", f"{cf_threshold:.2f}", config.COLORS["cyan"],
                    )

                elevated = cf_diag.get("elevated_students", [])
                if elevated:
                    components.render_data_table(
                        pd.DataFrame(elevated), "Students Elevated by CF",
                    )
                else:
                    st.info("CF found no additional at-risk students beyond parametric detection.")

            st.markdown("---")
        except Exception as e:
            st.warning(f"Collaborative Filtering encountered an error: {e}")
            st.markdown("---")

    # Score distributions
    components.render_score_distributions(struggle_df, difficulty_df)

    st.markdown("---")

    # Formula info panel
    components.render_formula_info()


# Student Drill-Down View

def student_detail_view(df: pd.DataFrame, student_id: str, struggle_df: pd.DataFrame, difficulty_df: pd.DataFrame | None = None) -> None:
    """Detailed view for a single student."""
    # Back button
    if components.render_back_button(key="back_student"):
        st.session_state["selected_student"] = None
        st.session_state.pop("student_leaderboard", None)
        st.rerun()

    # Filter to this student
    student_df = df[df["user"] == student_id].copy()
    if student_df.empty:
        st.warning(f"No data found for student: {student_id}")
        return

    student_row = struggle_df[struggle_df["user"] == student_id]

    if student_row.empty:
        st.warning(f"Could not compute scores for student: {student_id}")
        return

    student_data = student_row.iloc[0].to_dict()

    # Header card
    components.render_entity_header_card(
        title=student_id,
        score=student_data["struggle_score"],
        level_label=student_data["struggle_level"],
        level_color=student_data["struggle_color"],
    )

    # 4 Metric cards
    components.render_student_detail_metrics(student_data)

    st.markdown("---")

    # Questions Attempted chart (top 10)
    question_counts = (
        student_df.groupby("question").size().reset_index(name="attempts")
        .sort_values("attempts", ascending=False)
    )
    components.render_bar_chart(
        question_counts,
        x_col="attempts",
        y_col="question",
        title="Questions Attempted",
        color=config.COLORS["cyan"],
        orientation="h",
        max_items=config.STUDENT_DETAIL_TOP_QUESTIONS,
    )

    st.markdown("---")

    # Questions table
    student_df_with_fb = data_loader.add_feedback_flag(student_df)

    questions_table = (
        student_df_with_fb.groupby("question")
        .agg(
            attempts=("question", "size"),
            feedback_requests=("has_feedback", "sum"),
        )
        .reset_index()
        .sort_values("attempts", ascending=False)
    )
    if difficulty_df is not None and not difficulty_df.empty:
        diff_cols = difficulty_df[["question", "difficulty_level", "difficulty_score"]].copy()
        questions_table = questions_table.merge(diff_cols, on="question", how="left")
    components.render_data_table(questions_table, "Questions Attempted")

    st.markdown("---")

    # Submission Timeline (hourly)
    components.render_timeline_chart(
        student_df, "timestamp", "Submission Timeline", config.COLORS["cyan"]
    )

    st.markdown("---")

    # Retry intensity trend — attempt number per question, rolling average
    trend_df = student_df.sort_values("timestamp").copy().reset_index(drop=True)
    trend_df["attempt_number"] = trend_df.groupby("question").cumcount() + 1
    if len(trend_df) >= 3:
        window = min(5, len(trend_df))
        trend_df["rolling_retry"] = trend_df["attempt_number"].rolling(window, min_periods=1).mean()
        components.render_retry_trend(trend_df)

    st.markdown("---")

    # Recent Submissions table (last 10, newest first)
    recent = (
        student_df.sort_values("timestamp", ascending=False)
        .head(config.RECENT_SUBMISSIONS_LIMIT)
        [["timestamp", "question", "student_answer", "ai_feedback"]]
    )
    components.render_data_table(recent, "Recent Submissions", max_rows=config.RECENT_SUBMISSIONS_LIMIT)

    # --- CF: Similar Students ---
    if st.session_state.get("cf_enabled", False):
        try:
            similar_df = analytics.get_similar_students(student_id, struggle_df, k=5)
            if similar_df is not None and not similar_df.empty:
                st.markdown("---")
                st.markdown(
                    f'<h3 style="color:{config.COLORS["purple"]}; font-family:{config.FONT_HEADING}; '
                    f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">'
                    f'Most Similar Students (CF)</h3>',
                    unsafe_allow_html=True,
                )
                st.caption(
                    "Students ranked by cosine similarity across five behavioural features. "
                    "High similarity means comparable submission patterns."
                )
                components.render_data_table(similar_df, "", max_rows=5)
        except Exception as e:
            st.warning(f"Could not compute similar students: {e}")


# Question Drill-Down View

def question_detail_view(df: pd.DataFrame, question_id: str, difficulty_df: pd.DataFrame) -> None:
    """Detailed view for a single question."""
    # Back button
    if components.render_back_button(key="back_question"):
        st.session_state["selected_question"] = None
        st.session_state.pop("question_leaderboard", None)
        st.rerun()

    # Filter to this question
    question_df = df[df["question"] == question_id].copy()
    if question_df.empty:
        st.warning(f"No data found for question: {question_id}")
        return

    question_row = difficulty_df[difficulty_df["question"] == question_id]

    if question_row.empty:
        st.warning(f"Could not compute scores for question: {question_id}")
        return

    question_data = question_row.iloc[0].to_dict()

    # Header card
    components.render_entity_header_card(
        title=question_id,
        score=question_data["difficulty_score"],
        level_label=question_data["difficulty_level"],
        level_color=question_data["difficulty_color"],
    )

    # 4 Metric cards
    components.render_question_detail_metrics(question_data)

    st.markdown("---")

    # Mistake Clusters
    if "incorrectness" not in question_df.columns:
        st.info("Incorrectness scores not yet computed.")
    else:
        wrong_count = (question_df["incorrectness"] >= config.CORRECT_THRESHOLD).sum()
        if wrong_count < config.CLUSTER_MIN_WRONG:
            st.info(
                f"Not enough incorrect answers to cluster "
                f"({wrong_count} found — need at least {config.CLUSTER_MIN_WRONG})."
            )
        else:
            with st.spinner("Analysing mistake patterns..."):
                clusters = analytics.cluster_question_mistakes(question_df, question_id)
            if clusters is None:
                st.info("Could not generate clusters for this question.")
            else:
                components.render_mistake_clusters(clusters)

    st.markdown("---")

    # Students table
    question_df_with_fb = data_loader.add_feedback_flag(question_df)

    students_table = (
        question_df_with_fb.groupby("user")
        .agg(
            attempts=("user", "size"),
            feedback_requests=("has_feedback", "sum"),
        )
        .reset_index()
        .sort_values("attempts", ascending=False)
    )
    components.render_data_table(students_table, "Students Who Attempted")

    st.markdown("---")

    # Attempt Timeline (hourly)
    components.render_timeline_chart(
        question_df, "timestamp", "Attempt Timeline", config.COLORS["magenta"]
    )



# Data Analysis View

def data_analysis_view(df: pd.DataFrame) -> None:
    """Secondary view with 5 analytical chart types."""
    components.render_info_bar(
        view_name="Data Analysis",
        total_submissions=len(df),
        unique_students=df["user"].nunique() if not df.empty else 0,
        unique_questions=df["question"].nunique() if not df.empty else 0,
    )

    if df.empty:
        st.warning("No data available for analysis.")
        return

    chart_options = [
        "Module Usage",
        "Top Questions",
        "User Activity",
        "Activity Timeline",
        "Activity by Academic Week",
        "Students by Module",
    ]
    selected_chart = st.selectbox("Select Analysis", chart_options, key="analysis_chart")

    st.markdown("---")

    if selected_chart == "Module Usage":
        components.render_module_usage_chart(df)

    elif selected_chart == "Top Questions":
        modules = ["All Modules"] + sorted(df["module"].unique().tolist())
        module = st.selectbox("Select Module", modules, key="analysis_module_questions")
        components.render_top_questions_chart(df, module)

    elif selected_chart == "User Activity":
        modules = ["All Modules"] + sorted(df["module"].unique().tolist())
        module = st.selectbox("Filter by Module (optional)", modules, key="analysis_module_users")
        components.render_user_activity_chart(df, module)

    elif selected_chart == "Activity Timeline":
        components.render_activity_timeline_chart(df)

    elif selected_chart == "Activity by Academic Week":
        components.render_academic_period_chart(df)

    elif selected_chart == "Students by Module":
        components.render_students_by_module_chart(df)


# Settings View

def _setting_toggle(label: str, state_key: str, **kwargs) -> None:
    """Render a checkbox that persists via session state (survives view changes).

    Streamlit deletes widget-bound keys when the widget stops rendering.
    This helper uses a dedicated widget key and an ``on_change`` callback
    to copy the value back into the canonical session-state key so the
    setting survives navigation away from the Settings page.
    """
    widget_key = f"_w_{state_key}"

    def _sync():
        st.session_state[state_key] = st.session_state[widget_key]

    st.checkbox(
        label,
        value=st.session_state.get(state_key, False),
        key=widget_key,
        on_change=_sync,
        **kwargs,
    )


def _setting_slider(label: str, state_key: str, **kwargs) -> None:
    """Render a slider that persists via session state."""
    widget_key = f"_w_{state_key}"

    def _sync():
        st.session_state[state_key] = st.session_state[widget_key]

    st.slider(
        label,
        value=st.session_state.get(state_key, kwargs.pop("default", 0.5)),
        key=widget_key,
        on_change=_sync,
        **kwargs,
    )


def _setting_selectbox(label: str, state_key: str, options, **kwargs) -> None:
    """Render a selectbox that persists via session state."""
    widget_key = f"_w_{state_key}"

    def _sync():
        st.session_state[state_key] = st.session_state[widget_key]

    current = st.session_state.get(state_key)
    idx = options.index(current) if current in options else 0

    st.selectbox(
        label,
        options,
        index=idx,
        key=widget_key,
        on_change=_sync,
        **kwargs,
    )


def settings_view(df: pd.DataFrame) -> None:
    """Application settings."""
    components.render_info_bar(
        view_name="Settings",
        total_submissions=len(df),
        unique_students=df["user"].nunique() if not df.empty else 0,
        unique_questions=df["question"].nunique() if not df.empty else 0,
    )

    st.markdown("---")

    st.markdown(
        f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">Sound Effects</h3>',
        unsafe_allow_html=True,
    )
    _setting_toggle("Enable Sound Effects", "sounds_enabled", help="Play sci-fi sound effects for key events (session start/end, student selection, data refresh, etc.).")

    st.markdown("---")

    st.markdown(
        f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">Refresh</h3>',
        unsafe_allow_html=True,
    )
    _setting_toggle("Enable Auto-Refresh", "auto_refresh")
    _setting_selectbox(
        "Interval (seconds)",
        "refresh_interval",
        config.AUTO_REFRESH_OPTIONS,
        disabled=not st.session_state.get("auto_refresh", False),
    )

    if st.session_state["last_refresh"]:
        st.caption(f"Last refresh: {st.session_state['last_refresh'].strftime('%H:%M:%S')}")

    if st.button("Refresh Now", key="settings_refresh_now"):
        data_loader.fetch_raw_data.clear()
        st.rerun()

    st.markdown("---")

    st.markdown(
        f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">Collaborative Filtering</h3>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "When enabled, CF identifies students who behave similarly to those already flagged as "
        "struggling by the parametric model, but whose own scores fall just below the threshold. "
        "It compares five normalised behavioural features using cosine similarity and checks the "
        "3 nearest neighbours of each unflagged student. If those neighbours include flagged "
        "students, the student is highlighted as potentially at risk.",
    )

    _setting_toggle(
        "Enable Collaborative Filtering",
        "cf_enabled",
        help="Run CF as a secondary detection layer after parametric scoring.",
    )

    if st.session_state.get("cf_enabled", False):
        _setting_slider(
            "Struggle Score Threshold (τ)",
            "cf_threshold",
            min_value=0.0,
            max_value=1.0,
            step=0.05,
            default=0.5,
            help="Students with a parametric struggle score at or above this value are used as reference 'struggling' students for CF.",
        )

    st.markdown("---")

    st.markdown(
        f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">Improved Models</h3>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "When enabled, alternative scoring models (IRT difficulty, BKT mastery) "
        "run alongside the baseline. The baseline is never replaced — improved "
        "models provide a second estimate for comparison.",
    )

    _setting_toggle(
        "Enable Improved Models",
        "improved_models_enabled",
        help="Run IRT difficulty estimation alongside the baseline model. "
             "Results are cached in session state for use by future comparison views.",
    )

    st.markdown("---")


def previous_sessions_view(df: pd.DataFrame) -> None:
    """Saved previous sessions view."""
    components.render_info_bar(
        view_name="Previous Sessions",
        total_submissions=len(df),
        unique_students=df["user"].nunique() if not df.empty else 0,
        unique_questions=df["question"].nunique() if not df.empty else 0,
    )

    st.markdown("---")

    st.markdown(
        f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">Previous Sessions</h3>',
        unsafe_allow_html=True,
    )

    saved_sessions = data_loader.load_saved_sessions()
    if not saved_sessions:
        st.caption("No previous sessions yet. End an active lab session to store one.")
        return

    # Academic period filter
    from learning_dashboard.academic_calendar import get_academic_period, academic_period_sorter

    def _session_period(record):
        raw = record.get("start_time", "")
        if not raw:
            return "Unknown"
        try:
            return get_academic_period(datetime.fromisoformat(raw))
        except (ValueError, TypeError):
            return "Unknown"

    period_labels = list({_session_period(r) for r in saved_sessions})
    period_labels.sort(key=lambda p: academic_period_sorter(p) if p != "Unknown" else (99, 0))
    period_options = ["All Periods"] + period_labels
    selected_period = st.selectbox("Filter by Academic Period", period_options, key="sessions_period_filter")

    if selected_period != "All Periods":
        saved_sessions = [r for r in saved_sessions if _session_period(r) == selected_period]

    if not saved_sessions:
        st.caption("No sessions found for this period.")
        return

    pending_delete = st.session_state.get("pending_delete_session_id")

    for record in saved_sessions:
        session_id = str(record.get("id", ""))
        if not session_id:
            continue

        context = record.get("context", {})
        if not isinstance(context, dict):
            context = {}

        is_loaded = st.session_state.get("loaded_session_id") == session_id
        session_name = record.get("name", "Untitled Session")
        start_at = _format_session_timestamp(record.get("start_time", ""))
        end_at = _format_session_timestamp(record.get("end_time", ""))
        duration = _format_duration(record.get("duration_seconds", 0))
        dashboard_view = context.get("dashboard_view", "In Class View")
        module_filter = context.get("secondary_module_filter", "All Modules")
        time_filter_state = "Enabled" if context.get("time_filter_enabled") else "Disabled"

        with st.container(border=True):
            loaded_note = " | LOADED" if is_loaded else ""
            st.markdown(f"**{session_name}**{loaded_note}")
            st.caption(
                f"Start: {start_at} | End: {end_at} | Duration: {duration} | "
                f"View: {dashboard_view} | Module: {module_filter} | Time Filter: {time_filter_state}"
            )

            action_col_1, action_col_2, action_col_3 = st.columns([1, 1, 6])
            with action_col_1:
                if st.button("Load", key=f"load_session_{session_id}"):
                    st.session_state["pending_session_load_record"] = record
                    st.session_state["pending_delete_session_id"] = None
                    st.rerun()

            with action_col_2:
                if st.button("Delete", key=f"delete_session_{session_id}"):
                    st.session_state["pending_delete_session_id"] = session_id
                    st.rerun()

            if pending_delete == session_id:
                st.warning("Confirm delete for this saved session.")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Confirm Delete", key=f"confirm_delete_session_{session_id}"):
                        data_loader.delete_session_record(session_id)
                        st.session_state["pending_delete_session_id"] = None
                        if st.session_state.get("loaded_session_id") == session_id:
                            st.session_state["loaded_session_id"] = None
                            st.session_state["loaded_session_start"] = None
                            st.session_state["loaded_session_end"] = None
                        st.rerun()
                with cancel_col:
                    if st.button("Cancel", key=f"cancel_delete_session_{session_id}"):
                        st.session_state["pending_delete_session_id"] = None
                        st.rerun()
