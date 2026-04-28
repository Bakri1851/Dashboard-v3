"""Shared lab-session state management for instructor and assistant apps."""

from __future__ import annotations

import json
import random
import string
from datetime import datetime
from typing import Any, Optional

from filelock import FileLock

from learning_dashboard import config, paths


_LOCK_TIMEOUT_SECONDS = 5
_SESSION_CODE_ALPHABET = string.ascii_uppercase + string.digits


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _default_state() -> dict[str, Any]:
    return {
        "session_code": None,
        "session_active": False,
        "session_start": None,
        "generated_at": _now_iso(),
        "lab_assistants": {},
        "assignments": {},
        "allow_self_allocation": False,
        "class_id": None,
        "class_label": None,
        "demo_mode": False,
    }


def _lock() -> FileLock:
    lock_file = paths.lab_session_lock_path()
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    return FileLock(str(lock_file), timeout=_LOCK_TIMEOUT_SECONDS)


def _normalize_state(raw_state: Any) -> dict[str, Any]:
    state = _default_state()
    if not isinstance(raw_state, dict):
        return state

    session_code = raw_state.get("session_code")
    if isinstance(session_code, str) and session_code:
        state["session_code"] = session_code.strip().upper()

    state["session_active"] = bool(raw_state.get("session_active", False))
    state["allow_self_allocation"] = bool(raw_state.get("allow_self_allocation", False))
    state["demo_mode"] = bool(raw_state.get("demo_mode", False))

    session_start = raw_state.get("session_start")
    if isinstance(session_start, str) and session_start:
        state["session_start"] = session_start

    generated_at = raw_state.get("generated_at")
    if isinstance(generated_at, str) and generated_at:
        state["generated_at"] = generated_at

    class_id = raw_state.get("class_id")
    if isinstance(class_id, str) and class_id.strip():
        state["class_id"] = class_id.strip()

    class_label = raw_state.get("class_label")
    if isinstance(class_label, str) and class_label.strip():
        state["class_label"] = class_label.strip()

    assistants_raw = raw_state.get("lab_assistants", {})
    assistants: dict[str, dict[str, Any]] = {}
    if isinstance(assistants_raw, dict):
        for assistant_id, info in assistants_raw.items():
            if not isinstance(assistant_id, str) or not assistant_id.strip():
                continue
            if not isinstance(info, dict):
                continue
            name = info.get("name")
            if not isinstance(name, str) or not name.strip():
                continue
            joined_at = info.get("joined_at")
            assistants[assistant_id] = {
                "name": name.strip(),
                "joined_at": joined_at if isinstance(joined_at, str) and joined_at else _now_iso(),
                "assigned_student": None,
            }

    assignments_raw = raw_state.get("assignments", {})
    assignments: dict[str, dict[str, Any]] = {}
    assistant_taken: set[str] = set()
    if isinstance(assignments_raw, dict):
        for student_id, entry in assignments_raw.items():
            if not isinstance(student_id, str) or not student_id.strip():
                continue
            if not isinstance(entry, dict):
                continue
            assistant_id = entry.get("assistant_id")
            if not isinstance(assistant_id, str) or assistant_id not in assistants:
                continue
            if assistant_id in assistant_taken:
                continue

            status = entry.get("status")
            if status not in {"helping", "helped"}:
                status = "helping"

            assignment = {
                "assistant_id": assistant_id,
                "status": status,
                "assigned_at": (
                    entry.get("assigned_at")
                    if isinstance(entry.get("assigned_at"), str) and entry.get("assigned_at")
                    else _now_iso()
                ),
            }
            helped_at = entry.get("helped_at")
            if isinstance(helped_at, str) and helped_at:
                assignment["helped_at"] = helped_at

            assignments[student_id] = assignment
            assistants[assistant_id]["assigned_student"] = student_id
            assistant_taken.add(assistant_id)

    state["lab_assistants"] = assistants
    state["assignments"] = assignments
    return state


def _read_state_unlocked() -> dict[str, Any]:
    state_file = paths.lab_session_path()
    if not state_file.exists():
        return _default_state()
    try:
        raw = json.loads(state_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return _default_state()
    return _normalize_state(raw)


def _write_state_unlocked(state: dict[str, Any]) -> None:
    state_file = paths.lab_session_path()
    state_file.parent.mkdir(parents=True, exist_ok=True)
    normalized = _normalize_state(state)
    tmp_file = state_file.with_suffix(".tmp")
    tmp_file.write_text(json.dumps(normalized, indent=2), encoding="utf-8")
    tmp_file.replace(state_file)


def _build_assistant_id(name: str, existing_ids: set[str]) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "_" for ch in name.strip())
    base = "_".join(part for part in base.split("_") if part)[:18] or "assistant"
    for _ in range(200):
        candidate = f"{base}_{random.randint(1000, 9999)}"
        if candidate not in existing_ids:
            return candidate
    candidate = f"{base}_{int(datetime.now().timestamp())}"
    return candidate


