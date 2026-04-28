"""Canned mock data for the In-Class assign-column UI preview.

Returned by `/live`, `/struggle`, `/difficulty`, `/student/{id}`,
`/lab/student/{id}/struggling-questions`, and `/rag/student/{id}` only when
`lab_state.is_demo_mode()` is true (i.e. the session was started via
`/lab/seed-demo`). Lets the user demo the full instructor + assistant
flow without a real data source.
"""
from __future__ import annotations

from backend.schemas import (
    LevelBucket,
    LiveDataResponse,
    MistakeCluster,
    ProgressionPoint,
    QuestionDetail,
    QuestionDifficulty,
    QuestionRecentAttempt,
    QuestionStudentRow,
    RagSuggestions,
    SavedSession,
    ScoreComponent,
    SessionProgression,
    StrugglingQuestionRow,
    StudentDetail,
    StudentQuestionRow,
    StudentRecentRow,
    StudentStruggle,
)
from learning_dashboard import lab_state


# (id, level, score, submissions, recent, trend)
_DEMO_STRUGGLE: tuple[tuple[str, str, float, int, float, float], ...] = (
    ("psyc2041", "Needs Help", 0.71, 48, 0.68, -0.04),
    ("math1157", "Needs Help", 0.58, 37, 0.61, -0.02),
    ("phys2023", "Needs Help", 0.52, 29, 0.55, 0.01),
    ("biol1492", "Struggling", 0.46, 42, 0.49, -0.03),
    ("chem3108", "Struggling", 0.41, 33, 0.44, 0.02),
    ("cmps2211", "Struggling", 0.38, 26, 0.41, -0.01),
    ("hist1024", "Minor Issues", 0.31, 22, 0.34, 0.05),
    ("econ2260", "Minor Issues", 0.28, 19, 0.29, -0.02),
    ("ling1805", "Minor Issues", 0.24, 24, 0.22, 0.04),
    ("phil2017", "On Track", 0.18, 31, 0.16, 0.06),
    ("arch1199", "On Track", 0.15, 28, 0.13, 0.03),
    ("geog2350", "On Track", 0.11, 35, 0.10, 0.02),
)


# (id, level, score, students, avg_attempts, module)
_DEMO_DIFFICULTY: tuple[tuple[str, str, float, int, float, str], ...] = (
    ("Q-1407", "Very Hard", 0.81, 34, 4.2, "25COA122"),
    ("Q-0928", "Very Hard", 0.77, 41, 3.9, "25COA122"),
    ("Q-2311", "Hard", 0.68, 38, 3.1, "25COA122"),
    ("Q-0471", "Hard", 0.62, 29, 2.8, "25COA122"),
    ("Q-1802", "Hard", 0.55, 35, 2.5, "25COA122"),
    ("Q-2045", "Medium", 0.46, 32, 2.1, "25COA122"),
    ("Q-0683", "Medium", 0.42, 28, 1.9, "25COA122"),
    ("Q-1119", "Medium", 0.37, 34, 1.7, "25COA122"),
    ("Q-2502", "Easy", 0.21, 30, 1.3, "25COA122"),
    ("Q-1733", "Easy", 0.14, 33, 1.1, "25COA122"),
)


def is_active() -> bool:
    return lab_state.is_demo_mode()


def struggle_rows() -> list[StudentStruggle]:
    return [
        StudentStruggle(id=sid, level=lvl, score=score, submissions=subs, recent=rec, trend=tr)
        for sid, lvl, score, subs, rec, tr in _DEMO_STRUGGLE
    ]


def difficulty_rows() -> list[QuestionDifficulty]:
    return [
        QuestionDifficulty(
            id=qid, level=lvl, score=score, students=stu, avgAttempts=att, module=mod,
        )
        for qid, lvl, score, stu, att, mod in _DEMO_DIFFICULTY
    ]


def _bucket(rows: list, level_attr: str, order: list[str]) -> list[LevelBucket]:
    counts: dict[str, int] = {lbl: 0 for lbl in order}
    for r in rows:
        counts[getattr(r, level_attr)] = counts.get(getattr(r, level_attr), 0) + 1
    return [LevelBucket(label=lbl, count=counts[lbl]) for lbl in order]


