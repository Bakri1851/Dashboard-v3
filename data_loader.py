# ============================================================
# data_loader.py — API fetching, parsing, normalization, cleaning
# ============================================================
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional

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
