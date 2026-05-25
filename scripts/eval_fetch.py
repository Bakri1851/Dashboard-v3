"""Phase 1 of the v2 weights/hyperparams evaluation pipeline.

One-shot fetch of all submissions via ``cache.load_dataframe()``, write to
``data/eval_submissions.{parquet|pkl}``, then sanity-print per-session row
and student counts so we can confirm the API still serves historical data
before committing to the rest of the pipeline.

Run from repo root::

    python scripts/eval_fetch.py            # uses on-disk cache if present
    python scripts/eval_fetch.py --refetch  # forces a fresh API GET
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "code2"))

import pandas as pd  # noqa: E402

from backend import cache, paths  # noqa: E402


def _persist(df: pd.DataFrame, stem: Path) -> Path:
    """Write df to parquet if pyarrow is available, else pickle."""
    parquet_path = stem.with_suffix(".parquet")
    try:
        df.to_parquet(parquet_path, index=False)
        return parquet_path
    except (ImportError, ValueError) as exc:
        pickle_path = stem.with_suffix(".pkl")
        df.to_pickle(pickle_path)
        print(f"  (parquet unavailable: {type(exc).__name__}; fell back to pickle)")
        return pickle_path


def _load_existing(stem: Path) -> Optional[pd.DataFrame]:
    """Return df from disk if a previous fetch is cached, else None."""
    for suffix in (".parquet", ".pkl"):
        path = stem.with_suffix(suffix)
        if not path.exists():
            continue
        try:
            if suffix == ".parquet":
                return pd.read_parquet(path)
            return pd.read_pickle(path)
        except Exception as exc:
            print(f"  WARN: failed to load {path.name}: {type(exc).__name__}: {exc}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--refetch",
        action="store_true",
        help="Ignore on-disk cache; force a fresh API GET via cache.load_dataframe().",
    )
    args = parser.parse_args()

    stem = paths.DATA_DIR / "eval_submissions"

    df: Optional[pd.DataFrame] = None
    if not args.refetch:
        df = _load_existing(stem)
        if df is not None:
            print(f"Reusing cached snapshot ({len(df):,} rows)")

    if df is None:
        print("Fetching full DataFrame via cache.load_dataframe()...")
        df, err = cache.load_dataframe()
        if df.empty:
            print(f"ERROR: empty DataFrame. {err}")
            return 1
        written = _persist(df, stem)
        print(f"Saved {len(df):,} rows to {written}")

    print()
    print(f"Columns: {list(df.columns)}")
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
        valid_ts = ts.dropna()
        if not valid_ts.empty:
            print(f"Time range: {valid_ts.min()} -> {valid_ts.max()}")
    print()

    sessions_path = paths.saved_sessions_path()
    sessions_blob = json.loads(sessions_path.read_text(encoding="utf-8"))
    sessions = sessions_blob.get("sessions", [])
    print(f"Per-session sanity ({len(sessions)} saved sessions):")
    print(
        f"{'#':>3}  {'name':<40}  {'start (UTC)':<20}  "
        f"{'rows':>8}  {'students':>8}  {'modules':>7}"
    )
    print("  " + "-" * 90)

    healthy = 0
    for i, sess in enumerate(sessions, 1):
        name = (sess.get("name") or "?")[:38]
        start = sess.get("start_time") or sess.get("start") or ""
        end = sess.get("end_time") or sess.get("end") or ""
        sliced = cache.filter_df(df, start, end)
        rows = len(sliced)
        students = int(sliced["user"].nunique()) if "user" in sliced.columns else 0
        modules = int(sliced["module"].nunique()) if "module" in sliced.columns else 0
        marker = " " if rows >= 100 and students >= 10 else "!"
        print(
            f"{i:>3}{marker} {name:<40}  {str(start)[:19]:<20}  "
            f"{rows:>8,}  {students:>8}  {modules:>7}"
        )
        if rows >= 100 and students >= 10:
            healthy += 1

    print()
    print(f"Healthy (>=10 students AND >=100 submissions): {healthy}/{len(sessions)}")
    if healthy >= 15:
        print("PASS: enough sessions to proceed with Phase 2.")
    elif healthy >= 5:
        print(
            "PARTIAL: some early sessions look truncated. Phase 2 can proceed "
            "on the healthy subset; flag the truncation in eval_results.md."
        )
    else:
        print(
            "FAIL: too few healthy sessions. Likely the API truncated history; "
            "consider falling back to a user-supplied dump."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
