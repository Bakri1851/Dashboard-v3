# Learning Analytics Dashboard — Product Requirements Document

## YOUR TASK

Build a real-time learning analytics dashboard from this PRD. The system must deliver all the functionality, scoring models, and visual design described below. You have full freedom in how you structure and implement the code, but the following constraints are non-negotiable:

### Constraints
- **Tech stack**: Python, Streamlit, Plotly, Pandas. The dashboard must be a Streamlit app with Plotly charts.
- **Mathematical models**: Implement the formulas in Section 4 exactly — same weights, same thresholds, same scoring logic. These are research-validated and must not be altered.
- **Visual design**: Match the sci-fi neon theme described in Section 5 — same colour palette, same fonts, same dark aesthetic.
- **Data source**: Fetch from the API endpoint described in Section 3. Support both JSON and XML response formats.

### Modularity Requirement
Build a well-structured, modular codebase. At minimum, separate concerns into:
- **Configuration** — all tunable parameters in one place (weights, thresholds, colours, API config)
- **Analytics engine** — scoring calculations, independent of UI
- **Data loading** — API fetching and parsing, independent of UI
- **UI theme** — styling/theming, reusable across components
- **UI components** — individual visual elements (cards, charts, leaderboards)
- **Views** — page-level layouts that compose components
- **App entry point** — routing, state management, sidebar controls

### Known Bugs to Fix
1. The formula info display should read threshold values dynamically from config, not hardcode them
2. Feedback request counting should count non-empty feedback entries in a single pass (not double-count via separate null and length checks)

---

## 1. Product Overview

### Problem
During university lab sessions, lecturers have no real-time visibility into which students are struggling or which questions are proving too difficult. They can only discover problems reactively — when students raise their hands or after marking.

### Solution
A live dashboard that continuously ingests student submission data from an existing learning platform, computes struggle and difficulty scores using weighted mathematical models, and displays ranked leaderboards that update automatically. Lecturers can identify at a glance who needs help and which questions need attention.

### Users
University lecturers and lab demonstrators running live coding/lab sessions with 20-200+ students.

### Key Outcomes
- Lecturer can see a ranked list of struggling students within seconds of starting a session
- Lecturer can see which questions are proving most difficult
- Lecturer can drill into any student or question for detailed analytics
- Dashboard updates automatically without manual refresh
- All scoring is transparent — formulas and weights are visible in the UI

---

## 2. Data Source

### API Endpoint
```
http://sccb2.sci-project.lboro.ac.uk/retrievalEndpoint.php
```
HTTP GET request. 30-second timeout. Cache responses for 10 seconds to avoid hammering the endpoint.

### Response Formats
The endpoint may return either JSON or XML. The system must auto-detect the format and handle both.

**JSON format**: Newline-delimited JSON objects. Each object represents a payload with fields: `module`, `question`, `session`, `user`, `timestamp`. May also contain an `xml` field with embedded XML holding individual submissions.

**Embedded XML structure within JSON**:
```xml
<submission timestamp="...">
  <srep>student answer text</srep>
  <feedback>
    <response>AI feedback text</response>
  </feedback>
</submission>
```
Each `<submission>` element becomes a separate data record.

**Pure XML format**:
```xml
<Payloads>
  <Payload>
    <module>...</module>
    <question>...</question>
    <session>...</session>
    <user>...</user>
    <submission>
      <srep>student answer</srep>
      <timestamp>...</timestamp>
      <feedback><response>AI feedback</response></feedback>
    </submission>
  </Payload>
</Payloads>
```

### Normalised Data Schema
Regardless of source format, all data should be normalised to records with these fields:

| Field | Description |
|-------|-------------|
| `module` | Course/module identifier (e.g., "25COP504") |
| `question` | Question ID or text |
| `timestamp` | When the submission occurred |
| `student_answer` | The student's submitted answer |
| `ai_feedback` | AI-generated feedback on the answer |
| `session` | Session identifier |
| `user` | Student user ID |

### Data Cleaning Rules
- **Exclude modules**: Remove `AI_TEST`, `24COB231`, `24WSC701`
- **Rename modules**: Map `25COA504` to `25COP504`
- **Parse timestamps**: Convert to datetime, discard records with unparseable timestamps

---

## 3. Scoring Models

These formulas are the core of the system. Implement them exactly.

### 3.1 Student Struggle Score

Measures how much a student is struggling during a session. Score range: [0, 1].

**Formula:**
```
S_raw(s) = 0.15 * n_hat + 0.20 * t_hat + 0.25 * e_hat + 0.20 * f_hat + 0.20 * A_raw
```

**Components:**

