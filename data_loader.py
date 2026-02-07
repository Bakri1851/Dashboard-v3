# ============================================================
# data_loader.py — API fetching, parsing, normalization, cleaning
# ============================================================
import json
import xml.etree.ElementTree as ET
from datetime import date as dt_date, datetime, time as dt_time
from pathlib import Path
from typing import Optional
from uuid import uuid4

import pandas as pd
import requests
import streamlit as st

import config


@st.cache_data(ttl=config.CACHE_TTL)
def fetch_raw_data() -> str:
    """GET request to the API endpoint. Cached for CACHE_TTL seconds."""
    response = requests.get(config.API_URL, timeout=config.API_TIMEOUT)
    response.raise_for_status()
    return response.text


def detect_format(raw: str) -> str:
    """Auto-detect whether the raw response is JSON or XML."""
    stripped = raw.strip()
    if not stripped:
        return "json"
    first_line = stripped.split("\n", 1)[0].strip()
    try:
        json.loads(first_line)
        return "json"
    except (json.JSONDecodeError, ValueError):
        return "xml"


def parse_json_response(raw: str) -> list[dict]:
    """Parse newline-delimited JSON objects with optional embedded XML."""
    records = []
    for line in raw.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue

        if not isinstance(obj, dict):
            continue

        base = {
            "module": obj.get("module", ""),
            "question": obj.get("question", ""),
            "session": obj.get("session", ""),
            "user": obj.get("user", ""),
        }

        xml_field = obj.get("xml", "")
        if xml_field and isinstance(xml_field, str) and xml_field.strip():
            try:
                root = ET.fromstring(f"<root>{xml_field}</root>")
                submissions = root.findall(".//submission")
                if submissions:
                    for sub in submissions:
                        record = base.copy()
                        record["timestamp"] = sub.get(
                            "timestamp", obj.get("timestamp", "")
                        )
                        srep = sub.find("srep")
                        record["student_answer"] = (
                            srep.text if srep is not None and srep.text else ""
                        )
                        feedback_resp = sub.find(".//feedback/response")
                        record["ai_feedback"] = (
                            feedback_resp.text
                            if feedback_resp is not None and feedback_resp.text
                            else ""
                        )
                        records.append(record)
                else:
                    record = base.copy()
                    record["timestamp"] = obj.get("timestamp", "")
                    record["student_answer"] = ""
                    record["ai_feedback"] = ""
                    records.append(record)
            except ET.ParseError:
                record = base.copy()
                record["timestamp"] = obj.get("timestamp", "")
                record["student_answer"] = ""
                record["ai_feedback"] = ""
                records.append(record)
        else:
            record = base.copy()
            record["timestamp"] = obj.get("timestamp", "")
            record["student_answer"] = obj.get("student_answer", "")
            record["ai_feedback"] = obj.get("ai_feedback", "")
            records.append(record)

    return records


def parse_xml_response(raw: str) -> list[dict]:
    """Parse pure XML format: <Payloads><Payload>...</Payload></Payloads>."""
    records = []
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        return records

    for payload in root.findall(".//Payload"):
        base = {
            "module": _xml_text(payload, "module"),
            "question": _xml_text(payload, "question"),
            "session": _xml_text(payload, "session"),
            "user": _xml_text(payload, "user"),
        }
        submissions = payload.findall(".//submission")
        if submissions:
            for sub in submissions:
                record = base.copy()
                record["timestamp"] = _xml_text(sub, "timestamp")
                record["student_answer"] = _xml_text(sub, "srep")
                feedback_resp = sub.find(".//feedback/response")
                record["ai_feedback"] = (
                    feedback_resp.text
                    if feedback_resp is not None and feedback_resp.text
                    else ""
                )
                records.append(record)
        else:
            record = base.copy()
            record["timestamp"] = ""
            record["student_answer"] = ""
            record["ai_feedback"] = ""
            records.append(record)

    return records


def _xml_text(element: ET.Element, tag: str) -> str:
    """Safely extract text from a child XML element."""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return ""


