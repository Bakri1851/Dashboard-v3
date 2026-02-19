# views.py — Page-level view layouts
from datetime import datetime

import pandas as pd
import streamlit as st

import analytics
import components
import config
import data_loader


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

def in_class_view(df: pd.DataFrame) -> None:
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

    # Compute scores
    struggle_df = analytics.compute_student_struggle_scores(view_df)
    difficulty_df = analytics.compute_question_difficulty_scores(view_df)

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

    # Score distributions
    components.render_score_distributions(struggle_df, difficulty_df)

    st.markdown("---")

    # Formula info panel
    components.render_formula_info()


# Student Drill-Down View

def student_detail_view(df: pd.DataFrame, student_id: str) -> None:
    """Detailed view for a single student."""
    # Back button
    if components.render_back_button(key="back_student"):
        st.session_state["selected_student"] = None
        st.rerun()

    # Filter to this student
    student_df = df[df["user"] == student_id].copy()
    if student_df.empty:
        st.warning(f"No data found for student: {student_id}")
        return

    # Compute struggle score for this student (needs full dataset for normalization)
    all_struggle = analytics.compute_student_struggle_scores(df)
    student_row = all_struggle[all_struggle["user"] == student_id]

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
    # Count feedback requests per question (single-pass, Bug #2 fix)
    has_fb = student_df["ai_feedback"].notna() & (student_df["ai_feedback"].astype(str).str.strip() != "")
    student_df_with_fb = student_df.copy()
    student_df_with_fb["has_feedback"] = has_fb

    questions_table = (
        student_df_with_fb.groupby("question")
        .agg(
            attempts=("question", "size"),
            feedback_requests=("has_feedback", "sum"),
        )
        .reset_index()
        .sort_values("attempts", ascending=False)
    )
    components.render_data_table(questions_table, "Questions Attempted")

    st.markdown("---")

    # Submission Timeline (hourly)
    components.render_timeline_chart(
        student_df, "timestamp", "Submission Timeline", config.COLORS["cyan"]
    )

    st.markdown("---")

    # Recent Submissions table (last 10, newest first)
    recent = (
        student_df.sort_values("timestamp", ascending=False)
        .head(config.RECENT_SUBMISSIONS_LIMIT)
        [["timestamp", "question", "student_answer", "ai_feedback"]]
    )
    components.render_data_table(recent, "Recent Submissions", max_rows=config.RECENT_SUBMISSIONS_LIMIT)


# Question Drill-Down View

def question_detail_view(df: pd.DataFrame, question_id: str) -> None:
    """Detailed view for a single question."""
    # Back button
    if components.render_back_button(key="back_question"):
        st.session_state["selected_question"] = None
        st.rerun()

    # Filter to this question
    question_df = df[df["question"] == question_id].copy()
    if question_df.empty:
        st.warning(f"No data found for question: {question_id}")
        return

    # Compute difficulty score (needs full dataset for normalization)
    all_difficulty = analytics.compute_question_difficulty_scores(df)
    question_row = all_difficulty[all_difficulty["question"] == question_id]

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

    # Students Who Attempted chart (top 15)
    student_counts = (
        question_df.groupby("user").size().reset_index(name="attempts")
        .sort_values("attempts", ascending=False)
    )
    components.render_bar_chart(
        student_counts,
        x_col="attempts",
        y_col="user",
        title="Students Who Attempted",
        color=config.COLORS["magenta"],
        orientation="h",
        max_items=config.QUESTION_DETAIL_TOP_STUDENTS,
    )

    st.markdown("---")

    # Students table
    has_fb = question_df["ai_feedback"].notna() & (question_df["ai_feedback"].astype(str).str.strip() != "")
    question_df_with_fb = question_df.copy()
    question_df_with_fb["has_feedback"] = has_fb

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

    st.markdown("---")

    # Sample Answers table (first 10)
    samples = (
        question_df.sort_values("timestamp")
        .head(config.SAMPLE_ANSWERS_LIMIT)
        [["user", "timestamp", "student_answer", "ai_feedback"]]
    )
    components.render_data_table(samples, "Sample Answers", max_rows=config.SAMPLE_ANSWERS_LIMIT)


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

    elif selected_chart == "Students by Module":
        components.render_students_by_module_chart(df)


# Settings View

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
        f'text-transform:uppercase; letter-spacing:2px; font-size:1rem;">Refresh</h3>',
        unsafe_allow_html=True,
    )
    st.checkbox("Enable Auto-Refresh", key="auto_refresh")
    st.selectbox(
        "Interval (seconds)",
        config.AUTO_REFRESH_OPTIONS,
        key="refresh_interval",
        disabled=not st.session_state["auto_refresh"],
    )

    if st.session_state["last_refresh"]:
        st.caption(f"Last refresh: {st.session_state['last_refresh'].strftime('%H:%M:%S')}")

    if st.button("Refresh Now", key="settings_refresh_now"):
        data_loader.fetch_raw_data.clear()
        st.rerun()

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