def live_response() -> LiveDataResponse:
    from datetime import datetime, timezone

    s = struggle_rows()
    d = difficulty_rows()
    total_subs = sum(row.submissions for row in s)
    mean_inc = round(sum(row.recent for row in s) / max(len(s), 1), 3)

    # Tiny synthetic 24h heartbeat — gentle ramp peaking at the most recent hours.
    timeline = [0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 6, 5, 7, 9, 12, 14, 18, 22, 25, 28, 31, 34]

    return LiveDataResponse(
        records=total_subs,
        last_updated=datetime.now(timezone.utc).isoformat(),
        unique_students=len(s),
        unique_questions=len(d),
        unique_modules=1,
        mean_incorrectness=mean_inc,
        struggle_buckets=_bucket(s, "level", ["On Track", "Minor Issues", "Struggling", "Needs Help"]),
        difficulty_buckets=_bucket(d, "level", ["Easy", "Medium", "Hard", "Very Hard"]),
        timeline_24h=timeline,
        modules=["25COA122"],
        error=None,
    )


# Index struggle data by id so /student/<id> can build a detail row from it.
_STRUGGLE_BY_ID: dict[str, tuple[str, str, float, int, float, float]] = {
    row[0]: row for row in _DEMO_STRUGGLE
}

# Same for difficulty so /question/<id> can build a detail row from it.
_DIFFICULTY_BY_ID: dict[str, tuple[str, str, float, int, float, str]] = {
    row[0]: row for row in _DEMO_DIFFICULTY
}


def has_student(student_id: str) -> bool:
    return student_id in _STRUGGLE_BY_ID


def student_detail(student_id: str) -> StudentDetail | None:
    row = _STRUGGLE_BY_ID.get(student_id)
    if row is None:
        return None
    _id, level, score, subs, recent, trend = row

    # Synthetic component breakdown that sums (weighted) to roughly `score`.
    # Values are 0–1; weights mirror config but the exact total isn't critical
    # for the preview UI, which just renders bars + labels.
    components = [
        ScoreComponent(key="n_hat", label="n̂ submissions", value=min(subs / 50.0, 1.0), weight=0.10),
        ScoreComponent(key="t_hat", label="t̂ time active", value=0.55, weight=0.05),
        ScoreComponent(key="i_hat", label="ī mean incorrect.", value=recent, weight=0.30),
        ScoreComponent(key="r_hat", label="r̂ retry rate", value=min(score + 0.05, 1.0), weight=0.15),
        ScoreComponent(key="A_raw", label="A recent (EMA)", value=recent, weight=0.20),
        ScoreComponent(key="d_hat", label="d̂ trajectory", value=abs(trend) * 4, weight=0.10),
        ScoreComponent(key="rep_hat", label="rep̂ repetition", value=0.18, weight=0.10),
    ]

    # 10-point trajectory drifting around `recent` so the sparkline isn't flat.
    trajectory = [
        round(max(0.0, min(1.0, recent + 0.08 * ((i % 3) - 1) - 0.01 * i)), 3)
        for i in range(10)
    ]

    top_questions = [
        StudentQuestionRow(
            question="Q-1407: Explain virtual memory paging.",
            attempts=4,
            difficulty="Very Hard",
            last_incorrectness=0.82,
        ),
        StudentQuestionRow(
            question="Q-0928: Big-O of merge sort.",
            attempts=3,
            difficulty="Very Hard",
            last_incorrectness=0.71,
        ),
        StudentQuestionRow(
            question="Q-2311: Define ACID transactions.",
            attempts=3,
            difficulty="Hard",
            last_incorrectness=0.58,
        ),
    ]

    recent_submissions = [
        StudentRecentRow(
            timestamp="2026-04-27T13:48:00",
            question="Q-1407",
            answer="Virtual memory swaps pages from disk when…",
            incorrectness=0.81,
        ),
        StudentRecentRow(
            timestamp="2026-04-27T13:42:00",
            question="Q-0928",
            answer="O(n log n) for the average case…",
            incorrectness=0.34,
        ),
        StudentRecentRow(
            timestamp="2026-04-27T13:35:00",
            question="Q-2311",
            answer="ACID stands for Atomic, Consistent…",
            incorrectness=0.52,
        ),
    ]

    return StudentDetail(
        id=student_id,
        level=level,
        score=score,
        submissions=subs,
        recent=recent,
        trend=trend,
        mean_incorrectness=recent,
        time_active_min=42.0 + (subs % 7) * 3.5,
        retry_rate=min(score + 0.05, 1.0),
        components=components,
        trajectory=trajectory,
        top_questions=top_questions,
        recent_submissions=recent_submissions,
        timeline_24h=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 4, 5, 6, 4, 3, 2, 1, 0],
    )


