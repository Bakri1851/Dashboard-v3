# config.py — All tunable parameters for the dashboard

# --- API Configuration ---
API_URL: str = "http://sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php"
API_TIMEOUT: int = 30          # seconds
CACHE_TTL: int = 10            # seconds

# --- Data Cleaning ---
EXCLUDED_MODULES: list[str] = ["AI_TEST", "24COB231", "24WSC701"]
MODULE_RENAME_MAP: dict[str, str] = {"25COA504": "25COP504"}

# --- OpenAI Configuration ---
OPENAI_MODEL: str = "gpt-4o-mini"
OPENAI_BATCH_SIZE: int = 50       # max feedback items per API call

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
STRUGGLE_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.00, 0.20, "On Track",     "#00ff88"),
    (0.20, 0.35, "Minor Issues", "#ffcc00"),
    (0.35, 0.50, "Struggling",   "#ff6600"),
    (0.50, 1.00, "Needs Help",   "#ff2d55"),
]

# --- Question Difficulty Score Weights ---
DIFFICULTY_WEIGHT_C: float = 0.28   # incorrect rate (raw ratio)
DIFFICULTY_WEIGHT_T: float = 0.12   # avg time per student (min-max normalised, all students)
DIFFICULTY_WEIGHT_A: float = 0.20   # avg attempts per student (min-max normalised)
DIFFICULTY_WEIGHT_F: float = 0.20   # avg incorrectness score
DIFFICULTY_WEIGHT_P: float = 0.20   # first-attempt failure rate

# --- Question Difficulty Thresholds: (low, high, label, color) ---
DIFFICULTY_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.00, 0.35, "Easy",      "#00ff88"),
    (0.35, 0.50, "Medium",    "#ffcc00"),
    (0.50, 0.75, "Hard",      "#ff6600"),
    (0.75, 1.00, "Very Hard", "#ff2d55"),
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
SMOOTHING_ENABLED: bool = False   # infrastructure only — not activated

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
AUTO_REFRESH_INTERVAL_DEFAULT: int = 300  # seconds
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

# --- Phase 4: Improved Struggle Model ---
IMPROVED_STRUGGLE_WEIGHT_BEHAVIORAL: float = 0.45
IMPROVED_STRUGGLE_WEIGHT_MASTERY_GAP: float = 0.30
IMPROVED_STRUGGLE_WEIGHT_DIFFICULTY_ADJ: float = 0.25
