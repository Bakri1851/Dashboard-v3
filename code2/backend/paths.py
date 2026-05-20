"""Runtime path helpers for app data and backward-compatible migration."""

from __future__ import annotations

import shutil
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

LEGACY_SAVED_SESSIONS_PATH = PROJECT_ROOT / "saved_sessions.json"
LEGACY_LAB_SESSION_PATH = PROJECT_ROOT / "lab_session.json"

SAVED_SESSIONS_PATH = DATA_DIR / "saved_sessions.json"
LAB_SESSION_PATH = DATA_DIR / "lab_session.json"
LAB_SESSION_LOCK_PATH = DATA_DIR / "lab_session.lock"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _copy_if_missing(source: Path, destination: Path) -> None:
    if destination.exists() or not source.exists():
        return
    _ensure_data_dir()
    shutil.copy2(source, destination)


def ensure_runtime_data_layout() -> None:
    """Create the runtime data directory and migrate legacy root files once."""
    _ensure_data_dir()
    _copy_if_missing(LEGACY_SAVED_SESSIONS_PATH, SAVED_SESSIONS_PATH)
    _copy_if_missing(LEGACY_LAB_SESSION_PATH, LAB_SESSION_PATH)


def saved_sessions_path() -> Path:
    """Preferred saved-sessions path, with legacy fallback if migration fails."""
    ensure_runtime_data_layout()
    if SAVED_SESSIONS_PATH.exists():
        return SAVED_SESSIONS_PATH
    if LEGACY_SAVED_SESSIONS_PATH.exists():
        return LEGACY_SAVED_SESSIONS_PATH
    return SAVED_SESSIONS_PATH


def lab_session_path() -> Path:
    """Preferred shared lab-session path, with legacy fallback if migration fails."""
    ensure_runtime_data_layout()
    if LAB_SESSION_PATH.exists():
        return LAB_SESSION_PATH
    if LEGACY_LAB_SESSION_PATH.exists():
        return LEGACY_LAB_SESSION_PATH
    return LAB_SESSION_PATH


def lab_session_lock_path() -> Path:
    """Lock path paired with the effective lab-session file location."""
    ensure_runtime_data_layout()
    if lab_session_path() == LEGACY_LAB_SESSION_PATH:
        return LEGACY_LAB_SESSION_PATH.with_suffix(".lock")
    return LAB_SESSION_LOCK_PATH


def rag_chroma_dir() -> Path:
    """Persistent ChromaDB storage directory for the RAG pipeline."""
    _ensure_data_dir()
    p = DATA_DIR / "rag_chroma"
    p.mkdir(parents=True, exist_ok=True)
    return p


def incorrectness_cache_path() -> Path:
    """Disk-backed OpenAI incorrectness score cache — avoids ~10 min of
    serial scoring on every uvicorn restart."""
    _ensure_data_dir()
    return DATA_DIR / "incorrectness_cache.json"