def student_top_questions(student_id: str, limit: int = 3) -> list[StrugglingQuestionRow]:
    if student_id not in _STRUGGLE_BY_ID:
        return []
    canned = [
        StrugglingQuestionRow(question="Q-1407: Explain virtual memory paging.", avg_incorrectness=0.82),
        StrugglingQuestionRow(question="Q-0928: Big-O of merge sort.", avg_incorrectness=0.71),
        StrugglingQuestionRow(question="Q-2311: Define ACID transactions.", avg_incorrectness=0.58),
        StrugglingQuestionRow(question="Q-0471: Diff between TCP and UDP.", avg_incorrectness=0.49),
        StrugglingQuestionRow(question="Q-1802: Pointers vs references in C.", avg_incorrectness=0.41),
    ]
    return canned[: max(1, min(limit, len(canned)))]


def student_rag(student_id: str) -> RagSuggestions | None:
    if student_id not in _STRUGGLE_BY_ID:
        return None
    state = lab_state.read_lab_state()
    code = state.get("session_code")
    return RagSuggestions(
        audience="student",
        subject_id=student_id,
        bullets=[
            "Anchor on what they got right first — they showed correct intuition on Big-O before slipping on the merge step.",
            "Try paging the textbook example: walk through one page fault end-to-end on the whiteboard, then ask them to do the next.",
            "Avoid leading with the formal definition of ACID — start from a concrete bank-transfer scenario and let them name the properties.",
        ],
        session_id=str(code) if code else "demo",
    )


def has_question(question_id: str) -> bool:
    return question_id in _DIFFICULTY_BY_ID


# Per-question canned mistake clusters + recent answers. Keyed by question id.
_QUESTION_DETAILS: dict[str, dict] = {
    "Q-1407": {
        "clusters": [
            ("Confused page fault with cache miss", 14, 0.41,
             ["A page fault happens when the CPU cache is full",
              "It's the same as a cache miss but in RAM"]),
            ("Skipped the disk-fetch step entirely", 9, 0.27,
             ["The OS just allocates more memory",
              "The page is loaded directly from the swap"]),
            ("Forgot the TLB lookup", 6, 0.18,
             ["Translation goes straight from VA to PA"]),
        ],
        "answers": [
            "Virtual memory swaps pages from disk when the CPU cache is full",
            "Page fault triggers an OS interrupt and the missing page is read from swap",
            "When a process accesses a page not in RAM the MMU loads it from disk",
        ],
    },
    "Q-0928": {
        "clusters": [
            ("Said O(n²) for the average case", 18, 0.49,
             ["Merge sort is O(n²) like bubble sort",
              "Average case is O(n²)"]),
            ("Skipped the log n factor", 11, 0.30,
             ["It's O(n) because we visit each element once"]),
        ],
        "answers": [
            "O(n²) for the average case",
            "O(n log n) — split halves recursively then linear merge",
            "O(n) because each element is touched once",
        ],
    },
    "Q-2311": {
        "clusters": [
            ("Confused Atomicity with Consistency", 8, 0.34,
             ["Atomicity means the data is always consistent",
              "Atomic = consistent across replicas"]),
            ("Forgot Durability", 7, 0.30,
             ["ACID = Atomic, Consistent, Isolated"]),
        ],
        "answers": [
            "ACID = Atomic, Consistent, Isolated, Durable",
            "Atomicity is when all replicas have the same value",
            "Durability means transactions can roll back",
        ],
    },
}


def _generic_clusters(score: float) -> list[tuple[str, int, float, list[str]]]:
    severity = max(2, int(round(score * 12)))
    return [
        ("Off-by-one in the boundary case", severity, 0.40,
         ["Loop ran one too many times", "Used <= instead of <"]),
        ("Misread the question prompt", max(severity - 3, 1), 0.25,
         ["Solved a different problem"]),
    ]