| Symbol | Weight | Definition |
|--------|--------|------------|
| `n_hat` | 0.15 | Submission count, min-max normalised across all students |
| `t_hat` | 0.20 | Time active (minutes from first to last submission), min-max normalised across all students. 0 if only one submission. |
| `e_hat` | 0.25 | Error rate = (submissions with incorrectness > 0.5) / total submissions |
| `f_hat` | 0.20 | Feedback rate = (submissions with non-empty AI feedback) / total submissions |
| `A_raw` | 0.20 | Weighted recent incorrectness (see below) |

**Min-max normalisation:**
```
x_hat = (x - x_min) / (x_max - x_min)
```
Returns 0 if all values are equal. Clamped to [0, 1].

**Recent Incorrectness (`A_raw`):**
Take the student's last 5 submissions (most recent first). For each, estimate an incorrectness score (see Section 3.3). Apply convex weights:
```
weights = [0.35, 0.25, 0.20, 0.12, 0.08]
A_raw = sum(weight_i * incorrectness_i)
```
If fewer than 5 submissions, pad with zeros and re-normalise the active weights to sum to 1.0.

**Level classification:**

| Level | Score Range | Label | Colour |
|-------|-------------|-------|--------|
| None | 0.00 - 0.35 | On Track | `#00ff88` |
| Low | 0.35 - 0.50 | Minor Issues | `#ffcc00` |
| Medium | 0.50 - 0.75 | Struggling | `#ff6600` |
| High | 0.75 - 1.00 | Needs Help | `#ff2d55` |

### 3.2 Question Difficulty Score

Measures how difficult a question is proving to be. Score range: [0, 1].

**Formula:**
```
D_raw(q) = 0.30 * c_tilde + 0.20 * t_tilde + 0.30 * a_tilde + 0.20 * f_tilde
```

**Components:**

| Symbol | Weight | Definition |
|--------|--------|------------|
| `c_tilde` | 0.30 | Incorrect rate = 1 - (correct attempts / total attempts). "Correct" = incorrectness < 0.5 |
| `t_tilde` | 0.20 | Average time per student (minutes from first to last submission on this question, averaged across students who made 2+ attempts), min-max normalised across all questions |
| `a_tilde` | 0.30 | Average attempts per student (total attempts / unique students), min-max normalised across all questions |
| `f_tilde` | 0.20 | Average incorrectness score across all attempts on this question |

**Level classification:**

| Level | Score Range | Label | Colour |
|-------|-------------|-------|--------|
| Easy | 0.00 - 0.35 | Easy | `#00ff88` |
| Medium | 0.35 - 0.50 | Medium | `#ffcc00` |
| Hard | 0.50 - 0.75 | Hard | `#ff6600` |
| Very Hard | 0.75 - 1.00 | Very Hard | `#ff2d55` |

### 3.3 Incorrectness Estimation from AI Feedback

A heuristic that estimates how incorrect a student's answer was based on the AI feedback text. Returns a score in [0, 1] where 0 = correct, 1 = completely incorrect.

**Keyword matching** (case-insensitive, substring):

| Category | Keywords |
|----------|----------|
| Positive (correct) | correct, right, good, excellent, perfect, well done, great, yes, exactly, accurate |
| Negative (incorrect) | incorrect, wrong, error, mistake, try again, not quite, reconsider, check, review, missing, incomplete, no |
| Partial | partially, almost, close, nearly, but, however |

**Scoring rules** (applied in order, return first match):
1. Empty/null feedback -> 0.5
2. Only positive matches -> 0.1
3. Only negative matches -> 0.9
4. Any partial matches -> 0.5
5. More positive than negative -> 0.3
6. More negative than positive -> 0.7
7. Otherwise -> 0.5

### 3.4 Temporal Smoothing (Infrastructure Only)

The following formula should be available but is NOT actively used in score calculation yet:
```
S_t = (1 - 0.3) * S_previous + 0.3 * S_raw
```
Build it so it can be enabled in future.

---

## 4. Visual Design

### 4.1 Theme: Sci-Fi Neon

The dashboard uses a dark, futuristic aesthetic inspired by sci-fi command centres. Think glowing neon on dark panels.

**Fonts:**
- **Orbitron** (Google Font, weights 400 & 700): All headings, titles, badges, buttons. Futuristic geometric sans-serif.
- **Share Tech Mono** (Google Font): All body text, data values, labels. Monospace technical font.

**Background:**
- Main app: dark gradient from `#0a0e1a` through `#0d1526` to `#0a1628`
- Sidebar: dark gradient from `#0d1526` to `#0a0e1a`, with a faint cyan right border
- Panels/cards: semi-transparent dark (`rgba(13, 21, 38, 0.9)`) with thin cyan borders

**Text colours:**
- Primary text: `#a0d4e4` (light cyan-grey)
- Dimmed text: `#4a7a8a` (muted blue-grey)
- Headings: `#00f5ff` (bright cyan), uppercase, wide letter-spacing

