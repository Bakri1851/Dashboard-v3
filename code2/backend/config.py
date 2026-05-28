# config.py — All tunable parameters for the dashboard

# --- API Configuration ---
API_URL: str = "http://sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php"
API_TIMEOUT: int = 30          # seconds
CACHE_TTL: int = 60            # seconds

# --- Data Cleaning ---
EXCLUDED_MODULES: list[str] = ["24COB231", "24WSC701"]
EXCLUDED_MODULES: list[str] = ["AI_TEST", "24COB231", "24WSC701"]

# --- OpenAI Configuration ---
OPENAI_MODEL: str = "gpt-4o"  # upgraded from gpt-4o-mini 2026-05-26 after re-label experiment showed +0.18 Spearman ρ gain on difficulty v2 training
OPENAI_BATCH_SIZE: int = 20       # max (question, answer) pairs per API call — smaller batches parse more reliably
SCORING_PER_RUN_CAP: int = 500    # max new pairs scored per request; rest fall back to 0.5 and get scored on subsequent calls (keeps UI responsive on cold-start)
# Master switch for OpenAI incorrectness scoring. When False,
# compute_incorrectness_column returns 0.5 for every row without hitting the
# API and the leaderboards diverge from the canonical code/ Streamlit dashboard
# (which does score feedback). With scoring on, the first /struggle request
# blocks while SCORING_PER_RUN_CAP feedbacks are scored; remaining ones
# surface as 0.5 until later polls catch up, so the cache warms progressively
# instead of stalling the UI for minutes on a cold cache.
OPENAI_SCORING_ENABLED: bool = True

# --- Student Struggle Score Weights ---
STRUGGLE_WEIGHT_N: float = 0.10   # submission count (min-max normalised)
STRUGGLE_WEIGHT_T: float = 0.10   # time active (min-max normalised)
STRUGGLE_WEIGHT_I: float = 0.20   # mean incorrectness
STRUGGLE_WEIGHT_R: float = 0.10   # retry rate
STRUGGLE_WEIGHT_A: float = 0.38   # weighted recent incorrectness (exponential time decay)
STRUGGLE_WEIGHT_D: float = 0.05   # improvement trajectory slope (min-max normalised)
STRUGGLE_WEIGHT_REP: float = 0.07 # answer repetition rate (exact-match repeats / total)
# Sum: 0.10+0.10+0.20+0.10+0.38+0.05+0.07 = 1.00

# --- Recent Incorrectness (A_raw) ---
RECENT_SUBMISSION_COUNT: int = 5
# RECENT_WEIGHTS superseded by exponential time decay — kept for reference only.
# RECENT_WEIGHTS: list[float] = [0.35, 0.25, 0.20, 0.12, 0.08]
DECAY_HALFLIFE_SECONDS: int = 1800  # 30-min half-life; submission 30 min ago gets w=0.5 relative to now

# --- Bayesian Shrinkage ---
SHRINKAGE_K: int = 5  # students with n >> K are unaffected; n << K pulled toward class mean

# --- Student Struggle Thresholds: (low, high, label, color) ---
# Constrained CV-trained 2026-05-27 via scripts/experiments/threshold_search_v2composite.py
# on the DEPLOYED v2-OLS composite score (clip(sum(v2_weights * signals), 0, 1)).
# κ +0.038 → +0.384 (GroupKFold(5), n=1306; every band >= 10% of [0,1]).
# Recalibration: the earlier (0.315, 0.505, 0.605) were fit on the v1 baseline
# composite, but the deployed system feeds the compressed v2-OLS composite
# (~[0, 0.62], mean 0.24) through these thresholds — the old cuts put ~99% below
# "Needs Help". New band split on this cohort: 31/14/15/40%.
# Source: data/eval/experiments/threshold_search_v2composite.json.
STRUGGLE_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.000, 0.102, "On Track",     "#10a15d"),
    (0.102, 0.203, "Minor Issues", "#ffcc00"),
    (0.203, 0.326, "Struggling",   "#ff6600"),
    (0.326, 1.000, "Needs Help",   "#ff2d55"),
]

# --- Question Difficulty Score Weights ---
DIFFICULTY_WEIGHT_C: float = 0.28   # incorrect rate (raw ratio)
DIFFICULTY_WEIGHT_T: float = 0.12   # avg time per student (min-max normalised, all students)
DIFFICULTY_WEIGHT_A: float = 0.20   # avg attempts per student (min-max normalised)
DIFFICULTY_WEIGHT_F: float = 0.20   # avg incorrectness score
DIFFICULTY_WEIGHT_P: float = 0.20   # first-attempt failure rate

