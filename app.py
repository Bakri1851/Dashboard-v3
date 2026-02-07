# ============================================================
# app.py — Main entry point: sidebar, routing, state, auto-refresh
# ============================================================
from datetime import datetime, time as dt_time

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import config
import data_loader
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
        "auto_refresh": config.AUTO_REFRESH_DEFAULT,
        "refresh_interval": config.AUTO_REFRESH_INTERVAL_DEFAULT,
        "last_refresh": None,
        "time_filter_enabled": False,
        "previous_scores": {},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


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
                st.session_state["session_active"] = True
                st.session_state["session_start"] = datetime.now()
                data_loader.fetch_raw_data.clear()
                st.rerun()
        else:
            elapsed = datetime.now() - st.session_state["session_start"]
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            st.markdown(
                f"""
                <div class="session-active">
                    <div class="session-label">SESSION ACTIVE</div>
                    <div class="session-timer">{hours:02d}:{minutes:02d}:{seconds:02d}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("End Session", key="end_session"):
                st.session_state["session_active"] = False
                st.session_state["session_start"] = None
                data_loader.fetch_raw_data.clear()
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
    df = data_loader.load_data()
    if df.empty and st.session_state["current_view"] != "Settings":
        st.error(
            "Unable to load data from the API. Please check your connection and try again."
        )
        st.stop()

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
    elif st.session_state["current_view"] == "Settings":
        views.settings_view(df)


if __name__ == "__main__":
    main()
