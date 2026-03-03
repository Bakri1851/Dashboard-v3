# lab_app.py — Mobile lab assistant app (runs on separate port)
# Usage: streamlit run lab_app.py --server.port 8502
import html
from typing import Optional

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import analytics
import config
import data_loader
import lab_state
import theme
import sound


# Helpers

_JOIN_NOTICE_KEY = "lab_join_notice"

@st.cache_data(ttl=10)
def _load_student_data() -> tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """Fetch live data and compute struggle scores. Returns (df, struggle_df)."""
    df, _err = data_loader.load_data()
    if df.empty:
        return df, None
    struggle_df = analytics.compute_student_struggle_scores(df)
    return df, struggle_df


def _heading(text: str, sub: str = "") -> None:
    """Render a centred page heading with optional subtitle."""
    st.markdown(
        f'<h2 style="text-align:center; margin-bottom:0;">{text}</h2>',
        unsafe_allow_html=True,
    )
    if sub:
        st.markdown(
            f'<p style="text-align:center; color:{config.COLORS["text_dim"]}; '
            f'font-size:0.75rem; letter-spacing:2px; margin-top:2px;">{sub}</p>',
            unsafe_allow_html=True,
        )


def _section_label(text: str) -> None:
    st.markdown(
        f'<p class="section-label">{text}</p>',
        unsafe_allow_html=True,
    )


def _struggle_badge(level: str, color: str) -> str:
    return (
        f'<span class="struggle-badge" '
        f'style="color:{color}; border-color:{color}; background:rgba(0,0,0,0.35);">'
        f'{level}</span>'
    )


def _set_join_notice(message: str) -> None:
    st.session_state[_JOIN_NOTICE_KEY] = message


def _pop_join_notice() -> Optional[str]:
    value = st.session_state.get(_JOIN_NOTICE_KEY)
    if value:
        st.session_state[_JOIN_NOTICE_KEY] = None
        return str(value)
    return None


def _clear_assistant_query_param() -> None:
    params = st.query_params
    if "aid" in params:
        del params["aid"]


def _coerce_query_value(raw_value: object) -> Optional[str]:
    if isinstance(raw_value, list):
        if not raw_value:
            return None
        raw_value = raw_value[0]
    if isinstance(raw_value, str):
        value = raw_value.strip()
        return value or None
    return None


def _leave_session(assistant_id: str) -> None:
    ok, err = lab_state.leave_session(assistant_id)
    if ok:
        _set_join_notice("You have left the session. Rejoin when you are ready.")
        _clear_assistant_query_param()
        st.rerun()
    st.error(f"Could not leave session: {err or 'Unknown error.'}")


