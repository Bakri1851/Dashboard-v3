"""Lab class discovery and tagging.

A lab class is the tuple (module, academic_week, day_of_week, time_slot).
Sessions are auto-derived from observed records by gap-clustering timestamps
within each (module, week, dow) group; the cluster's slot is bucketed by the
hour of its median timestamp.

class_id format: ``f"{module_slug}|w{NN}|{dow}|{slot}"`` e.g. ``"coa122|w08|tue|aft"``.
class_label format: ``f"{MODULE} · {Week} · {Dow} {HH:MM}"`` e.g. ``"COA122 · Sem 2 - Wk 8 · Tue 14:00"``.

No Streamlit imports — this module is shared between code/ and code2/.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, time as dt_time, timedelta
from typing import Optional

import pandas as pd

from learning_dashboard.academic_calendar import get_academic_period


_GAP_THRESHOLD_SECONDS = 45 * 60   # split clusters where consecutive records gap > 45 min

_DOW_SHORT = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
_DOW_TITLE = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


@dataclass(frozen=True)
class ClassRecord:
    """One discovered lab class candidate."""
    class_id: str
    class_label: str
    module: str
    week_label: str
    week_num: int
    dow: int                  # 0=Mon..6=Sun
    slot: str                 # mor/aft/eve, with optional disambiguating suffix
    slot_start: pd.Timestamp
    slot_end: pd.Timestamp
    slot_median: pd.Timestamp
    n_records: int
    n_students: int

    def to_dict(self) -> dict:
        d = asdict(self)
        for k in ("slot_start", "slot_end", "slot_median"):
            v = d.get(k)
            if isinstance(v, pd.Timestamp):
                d[k] = v.isoformat()
        return d


def _slot_short_for_hour(hour: int) -> str:
    if hour < 12:
        return "mor"
    if hour < 17:
        return "aft"
    return "eve"


def _week_num_from_label(label: str) -> int:
    """Extract integer week number from an academic period label.

    Returns 0 for non-week labels (Christmas/Easter/Inter Semester/Break).
    """
    if not isinstance(label, str):
        return 0
    if "Wk" in label:
        try:
            return int(label.split("Wk")[1].strip())
        except (ValueError, IndexError):
            return 0
    return 0


def _module_slug(module: str) -> str:
    return str(module or "").strip().lower() or "unknown"


def build_class_id(module: str, week_num: int, dow: int, slot: str) -> str:
    return f"{_module_slug(module)}|w{int(week_num):02d}|{_DOW_SHORT[int(dow) % 7]}|{slot}"


def build_class_label(module: str, week_label: str, dow: int, median_ts: pd.Timestamp) -> str:
    mod = str(module or "").upper() or "UNKNOWN"
    wk = week_label or "Unknown"
    dow_title = _DOW_TITLE[int(dow) % 7]
    if isinstance(median_ts, pd.Timestamp) and not pd.isna(median_ts):
        # round to nearest 5 min for readability
        rounded = median_ts.round("5min") if hasattr(median_ts, "round") else median_ts
        hhmm = rounded.strftime("%H:%M")
    else:
        hhmm = "??:??"
    return f"{mod} · {wk} · {dow_title} {hhmm}"


def _gap_cluster(timestamps: pd.Series) -> list[list[int]]:
    """Cluster a sorted series of timestamps into groups split where consecutive gap > threshold.

    Returns a list of index lists (each list contains the original index of records in that cluster).
    """
    if timestamps.empty:
        return []
    sorted_idx = timestamps.sort_values().index.tolist()
    clusters: list[list[int]] = [[sorted_idx[0]]]
    prev_ts = timestamps.loc[sorted_idx[0]]
    for idx in sorted_idx[1:]:
        cur_ts = timestamps.loc[idx]
        gap = (cur_ts - prev_ts).total_seconds()
        if gap > _GAP_THRESHOLD_SECONDS:
            clusters.append([idx])
        else:
            clusters[-1].append(idx)
        prev_ts = cur_ts
    return clusters


def discover_classes(df: pd.DataFrame) -> list[ClassRecord]:
    """Return one ClassRecord per discovered (module, week, dow, slot) cluster."""
    if df is None or df.empty or "timestamp" not in df.columns or "module" not in df.columns:
        return []

    work = df[["module", "timestamp", "user"]].copy()
    work = work.dropna(subset=["timestamp"])
    if work.empty:
        return []

    work["timestamp"] = pd.to_datetime(work["timestamp"], errors="coerce")
    work = work.dropna(subset=["timestamp"])
    if work.empty:
        return []

    work["_date"] = work["timestamp"].dt.date
    work["_dow"] = work["timestamp"].dt.dayofweek
    work["_week_label"] = work["_date"].apply(get_academic_period)
    work["_week_num"] = work["_week_label"].apply(_week_num_from_label)

    out: list[ClassRecord] = []
    for (module, week_label, week_num, dow), group in work.groupby(
        ["module", "_week_label", "_week_num", "_dow"], dropna=False
    ):
        clusters = _gap_cluster(group["timestamp"])
        # Track slot collisions per group (e.g. two morning clusters → mor, mor2)
        slot_counts: dict[str, int] = {}
        for cluster_idx in clusters:
            cluster = group.loc[cluster_idx]
            slot_start = cluster["timestamp"].min()
            slot_end = cluster["timestamp"].max()
            slot_median = cluster["timestamp"].median()
            base_slot = _slot_short_for_hour(int(slot_median.hour))
            slot_counts[base_slot] = slot_counts.get(base_slot, 0) + 1
            slot = base_slot if slot_counts[base_slot] == 1 else f"{base_slot}{slot_counts[base_slot]}"
            class_id = build_class_id(module, int(week_num), int(dow), slot)
            class_label = build_class_label(module, week_label, int(dow), slot_median)
            out.append(
                ClassRecord(
                    class_id=class_id,
                    class_label=class_label,
                    module=str(module),
                    week_label=str(week_label),
                    week_num=int(week_num),
                    dow=int(dow),
                    slot=slot,
                    slot_start=slot_start,
                    slot_end=slot_end,
                    slot_median=slot_median,
                    n_records=int(len(cluster)),
                    n_students=int(cluster["user"].nunique()) if "user" in cluster.columns else 0,
                )
            )

    return out


def tag_records(df: pd.DataFrame) -> pd.DataFrame:
    """Return ``df`` with a ``class_id`` column populated for each record."""
    if df is None or df.empty:
        return df
    if "timestamp" not in df.columns or "module" not in df.columns:
        return df

    classes = discover_classes(df)
    if not classes:
        out = df.copy()
        out["class_id"] = None
        return out

    # Build a lookup: (module, week_num, dow) -> list of (slot_start, slot_end, class_id)
    lookup: dict[tuple, list[tuple]] = {}
    for c in classes:
        key = (c.module, c.week_num, c.dow)
        lookup.setdefault(key, []).append((c.slot_start, c.slot_end, c.class_id))

    out = df.copy()
    ts = pd.to_datetime(out["timestamp"], errors="coerce")
    dow = ts.dt.dayofweek
    week_labels = ts.dt.date.apply(lambda d: get_academic_period(d) if pd.notna(d) else None)
    week_nums = week_labels.apply(_week_num_from_label)

    class_ids: list[Optional[str]] = []
    for module, t, d, w in zip(out["module"].fillna(""), ts, dow, week_nums):
        if pd.isna(t) or pd.isna(d):
            class_ids.append(None)
            continue
        key = (str(module), int(w), int(d))
        candidates = lookup.get(key)
        if not candidates:
            class_ids.append(None)
            continue
        match = None
        for slot_start, slot_end, cid in candidates:
            if slot_start <= t <= slot_end:
                match = cid
                break
        class_ids.append(match)

    out["class_id"] = class_ids
    return out


def class_id_for_timestamp(
    module: str,
    timestamp,
) -> Optional[str]:
    """Convenience: derive class_id from a single (module, timestamp).

    Used by the saved-sessions backfill where we have only one timestamp per
    record, not a cluster. Slot is bucketed by the hour of the timestamp.
    """
    ts = pd.to_datetime(timestamp, errors="coerce")
    if pd.isna(ts):
        return None
    week_label = get_academic_period(ts.date())
    week_num = _week_num_from_label(week_label)
    slot = _slot_short_for_hour(int(ts.hour))
    return build_class_id(module, week_num, int(ts.weekday()), slot)


def class_label_for_timestamp(
    module: str,
    timestamp,
) -> Optional[str]:
    ts = pd.to_datetime(timestamp, errors="coerce")
    if pd.isna(ts):
        return None
    week_label = get_academic_period(ts.date())
    return build_class_label(module, week_label, int(ts.weekday()), ts)
