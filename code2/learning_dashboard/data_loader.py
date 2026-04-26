# data_loader.py — API fetching, parsing, normalization, cleaning
import json
import logging
import xml.etree.ElementTree as ET
from datetime import date as dt_date, datetime, time as dt_time
from pathlib import Path
from typing import Optional
from uuid import uuid4

import pandas as pd
import requests

from learning_dashboard import config, paths

logger = logging.getLogger(__name__)


def fetch_raw_data_uncached() -> str:
    """GET request to the API endpoint. Caching is handled by backend/cache.py."""
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
                        # Live schema: <feedback model="..." friend="..." time="...">TEXT</feedback>
                        # (no nested <response>). Text is HTML-escaped — GPT handles that fine.
                        feedback_el = sub.find("feedback")
                        record["ai_feedback"] = (
                            feedback_el.text
                            if feedback_el is not None and feedback_el.text
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
                # Live schema: <feedback model="..." friend="..." time="...">TEXT</feedback>
                # (no nested <response>).
                feedback_el = sub.find("feedback")
                record["ai_feedback"] = (
                    feedback_el.text
                    if feedback_el is not None and feedback_el.text
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

    # Add academic period label
    from learning_dashboard.academic_calendar import add_academic_period_column
    df = add_academic_period_column(df)

    return df


def add_feedback_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of df with a boolean 'has_feedback' column."""
    out = df.copy()
    out["has_feedback"] = out["ai_feedback"].notna() & (out["ai_feedback"].astype(str).str.strip() != "")
    return out


def _saved_sessions_path() -> Path:
    """Absolute path to the local saved-session store."""
    return paths.saved_sessions_path()


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
        logger.warning("Saved sessions file was corrupted and has been reset.")
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
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _backfill_saved_session_class_ids(
    sessions: list[dict],
    default_module: str = "coa122",
) -> tuple[list[dict], bool]:
    """One-shot migration: assign class_id/class_label to legacy records.

    Records without ``class_id`` get one derived from their ``start_time``,
    assuming module=``default_module`` (the only module historically present
    in saved_sessions.json). Idempotent.
    """
    from learning_dashboard.lab_classes import (
        class_id_for_timestamp,
        class_label_for_timestamp,
    )

    changed = False
    out: list[dict] = []
    for record in sessions:
        if not isinstance(record, dict):
            out.append(record)
            continue
        if record.get("class_id"):
            out.append(record)
            continue
        start_iso = record.get("start_time")
        cid = class_id_for_timestamp(default_module, start_iso) if start_iso else None
        if not cid:
            out.append(record)
            continue
        record = dict(record)
        record["class_id"] = cid
        record["class_label"] = class_label_for_timestamp(default_module, start_iso)
        out.append(record)
        changed = True
    return out, changed


def load_saved_sessions() -> list[dict]:
    """Return saved session records sorted by newest end_time first."""
    payload = _read_saved_sessions_payload()
    sessions = payload.get("sessions", [])

    backfilled, changed = _backfill_saved_session_class_ids(sessions)
    if changed:
        try:
            _write_saved_sessions_payload(
                {
                    "version": config.SAVED_SESSIONS_VERSION,
                    "sessions": backfilled,
                }
            )
        except OSError:
            pass
        sessions = backfilled

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
