# app.py — Main entry point: sidebar, routing, state, auto-refresh
from datetime import datetime, time as dt_time, timedelta
import html
import os
import time

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from learning_dashboard import analytics, config, data_loader, sound
from learning_dashboard.academic_calendar import (
    ALL_PERIOD_LABELS,
    format_academic_period_window,
    get_academic_week_window,
    get_period_date_range,
)
from learning_dashboard import lab_state as _lab_state
from learning_dashboard.models import measurement
from learning_dashboard.models import irt
from learning_dashboard.models import bkt
from learning_dashboard.models import improved_struggle
from learning_dashboard.ui import components, theme, views

try:
    os.environ.setdefault("OPENAI_API_KEY", st.secrets.get("OPENAI_API_KEY", ""))
except Exception:
    pass

# Session State Initialization

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
        "time_filter_preset": "Today",
        "previous_scores": {},
        "smoothing_enabled": config.SMOOTHING_ENABLED,
        "lab_session_code": None,
        "pending_remove_assistant_id": None,
        "_autorefresh_count": None,
        "_struggle_df": None,
        "_difficulty_df": None,
        "cf_enabled": True,
        "cf_threshold": 0.5,
        "sounds_enabled":            config.SOUNDS_ENABLED_DEFAULT,
        "_prev_session_active":      False,
        "_prev_selected_student":    None,
        "_prev_selected_question":   None,
        "_prev_dashboard_view":      "In Class View",
        "_prev_high_struggle_count": 0,
        "struggle_model": "Baseline",
        "difficulty_model": "Baseline",
        "_measurement_df": None,
        "_improved_models_key": None,
        "_improved_struggle_df": None,
        # BKT parameter overrides (used when struggle_model == "Improved")
        "bkt_p_init":                    config.BKT_P_INIT,
        "bkt_p_learn":                   config.BKT_P_LEARN,
        "bkt_p_guess":                   config.BKT_P_GUESS,
        "bkt_p_slip":                    config.BKT_P_SLIP,
        "_improved_models_settings_key": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _coerce_datetime(value):
    """Convert supported date-like values to Python datetimes."""
    if value is None:
        return None

    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError):
        return None

    if pd.isna(ts):
        return None

    return ts.to_pydatetime()


def _get_dataframe_window(df: pd.DataFrame) -> tuple[datetime | None, datetime | None]:
    """Return min/max timestamps for the currently displayed dataframe."""
    if df.empty or "timestamp" not in df.columns:
        return None, None

    timestamps = df["timestamp"].dropna()
    if timestamps.empty:
        return None, None

    return _coerce_datetime(timestamps.min()), _coerce_datetime(timestamps.max())


TIME_FILTER_PRESETS = [
    "All Time",
    "Live Session",
    "Today",
    "Past Hour",
    "Past 24 Hours",
    "Current Academic Week",
    "Last Academic Week",
    "Custom",
]


def _resolve_custom_window() -> tuple[datetime | None, datetime | None]:
    """Combine the Custom date_range + time_start/end widgets into a datetime window."""
    date_range = st.session_state.get("time_date_range")
    if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
        return None, None

    start_time = st.session_state.get("time_start")
    end_time = st.session_state.get("time_end")
    if not isinstance(start_time, dt_time):
        start_time = dt_time(0, 0)
    if not isinstance(end_time, dt_time):
        end_time = dt_time(23, 59)

    try:
        start_dt = datetime.combine(pd.Timestamp(date_range[0]).date(), start_time) if date_range[0] else None
        end_dt = datetime.combine(pd.Timestamp(date_range[1]).date(), end_time) if date_range[1] else None
    except (TypeError, ValueError):
        return None, None
    return start_dt, end_dt


