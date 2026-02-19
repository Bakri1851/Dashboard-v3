# config.py — All tunable parameters for the dashboard

# --- API Configuration ---
API_URL: str = "http://sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php"
API_TIMEOUT: int = 30          # seconds
CACHE_TTL: int = 10            # seconds

# --- Data Cleaning ---
EXCLUDED_MODULES: list[str] = ["AI_TEST", "24COB231", "24WSC701"]
MODULE_RENAME_MAP: dict[str, str] = {"25COA504": "25COP504"}

# --- Incorrectness Estimation Keywords ---
POSITIVE_KEYWORDS: list[str] = [
    "correct", "right", "good", "excellent", "perfect",
    "well done", "great", "yes", "exactly", "accurate",
]
NEGATIVE_KEYWORDS: list[str] = [
    "incorrect", "wrong", "error", "mistake", "try again",
    "not quite", "reconsider", "check", "review", "missing",
    "incomplete", "no",
]
PARTIAL_KEYWORDS: list[str] = [
    "partially", "almost", "close", "nearly", "but", "however",
]

# --- Incorrectness Scores ---
INCORRECTNESS_EMPTY: float = 0.5
INCORRECTNESS_ONLY_POSITIVE: float = 0.1
INCORRECTNESS_ONLY_NEGATIVE: float = 0.9
INCORRECTNESS_PARTIAL: float = 0.5
INCORRECTNESS_MORE_POSITIVE: float = 0.3
INCORRECTNESS_MORE_NEGATIVE: float = 0.7
INCORRECTNESS_DEFAULT: float = 0.5

# --- Student Struggle Score Weights ---
STRUGGLE_WEIGHT_N: float = 0.10   # submission count (min-max → collapses; minimal)
STRUGGLE_WEIGHT_T: float = 0.10   # time active      (min-max → collapses; halved)
STRUGGLE_WEIGHT_E: float = 0.25   # error rate       (raw ratio → stable; elevated)
STRUGGLE_WEIGHT_F: float = 0.15   # feedback rate    (raw ratio → stable; reduced)
STRUGGLE_WEIGHT_A: float = 0.45   # recent incorrectness (absolute → most sensitive; elevated)

# --- Recent Incorrectness (A_raw) ---
RECENT_SUBMISSION_COUNT: int = 5
RECENT_WEIGHTS: list[float] = [0.35, 0.25, 0.20, 0.12, 0.08]

# --- Student Struggle Thresholds: (low, high, label, color) ---
STRUGGLE_THRESHOLDS: list[tuple[float, float, str, str]] = [
    (0.00, 0.20, "On Track",     "#00ff88"),
    (0.20, 0.35, "Minor Issues", "#ffcc00"),
    (0.35, 0.50, "Struggling",   "#ff6600"),
    (0.50, 1.00, "Needs Help",   "#ff2d55"),
]

# --- Question Difficulty Score Weights ---
DIFFICULTY_WEIGHT_C: float = 0.35   # incorrect rate       (raw ratio → stable; elevated)
DIFFICULTY_WEIGHT_T: float = 0.15   # avg time per student (min-max → collapses; halved)
DIFFICULTY_WEIGHT_A: float = 0.25   # avg attempts         (min-max → collapses; reduced)
DIFFICULTY_WEIGHT_F: float = 0.25   # avg incorrectness    (raw mean → stable; elevated)

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
DATA_ANALYSIS_TOP_QUESTIONS: int = 10
DATA_ANALYSIS_TOP_USERS: int = 20

# --- Auto-Refresh ---
AUTO_REFRESH_DEFAULT: bool = True
AUTO_REFRESH_INTERVAL_DEFAULT: int = 60  # seconds
AUTO_REFRESH_OPTIONS: list[int] = [5, 10, 15, 30, 60]

# --- Saved Session Persistence ---
SAVED_SESSIONS_FILE: str = "saved_sessions.json"
SAVED_SESSIONS_VERSION: int = 1

# --- Lab Session State ---
LAB_SESSION_FILE: str = "lab_session.json"
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
