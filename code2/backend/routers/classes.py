"""Lab class discovery endpoints — for the React Start Lab Session UI."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

from backend.cache import load_dataframe
from backend.schemas import LabClass
from learning_dashboard import lab_classes

router = APIRouter(tags=["classes"])


def _to_lab_class(c: lab_classes.ClassRecord) -> LabClass:
    return LabClass(
        class_id=c.class_id,
        class_label=c.class_label,
        module=c.module,
        week_label=c.week_label,
        week_num=c.week_num,
        dow=c.dow,
        slot=c.slot,
        slot_start=c.slot_start.isoformat() if c.slot_start is not None else None,
        slot_end=c.slot_end.isoformat() if c.slot_end is not None else None,
        n_records=c.n_records,
        n_students=c.n_students,
    )


@router.get("/classes", response_model=list[LabClass])
def list_classes(
    only_current: bool = Query(default=False, description="Restrict to classes happening now (±90 min on the same dow)."),
) -> list[LabClass]:
    """Return discovered lab classes from the cached dataframe.

    With ``only_current=true``, returns just the candidates the instructor is
    likely to be starting right now — used by the Start Lab Session dropdown.
    """
    df, _err = load_dataframe()
    if df.empty:
        return []
    if only_current:
        records = lab_classes.current_class_candidates(df, datetime.now())
    else:
        records = lab_classes.discover_classes(df)
    return [_to_lab_class(c) for c in records]