def _resolve_time_filter_window() -> tuple[datetime | None, datetime | None]:
    """Return the active explicit time-filter window based on the preset, if any."""
    preset = st.session_state.get("time_filter_preset", "Today")
    now = datetime.now()

    if preset == "All Time":
        return None, None

    if preset == "Live Session":
        session_start = _coerce_datetime(st.session_state.get("session_start"))
        if session_start is not None and st.session_state.get("session_active"):
            return session_start, None
        return None, None

    if preset == "Today":
        today = now.date()
        return datetime.combine(today, dt_time(0, 0)), datetime.combine(today, dt_time(23, 59))

    if preset == "Past Hour":
        return now - timedelta(hours=1), now

    if preset == "Past 24 Hours":
        return now - timedelta(hours=24), now

    if preset == "Current Academic Week":
        window = get_academic_week_window(now)
        if window is None:
            return None, None
        start_d, end_d = window
        return datetime.combine(start_d, dt_time(0, 0)), datetime.combine(end_d, dt_time(23, 59))

    if preset == "Last Academic Week":
        window = get_academic_week_window(now, offset=-1)
        if window is None:
            return None, None
        start_d, end_d = window
        return datetime.combine(start_d, dt_time(0, 0)), datetime.combine(end_d, dt_time(23, 59))

    return _resolve_custom_window()


def _resolve_display_academic_period(df: pd.DataFrame) -> str:
    """Resolve the academic period label for the data currently on screen."""
    loaded_start = _coerce_datetime(st.session_state.get("loaded_session_start"))
    loaded_end = _coerce_datetime(st.session_state.get("loaded_session_end"))
    if loaded_start is not None or loaded_end is not None:
        return format_academic_period_window(loaded_start, loaded_end)

    if st.session_state.get("session_active"):
        session_start = _coerce_datetime(st.session_state.get("session_start"))
        if session_start is not None:
            _, df_end = _get_dataframe_window(df)
            return format_academic_period_window(session_start, df_end or datetime.now())

    filter_start, filter_end = _resolve_time_filter_window()
    if filter_start is not None or filter_end is not None:
        return format_academic_period_window(filter_start, filter_end)

    df_start, df_end = _get_dataframe_window(df)
    if df_start is not None or df_end is not None:
        return format_academic_period_window(df_start, df_end)

    return format_academic_period_window(datetime.now(), None)


# Lab Assignment Panel

def _render_lab_assignment_panel() -> None:
    """
    Render lab assistant management panel inside the sidebar.
    Shows joined assistants, their current assignments, and allows
    the instructor to assign struggling students to waiting assistants.
    Called only when a session is active.
    """
    lab_data = st.session_state.get("_lab_state_cache") or _lab_state.read_lab_state()
    if not lab_data.get("session_active"):
        st.session_state["pending_remove_assistant_id"] = None
        return

    assistants = lab_data.get("lab_assistants", {})
    assignments = lab_data.get("assignments", {})
    pending_remove_id = st.session_state.get("pending_remove_assistant_id")
    if pending_remove_id and pending_remove_id not in assistants:
        st.session_state["pending_remove_assistant_id"] = None

    st.markdown("---")

    n_assigned = sum(1 for info in assistants.values() if info.get("assigned_student"))
    if assistants:
        summary = f"Lab Assistants ({len(assistants)}) — {n_assigned} assigned"
    else:
        summary = "Lab Assistants (0)"
    expander_default = len(assistants) <= 1

    with st.expander(summary, expanded=expander_default):
        allow_self = lab_data.get("allow_self_allocation", False)
        new_allow = st.checkbox(
            "Allow assistants to self-allocate",
            value=allow_self,
            key="allow_self_allocation_toggle",
            help="When off, assistants must wait for you to assign them a student.",
        )
        if new_allow != allow_self:
            _lab_state.set_allow_self_allocation(new_allow)
            st.rerun()

        if not assistants:
            st.session_state["pending_remove_assistant_id"] = None
            st.caption("No lab assistants have joined yet.")
            return

        # Use scores cached from the previous render cycle (at most one rerun stale)
        struggle_df = st.session_state.get("_struggle_df")

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
                    f'text-transform:uppercase; letter-spacing:1px; margin-top:8px;">'
                    f'Assign a student to an assistant</p>',
                    unsafe_allow_html=True,
                )
                chosen_student = st.selectbox(
                    "Struggling student",
                    options=eligible,
                    key="assign_student_select",
                )
                assistant_options = {name: aid for aid, name in unassigned_assistants}
                chosen_name = st.selectbox(
                    "Assign to assistant",
                    options=list(assistant_options.keys()),
                    key="assign_assistant_select",
                )
                if st.button("Assign", key="do_assign"):
                    ok = _lab_state.assign_student(chosen_student, assistant_options[chosen_name])
                    if ok:
                        st.rerun()
                    else:
                        st.error("Assignment failed — student may already be claimed.")


