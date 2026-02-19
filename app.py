# ============================================================
# app.py — Main entry point: sidebar, routing, state, auto-refresh
# ============================================================
from datetime import datetime, time as dt_time
import html

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import analytics
import config
import data_loader
import lab_state as _lab_state
import theme
import views


# -----------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------

def init_session_state() -> None:
    """Initialize all session state keys with defaults if not present."""
    defaults = {
        "current_view": "In Class View",
        "dashboard_view": "In Class View",
        "selected_student": None,
        "selected_question": None,
        "session_active": False,
        "session_start": None,
        "session_name_draft": "",
        "loaded_session_id": None,
        "loaded_session_start": None,
        "loaded_session_end": None,
        "session_load_warning": None,
        "pending_delete_session_id": None,
        "pending_session_load_record": None,
        "pending_return_to_live_data": False,
        "auto_refresh": config.AUTO_REFRESH_DEFAULT,
        "refresh_interval": config.AUTO_REFRESH_INTERVAL_DEFAULT,
        "last_refresh": None,
        "time_filter_enabled": False,
        "previous_scores": {},
        "lab_session_code": None,
        "pending_remove_assistant_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# -----------------------------------------------------------------
# Lab Assignment Panel
# -----------------------------------------------------------------

def _render_lab_assignment_panel(df: pd.DataFrame) -> None:
    """
    Render lab assistant management panel inside the sidebar.
    Shows joined assistants, their current assignments, and allows
    the instructor to assign struggling students to waiting assistants.
    Called only when a session is active.
    """
    lab_data = _lab_state.read_lab_state()
    if not lab_data.get("session_active"):
        st.session_state["pending_remove_assistant_id"] = None
        return

    assistants = lab_data.get("lab_assistants", {})
    assignments = lab_data.get("assignments", {})
    pending_remove_id = st.session_state.get("pending_remove_assistant_id")
    if pending_remove_id and pending_remove_id not in assistants:
        st.session_state["pending_remove_assistant_id"] = None

    st.markdown("---")
    st.markdown(
        f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
        f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">'
        f'Lab Assistants ({len(assistants)})</h3>',
        unsafe_allow_html=True,
    )

    if not assistants:
        st.session_state["pending_remove_assistant_id"] = None
        st.caption("No lab assistants have joined yet.")
        return

    # Build struggle data for the assignment UI
    struggle_df = None
    if not df.empty:
        struggle_df = analytics.compute_student_struggle_scores(df)

    # List each assistant with their current assignment
    unassigned_assistants: list[tuple[str, str]] = []
    for aid, info in assistants.items():
        assigned_student = info.get("assigned_student")
        if assigned_student:
            entry = assignments.get(assigned_student, {})
            status = entry.get("status", "helping")
            status_color = (
                config.COLORS["green"] if status == "helped" else config.COLORS["yellow"]
            )
            st.markdown(
                f'<div style="font-size:0.8rem; padding:3px 0;">'
                f'<span style="color:{config.COLORS["cyan"]};">{info["name"]}</span>'
                f' &rarr; <span style="color:{config.COLORS["text"]};">{assigned_student}</span>'
                f' <span style="color:{status_color}; font-size:0.65rem;">({status})</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            release_col, remove_col = st.columns(2)
            with release_col:
                if st.button(f"Release {info['name']}", key=f"release_{aid}"):
                    _lab_state.unassign_student(assigned_student)
                    st.rerun()
            with remove_col:
                if st.button(f"Remove {info['name']}", key=f"remove_{aid}"):
                    st.session_state["pending_remove_assistant_id"] = aid
                    st.rerun()
        else:
            unassigned_assistants.append((aid, info["name"]))
            st.markdown(
                f'<div style="font-size:0.8rem; padding:3px 0;">'
                f'<span style="color:{config.COLORS["cyan"]};">{info["name"]}</span>'
                f' &mdash; <span style="color:{config.COLORS["text_dim"]};">waiting</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button(f"Remove {info['name']}", key=f"remove_{aid}"):
                st.session_state["pending_remove_assistant_id"] = aid
                st.rerun()

        if st.session_state.get("pending_remove_assistant_id") == aid:
            st.warning("This will remove the assistant and release their current student.")
            confirm_col, cancel_col = st.columns(2)
            with confirm_col:
                if st.button("Confirm Remove", key=f"confirm_remove_{aid}"):
                    ok, err = _lab_state.remove_assistant(aid)
                    st.session_state["pending_remove_assistant_id"] = None
                    if ok:
                        st.rerun()
                    st.error(err or "Could not remove assistant.")
            with cancel_col:
                if st.button("Cancel", key=f"cancel_remove_{aid}"):
                    st.session_state["pending_remove_assistant_id"] = None
                    st.rerun()

    # Instructor assignment controls
    if struggle_df is not None and not struggle_df.empty and unassigned_assistants:
        assigned_student_ids = set(assignments.keys())
        eligible = struggle_df[
            (struggle_df["struggle_level"].isin({"Struggling", "Needs Help"}))
            & (~struggle_df["user"].isin(assigned_student_ids))
        ]["user"].tolist()

        if eligible:
            st.markdown(
                f'<p style="font-size:0.75rem; color:{config.COLORS["cyan"]}; '
                f'text-transform:uppercase; letter-spacing:1px; margin-top:8px;">Assign</p>',
                unsafe_allow_html=True,
            )
            chosen_student = st.selectbox(
                "Student",
                options=eligible,
                key="assign_student_select",
                label_visibility="collapsed",
            )
            assistant_options = {name: aid for aid, name in unassigned_assistants}
            chosen_name = st.selectbox(
                "Assistant",
                options=list(assistant_options.keys()),
                key="assign_assistant_select",
                label_visibility="collapsed",
            )
            if st.button("Assign", key="do_assign"):
                ok = _lab_state.assign_student(chosen_student, assistant_options[chosen_name])
                if ok:
                    st.rerun()
                else:
                    st.error("Assignment failed — student may already be claimed.")


# -----------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------

def _on_view_change() -> None:
    """Callback when the view radio changes — clear drill-down selections."""
    st.session_state["selected_student"] = None
    st.session_state["selected_question"] = None


def _on_dashboard_view_change() -> None:
    """Switch the active page from the dashboard view selector."""
    st.session_state["current_view"] = st.session_state["dashboard_view"]
    _on_view_change()


def _render_lab_code_card(code: str) -> None:
    safe_code = html.escape(code.strip().upper())
    st.markdown(
        f"""
        <div class="lab-code-card">
            <div class="lab-code-label">Lab Code</div>
            <div class="lab-code-value">{safe_code}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Render all sidebar controls and return the filtered DataFrame."""
    with st.sidebar:
        # --- Lab Session Management ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">Lab Session</h3>',
            unsafe_allow_html=True,
        )

        if not st.session_state["session_active"]:
            if st.button("Start Lab Session", key="start_session"):
                start_time = datetime.now()
                st.session_state["session_active"] = True
                st.session_state["session_start"] = start_time
                st.session_state["pending_remove_assistant_id"] = None
                st.session_state["session_name_draft"] = (
                    f"Lab Session {start_time.strftime('%Y-%m-%d %H:%M')}"
                )
                st.session_state["loaded_session_id"] = None
                st.session_state["loaded_session_start"] = None
                st.session_state["loaded_session_end"] = None
                code = _lab_state.generate_session_code()
                st.session_state["lab_session_code"] = code
                _lab_state.start_lab_session(code)
                data_loader.fetch_raw_data.clear()
                st.rerun()
        else:
            elapsed = datetime.now() - st.session_state["session_start"]
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            st.text_input("Session Name", key="session_name_draft", max_chars=80)
            st.markdown(
                f"""
                <div class="session-active">
                    <div class="session-label">SESSION ACTIVE</div>
                    <div class="session-timer">{hours:02d}:{minutes:02d}:{seconds:02d}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            code = st.session_state.get("lab_session_code", "")
            if code:
                _render_lab_code_card(code)
                st.markdown('<div class="session-action-gap"></div>', unsafe_allow_html=True)
            if st.button("End Session", key="end_session"):
                end_time = datetime.now()
                record = data_loader.build_session_record_from_state(end_time)
                if record is not None:
                    try:
                        data_loader.save_session_record(record)
                        st.session_state["loaded_session_id"] = record["id"]
                    except Exception:
                        st.session_state["session_load_warning"] = (
                            "Session ended, but it could not be saved to local history."
                        )
                _lab_state.end_lab_session()
                st.session_state["lab_session_code"] = None
                st.session_state["session_active"] = False
                st.session_state["session_start"] = None
                st.session_state["pending_remove_assistant_id"] = None
                data_loader.fetch_raw_data.clear()
                st.rerun()

        if st.session_state["session_active"]:
            _render_lab_assignment_panel(df)

        if (
            not st.session_state["session_active"]
            and st.session_state.get("loaded_session_start") is not None
            and st.session_state.get("loaded_session_end") is not None
        ):
            session_name = st.session_state.get("session_name_draft", "Saved Session")
            st.caption(f"Viewing saved session: {session_name}")
            if st.button("Back to Live Data", key="back_to_live_data"):
                st.session_state["pending_return_to_live_data"] = True
                st.rerun()

        st.markdown("---")

        # Keep selector and active view aligned before rendering the widget.
        if st.session_state["current_view"] in {"In Class View", "Data Analysis View"}:
            st.session_state["dashboard_view"] = st.session_state["current_view"]

        # --- Dashboard View ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">Dashboard View</h3>',
            unsafe_allow_html=True,
        )
        st.radio(
            "Dashboard View Selector",
            ["In Class View", "Data Analysis View"],
            key="dashboard_view",
            on_change=_on_dashboard_view_change,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # --- Time Filter ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">Time Filter</h3>',
            unsafe_allow_html=True,
        )

        st.checkbox("Enable Time Filter", key="time_filter_enabled")

        if st.session_state["time_filter_enabled"]:
            today = datetime.now().date()
            # Default to today if data exists for today
            if not df.empty:
                min_date = df["timestamp"].min().date()
                max_date = df["timestamp"].max().date()
                has_today = min_date <= today <= max_date
            else:
                min_date = today
                max_date = today
                has_today = False

            default_start = today if has_today else min_date
            default_end = today if has_today else max_date

            date_range = st.date_input(
                "Date Range",
                value=(default_start, default_end),
                key="time_date_range",
            )

            start_time = st.time_input("Start Time", value=dt_time(0, 0), key="time_start")
            end_time = st.time_input("End Time", value=dt_time(23, 59), key="time_end")

            if isinstance(date_range, tuple) and len(date_range) == 2:
                df = data_loader.filter_by_time(
                    df,
                    start_date=date_range[0],
                    end_date=date_range[1],
                    start_time=start_time,
                    end_time=end_time,
                )

            st.caption(f"Filtered records: {len(df):,}")

        # --- Session-based filtering ---
        elif st.session_state["session_active"] and st.session_state["session_start"]:
            df = data_loader.filter_by_session_start(df, st.session_state["session_start"])
        elif (
            st.session_state.get("loaded_session_start") is not None
            and st.session_state.get("loaded_session_end") is not None
        ):
            df = data_loader.filter_by_datetime_window(
                df,
                st.session_state.get("loaded_session_start"),
                st.session_state.get("loaded_session_end"),
            )
            st.caption(f"Filtered records: {len(df):,} (loaded saved session)")

        st.markdown("---")

        # --- Settings ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">Settings</h3>',
            unsafe_allow_html=True,
        )
        if st.session_state["current_view"] == "Settings":
            if st.button("Back to Dashboard", key="back_to_dashboard"):
                _on_view_change()
                st.session_state["current_view"] = st.session_state["dashboard_view"]
                st.rerun()
            st.caption("Currently viewing settings.")
        else:
            if st.button("Open Settings", key="open_settings"):
                _on_view_change()
                st.session_state["current_view"] = "Settings"
                st.rerun()

        st.markdown("---")

        # --- Previous Sessions ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">History</h3>',
            unsafe_allow_html=True,
        )
        if st.session_state["current_view"] == "Previous Sessions":
            if st.button("Back to Dashboard", key="back_from_previous_sessions"):
                _on_view_change()
                st.session_state["current_view"] = st.session_state["dashboard_view"]
                st.rerun()
            st.caption("Currently viewing previous sessions.")
        else:
            if st.button("Open Previous Sessions", key="open_previous_sessions"):
                _on_view_change()
                st.session_state["current_view"] = "Previous Sessions"
                st.rerun()

    return df


# -----------------------------------------------------------------
# Main
# -----------------------------------------------------------------

def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title="Learning Analytics Dashboard",
        layout="wide",
        page_icon="📶",
    )

    # Initialize state
    init_session_state()

    # Inject theme
    st.markdown(theme.get_google_fonts_import(), unsafe_allow_html=True)
    st.markdown(f"<style>{theme.get_main_css()}</style>", unsafe_allow_html=True)

    # Auto-refresh
    if st.session_state["auto_refresh"]:
        st_autorefresh(
            interval=st.session_state["refresh_interval"] * 1000,
            limit=None,
            key="auto_refresh_component",
        )
        st.session_state["last_refresh"] = datetime.now()

    # Load data
    df, load_error = data_loader.load_data()
    if st.session_state["current_view"] not in {"Settings", "Previous Sessions"}:
        if load_error:
            st.error(load_error)
            st.stop()
        if df.empty:
            st.error(
                "Unable to load data from the API. Please check your connection and try again."
            )
            st.stop()

    pending_record = st.session_state.get("pending_session_load_record")
    if isinstance(pending_record, dict):
        available_modules = (
            ["All Modules"] + sorted(df["module"].unique().tolist())
            if not df.empty
            else ["All Modules"]
        )
        data_loader.apply_saved_session_to_state(
            pending_record,
            available_modules=available_modules,
        )
        st.session_state["pending_session_load_record"] = None
        st.rerun()

    if st.session_state.get("pending_return_to_live_data"):
        st.session_state["pending_return_to_live_data"] = False
        st.session_state["loaded_session_id"] = None
        st.session_state["loaded_session_start"] = None
        st.session_state["loaded_session_end"] = None
        st.session_state["session_name_draft"] = ""
        st.session_state["session_load_warning"] = None
        st.session_state["pending_delete_session_id"] = None
        st.session_state["pending_session_load_record"] = None
        st.session_state["pending_remove_assistant_id"] = None
        st.session_state["time_filter_enabled"] = False
        st.session_state["secondary_module_filter"] = "All Modules"
        st.session_state["selected_student"] = None
        st.session_state["selected_question"] = None
        st.session_state["dashboard_view"] = "In Class View"
        st.session_state["current_view"] = "In Class View"
        st.rerun()

    # Sidebar controls and filtering
    df = render_sidebar(df)

    # Route to view
    if st.session_state["selected_student"] is not None:
        views.student_detail_view(df, st.session_state["selected_student"])
    elif st.session_state["selected_question"] is not None:
        views.question_detail_view(df, st.session_state["selected_question"])
    elif st.session_state["current_view"] == "In Class View":
        views.in_class_view(df)
    elif st.session_state["current_view"] == "Data Analysis View":
        views.data_analysis_view(df)
    elif st.session_state["current_view"] == "Previous Sessions":
        views.previous_sessions_view(df)
    elif st.session_state["current_view"] == "Settings":
        views.settings_view(df)


if __name__ == "__main__":
    main()