**Accent colours:**
- Primary accent: `#00f5ff` (cyan) — borders, highlights, interactive elements
- Success: `#00ff88` (neon green)
- Warning: `#ffcc00` (yellow), `#ff6600` (orange)
- Danger: `#ff2d55` (neon red)
- Secondary: `#ff00ff` (magenta), `#b300ff` (purple), `#0080ff` (blue)

**Interactive elements:**
- Buttons: cyan gradient backgrounds, uppercase Orbitron text, glow on hover
- Selectboxes: dark background, cyan border
- Cards: glow borders using box-shadow with cyan/level colours

**Charts (Plotly):**
- Dark transparent backgrounds matching the app theme
- Cyan grid lines (very faint), cyan axis lines
- Text in Share Tech Mono, `#a0d4e4`
- Legend with dark background and cyan border

### 4.2 Colour System

The 4-level severity scale is used consistently throughout:

| Severity | Struggle Label | Difficulty Label | Colour |
|----------|---------------|------------------|--------|
| None/Easy | On Track | Easy | `#00ff88` (green) |
| Low/Medium | Minor Issues | Medium | `#ffcc00` (yellow) |
| Medium/Hard | Struggling | Hard | `#ff6600` (orange) |
| High/Very Hard | Needs Help | Very Hard | `#ff2d55` (red) |

Full palette:
```
green: #00ff88    yellow: #ffcc00    orange: #ff6600    red: #ff2d55
cyan: #00f5ff     magenta: #ff00ff   purple: #b300ff    blue: #0080ff
dark_bg: #0a0e1a  panel_bg: #0d1526  text: #a0d4e4      text_dim: #4a7a8a
```

---

## 5. Features & Requirements

### 5.1 Dashboard Header

**What the user sees:** A prominent centered title "LEARNING ANALYTICS DASHBOARD" with a gradient colour effect (cyan to green to cyan), and a subtitle "REAL-TIME STUDENT STRUGGLE & QUESTION DIFFICULTY TRACKING" in dim text. Separated from content below by a faint line.

---

### 5.2 Summary Metrics

**What the user sees:** 4 metric cards in a row showing student counts by struggle level:

| Card | Label | Colour |
|------|-------|--------|
| 1 | NEEDS HELP | Red |
| 2 | STRUGGLING | Orange |
| 3 | MINOR ISSUES | Yellow |
| 4 | ON TRACK | Green |

Each card displays a large count number in its level colour, with the label below in dim text. Cards have dark backgrounds with coloured borders.

---

### 5.3 Student Struggle Leaderboard

**What the user sees:** A horizontal bar chart ranking students by struggle score (highest at top). Each bar is coloured by the student's struggle level. The student's name appears inside the bar, and the exact score appears to the right.

**Behaviour:**
- Displays up to 15 students
- 4 filter checkboxes (all on by default) let the user show/hide levels: Needs Help, Struggling, Minor Issues, On Track
- **Clicking a bar** navigates to that student's detail view (drill-down)
- Bar height adjusts dynamically based on the number of students shown

**Acceptance criteria:**
- Bars are colour-coded by struggle level
- Score annotations show 3 decimal places
- Click interaction navigates to student drill-down

---

### 5.4 Question Difficulty Leaderboard

**What the user sees:** Same layout as the student leaderboard, but ranking questions by difficulty score. Long question names are truncated with "..." (max ~35 characters shown, full name on hover).

**Behaviour:**
- Displays up to 15 questions
- 4 filter checkboxes: Very Hard, Hard, Medium, Easy
- **Clicking a bar** navigates to that question's detail view
- Otherwise identical interaction pattern to student leaderboard

---

### 5.5 Score Distributions

**What the user sees:** Two side-by-side histograms:
- Left: Student struggle score distribution (20 bins, cyan colour)
- Right: Question difficulty score distribution (20 bins, magenta colour)

---

### 5.6 Formula Info Panel

**What the user sees:** An expandable/collapsible section showing the mathematical formulas used for scoring. Two columns:
- Left: Student Struggle Score formula, current weights, threshold ranges
- Right: Question Difficulty Score formula, current weights, threshold ranges

**Important:** Threshold values must be read from configuration, not hardcoded.

---

### 5.7 Student Drill-Down View

Triggered when a user clicks a student bar in the leaderboard.

**What the user sees:**
1. **Back button** — returns to the main leaderboard view
2. **Header card** — student name, struggle score, and level label, bordered in the level colour
3. **4 metric cards** — Total Submissions, Time Active (minutes), Error Rate (%), Recent Incorrectness
4. **Questions Attempted chart** — bar chart of the top 10 questions this student attempted, sorted by attempt count
5. **Questions table** — all questions with attempt counts and feedback request counts
6. **Submission Timeline** — hourly line chart showing when the student was active
7. **Recent Submissions table** — last 10 submissions (newest first) showing timestamp, question, answer, and AI feedback