# Sidebar

def _on_view_change() -> None:
    """Callback when the view radio changes — clear drill-down selections."""
    st.session_state["selected_student"] = None
    st.session_state["selected_question"] = None
    st.session_state.pop("student_leaderboard", None)
    st.session_state.pop("question_leaderboard", None)
    st.session_state["_nav_loading"] = True


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
            _render_lab_assignment_panel()

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
        if st.session_state["current_view"] in {"In Class View", "Data Analysis View", "Model Comparison"}:
            st.session_state["dashboard_view"] = st.session_state["current_view"]

        # --- Dashboard View ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">Dashboard View</h3>',
            unsafe_allow_html=True,
        )
        st.radio(
            "Dashboard View Selector",
            ["In Class View", "Data Analysis View", "Model Comparison"],
            key="dashboard_view",
            on_change=_on_dashboard_view_change,
            label_visibility="collapsed",
        )

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

        # --- Quick Refresh ---
        if st.session_state.get("auto_refresh") and st.session_state["last_refresh"]:
            st.caption(
                f"Last refresh: {st.session_state['last_refresh'].strftime('%H:%M:%S')}"
            )
        if st.button("Refresh Now", key="sidebar_refresh_now"):
            data_loader.fetch_raw_data.clear()
            st.rerun()

        st.markdown("---")

        # --- History (time filter + previous sessions + save) ---
        st.markdown(
            f'<h3 style="color:{config.COLORS["cyan"]}; font-family:{config.FONT_HEADING}; '
            f'text-transform:uppercase; letter-spacing:2px; font-size:0.9rem;">History</h3>',
            unsafe_allow_html=True,
        )

        # Loaded saved session overrides the preset entirely
        loaded_start = st.session_state.get("loaded_session_start")
        loaded_end = st.session_state.get("loaded_session_end")
        viewing_saved_session = loaded_start is not None and loaded_end is not None

        if viewing_saved_session:
            df = data_loader.filter_by_datetime_window(df, loaded_start, loaded_end)
            st.caption(f"Filtered records: {len(df):,} (loaded saved session)")
        else:
            current_preset = st.session_state.get("time_filter_preset", "Today")
            if current_preset not in TIME_FILTER_PRESETS:
                st.session_state["time_filter_preset"] = "Today"
                current_preset = "Today"

            preset = st.selectbox(
                "Date range",
                TIME_FILTER_PRESETS,
                key="time_filter_preset",
            )

            if preset == "Custom":
                today = datetime.now().date()
                if "time_date_range" not in st.session_state:
                    if not df.empty:
                        min_date = df["timestamp"].min().date()
                        max_date = df["timestamp"].max().date()
                        default_start = today if min_date <= today <= max_date else min_date
                        default_end = today if min_date <= today <= max_date else max_date
                    else:
                        default_start = default_end = today
                    st.session_state["time_date_range"] = (default_start, default_end)

                st.date_input("Date range", key="time_date_range")
                st.time_input("Start time", value=dt_time(0, 0), key="time_start")
                st.time_input("End time", value=dt_time(23, 59), key="time_end")

                if not df.empty and "academic_period" in df.columns:
                    data_periods = set(df["academic_period"].unique())
                    available_labels = [p for p in ALL_PERIOD_LABELS if p in data_periods]
                else:
                    available_labels = []
                if available_labels:
                    def _on_week_pick():
                        picked = st.session_state.get("time_custom_week")
                        if picked and picked != "—":
                            pr = get_period_date_range(picked)
                            if pr:
                                st.session_state["time_date_range"] = pr

                    st.selectbox(
                        "Pick academic week",
                        ["—"] + available_labels,
                        key="time_custom_week",
                        on_change=_on_week_pick,
                    )

            start_dt, end_dt = _resolve_time_filter_window()

            if preset == "Live Session" and not (
                st.session_state.get("session_active") and st.session_state.get("session_start")
            ):
                st.caption("No live session — showing all records.")
            elif preset != "All Time":
                df = data_loader.filter_by_datetime_window(df, start_dt, end_dt)
                st.caption(f"Filtered records: {len(df):,}")

        st.markdown("")

        # Previous sessions / save
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

        if st.button("Save Current Session", key="save_retro_session"):
            st.session_state["_retro_save_open"] = True
            st.rerun()

        if st.session_state.get("_retro_save_open"):
            retro_name = st.text_input(
                "Session Name",
                value=f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                key="retro_session_name",
                max_chars=80,
            )
            if st.button("Confirm Save", key="confirm_retro_session"):
                filter_start, filter_end = _resolve_time_filter_window()
                if filter_start is not None and filter_end is not None:
                    record = data_loader.build_retroactive_session_record(
                        name=retro_name,
                        start_date=filter_start.date(),
                        end_date=filter_end.date(),
                        start_time=filter_start.time(),
                        end_time=filter_end.time(),
                    )
                else:
                    today = datetime.now().date()
                    record = data_loader.build_retroactive_session_record(
                        name=retro_name,
                        start_date=today,
                        end_date=today,
                    )
                try:
                    data_loader.save_session_record(record)
                    st.session_state["loaded_session_id"] = record["id"]
                    st.session_state["_retro_save_open"] = False
                    st.success("Session saved.")
                except Exception:
                    st.error("Could not save session.")
                st.rerun()
            if st.button("Cancel", key="cancel_retro_session"):
                st.session_state["_retro_save_open"] = False
                st.rerun()

    return df