# --- Question Difficulty Thresholds: (low, high, label, color) ---
# Constrained CV-trained 2026-05-27 via scripts/experiments/threshold_search_v2composite.py
# on the DEPLOYED v2-OLS difficulty composite (clip(sum(v2_weights * signals), 0, 1)).
# κ +0.225 → +0.387 (LeaveOneOut, n=72; every band >= 10% of [0,1]).
# Recalibration over the earlier (0.363, 0.463, 0.587), which were fit on the v1
# baseline composite. Cohort skews hard (67% "Very Hard"); bands kept for
# future-cohort generality. Source: data/eval/experiments/threshold_search_v2composite.json.
DIFFICULTY_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.000, 0.288, "Easy",      "#00ff88"),
    (0.288, 0.388, "Medium",    "#ffcc00"),
    (0.388, 0.531, "Hard",      "#ff6600"),
    (0.531, 1.000, "Very Hard", "#ff2d55"),
]

# --- Darker bar fills for leaderboards (white text readability) ---
LEADERBOARD_BAR_COLORS: dict[str, str] = {
    "Needs Help":   "#991b36",
    "Struggling":   "#994400",
    "Minor Issues": "#806600",
    "On Track":     "#0d6b3a",
    "Very Hard":    "#991b36",
    "Hard":         "#994400",
    "Medium":       "#806600",
    "Easy":         "#0d6b3a",
}

# --- Temporal Smoothing ---
SMOOTHING_ALPHA: float = 0.3
SMOOTHING_ENABLED: bool = True    # EMA across refresh cycles; alpha=0.3

# --- Incorrectness Threshold for "correct" ---
CORRECT_THRESHOLD: float = 0.5   # incorrectness < this = "correct"

# --- UI Limits ---
LEADERBOARD_MAX_ITEMS: int = 15
QUESTION_LABEL_MAX_LEN: int = 35
STUDENT_DETAIL_TOP_QUESTIONS: int = 10
QUESTION_DETAIL_TOP_STUDENTS: int = 15
RECENT_SUBMISSIONS_LIMIT: int = 10
SAMPLE_ANSWERS_LIMIT: int = 10
HISTOGRAM_BINS: int = 20

# --- Mistake Clustering ---
CLUSTER_MIN_WRONG: int = 3             # min incorrect submissions needed to attempt clustering
CLUSTER_MAX_K: int = 5                 # max clusters to evaluate via silhouette
CLUSTER_MAX_EXAMPLES: int = 3         # representative answers shown per cluster
CLUSTER_EXAMPLE_MAX_CHARS: int = 300  # truncate long answers in UI
DATA_ANALYSIS_TOP_QUESTIONS: int = 10
DATA_ANALYSIS_TOP_USERS: int = 20

# --- Auto-Refresh ---
AUTO_REFRESH_DEFAULT: bool = True
AUTO_REFRESH_INTERVAL_DEFAULT: int = 60  # seconds
AUTO_REFRESH_OPTIONS: list[int] = [5, 10, 15, 30, 60, 120,300]

# --- Sound Effects ---
SOUNDS_ENABLED_DEFAULT: bool = True

# --- Saved Session Persistence ---
SAVED_SESSIONS_VERSION: int = 1

# --- Lab Session State ---
LAB_CODE_LENGTH: int = 6

# --- Color Palette ---
COLORS: dict[str, str] = {
    "green":    "#00ff88",
    "yellow":   "#ffcc00",
    "orange":   "#ff6600",
    "red":      "#ff2d55",
    "cyan":     "#00f5ff",
    "magenta":  "#ff00ff",
    "purple":   "#b300ff",
    "blue":     "#0080ff",
    "dark_bg":  "#0a0e1a",
    "panel_bg": "#0d1526",
    "mid_bg":   "#0a1628",
    "card_bg":  "rgba(13, 21, 38, 0.9)",
    "text":     "#a0d4e4",
    "text_dim": "#4a7a8a",
}

# --- Font Configuration ---
FONT_HEADING: str = "Orbitron"
FONT_BODY: str = "Share Tech Mono"

# --- Phase 1: Measurement Confidence ---
MEASUREMENT_CONFIDENCE_MIN_LENGTH: int = 20
MEASUREMENT_CONFIDENCE_BASE: float = 0.7

# --- Phase 2: IRT Difficulty ---
IRT_MIN_ATTEMPTS_PER_QUESTION: int = 2
IRT_MIN_ATTEMPTS_PER_STUDENT: int = 2
IRT_MAX_ITER: int = 100
IRT_DIFFICULTY_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.00, 0.35, "Easy",      "#00ff88"),
    (0.35, 0.50, "Medium",    "#ffcc00"),
    (0.50, 0.75, "Hard",      "#ff6600"),
    (0.75, 1.00, "Very Hard", "#ff2d55"),
]

