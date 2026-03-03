# components.py — Reusable Streamlit UI components
from typing import Optional

import plotly.graph_objects as go
import pandas as pd
import streamlit as st

import config
import theme


# Header

def render_header() -> None:
    """Dashboard title with gradient text and subtitle."""
    st.markdown(
        """
        <div class="dashboard-header">
            <div class="title">LEARNING ANALYTICS DASHBOARD</div>
            <div class="subtitle">REAL-TIME STUDENT STRUGGLE &amp; QUESTION DIFFICULTY TRACKING</div>
            <div class="header-line"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Info Bar

def render_info_bar(
    view_name: str,
    total_submissions: int,
    unique_students: int,
    unique_questions: int,
) -> None:
    """Subtle summary bar with key counts."""
    c = config.COLORS
    st.markdown(
        f"""
        <div class="info-bar">
            <div class="info-item"><span class="info-value">{view_name}</span></div>
            <div class="info-item">Submissions: <span class="info-value">{total_submissions:,}</span></div>
            <div class="info-item">Students: <span class="info-value">{unique_students:,}</span></div>
            <div class="info-item">Questions: <span class="info-value">{unique_questions:,}</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Metric Cards

def render_metric_card(label: str, value, color: str) -> None:
    """Single metric card with glow border."""
    st.markdown(
        f"""
        <div class="metric-card" style="border: 1px solid {color}; box-shadow: 0 0 12px {color}33;">
            <div class="metric-value" style="color: {color};">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_summary_cards(struggle_df: pd.DataFrame) -> None:
    """4 summary cards counting students per struggle level."""
    # Count per level — order: Needs Help, Struggling, Minor Issues, On Track
    level_order = list(reversed(config.STRUGGLE_THRESHOLDS))
    cols = st.columns(4)

    for i, (low, high, label, color) in enumerate(level_order):
        count = len(struggle_df[struggle_df["struggle_level"] == label])
        with cols[i]:
            render_metric_card(label, count, color)


def render_student_detail_metrics(student_data: dict) -> None:
    """4 metric cards for student drill-down."""
    cols = st.columns(4)
    metrics = [
        ("Total Submissions", student_data.get("submission_count", 0), config.COLORS["cyan"]),
        ("Time Active (min)", student_data.get("time_active_min", 0), config.COLORS["blue"]),
        ("Error Rate (%)", student_data.get("error_rate_pct", 0), config.COLORS["orange"]),
        ("Recent Incorrectness", student_data.get("recent_incorrectness", 0), config.COLORS["magenta"]),
    ]
    for col, (label, value, color) in zip(cols, metrics):
        with col:
            render_metric_card(label, value, color)


def render_question_detail_metrics(question_data: dict) -> None:
    """4 metric cards for question drill-down."""
    cols = st.columns(4)
    metrics = [
        ("Total Attempts", question_data.get("total_attempts", 0), config.COLORS["cyan"]),
        ("Unique Students", question_data.get("unique_students", 0), config.COLORS["blue"]),
        ("Avg Attempts/Student", question_data.get("avg_attempts", 0), config.COLORS["purple"]),
        ("Incorrect Rate (%)", question_data.get("incorrect_rate_pct", 0), config.COLORS["orange"]),
    ]
    for col, (label, value, color) in zip(cols, metrics):
        with col:
            render_metric_card(label, value, color)


# Leaderboard Charts

def _apply_leaderboard_layout(
    fig: go.Figure,
    title: str,
    score_max: float,
    n_items: int,
) -> None:
    """Apply shared layout to both leaderboard bar charts."""
    layout = theme.get_plotly_layout_defaults()
    fig.update_layout(**layout)
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(family=f"{config.FONT_HEADING}, sans-serif", size=14, color=config.COLORS["cyan"]),
        ),
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,
            font=dict(family=f"{config.FONT_BODY}, monospace", size=11),
        ),
        yaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=None,
            categoryorder="trace",
            autorange="reversed",
        ),
        xaxis=dict(
            visible=False,
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            title=None,
            range=[0, min(1.15, score_max + 0.15)],
        ),
        barmode="overlay",
        height=max(300, n_items * 38),
        bargap=0.15,
    )



def render_student_leaderboard(
    struggle_df: pd.DataFrame,
) -> Optional[str]:
    """
    Horizontal bar chart of students ranked by struggle score.
    Clickable legend toggles level visibility.
    Returns selected student user ID if a bar was clicked, else None.
    """
    if struggle_df.empty:
        st.info("No student data available.")
        return None

    display = struggle_df.head(config.LEADERBOARD_MAX_ITEMS).copy()

    if display.empty:
        st.info("No student data available.")
        return None

    fig = go.Figure()

    # One trace per struggle level (reversed so legend reads severe → mild)
    for _low, _high, label, color in reversed(config.STRUGGLE_THRESHOLDS):
        level_df = display[display["struggle_level"] == label]
        if level_df.empty:
            continue
        bar_color = config.LEADERBOARD_BAR_COLORS.get(label, color)
        fig.add_trace(go.Bar(
            y=level_df["user"],
            x=level_df["struggle_score"],
            orientation="h",
            name=label,
            legendgroup=label,
            marker_color=bar_color,
            text=level_df["user"],
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(
                family=f"{config.FONT_BODY}, monospace",
                color="white",
                size=11,
            ),
            customdata=level_df["user"].values,
            hovertemplate="Student: %{customdata}<br>Score: %{x:.3f}<extra></extra>",
        ))
        # Score text outside bar (right of bar end) — same legendgroup so it toggles
        fig.add_trace(go.Scatter(
            y=level_df["user"],
            x=level_df["struggle_score"] + 0.005,
            mode="text",
            text=[f"{s:.3f}" for s in level_df["struggle_score"]],
            textposition="middle right",
            textfont=dict(
                family=f"{config.FONT_BODY}, monospace",
                color=color,
                size=11,
            ),
            legendgroup=label,
            showlegend=False,
            hoverinfo="skip",
            cliponaxis=False,
        ))

    _apply_leaderboard_layout(
        fig,
        title="STUDENT STRUGGLE LEADERBOARD",
        score_max=display["struggle_score"].max(),
        n_items=len(display),
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        selection_mode=("points",),
        key="student_leaderboard",
    )

    if event and event.selection and event.selection.get("points"):
        point = event.selection["points"][0]
        user = point.get("customdata")
        if user:
            return user

    return None


def render_question_leaderboard(
    difficulty_df: pd.DataFrame,
) -> Optional[str]:
    """
    Horizontal bar chart of questions ranked by difficulty score.
    Clickable legend toggles level visibility.
    Returns selected question ID if a bar was clicked, else None.
    """
    if difficulty_df.empty:
        st.info("No question data available.")
        return None

    display = difficulty_df.head(config.LEADERBOARD_MAX_ITEMS).copy()

    if display.empty:
        st.info("No question data available.")
        return None

    # Truncate labels
    max_len = config.QUESTION_LABEL_MAX_LEN
    display["display_label"] = display["question"].apply(
        lambda q: q if len(str(q)) <= max_len else str(q)[:max_len] + "..."
    )

    fig = go.Figure()

    # One trace per difficulty level (reversed so legend reads severe → mild)
    for _low, _high, label, color in reversed(config.DIFFICULTY_THRESHOLDS):
        level_df = display[display["difficulty_level"] == label]
        if level_df.empty:
            continue
        bar_color = config.LEADERBOARD_BAR_COLORS.get(label, color)
        fig.add_trace(go.Bar(
            y=level_df["display_label"],
            x=level_df["difficulty_score"],
            orientation="h",
            name=label,
            legendgroup=label,
            marker_color=bar_color,
            text=level_df["display_label"],
            textposition="inside",
            insidetextanchor="start",
            textfont=dict(
                family=f"{config.FONT_BODY}, monospace",
                color="white",
                size=10,
            ),
            customdata=level_df["question"].values,
            hovertemplate="Question: %{customdata}<br>Score: %{x:.3f}<extra></extra>",
        ))
        # Score text outside bar (right of bar end) — same legendgroup so it toggles
        fig.add_trace(go.Scatter(
            y=level_df["display_label"],
            x=level_df["difficulty_score"] + 0.005,
            mode="text",
            text=[f"{s:.3f}" for s in level_df["difficulty_score"]],
            textposition="middle right",
            textfont=dict(
                family=f"{config.FONT_BODY}, monospace",
                color=color,
                size=11,
            ),
            legendgroup=label,
            showlegend=False,
            hoverinfo="skip",
            cliponaxis=False,
        ))

    _apply_leaderboard_layout(
        fig,
        title="QUESTION DIFFICULTY LEADERBOARD",
        score_max=display["difficulty_score"].max(),
        n_items=len(display),
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        on_select="rerun",
        selection_mode=("points",),
        key="question_leaderboard",
    )

    if event and event.selection and event.selection.get("points"):
        point = event.selection["points"][0]
        question = point.get("customdata")
        if question:
            return question

    return None


# Score Distributions

def render_score_distributions(
    struggle_df: pd.DataFrame,
    difficulty_df: pd.DataFrame,
) -> None:
    """Two side-by-side histograms: struggle scores and difficulty scores."""
    col1, col2 = st.columns(2)
    layout = theme.get_plotly_layout_defaults()

    with col1:
        if not struggle_df.empty:
            fig = go.Figure(
                go.Histogram(
                    x=struggle_df["struggle_score"],
                    nbinsx=config.HISTOGRAM_BINS,
                    marker_color=config.COLORS["cyan"],
                    opacity=0.8,
                )
            )
            fig.update_layout(**layout)
            fig.update_layout(
                title=dict(
                    text="STRUGGLE SCORE DISTRIBUTION",
                    font=dict(family=f"{config.FONT_HEADING}, sans-serif", size=13, color=config.COLORS["cyan"]),
                ),
                xaxis=dict(title="Score"),
                yaxis=dict(title="Count"),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True, key="struggle_dist")
        else:
            st.info("No student data for distribution.")

    with col2:
        if not difficulty_df.empty:
            fig = go.Figure(
                go.Histogram(
                    x=difficulty_df["difficulty_score"],
                    nbinsx=config.HISTOGRAM_BINS,
                    marker_color=config.COLORS["magenta"],
                    opacity=0.8,
                )
            )
            fig.update_layout(**layout)
            fig.update_layout(
                title=dict(
                    text="DIFFICULTY SCORE DISTRIBUTION",
                    font=dict(family=f"{config.FONT_HEADING}, sans-serif", size=13, color=config.COLORS["cyan"]),
                ),
                xaxis=dict(title="Score"),
                yaxis=dict(title="Count"),
                height=300,
            )
            st.plotly_chart(fig, use_container_width=True, key="difficulty_dist")
        else:
            st.info("No question data for distribution.")


# Formula Info Panel (Bug #1 fix: all values from config)

def render_formula_info() -> None:
    """Expandable section showing scoring formulas with dynamic config values."""
    with st.expander("Scoring Formulas & Methodology", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(f"### Student Struggle Score")
            st.markdown(
                f"**S_raw** = {config.STRUGGLE_WEIGHT_N} \u00d7 n\u0302 + "
                f"{config.STRUGGLE_WEIGHT_T} \u00d7 t\u0302 + "
                f"{config.STRUGGLE_WEIGHT_E} \u00d7 \u00ea + "
                f"{config.STRUGGLE_WEIGHT_F} \u00d7 f\u0302 + "
                f"{config.STRUGGLE_WEIGHT_A} \u00d7 A_raw"
            )
            st.markdown("**Components:**")
            st.markdown(
                f"- **n\u0302** (w={config.STRUGGLE_WEIGHT_N}): Submission count, min-max normalised\n"
                f"- **t\u0302** (w={config.STRUGGLE_WEIGHT_T}): Time active (minutes), min-max normalised\n"
                f"- **\u00ea** (w={config.STRUGGLE_WEIGHT_E}): Error rate (incorrectness > {config.CORRECT_THRESHOLD})\n"
                f"- **f\u0302** (w={config.STRUGGLE_WEIGHT_F}): Feedback request rate\n"
                f"- **A_raw** (w={config.STRUGGLE_WEIGHT_A}): Weighted recent incorrectness (last {config.RECENT_SUBMISSION_COUNT})"
            )
            st.markdown("**Thresholds:**")
            for low, high, label, color in config.STRUGGLE_THRESHOLDS:
                st.markdown(
                    f'<span style="color:{color}; font-weight:bold;">\u2588 {label}: '
                    f'{low:.2f} - {high:.2f}</span>',
                    unsafe_allow_html=True,
                )

        with col2:
            st.markdown(f"### Question Difficulty Score")
            st.markdown(
                f"**D_raw** = {config.DIFFICULTY_WEIGHT_C} \u00d7 c\u0303 + "
                f"{config.DIFFICULTY_WEIGHT_T} \u00d7 t\u0303 + "
                f"{config.DIFFICULTY_WEIGHT_A} \u00d7 a\u0303 + "
                f"{config.DIFFICULTY_WEIGHT_F} \u00d7 f\u0303"
            )
            st.markdown("**Components:**")
            st.markdown(
                f"- **c\u0303** (w={config.DIFFICULTY_WEIGHT_C}): Incorrect rate (1 - correct/total)\n"
                f"- **t\u0303** (w={config.DIFFICULTY_WEIGHT_T}): Avg time per student, min-max normalised\n"
                f"- **a\u0303** (w={config.DIFFICULTY_WEIGHT_A}): Avg attempts per student, min-max normalised\n"
                f"- **f\u0303** (w={config.DIFFICULTY_WEIGHT_F}): Avg incorrectness score"
            )
            st.markdown("**Thresholds:**")
            for low, high, label, color in config.DIFFICULTY_THRESHOLDS:
                st.markdown(
                    f'<span style="color:{color}; font-weight:bold;">\u2588 {label}: '
                    f'{low:.2f} - {high:.2f}</span>',
                    unsafe_allow_html=True,
                )


# Back Button

def render_back_button(key: str = "back") -> bool:
    """Styled back button. Returns True if clicked."""
    return st.button("\u2190 Back to Dashboard", key=key)


# Entity Header Card (drill-down)

def render_entity_header_card(
    title: str,
    score: float,
    level_label: str,
    level_color: str,
) -> None:
    """Header card for drill-down views."""
    st.markdown(
        f"""
        <div class="entity-header" style="border: 2px solid {level_color}; box-shadow: 0 0 20px {level_color}33;">
            <div class="entity-name">{title}</div>
            <div class="entity-score" style="color: {level_color};">{score:.3f}</div>
            <div class="entity-level" style="color: {level_color}; border-color: {level_color};">{level_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Generic Charts for Drill-Downs

def render_bar_chart(
    data: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    color: str,
    orientation: str = "v",
    max_items: int = 15,
) -> None:
    """Generic themed bar chart."""
    display = data.head(max_items)
    if display.empty:
        st.info("No data available for this chart.")
        return

    if orientation == "h":
        display = display.iloc[::-1]
        fig = go.Figure(
            go.Bar(
                y=display[y_col],
                x=display[x_col],
                orientation="h",
                marker_color=color,
                opacity=0.85,
            )
        )
    else:
        fig = go.Figure(
            go.Bar(
                x=display[x_col],
                y=display[y_col],
                marker_color=color,
                opacity=0.85,
            )
        )

    layout = theme.get_plotly_layout_defaults()
    fig.update_layout(**layout)
    fig.update_layout(
        title=dict(
            text=title.upper(),
            font=dict(family=f"{config.FONT_HEADING}, sans-serif", size=13, color=config.COLORS["cyan"]),
        ),
        height=max(300, min(len(display) * 30, 500)) if orientation == "h" else 400,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_timeline_chart(
    df: pd.DataFrame,
    timestamp_col: str,
    title: str,
    color: str,
    freq: str = "h",
) -> None:
    """Hourly line chart of event frequency over time."""
    if df.empty:
        st.info("No data available for timeline.")
        return

    timeline = (
        df.set_index(timestamp_col)
        .resample(freq)
        .size()
        .reset_index(name="count")
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=timeline[timestamp_col],
            y=timeline["count"],
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(size=5, color=color),
            fill="tozeroy",
            fillcolor=f"rgba({_hex_to_rgb(color)}, 0.1)",
        )
    )

    layout = theme.get_plotly_layout_defaults()
    fig.update_layout(**layout)
    fig.update_layout(
        title=dict(
            text=title.upper(),
            font=dict(family=f"{config.FONT_HEADING}, sans-serif", size=13, color=config.COLORS["cyan"]),
        ),
        xaxis=dict(title="Time"),
        yaxis=dict(title="Count"),
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)


def render_data_table(
    df: pd.DataFrame,
    title: str,
    max_rows: Optional[int] = None,
) -> None:
    """Styled dataframe display."""
    st.markdown(
        f'<h4 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}, sans-serif; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:0.95rem;">{title}</h4>',
        unsafe_allow_html=True,
    )
    display = df.head(max_rows) if max_rows else df
    st.dataframe(display, use_container_width=True, hide_index=True)


# Data Analysis Charts

def render_module_usage_chart(df: pd.DataFrame) -> None:
    """Vertical bar chart of submission counts per module."""
    if df.empty:
        st.info("No data available.")
        return
    counts = df.groupby("module").size().reset_index(name="submissions").sort_values("submissions", ascending=False)
    render_bar_chart(counts, x_col="module", y_col="submissions", title="Module Usage", color=config.COLORS["cyan"])


def render_top_questions_chart(df: pd.DataFrame, module: str) -> None:
    """Horizontal bar chart of top 10 questions in a module."""
    filtered = df if not module or module == "All Modules" else df[df["module"] == module]
    if filtered.empty:
        st.info("No data available for this module.")
        return
    counts = (
        filtered.groupby("question").size().reset_index(name="attempts")
        .sort_values("attempts", ascending=False)
        .head(config.DATA_ANALYSIS_TOP_QUESTIONS)
    )
    render_bar_chart(counts, x_col="attempts", y_col="question", title=f"Top Questions — {module}", color=config.COLORS["magenta"], orientation="h", max_items=config.DATA_ANALYSIS_TOP_QUESTIONS)


def render_user_activity_chart(df: pd.DataFrame, module: Optional[str] = None) -> None:
    """Vertical bar chart of top 20 most active users."""
    filtered = df if not module or module == "All Modules" else df[df["module"] == module]
    if filtered.empty:
        st.info("No data available.")
        return
    counts = (
        filtered.groupby("user").size().reset_index(name="submissions")
        .sort_values("submissions", ascending=False)
        .head(config.DATA_ANALYSIS_TOP_USERS)
    )
    render_bar_chart(counts, x_col="user", y_col="submissions", title="User Activity", color=config.COLORS["green"])


def render_activity_timeline_chart(df: pd.DataFrame) -> None:
    """Line chart with hourly granularity and filled area glow."""
    render_timeline_chart(df, "timestamp", "Activity Timeline", config.COLORS["cyan"])


def render_students_by_module_chart(df: pd.DataFrame) -> None:
    """Vertical bar chart of unique student counts per module."""
    if df.empty:
        st.info("No data available.")
        return
    counts = df.groupby("module")["user"].nunique().reset_index(name="students").sort_values("students", ascending=False)
    render_bar_chart(counts, x_col="module", y_col="students", title="Students by Module", color=config.COLORS["purple"])


# Helpers

def _hex_to_rgb(hex_color: str) -> str:
    """Convert '#rrggbb' to 'r, g, b' string for rgba()."""
    h = hex_color.lstrip("#")
    return f"{int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)}"