# Main

def main() -> None:
    """Main application entry point."""
    st.set_page_config(
        page_title="Learning Analytics Dashboard",
        layout="wide",
        page_icon="📶",
    )

    # Initialize state
    init_session_state()

    # Sound: session lifecycle (detect start/end transitions)
    _prev_active = st.session_state.get("_prev_session_active", False)
    _curr_active = st.session_state["session_active"]
    if _curr_active and not _prev_active:
        sound.play_session_start()
    elif not _curr_active and _prev_active:
        sound.play_session_end()
    st.session_state["_prev_session_active"] = _curr_active

    # Inject theme
    st.markdown(theme.get_google_fonts_import(), unsafe_allow_html=True)
    st.markdown(f"<style>{theme.get_main_css()}</style>", unsafe_allow_html=True)

    # Navigation loader gate: on a user-initiated view change the previous
    # view's DOM lingers until the new view's deltas arrive. Render a full-page
    # loader for one render cycle so the old content is visually replaced before
    # we kick off data loading and analytics.
    if st.session_state.pop("_nav_loading", False):
        components.render_nav_loader()
        time.sleep(0.08)
        st.rerun()

    # Auto-refresh
    if st.session_state["auto_refresh"]:
        refresh_count = st_autorefresh(
            interval=st.session_state["refresh_interval"] * 1000,
            limit=None,
            key="auto_refresh_component",
        )
        prev_count = st.session_state.get("_autorefresh_count", refresh_count)
        if refresh_count != prev_count:
            data_loader.fetch_raw_data.clear()
            st.session_state["last_refresh"] = datetime.now()
            sound.play_refresh()
        st.session_state["_autorefresh_count"] = refresh_count

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
        st.session_state["_nav_loading"] = True
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
        st.session_state["time_filter_preset"] = "Today"
        st.session_state["secondary_module_filter"] = "All Modules"
        st.session_state["selected_student"] = None
        st.session_state["selected_question"] = None
        st.session_state["dashboard_view"] = "In Class View"
        st.session_state["current_view"] = "In Class View"
        st.session_state["_nav_loading"] = True
        st.rerun()

    # Cache lab session state — read file at most once per second across all consumers
    _now = time.time()
    if _now - st.session_state.get("_lab_state_ts", 0) > 1.0:
        st.session_state["_lab_state_cache"] = _lab_state.read_lab_state()
        st.session_state["_lab_state_ts"] = _now

    # Sidebar controls and filtering (preset-driven — see render_sidebar)
    df = render_sidebar(df)
    st.session_state["_today_has_data"] = True

    st.session_state["current_academic_period"] = _resolve_display_academic_period(df)

    # Sound: navigation transition
    _prev_view = st.session_state.get("_prev_dashboard_view")
    _curr_view = st.session_state["current_view"]
    if _prev_view is not None and _prev_view != _curr_view and _curr_view in {"In Class View", "Data Analysis View"}:
        sound.play_navigation()
    st.session_state["_prev_dashboard_view"] = _curr_view

    # Sound: student selected
    _prev_s = st.session_state.get("_prev_selected_student")
    _curr_s = st.session_state["selected_student"]
    if _curr_s is not None and _curr_s != _prev_s:
        sound.play_selection()
    st.session_state["_prev_selected_student"] = _curr_s

    # Sound: question selected
    _prev_q = st.session_state.get("_prev_selected_question")
    _curr_q = st.session_state["selected_question"]
    if _curr_q is not None and _curr_q != _prev_q:
        sound.play_selection()
    st.session_state["_prev_selected_question"] = _curr_q

    # Sound: lab assistant joined (instructor hears it)
    _lab_sound_data = st.session_state.get("_lab_state_cache", {})
    _curr_aids = set((_lab_sound_data.get("lab_assistants") or {}).keys())
    _prev_aids = st.session_state.get("_prev_lab_assistant_ids", _curr_aids)
    if _curr_aids - _prev_aids:
        sound.play_assistant_join()
    st.session_state["_prev_lab_assistant_ids"] = _curr_aids

    # Cache analytics scores — only recompute when the filtered data changes.
    # Key on row count + timestamp range as a fast fingerprint of df content.
    _analytics_key = (len(df), str(df["timestamp"].min()), str(df["timestamp"].max()),
                      int(pd.util.hash_pandas_object(df).sum()))
    if st.session_state.get("_analytics_key") != _analytics_key:
        struggle_df = analytics.compute_student_struggle_scores(df)
        # Apply temporal EMA if enabled
        if st.session_state.get("smoothing_enabled", True) and not struggle_df.empty:
            prev = st.session_state.get("previous_scores", {})
            struggle_df = struggle_df.copy()
            new_prev = {}
            for idx, row in struggle_df.iterrows():
                student = row["user"]
                smoothed = analytics.apply_temporal_smoothing(
                    row["struggle_score"], prev.get(student)
                )
                struggle_df.at[idx, "struggle_score"] = smoothed
                level, color = analytics.classify_score(smoothed, config.STRUGGLE_THRESHOLDS)
                struggle_df.at[idx, "struggle_level"] = level
                struggle_df.at[idx, "struggle_color"] = color
                new_prev[student] = smoothed
            st.session_state["previous_scores"] = new_prev
        difficulty_df = analytics.compute_question_difficulty_scores(df)
        st.session_state["_struggle_df"] = struggle_df
        st.session_state["_difficulty_df"] = difficulty_df
        st.session_state["_analytics_key"] = _analytics_key
        st.session_state["_sec_analytics_key"] = None  # invalidate secondary cache
        st.session_state["_improved_models_key"] = None  # invalidate improved models cache
    else:
        struggle_df = st.session_state["_struggle_df"]
        difficulty_df = st.session_state["_difficulty_df"]

    df["incorrectness"] = analytics.compute_incorrectness_column(df)

    # --- Improved models (Phases 1–4), gated by the Settings dropdowns ---
    _struggle_model = st.session_state.get("struggle_model", "Baseline")
    _difficulty_model = st.session_state.get("difficulty_model", "Baseline")
    _improved_struggle_active = _struggle_model == "Improved"
    _irt_active = _difficulty_model == "IRT" or _improved_struggle_active
    _bkt_active = _improved_struggle_active
    st.session_state["improved_models_enabled"] = (
        _improved_struggle_active or _difficulty_model == "IRT"
    )

    if st.session_state["improved_models_enabled"]:
        _improved_settings_key = (
            _struggle_model,
            _difficulty_model,
            st.session_state.get("bkt_p_init", config.BKT_P_INIT),
            st.session_state.get("bkt_p_learn", config.BKT_P_LEARN),
            st.session_state.get("bkt_p_guess", config.BKT_P_GUESS),
            st.session_state.get("bkt_p_slip", config.BKT_P_SLIP),
        )
        _need_recompute = (
            st.session_state.get("_improved_models_key") != _analytics_key
            or st.session_state.get("_improved_models_settings_key") != _improved_settings_key
            or st.session_state.get("_mastery_summary_df") is None
        )
        if _need_recompute:
            st.session_state["_measurement_df"] = measurement.compute_incorrectness_with_confidence(df)

            if _irt_active:
                st.session_state["_irt_difficulty_df"] = irt.compute_irt_difficulty_scores(df)
            else:
                st.session_state["_irt_difficulty_df"] = None

            if _bkt_active:
                mastery_df = bkt.compute_all_mastery(
                    df,
                    p_init=st.session_state.get("bkt_p_init", config.BKT_P_INIT),
                    p_learn=st.session_state.get("bkt_p_learn", config.BKT_P_LEARN),
                    p_guess=st.session_state.get("bkt_p_guess", config.BKT_P_GUESS),
                    p_slip=st.session_state.get("bkt_p_slip", config.BKT_P_SLIP),
                )
                st.session_state["_mastery_df"] = mastery_df
                st.session_state["_mastery_summary_df"] = bkt.compute_student_mastery_summary(mastery_df)
            else:
                st.session_state["_mastery_df"] = None
                st.session_state["_mastery_summary_df"] = None

            if _improved_struggle_active:
                st.session_state["_improved_struggle_df"] = improved_struggle.compute_improved_struggle_scores(
                    df,
                    mastery_summary=st.session_state["_mastery_summary_df"],
                    irt_difficulty=st.session_state["_irt_difficulty_df"],
                )
            else:
                st.session_state["_improved_struggle_df"] = None

            st.session_state["_improved_models_key"] = _analytics_key
            st.session_state["_improved_models_settings_key"] = _improved_settings_key
    else:
        if st.session_state.get("_improved_models_key") is not None:
            st.session_state["_measurement_df"] = None
            st.session_state["_irt_difficulty_df"] = None
            st.session_state["_mastery_df"] = None
            st.session_state["_mastery_summary_df"] = None
            st.session_state["_improved_struggle_df"] = None
            st.session_state["_improved_models_key"] = None
            st.session_state["_improved_models_settings_key"] = None

    # Sound: high-struggle student count increased
    if st.session_state["session_active"] and struggle_df is not None and not struggle_df.empty:
        _curr_hs = int((struggle_df["struggle_level"] == "Needs Help").sum())
        _prev_hs = st.session_state.get("_prev_high_struggle_count", 0)
        if _curr_hs > _prev_hs:
            sound.play_high_struggle()
        st.session_state["_prev_high_struggle_count"] = _curr_hs

    # Route to view
    if st.session_state["selected_student"] is not None:
        views.student_detail_view(df, st.session_state["selected_student"], struggle_df, difficulty_df)
    elif st.session_state["selected_question"] is not None:
        views.question_detail_view(df, st.session_state["selected_question"], difficulty_df)
    elif st.session_state["current_view"] == "In Class View":
        views.in_class_view(df, struggle_df, difficulty_df)
    elif st.session_state["current_view"] == "Data Analysis View":
        views.data_analysis_view(df)
    elif st.session_state["current_view"] == "Previous Sessions":
        views.previous_sessions_view(df)
    elif st.session_state["current_view"] == "Settings":
        views.settings_view(df)
    elif st.session_state["current_view"] == "Model Comparison":
        views.comparison_view(df)


if __name__ == "__main__":
    main()