def normalize_and_clean(records: list[dict]) -> pd.DataFrame:
    """Convert records to DataFrame and apply cleaning rules."""
    if not records:
        return pd.DataFrame(
            columns=[
                "module", "question", "timestamp",
                "student_answer", "ai_feedback", "session", "user",
            ]
        )

    df = pd.DataFrame(records)

    expected_cols = [
        "module", "question", "timestamp",
        "student_answer", "ai_feedback", "session", "user",
    ]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = ""

    # Exclude modules
    df = df[~df["module"].isin(config.EXCLUDED_MODULES)].copy()

    # Rename modules
    df["module"] = df["module"].replace(config.MODULE_RENAME_MAP)

    # Parse timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp"]).copy()

    # Sort by timestamp
    df = df.sort_values("timestamp").reset_index(drop=True)

    return df


def load_data() -> tuple[pd.DataFrame, str]:
    """Top-level: fetch -> detect -> parse -> clean. Returns (DataFrame, error_msg)."""
    _empty = pd.DataFrame(
        columns=[
            "module", "question", "timestamp",
            "student_answer", "ai_feedback", "session", "user",
        ]
    )
    try:
        raw = fetch_raw_data()
    except Exception as e:
        return _empty, f"API connection failed: {type(e).__name__} — {e}"

    fmt = detect_format(raw)

    if fmt == "json":
        try:
            records = parse_json_response(raw)
        except Exception:
            try:
                records = parse_xml_response(raw)
            except Exception:
                return pd.DataFrame(
                    columns=[
                        "module", "question", "timestamp",
                        "student_answer", "ai_feedback", "session", "user",
                    ]
                )
    else:
        try:
            records = parse_xml_response(raw)
        except Exception:
            try:
                records = parse_json_response(raw)
            except Exception:
                return pd.DataFrame(
                    columns=[
                        "module", "question", "timestamp",
                        "student_answer", "ai_feedback", "session", "user",
                    ]
                )

    return normalize_and_clean(records)


def _saved_sessions_path() -> Path:
    """Absolute path to the local saved-session store."""
    return Path(__file__).resolve().parent / config.SAVED_SESSIONS_FILE


def _empty_saved_sessions_payload() -> dict:
    return {"version": config.SAVED_SESSIONS_VERSION, "sessions": []}