def read_lab_state() -> dict[str, Any]:
    with _lock():
        return _read_state_unlocked()


def generate_session_code() -> str:
    return "".join(random.choices(_SESSION_CODE_ALPHABET, k=config.LAB_CODE_LENGTH))


def start_lab_session(
    session_code: Optional[str] = None,
    class_id: Optional[str] = None,
    class_label: Optional[str] = None,
) -> None:
    code = (session_code or "").strip().upper()
    if len(code) != config.LAB_CODE_LENGTH:
        code = generate_session_code()

    with _lock():
        state = _default_state()
        state["session_code"] = code
        state["session_active"] = True
        state["session_start"] = _now_iso()
        state["generated_at"] = _now_iso()
        if isinstance(class_id, str) and class_id.strip():
            state["class_id"] = class_id.strip()
        if isinstance(class_label, str) and class_label.strip():
            state["class_label"] = class_label.strip()
        _write_state_unlocked(state)


def end_lab_session() -> None:
    with _lock():
        state = _read_state_unlocked()
        state["session_active"] = False
        state["assignments"] = {}
        for info in state["lab_assistants"].values():
            info["assigned_student"] = None
        # class_id / class_label retained on the inactive record.
        _write_state_unlocked(state)


def join_session(session_code: str, name: str) -> tuple[bool, Optional[str], Optional[str]]:
    code = (session_code or "").strip().upper()
    clean_name = (name or "").strip()
    if not clean_name:
        return False, None, "Name is required."

    with _lock():
        state = _read_state_unlocked()
        if not state.get("session_active"):
            return False, None, "No active lab session."
        if code != state.get("session_code"):
            return False, None, "Invalid session code."

        for assistant_id, info in state["lab_assistants"].items():
            existing_name = str(info.get("name", "")).strip()
            if existing_name.casefold() == clean_name.casefold():
                info["assigned_student"] = None
                _write_state_unlocked(state)
                return True, assistant_id, None

        assistant_id = _build_assistant_id(clean_name, set(state["lab_assistants"].keys()))
        state["lab_assistants"][assistant_id] = {
            "name": clean_name,
            "joined_at": _now_iso(),
            "assigned_student": None,
        }
        _write_state_unlocked(state)
        return True, assistant_id, None


def assign_student(student_id: str, assistant_id: str) -> bool:
    student = (student_id or "").strip()
    aid = (assistant_id or "").strip()
    if not student or not aid:
        return False

    with _lock():
        state = _read_state_unlocked()
        if not state.get("session_active"):
            return False

        assistants = state["lab_assistants"]
        assignments = state["assignments"]
        assistant = assistants.get(aid)
        if assistant is None:
            return False

        existing = assignments.get(student)
        if existing:
            return existing.get("assistant_id") == aid

        current_student = assistant.get("assigned_student")
        if current_student and current_student != student:
            return False

        assignments[student] = {
            "assistant_id": aid,
            "status": "helping",
            "assigned_at": _now_iso(),
        }
        assistant["assigned_student"] = student
        _write_state_unlocked(state)
        return True


def self_claim_student(student_id: str, assistant_id: str) -> tuple[bool, Optional[str]]:
    student = (student_id or "").strip()
    aid = (assistant_id or "").strip()
    if not student:
        return False, "Student is required."
    if not aid:
        return False, "Assistant ID is required."

    with _lock():
        state = _read_state_unlocked()
        if not state.get("session_active"):
            return False, "No active lab session."

        assistants = state["lab_assistants"]
        assignments = state["assignments"]
        assistant = assistants.get(aid)
        if assistant is None:
            return False, "Assistant is not part of this session."

        current_student = assistant.get("assigned_student")
        if current_student and current_student != student:
            return False, "You are already assigned to another student."

        existing = assignments.get(student)
        if existing and existing.get("assistant_id") != aid:
            return False, "Student has already been claimed."
        if existing and existing.get("assistant_id") == aid:
            return True, None

        assignments[student] = {
            "assistant_id": aid,
            "status": "helping",
            "assigned_at": _now_iso(),
        }
        assistant["assigned_student"] = student
        _write_state_unlocked(state)
        return True, None


def set_allow_self_allocation(enabled: bool) -> None:
    with _lock():
        state = _read_state_unlocked()
        state["allow_self_allocation"] = bool(enabled)
        _write_state_unlocked(state)