# --- Phase 3: BKT Mastery Tracking ---
BKT_P_INIT: float = 0.3       # P(L_0): prior probability student knows skill
BKT_P_LEARN: float = 0.1      # P(T):   probability of learning per opportunity
BKT_P_GUESS: float = 0.2      # P(G):   probability of guessing correctly
BKT_P_SLIP: float = 0.1       # P(S):   probability of slipping (wrong despite knowing)
BKT_MASTERY_THRESHOLD: float = 0.95  # P(L) above this = "mastered"

# BKT parameter fitting (MLE via forward algorithm, L-BFGS-B)
BKT_FIT_MIN_OBSERVATIONS: int = 50  # refuse to fit on fewer attempts than this
BKT_FIT_MAX_ITER: int = 200          # matches IRT_MAX_ITER spirit

# --- Phase 4: Improved Struggle Model ---
IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL: float = 0.45
IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP: float = 0.30
IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ: float = 0.25

# --- Phase 5: V2 optimised weights and hyperparams (data-driven refinements) ---
# These point to JSON files written by scripts/optimise_v2_weights.py and
# scripts/optimise_hyperparams.py. The trained v2 weights + Optuna-tuned
# hyperparams are loaded unconditionally as the deployed default (composite
# weights via cache.py, the scalar hyperparams via runtime_config). There is
# no runtime v1/v2 selector. The hand-set v1 weights above are retained as
# constants for the offline evaluation comparison only; a missing or malformed
# v2 JSON logs a warning and falls back to those v1 constants.
from . import paths as _paths
STRUGGLE_WEIGHTS_V2_PATH = _paths.DATA_DIR / "eval" / "optimised_struggle_weights_v2.json"
DIFFICULTY_WEIGHTS_V2_PATH = _paths.DATA_DIR / "eval" / "optimised_difficulty_weights_v2.json"
IMPROVED_WEIGHTS_V2_PATH = _paths.DATA_DIR / "eval" / "optimised_improved_weights_v2.json"
OPTIMISED_HYPERPARAMS_V2_PATH = _paths.DATA_DIR / "eval" / "optimised_hyperparams_v2.json"

# Promote SHRINKAGE_K to a runtime-tunable. The hyperparams v2 toggle can
# override it without a code change; default stays at the v1 value.
SHRINKAGE_K_DEFAULT: int = SHRINKAGE_K

# --- Phase 9: RAG Suggested Feedback ---
RAG_ENABLED_DEFAULT: bool = True
RAG_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"   # sentence-transformers, local, no API cost
RAG_SUGGESTION_MAX_RESULTS: int = 5              # top-k chunks retrieved per query
RAG_MIN_SUBMISSIONS: int = 2                     # min student submissions before RAG is attempted

# RAG corpus sampling: keep the embedding corpus small enough to build in
# tens of seconds on CPU. The shared `submissions` ChromaDB collection holds
# a stratified per-ISO-week sample instead of the full dataframe. Set
# RAG_SAMPLE_PER_WEEK = 0 to disable sampling and embed the entire dataset.
RAG_SAMPLE_PER_WEEK: int = 150
RAG_SAMPLE_SEED: int = 42


# --- Weight-sum invariants (import-time sanity checks) ---
_STRUGGLE_WEIGHT_SUM = (
    STRUGGLE_WEIGHT_N + STRUGGLE_WEIGHT_T + STRUGGLE_WEIGHT_I
    + STRUGGLE_WEIGHT_R + STRUGGLE_WEIGHT_A + STRUGGLE_WEIGHT_D
    + STRUGGLE_WEIGHT_REP
)
assert abs(_STRUGGLE_WEIGHT_SUM - 1.0) < 1e-9, (
    f"STRUGGLE_WEIGHT_* must sum to 1.0, got {_STRUGGLE_WEIGHT_SUM}"
)

_DIFFICULTY_WEIGHT_SUM = (
    DIFFICULTY_WEIGHT_C + DIFFICULTY_WEIGHT_T + DIFFICULTY_WEIGHT_A
    + DIFFICULTY_WEIGHT_F + DIFFICULTY_WEIGHT_P
)
assert abs(_DIFFICULTY_WEIGHT_SUM - 1.0) < 1e-9, (
    f"DIFFICULTY_WEIGHT_* must sum to 1.0, got {_DIFFICULTY_WEIGHT_SUM}"
)

_IMPROVED_STRUGGLE_WEIGHT_SUM = (
    IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL
    + IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP
    + IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ
)
assert abs(_IMPROVED_STRUGGLE_WEIGHT_SUM - 1.0) < 1e-9, (
    f"IMPROVED_STRUGGLE_WEIGHT_* must sum to 1.0, got {_IMPROVED_STRUGGLE_WEIGHT_SUM}"
)
