"""Pydantic response schemas. Mirror of frontend src/types/api.ts."""
from __future__ import annotations

from pydantic import BaseModel, Field


# ----------------------------------------------------------------
# Shared primitives
# ----------------------------------------------------------------


class LevelBucket(BaseModel):
    label: str
    count: int


class ScoreComponent(BaseModel):
    """One row in the Student-detail score-components bar chart."""
    key: str
    label: str
    value: float
    weight: float


class StudentQuestionRow(BaseModel):
    """One row in the Student-detail 'Top questions attempted' table."""
    question: str
    attempts: int
    difficulty: str
    last_incorrectness: float | None = None


class StudentRecentRow(BaseModel):
    """One row in the Student-detail 'Recent submissions' table."""
    timestamp: str
    question: str
    answer: str
    incorrectness: float


class MistakeCluster(BaseModel):
    """One mistake cluster from `analytics.cluster_question_mistakes`."""
    label: str
    count: int
    percent_of_wrong: float
    example_answers: list[str]


class QuestionRecentAttempt(BaseModel):
    timestamp: str
    user: str
    answer: str
    incorrectness: float


class QuestionStudentRow(BaseModel):
    """Per-student summary for a single question — 'who struggled most here'."""
    id: str
    attempts: int
    mean_incorrectness: float
    struggle_level: str
    struggle_score: float


# ----------------------------------------------------------------
# /api/live
# ----------------------------------------------------------------


class LiveDataResponse(BaseModel):
    """Status heartbeat + hero stats for the InClassView header."""
    records: int
    last_updated: str
    unique_students: int
    unique_questions: int
    unique_modules: int
    mean_incorrectness: float
    struggle_buckets: list[LevelBucket]
    difficulty_buckets: list[LevelBucket]
    timeline_24h: list[int]
    error: str | None = None


# ----------------------------------------------------------------
# /api/struggle
# ----------------------------------------------------------------


class StudentStruggle(BaseModel):
    id: str
    level: str
    score: float
    submissions: int
    recent: float
    trend: float


# ----------------------------------------------------------------
# /api/difficulty
# ----------------------------------------------------------------


class QuestionDifficulty(BaseModel):
    id: str
    level: str
    score: float
    students: int
    avgAttempts: float
    module: str


# ----------------------------------------------------------------
# /api/student/{id}
# ----------------------------------------------------------------


class StudentDetail(BaseModel):
    id: str
    level: str
    score: float
    submissions: int
    recent: float
    trend: float
    mean_incorrectness: float
    time_active_min: float
    retry_rate: float
    components: list[ScoreComponent]
    trajectory: list[float] = Field(description="Recent incorrectness values (oldest → newest), up to 10")
    top_questions: list[StudentQuestionRow]
    recent_submissions: list[StudentRecentRow]


# ----------------------------------------------------------------
# /api/question/{id}
# ----------------------------------------------------------------


class QuestionDetail(BaseModel):
    id: str
    level: str
    score: float
    module: str
    students: int
    avg_attempts: float
    incorrect_rate: float
    first_fail_rate: float
    mistake_clusters: list[MistakeCluster]
    recent_attempts: list[QuestionRecentAttempt]
    top_strugglers: list[QuestionStudentRow] = Field(
        default_factory=list,
        description="Students sorted by mean incorrectness on this question (descending).",
    )


# ----------------------------------------------------------------
# /api/sessions
# ----------------------------------------------------------------


class SavedSession(BaseModel):
    id: str
    name: str
    start_time: str | None = None
    end_time: str | None = None
    duration_minutes: float | None = None
    students: int | None = None
    flagged: int | None = None
    module_filter: str | None = None


# ----------------------------------------------------------------
# /api/settings
# ----------------------------------------------------------------


class Thresholds(BaseModel):
    struggle: list[tuple[float, float, str, str]]
    difficulty: list[tuple[float, float, str, str]]


class StruggleWeights(BaseModel):
    n: float
    t: float
    i: float
    r: float
    a: float
    d: float
    rep: float


class DifficultyWeights(BaseModel):
    c: float
    t: float
    a: float
    f: float
    p: float


class BKTParameters(BaseModel):
    p_init: float
    p_learn: float
    p_guess: float
    p_slip: float
    mastery_threshold: float


class Settings(BaseModel):
    cache_ttl: int
    correct_threshold: float
    smoothing_alpha: float
    struggle_weights: StruggleWeights
    difficulty_weights: DifficultyWeights
    thresholds: Thresholds
    bkt: BKTParameters
    leaderboard_max_items: int


# ----------------------------------------------------------------
# /api/analysis
# ----------------------------------------------------------------


class ModuleBreakdown(BaseModel):
    module: str
    submissions: int
    unique_students: int


class AnalysisStats(BaseModel):
    total_records: int
    unique_students: int
    unique_questions: int
    modules: int
    peak_hour: int
    peak_hour_count: int
    avg_attempts_per_question: float
    avg_session_minutes: float
    module_breakdown: list[ModuleBreakdown]
    timeline_24h: list[int]


# ----------------------------------------------------------------
# /api/models/compare
# ----------------------------------------------------------------


class ModelRow(BaseModel):
    id: str
    level: str
    score: float


class ModelCompareResponse(BaseModel):
    baseline: list[ModelRow]
    improved: list[ModelRow]
    spearman_rho: float | None = Field(default=None, description="Rank correlation baseline vs improved")
    top10_overlap: float | None = Field(default=None, description="Fraction overlap in top-10 needs-help sets")


# ----------------------------------------------------------------
# /api/lab/*
# ----------------------------------------------------------------


class LabAssistant(BaseModel):
    id: str
    name: str
    joined_at: str
    assigned_student: str | None = None


class LabAssignment(BaseModel):
    student_id: str
    assistant_id: str
    status: str  # "helping" | "helped"
    assigned_at: str
    helped_at: str | None = None


class LabState(BaseModel):
    session_code: str | None
    session_active: bool
    session_start: str | None
    generated_at: str
    allow_self_allocation: bool
    lab_assistants: list[LabAssistant]
    assignments: list[LabAssignment]


class JoinRequest(BaseModel):
    code: str
    name: str


class JoinResult(BaseModel):
    ok: bool
    assistant_id: str | None = None
    error: str | None = None


class AssistantIdRequest(BaseModel):
    assistant_id: str


class StudentIdRequest(BaseModel):
    student_id: str


class AssignRequest(BaseModel):
    student_id: str
    assistant_id: str


class SetBoolRequest(BaseModel):
    enabled: bool


class SimpleResult(BaseModel):
    ok: bool
    error: str | None = None


# ----------------------------------------------------------------
# /api/rag/*
# ----------------------------------------------------------------


class RagSuggestions(BaseModel):
    audience: str  # "student" | "question"
    subject_id: str
    bullets: list[str]
    session_id: str | None = None