def _backup_corrupt_saved_sessions(path: Path) -> None:
    """Move corrupt session JSON aside so the app can recover safely."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(f"{path.stem}.corrupt.{timestamp}{path.suffix}")
    path.replace(backup)


def _read_saved_sessions_payload() -> dict:
    path = _saved_sessions_path()
    if not path.exists():
        return _empty_saved_sessions_payload()

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        try:
            _backup_corrupt_saved_sessions(path)
        except OSError:
            pass
        st.warning("Saved sessions file was corrupted and has been reset.")
        return _empty_saved_sessions_payload()

    if not isinstance(payload, dict):
        return _empty_saved_sessions_payload()

    sessions = payload.get("sessions", [])
    if not isinstance(sessions, list):
        return _empty_saved_sessions_payload()

    return {
        "version": payload.get("version", config.SAVED_SESSIONS_VERSION),
        "sessions": sessions,
    }


def _write_saved_sessions_payload(payload: dict) -> None:
    path = _saved_sessions_path()
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def _parse_iso_date(raw_value) -> Optional[dt_date]:
    if not isinstance(raw_value, str) or not raw_value:
        return None
    try:
        return datetime.fromisoformat(raw_value).date()
    except ValueError:
        return None


def _parse_iso_time(raw_value) -> Optional[dt_time]:
    if not isinstance(raw_value, str) or not raw_value:
        return None
    try:
        return dt_time.fromisoformat(raw_value)
    except ValueError:
        return None


def _parse_iso_datetime(raw_value) -> Optional[datetime]:
    if not isinstance(raw_value, str) or not raw_value:
        return None
    try:
        return datetime.fromisoformat(raw_value)
    except ValueError:
        return None


def load_saved_sessions() -> list[dict]:
    """Return saved session records sorted by newest end_time first."""
    payload = _read_saved_sessions_payload()
    sessions = payload.get("sessions", [])

    deduped: dict[str, dict] = {}
    for record in sessions:
        if isinstance(record, dict) and record.get("id"):
            deduped[str(record["id"])] = record

    return sorted(
        deduped.values(),
        key=lambda rec: str(rec.get("end_time", "")),
        reverse=True,
    )


def save_session_record(record: dict) -> None:
    """Persist a single session record to the local JSON store."""
    if not isinstance(record, dict) or not record.get("id"):
        raise ValueError("Invalid session record.")

    sessions = load_saved_sessions()
    sessions = [s for s in sessions if s.get("id") != record["id"]]
    sessions.append(record)
    sessions.sort(key=lambda rec: str(rec.get("end_time", "")), reverse=True)

    _write_saved_sessions_payload(
        {
            "version": config.SAVED_SESSIONS_VERSION,
            "sessions": sessions,
        }
    )


def delete_session_record(session_id: str) -> bool:
    """Delete one session record by ID; returns True if deleted."""
    sessions = load_saved_sessions()
    filtered = [s for s in sessions if s.get("id") != session_id]
    if len(filtered) == len(sessions):
        return False

    _write_saved_sessions_payload(
        {
            "version": config.SAVED_SESSIONS_VERSION,
            "sessions": filtered,
        }
    )
    return True


def build_session_record_from_state(now: datetime) -> Optional[dict]:
    """Build a persisted record from the current Streamlit session state."""
    session_start = st.session_state.get("session_start")
    if not isinstance(session_start, datetime):
        return None

    session_name = str(st.session_state.get("session_name_draft", "")).strip()
    if not session_name:
        session_name = f"Lab Session {session_start.strftime('%Y-%m-%d %H:%M')}"

    time_filter_enabled = bool(st.session_state.get("time_filter_enabled", False))

    date_range_value = st.session_state.get("time_date_range")
    start_date_iso = None
    end_date_iso = None
    if isinstance(date_range_value, (tuple, list)) and len(date_range_value) == 2:
        start_date = date_range_value[0]
        end_date = date_range_value[1]
        if hasattr(start_date, "isoformat") and hasattr(end_date, "isoformat"):
            start_date_iso = start_date.isoformat()
            end_date_iso = end_date.isoformat()

    start_time_value = st.session_state.get("time_start")
    end_time_value = st.session_state.get("time_end")
    start_time_iso = (
        start_time_value.isoformat() if isinstance(start_time_value, dt_time) else None
    )
    end_time_iso = (
        end_time_value.isoformat() if isinstance(end_time_value, dt_time) else None
    )

    duration_seconds = max(0, int((now - session_start).total_seconds()))

    return {
        "id": str(uuid4()),
        "name": session_name,
        "created_at": now.isoformat(timespec="seconds"),
        "start_time": session_start.isoformat(timespec="seconds"),
        "end_time": now.isoformat(timespec="seconds"),
        "duration_seconds": duration_seconds,
        "context": {
            "dashboard_view": st.session_state.get("dashboard_view", "In Class View"),
            "secondary_module_filter": st.session_state.get(
                "secondary_module_filter", "All Modules"
            ),
            "time_filter_enabled": time_filter_enabled,
            "time_date_range": (
                [start_date_iso, end_date_iso]
                if time_filter_enabled and start_date_iso and end_date_iso
                else None
            ),
            "time_start": start_time_iso if time_filter_enabled else None,
            "time_end": end_time_iso if time_filter_enabled else None,
        },
        "notes": "",
    }


def apply_saved_session_to_state(
    record: dict,
    available_modules: Optional[list[str]] = None,
) -> None:
    """Apply a saved session record onto active Streamlit state."""
    if not isinstance(record, dict):
        return

    context = record.get("context", {})
    if not isinstance(context, dict):
        context = {}

    dashboard_view = context.get("dashboard_view", "In Class View")
    if dashboard_view not in {"In Class View", "Data Analysis View"}:
        dashboard_view = "In Class View"

    module_filter = context.get("secondary_module_filter", "All Modules") or "All Modules"
    warning_messages: list[str] = []

    if available_modules is not None and module_filter not in available_modules:
        module_filter = "All Modules"
        warning_messages.append(
            "Saved module filter is no longer available. Fallback applied: All Modules."
        )

    time_filter_enabled = bool(context.get("time_filter_enabled", False))
    date_range_value = context.get("time_date_range")
    saved_start_time = _parse_iso_time(context.get("time_start"))
    saved_end_time = _parse_iso_time(context.get("time_end"))
    session_start = _parse_iso_datetime(record.get("start_time"))
    session_end = _parse_iso_datetime(record.get("end_time"))
    if session_start is None or session_end is None:
        warning_messages.append(
            "Saved session time window is missing; showing all available data."
        )

    st.session_state["dashboard_view"] = dashboard_view
    st.session_state["current_view"] = "In Class View"
    st.session_state["secondary_module_filter"] = module_filter
    st.session_state["session_active"] = False
    st.session_state["session_start"] = None
    st.session_state["selected_student"] = None
    st.session_state["selected_question"] = None
    st.session_state["loaded_session_id"] = record.get("id")
    st.session_state["session_name_draft"] = record.get("name", "")
    st.session_state["time_filter_enabled"] = time_filter_enabled
    st.session_state["loaded_session_start"] = session_start
    st.session_state["loaded_session_end"] = session_end
    st.session_state["session_load_warning"] = (
        " ".join(warning_messages) if warning_messages else None
    )

    if time_filter_enabled:
        if isinstance(date_range_value, (list, tuple)) and len(date_range_value) == 2:
            start_date = _parse_iso_date(date_range_value[0])
            end_date = _parse_iso_date(date_range_value[1])
            if start_date and end_date:
                st.session_state["time_date_range"] = (start_date, end_date)

        st.session_state["time_start"] = saved_start_time or dt_time(0, 0)
        st.session_state["time_end"] = saved_end_time or dt_time(23, 59)


def filter_by_datetime_window(
    df: pd.DataFrame,
    start_dt: Optional[datetime],
    end_dt: Optional[datetime],
) -> pd.DataFrame:
    """Filter rows to an inclusive datetime window."""
    if df.empty:
        return df

    filtered = df.copy()
    if start_dt is not None:
        filtered = filtered[filtered["timestamp"] >= pd.Timestamp(start_dt)]
    if end_dt is not None:
        filtered = filtered[filtered["timestamp"] <= pd.Timestamp(end_dt)]
    return filtered


def filter_by_module(df: pd.DataFrame, module: Optional[str]) -> pd.DataFrame:
    """Filter to a single module. Pass 'All Modules' or None to skip."""
    if not module or module == "All Modules":
        return df
    return df[df["module"] == module].copy()


def filter_by_time(
    df: pd.DataFrame,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    start_time=None,
    end_time=None,
) -> pd.DataFrame:
    """Filter DataFrame to rows within the date/time range."""
    if df.empty:
        return df

    filtered = df.copy()

    if start_date is not None:
        start_dt = datetime.combine(start_date, start_time) if start_time else datetime.combine(start_date, datetime.min.time())
        filtered = filtered[filtered["timestamp"] >= pd.Timestamp(start_dt)]

    if end_date is not None:
        end_dt = datetime.combine(end_date, end_time) if end_time else datetime.combine(end_date, datetime.max.time().replace(microsecond=0))
        filtered = filtered[filtered["timestamp"] <= pd.Timestamp(end_dt)]

    return filtered


def filter_by_session_start(
    df: pd.DataFrame,
    session_start: Optional[datetime],
) -> pd.DataFrame:
    """Filter to rows with timestamp >= session_start."""
    if session_start is None or df.empty:
        return df
    return df[df["timestamp"] >= pd.Timestamp(session_start)].copy()