---

### 5.8 Question Drill-Down View

Triggered when a user clicks a question bar in the leaderboard.

**What the user sees:**
1. **Back button** — returns to the main leaderboard view
2. **Header card** — question text (word-wrapping for long names), difficulty score, and level label
3. **4 metric cards** — Total Attempts, Unique Students, Avg Attempts/Student, Incorrect Rate (%)
4. **Students Who Attempted chart** — bar chart of top 15 students by attempt count
5. **Students table** — all students with attempt and feedback request counts
6. **Attempt Timeline** — hourly line chart showing attempt frequency over time
7. **Sample Answers table** — first 10 submissions showing student, timestamp, answer, and AI feedback

---

### 5.9 Data Analysis View

A secondary view (switchable via sidebar) with 5 analytical charts, selectable from a dropdown:

1. **Module Usage** — vertical bar chart of submission counts per module
2. **Top Questions** — horizontal bar chart of top 10 questions within a selected module
3. **User Activity** — vertical bar chart of top 20 most active users (with optional module filter)
4. **Activity Timeline** — line chart with hourly granularity showing submission volume over time, with a filled area glow effect underneath
5. **Students by Module** — vertical bar chart of unique student counts per module

Each chart uses the themed dark styling with appropriate accent colours from the palette.

---

### 5.10 Info Bar

**What the user sees:** A subtle summary bar near the top of the content area showing: current view name, total submissions count, unique student count, unique question count.

---

## 6. Navigation & Interaction

### 6.1 View Structure

The app has 4 views:

```
+-------------------+     +-------------------+
|  In Class View    | <-> |  Data Analysis    |
| (default)         |     |  (secondary)      |
+--------+----------+     +-------------------+
         |
    click student bar    click question bar
         |                       |
+--------v----------+   +-------v-----------+
| Student Detail    |   | Question Detail   |
| (drill-down)      |   | (drill-down)      |
+-------------------+   +-------------------+
         |                       |
    "Back" button          "Back" button
         |                       |
         +--------> In Class View <--------+
```

- **In Class View** and **Data Analysis** are switchable via a sidebar radio selector
- **Student Detail** and **Question Detail** are entered by clicking bars in the leaderboards
- Switching views via the sidebar radio clears any active drill-down selection

### 6.2 Sidebar Controls

From top to bottom:

1. **Lab Session**
   - "Start Lab Session" button (when no session active)
   - Shows "SESSION ACTIVE" with running timer (HH:MM:SS) when active
   - "End Session" button to stop
   - Starting/ending a session clears cached data

2. **Dashboard View** — radio toggle: "In Class View" | "Data Analysis"

3. **Auto-Refresh**
   - Toggle on/off (default: on)
   - Interval selector: 5, 10, 15, 30, 60 seconds (default: 10)
   - Shows last refresh timestamp
   - Manual "Refresh Now" button

4. **Module Filter** — dropdown to filter all data by module ("All Modules" default)

5. **Time Filter**
   - Toggle on/off (default: off)
   - Date range picker (defaults to today if data exists for today)
   - Start time and end time inputs
   - Shows filtered record count

### 6.3 Module Filtering

There are two levels of module filtering:
- **Global filter** (sidebar): applies to all views and all score calculations
- **In Class View filter** (main content area): further narrows data within the In Class View only, recalculating scores for that subset. Drill-down views use the global filter only, not this secondary filter.

### 6.4 Session Awareness

When a lab session is active, the `session_start` timestamp is passed to the scoring functions. They should internally filter data to only include submissions from the session start onwards. If the time filter is enabled instead, it takes precedence and session filtering is disabled.

---

## 7. Non-Functional Requirements

### 7.1 Performance
- Data caching: 10-second TTL to avoid excessive API calls
- Auto-refresh clears the cache before re-fetching
- Charts should render responsively at full container width

### 7.2 Error Handling
- If the API is unreachable, show an error message and stop (don't crash)
- Handle both JSON and XML gracefully with automatic format detection
- Fallback: try JSON first, then XML, then show a parse error

### 7.3 Dependencies
The app needs these Python packages (use latest compatible versions):
- `streamlit` — web framework
- `plotly` — interactive charts
- `pandas` — data manipulation
- `numpy` — numerical operations
- `requests` — HTTP client
- `streamlit-autorefresh` — auto-refresh component

Generate a `requirements.txt` with all necessary packages.

### 7.4 Entry Point
The app should be runnable with `streamlit run app.py`.