def question_detail(question_id: str) -> QuestionDetail | None:
    row = _DIFFICULTY_BY_ID.get(question_id)
    if row is None:
        return None
    qid, level, score, students, avg_attempts, module = row

    canned = _QUESTION_DETAILS.get(qid)
    if canned is not None:
        cluster_specs = canned["clusters"]
        recent_answers = canned["answers"]
    else:
        cluster_specs = _generic_clusters(score)
        recent_answers = [
            f"Attempt referencing {qid} — partial answer",
            f"Different approach to {qid} — close but missed an edge case",
            f"Brief response to {qid}",
        ]

    mistake_clusters = [
        MistakeCluster(
            label=label,
            count=count,
            percent_of_wrong=pct,
            example_answers=examples[:3],
        )
        for label, count, pct, examples in cluster_specs
    ]

    # Pull a few real demo student ids so the cross-link to /student/<id> works.
    demo_student_ids = [r[0] for r in _DEMO_STRUGGLE]
    top_strugglers: list[QuestionStudentRow] = []
    for i, sid in enumerate(demo_student_ids[:7]):
        s_row = _STRUGGLE_BY_ID[sid]
        top_strugglers.append(
            QuestionStudentRow(
                id=sid,
                attempts=max(2, int(round(avg_attempts))) - (i % 2),
                mean_incorrectness=round(max(0.05, min(0.95, score - i * 0.05)), 3),
                struggle_level=s_row[1],
                struggle_score=s_row[2],
            )
        )

    recent_attempts = [
        QuestionRecentAttempt(
            timestamp=f"2026-04-27T13:{55 - i * 4:02d}:00",
            user=demo_student_ids[i % len(demo_student_ids)],
            answer=ans[:400],
            incorrectness=round(max(0.05, min(0.95, score + 0.05 - i * 0.10)), 3),
        )
        for i, ans in enumerate(recent_answers[:3])
    ]

    return QuestionDetail(
        id=qid,
        level=level,
        score=score,
        module=module,
        students=students,
        avg_attempts=avg_attempts,
        incorrect_rate=round(min(score, 0.99), 3),
        first_fail_rate=round(min(score * 0.85, 0.99), 3),
        mistake_clusters=mistake_clusters,
        recent_attempts=recent_attempts,
        top_strugglers=top_strugglers,
        timeline_24h=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3, 5, 7, 9, 7, 5, 3, 1, 0],
    )


def question_rag(question_id: str) -> RagSuggestions | None:
    row = _DIFFICULTY_BY_ID.get(question_id)
    if row is None:
        return None
    _qid, level, _score, _students, _attempts, _module = row
    state = lab_state.read_lab_state()
    code = state.get("session_code")

    bullets_by_level = {
        "Very Hard": [
            "Most wrong answers conflate two adjacent concepts — name both before contrasting them.",
            "Walk through one full worked example end-to-end on the board; abstract definitions land badly here.",
            "Anchor on the simplest passing case, then have the student articulate what changes for the failing one.",
        ],
        "Hard": [
            "A common mistake here is skipping the boundary check — ask the student to talk through the edge case first.",
            "Half of incorrect answers reuse the previous question's pattern; surface the difference explicitly.",
        ],
        "Medium": [
            "Students mostly get there with one nudge — ask what they expect the answer to look like before they compute it.",
        ],
        "Easy": [
            "If they're stuck on this one, the gap is usually further upstream. Check the prerequisite concept first.",
        ],
    }
    bullets = bullets_by_level.get(level, bullets_by_level["Medium"])
    return RagSuggestions(
        audience="question",
        subject_id=question_id,
        bullets=bullets,
        session_id=str(code) if code else "demo",
    )


# ----------------------------------------------------------------
# Saved sessions + progression replay (Previous Sessions view)
# ----------------------------------------------------------------

# (id, name, start_iso, end_iso, students, flagged)
_DEMO_SESSIONS: tuple[tuple[str, str, str, str, int, int], ...] = (
    ("demo-mon-1400",
     "25COA122 · Monday 14:00 (demo)",
     "2026-04-27T14:00:00", "2026-04-27T15:30:00", 14, 3),
    ("demo-thu-1000",
     "25COA122 · Thursday 10:00 (demo)",
     "2026-04-23T10:00:00", "2026-04-23T11:30:00", 12, 5),
    ("demo-fri-1300",
     "25COA122 · Friday 13:00 (demo)",
     "2026-04-17T13:00:00", "2026-04-17T14:30:00", 11, 2),
)

_DEMO_SESSION_IDS: frozenset[str] = frozenset(s[0] for s in _DEMO_SESSIONS)


def has_session(session_id: str) -> bool:
    return session_id in _DEMO_SESSION_IDS