def _render_session_status_strip(lab_data: dict, assistant_name: str) -> None:
    session_code = str(lab_data.get("session_code") or "------").upper()
    safe_name = html.escape(assistant_name)
    safe_code = html.escape(session_code)
    st.markdown(
        f"""
        <div class="assistant-session-strip">
            <div class="assistant-session-strip-label">Current Session</div>
            <div class="assistant-session-strip-meta">
                <span>Assistant: {safe_name}</span>
                <span>Code: {safe_code}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# View: No active session

def render_session_ended() -> None:
    st.markdown(
        f"""
        <div class="status-ended">
            <div style="font-family:'{config.FONT_HEADING}',sans-serif;
                        color:{config.COLORS['text_dim']}; font-size:0.75rem;
                        letter-spacing:3px; text-transform:uppercase;">
                Lab Assistant Portal
            </div>
            <div style="font-family:'{config.FONT_HEADING}',sans-serif;
                        color:{config.COLORS['red']}; font-size:1.5rem;
                        margin-top:16px; text-transform:uppercase; letter-spacing:2px;">
                No Active Session
            </div>
            <div style="color:{config.COLORS['text_dim']}; margin-top:12px;
                        font-size:0.88rem; line-height:1.6;">
                Ask your instructor to start a lab session,<br>then refresh this page.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# View: Join screen

def render_join_screen(lab_data: dict) -> None:
    _heading("Lab Assistant", sub="JOIN SESSION")
    st.markdown("---")
    notice = _pop_join_notice()
    if notice:
        st.info(notice)

    name = st.text_input("Your Name", placeholder="e.g. Alice", max_chars=40, key="join_name")
    code = st.text_input(
        "Session Code",
        placeholder=f"e.g. A3X7K2",
        max_chars=config.LAB_CODE_LENGTH,
        key="join_code",
    ).strip().upper()

    if st.button("Join Session", key="join_btn"):
        if not name.strip():
            st.error("Please enter your name.")
            return
        if len(code) != config.LAB_CODE_LENGTH:
            st.error(f"Session code must be {config.LAB_CODE_LENGTH} characters.")
            return

        success, aid, error = lab_state.join_session(code, name.strip())
        if not success:
            st.error(f"Could not join: {error}")
        else:
            st.query_params["aid"] = aid
            st.rerun()


# View: Joined but no assignment yet

def render_unassigned_view(
    assistant_id: str,
    lab_data: dict,
    struggle_df: Optional[pd.DataFrame],
) -> None:
    assistant_info = lab_data["lab_assistants"][assistant_id]
    _heading(f"Hello, {assistant_info['name']}", sub="WAITING FOR ASSIGNMENT")
    _render_session_status_strip(lab_data, assistant_info["name"])
    if st.button("Leave Session", key="leave_session_unassigned"):
        _leave_session(assistant_id)

    # Poll: check if instructor has now assigned this assistant
    current = lab_state.get_assignment_for_assistant(assistant_id)
    if current:
        st.rerun()

    assigned_student_ids = set(lab_data.get("assignments", {}).keys())

    st.markdown("---")
    _section_label("Available Students")

    if struggle_df is None or struggle_df.empty:
        st.info("No student data available yet. Refreshing…")
        return

    eligible_levels = {"Struggling", "Needs Help"}
    available = struggle_df[
        struggle_df["struggle_level"].isin(eligible_levels)
        & ~struggle_df["user"].isin(assigned_student_ids)
    ].copy()

    hidden_count = len(
        struggle_df[~struggle_df["struggle_level"].isin(eligible_levels)]
    )

    allow_self = lab_data.get("allow_self_allocation", True)

    if available.empty:
        st.success("All struggling students are covered — great work!")
    else:
        for _, row in available.iterrows():
            color = row["struggle_color"]
            score = row["struggle_score"]
            level = row["struggle_level"]
            user = row["user"]

            st.markdown(
                f"""
                <div class="student-list-item" style="border-left-color:{color};">
                    <div style="display:flex; justify-content:space-between;
                                align-items:center;">
                        <div>
                            <div style="font-family:'{config.FONT_HEADING}',sans-serif;
                                        font-size:0.85rem; color:{config.COLORS['text']};
                                        text-transform:uppercase; letter-spacing:1px;">
                                {user}
                            </div>
                            {_struggle_badge(level, color)}
                        </div>
                        <div style="font-family:'{config.FONT_HEADING}',sans-serif;
                                    font-size:1.5rem; font-weight:700; color:{color};">
                            {score:.2f}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if allow_self:
                if st.button(f"Help {user}", key=f"claim_{user}"):
                    ok, err = lab_state.self_claim_student(user, assistant_id)
                    if ok:
                        st.rerun()
                    else:
                        st.error(err)

        if not allow_self:
            st.caption("Self-allocation is disabled — wait for the instructor to assign you.")

    if hidden_count > 0:
        st.caption(f"{hidden_count} student(s) not shown (Minor Issues or On Track).")


# View: Assigned to a student

def render_assigned_view(
    assistant_id: str,
    student_id: str,
    lab_data: dict,
    df: pd.DataFrame,
    struggle_df: Optional[pd.DataFrame],
) -> None:
    assistant_info = lab_data["lab_assistants"][assistant_id]
    _heading(f"Hello, {assistant_info['name']}")
    _render_session_status_strip(lab_data, assistant_info["name"])
    if st.button("Leave Session", key="leave_session_assigned"):
        _leave_session(assistant_id)

    # Look up student struggle data
    student_row = None
    if struggle_df is not None and not struggle_df.empty:
        matches = struggle_df[struggle_df["user"] == student_id]
        if not matches.empty:
            student_row = matches.iloc[0]

    if student_row is None:
        st.warning("Student data not yet available. Refreshing…")
        return

    color = student_row["struggle_color"]
    score = float(student_row["struggle_score"])
    level = student_row["struggle_level"]

    # Student card
    st.markdown(
        f"""
        <div class="student-card"
             style="border: 2px solid {color};
                    box-shadow: 0 0 22px {color}33;
                    background: rgba(13,21,38,0.92);">
            <div class="card-label">Your Student</div>
            <div class="student-id">{student_id}</div>
            <div class="score-value" style="color:{color};">{score:.3f}</div>
            {_struggle_badge(level, color)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Top 3 struggling questions
    st.markdown("---")
    _section_label("Top Struggling Questions")

    if not df.empty:
        student_df = df[df["user"] == student_id].copy()
        if not student_df.empty:
            student_df["incorrectness"] = analytics.compute_incorrectness_column(student_df)
            q_scores = (
                student_df.groupby("question")["incorrectness"]
                .mean()
                .sort_values(ascending=False)
                .head(3)
                .reset_index()
            )
            q_scores.columns = ["question", "avg_incorrectness"]

            for _, qrow in q_scores.iterrows():
                pct = int(qrow["avg_incorrectness"] * 100)
                q_display = qrow["question"]
                if len(q_display) > 50:
                    q_display = q_display[:47] + "…"
                st.markdown(
                    f"""
                    <div style="padding:10px 0;
                                border-bottom:1px solid rgba(0,245,255,0.1);">
                        <div style="font-size:0.83rem; color:{config.COLORS['text']};
                                    word-break:break-word; line-height:1.4;">
                            {q_display}
                        </div>
                        <div style="font-size:0.7rem; color:{config.COLORS['text_dim']};
                                    margin-top:3px;">
                            Avg incorrectness: {pct}%
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No submission data for this student yet.")
    else:
        st.caption("No data available.")

    # Assignment status
    assignment = lab_data.get("assignments", {}).get(student_id, {})
    status = assignment.get("status", "helping")

    st.markdown("---")

    if status == "helped":
        st.success("Marked as helped.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mark as Helped", key="mark_helped"):
            lab_state.mark_student_helped(student_id)
            st.rerun()
    with col2:
        if st.button("Release Student", key="release_btn"):
            lab_state.unassign_student(student_id)
            st.rerun()

# Main

def main() -> None:
    st.set_page_config(
        page_title="Lab Assistant",
        layout="centered",
        page_icon="🔬",
        initial_sidebar_state="collapsed",
    )

    st.markdown(theme.get_google_fonts_import(), unsafe_allow_html=True)
    st.markdown(f"<style>{theme.get_mobile_css()}</style>", unsafe_allow_html=True)

    # Auto-refresh every 5 seconds to pick up state changes
    st_autorefresh(interval=5000, limit=None, key="lab_autorefresh")

    # Restore identity from URL params (survives phone browser refresh)
    params = st.query_params
    assistant_id: Optional[str] = _coerce_query_value(params.get("aid", None))

    # Fresh state read on every rerun
    lab_data = lab_state.read_lab_state()

    # Route
    if not lab_data.get("session_active"):
        render_session_ended()
        return

    assistants = lab_data.get("lab_assistants", {})
    if not assistant_id:
        render_join_screen(lab_data)
        return

    if assistant_id not in assistants:
        _set_join_notice("Your previous assistant session is no longer active. Please join again.")
        _clear_assistant_query_param()
        st.rerun()

    assigned_student = lab_state.get_assignment_for_assistant(assistant_id)

    # Sound: assignment received (None → assigned transition)
    if "sounds_enabled" not in st.session_state:
        st.session_state["sounds_enabled"] = True
    _prev_assigned = st.session_state.get("_prev_assigned_student")
    if assigned_student is not None and _prev_assigned is None:
        sound.play_assignment_received()
    st.session_state["_prev_assigned_student"] = assigned_student

    if assigned_student:
        assignment = lab_data.get("assignments", {}).get(assigned_student, {})
        if assignment.get("assistant_id") != assistant_id:
            assigned_student = None

    df, struggle_df = _load_student_data()

    if assigned_student:
        render_assigned_view(assistant_id, assigned_student, lab_data, df, struggle_df)
    else:
        render_unassigned_view(assistant_id, lab_data, struggle_df)


if __name__ == "__main__":
    main()