def get_assignment_for_assistant(assistant_id: str) -> Optional[str]:
    aid = (assistant_id or "").strip()
    if not aid:
        return None

    with _lock():
        state = _read_state_unlocked()
        assistant = state["lab_assistants"].get(aid)
        if assistant is None:
            return None

        assigned_student = assistant.get("assigned_student")
        if (
            isinstance(assigned_student, str)
            and assigned_student in state["assignments"]
            and state["assignments"][assigned_student].get("assistant_id") == aid
        ):
            return assigned_student

        for student_id, assignment in state["assignments"].items():
            if assignment.get("assistant_id") == aid:
                assistant["assigned_student"] = student_id
                _write_state_unlocked(state)
                return student_id

        if assistant.get("assigned_student") is not None:
            assistant["assigned_student"] = None
            _write_state_unlocked(state)
        return None


def mark_student_helped(student_id: str) -> bool:
    student = (student_id or "").strip()
    if not student:
        return False

    with _lock():
        state = _read_state_unlocked()
        assignment = state["assignments"].get(student)
        if assignment is None:
            return False
        assignment["status"] = "helped"
        assignment["helped_at"] = _now_iso()
        _write_state_unlocked(state)
        return True


def unassign_student(student_id: str) -> bool:
    student = (student_id or "").strip()
    if not student:
        return False

    with _lock():
        state = _read_state_unlocked()
        changed = False
        assignment = state["assignments"].pop(student, None)
        if assignment is not None:
            changed = True
            assistant_id = assignment.get("assistant_id")
            assistant = state["lab_assistants"].get(assistant_id)
            if assistant and assistant.get("assigned_student") == student:
                assistant["assigned_student"] = None

        for info in state["lab_assistants"].values():
            if info.get("assigned_student") == student:
                info["assigned_student"] = None
                changed = True

        if changed:
            _write_state_unlocked(state)
        return changed


def _remove_assistant_unlocked(
    state: dict[str, Any],
    assistant_id: str,
) -> tuple[bool, Optional[str]]:
    assistants = state["lab_assistants"]
    if assistant_id not in assistants:
        return False, "Assistant not found."

    assigned_student = assistants[assistant_id].get("assigned_student")
    if isinstance(assigned_student, str) and assigned_student:
        state["assignments"].pop(assigned_student, None)

    for student_id in list(state["assignments"].keys()):
        assignment = state["assignments"].get(student_id)
        if assignment and assignment.get("assistant_id") == assistant_id:
            state["assignments"].pop(student_id, None)

    assistants.pop(assistant_id, None)
    return True, None


def leave_session(assistant_id: str) -> tuple[bool, Optional[str]]:
    aid = (assistant_id or "").strip()
    if not aid:
        return False, "Assistant ID is required."

    with _lock():
        state = _read_state_unlocked()
        ok, err = _remove_assistant_unlocked(state, aid)
        if not ok:
            return False, err
        _write_state_unlocked(state)
        return True, None


def remove_assistant(assistant_id: str) -> tuple[bool, Optional[str]]:
    aid = (assistant_id or "").strip()
    if not aid:
        return False, "Assistant ID is required."

    with _lock():
        state = _read_state_unlocked()
        ok, err = _remove_assistant_unlocked(state, aid)
        if not ok:
            return False, err
        _write_state_unlocked(state)
        return True, None


_DEMO_ASSISTANTS: tuple[tuple[str, str, int], ...] = (
    ("amelia_r_demo", "Amelia R.", 25),
    ("dev_k_demo", "Dev K.", 18),
    ("noor_h_demo", "Noor H.", 12),
    ("sam_o_demo", "Sam O.", 6),
)

DEMO_MODULE = "25COA122"
DEMO_CLASS_ID = "25COA122|mon|14h"
DEMO_CLASS_LABEL = "25COA122 Monday 14:00 (demo)"


def seed_demo_session() -> None:
    """Populate a fake live session with four named assistants for UI previews.

    Idempotent: replaces any current state with a fresh demo session. The
    instructor still calls /lab/end (or end_lab_session) to tear it down.
    Marks demo_mode=True so the /live, /struggle, and /difficulty endpoints
    return canned mock data instead of the empty real dataset.
    """
    from datetime import timedelta

    start_lab_session(class_id=DEMO_CLASS_ID, class_label=DEMO_CLASS_LABEL)

    with _lock():
        state = _read_state_unlocked()
        state["demo_mode"] = True
        now = datetime.now()
        for aid, name, minutes_ago in _DEMO_ASSISTANTS:
            state["lab_assistants"][aid] = {
                "name": name,
                "joined_at": (now - timedelta(minutes=minutes_ago)).isoformat(timespec="seconds"),
                "assigned_student": None,
            }
        _write_state_unlocked(state)


def is_demo_mode() -> bool:
    """True when the active session was created via seed_demo_session()."""
    state = read_lab_state()
    return bool(state.get("session_active") and state.get("demo_mode"))