def _saved_session(record: tuple[str, str, str, str, int, int]) -> SavedSession:
    sid, name, start, end, students, flagged = record
    from datetime import datetime as _dt
    s = _dt.fromisoformat(start)
    e = _dt.fromisoformat(end)
    return SavedSession(
        id=sid,
        name=name,
        start_time=start,
        end_time=end,
        duration_minutes=round((e - s).total_seconds() / 60.0, 1),
        students=students,
        flagged=flagged,
        module_filter="25COA122",
        class_id="25COA122|mon|14h",
        class_label="25COA122 (demo)",
    )


def saved_sessions() -> list[SavedSession]:
    return [_saved_session(r) for r in _DEMO_SESSIONS]


def _progression_curve(
    buckets: int,
    *,
    start_inc: float,
    end_inc: float,
    start_needs: int,
    end_needs: int,
    start_strug: int,
    end_strug: int,
    total_students: int,
    flagged_at_end: int,
) -> list[ProgressionPoint]:
    """Synthesize a smooth replay where students improve over time.

    Mean incorrectness curves down from start_inc → end_inc; the Needs Help
    + Struggling counts shrink while On Track / Minor Issues grow. Difficulty
    distribution stays roughly stable (questions don't get easier mid-lab).
    """
    needs_help_pool = ["psyc2041", "math1157", "phys2023", "biol1492", "chem3108"]
    points: list[ProgressionPoint] = []
    for i in range(1, buckets + 1):
        frac = i / buckets
        cumulative_subs = int(round(40 + frac * 320))
        cumulative_studs = int(round(2 + frac * (total_students - 2)))
        mean_inc = round(start_inc + (end_inc - start_inc) * frac, 3)

        needs = max(end_needs, int(round(start_needs - (start_needs - end_needs) * frac)))
        strug = max(end_strug, int(round(start_strug - (start_strug - end_strug) * frac)))
        # On-track + minor grow as needs/strug shrink, capped at total students.
        on_track = min(total_students - needs - strug, max(0, int(round(frac * (total_students - end_needs - end_strug)))))
        minor = max(0, total_students - needs - strug - on_track)

        # Difficulty roughly steady — questions don't change mid-session. Tiny
        # tail growth in 'Easy' as students get exposure.
        easy = 2 + int(round(frac * 2))
        medium = 3
        hard = 3
        very_hard = 2

        # Pop the first few struggle ids as they get helped — visual narrative.
        slots = max(needs, flagged_at_end)
        needs_ids = needs_help_pool[:max(0, slots)]

        points.append(ProgressionPoint(
            t_end=f"2026-04-27T14:{min(int(frac * 90) + 0, 89):02d}:00+00:00",
            cumulative_submissions=cumulative_subs,
            cumulative_students=cumulative_studs,
            mean_incorrectness=mean_inc,
            struggle_buckets=[
                LevelBucket(label="On Track", count=on_track),
                LevelBucket(label="Minor Issues", count=minor),
                LevelBucket(label="Struggling", count=strug),
                LevelBucket(label="Needs Help", count=needs),
            ],
            difficulty_buckets=[
                LevelBucket(label="Easy", count=easy),
                LevelBucket(label="Medium", count=medium),
                LevelBucket(label="Hard", count=hard),
                LevelBucket(label="Very Hard", count=very_hard),
            ],
            needs_help_ids=needs_ids,
        ))
    return points


def session_progression(session_id: str, buckets: int = 12) -> SessionProgression | None:
    record = next((r for r in _DEMO_SESSIONS if r[0] == session_id), None)
    if record is None:
        return None
    meta = _saved_session(record)
    flagged = record[5]
    students = record[4]

    # Each session has a slightly different shape — Monday went well, Thursday
    # had a stubborn group, Friday was a quick clean lab.
    profiles = {
        "demo-mon-1400": dict(start_inc=0.55, end_inc=0.32, start_needs=5, end_needs=flagged,
                              start_strug=4, end_strug=2),
        "demo-thu-1000": dict(start_inc=0.62, end_inc=0.41, start_needs=6, end_needs=flagged,
                              start_strug=5, end_strug=3),
        "demo-fri-1300": dict(start_inc=0.48, end_inc=0.22, start_needs=4, end_needs=flagged,
                              start_strug=3, end_strug=1),
    }
    profile = profiles.get(session_id, profiles["demo-mon-1400"])

    points = _progression_curve(
        buckets,
        total_students=students,
        flagged_at_end=flagged,
        **profile,
    )
    bucket_minutes = round(90.0 / max(buckets, 1), 2)
    return SessionProgression(session=meta, bucket_minutes=bucket_minutes, points=points)
