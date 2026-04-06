# Ch3 – Design and Modelling

Thesis chapter covering system architecture, data endpoint, mathematical models, and UI design.

Related: [[Thesis Overview]], [[Report Sync]], [[Architecture]], [[Analytics Engine]], [[Student Struggle Logic]], [[Question Difficulty Logic]], [[IRT Difficulty Logic]]

**Source file:** `main sections/design and architecture.tex`
**Status:** Draft — architecture broadly correct, formulas outdated, Figma mockups need replacing

---

## Current contents

### 3.1 System Architecture (mostly accurate)

Three-layer design:
1. **Data Generation Layer** — student interactions at endpoint
2. **Data Ingestion and Processing Layer** — periodic retrieval, parsing, normalization, metric computation
3. **Decision and Action Layer** — analytics presented to instructor for decision-making

Includes architecture diagram (Fig 6).

**Mismatches with V2:**
- Mentions event-driven pipeline "currently under exploration" — still interval-based in V2
- Does not mention the `models/` package (IRT, BKT, improved struggle, measurement confidence)
- Does not mention saved sessions, academic calendar, or sound system

### 3.2 Data Endpoint (accurate)

Describes JSON format with embedded XML payload. Session-based organization. Derived metrics: attempts per question, time between attempts, AI-based correctness, feedback frequency.

This section is largely version-independent and matches the V2 implementation in `data_loader.py`.

### 3.3 Mathematical Models

#### 3.3.1 Student Struggle — FORMULA MISMATCH

**Thesis formula (5 components):**
`S_raw = alpha*n_hat + beta*t_hat + gamma*e_hat + delta*f_hat + eta*A_raw`

Components: submission count, time active, incorrect submissions, feedback requests, recent incorrectness.

**Actual V2 formula (7 components):**
`S = 0.10*n_hat + 0.10*t_hat + 0.20*i_hat + 0.10*r_hat + 0.38*A_raw + 0.05*d_hat + 0.07*rep_hat`

**Differences:**
| Thesis | Code | Notes |
|--------|------|-------|
| e_hat (incorrect submissions / total) | i_hat (mean incorrectness) | Different metric — thesis uses count ratio, code uses OpenAI score mean |
| f_hat (feedback requests / total) | — | Dropped in V2; replaced by other signals |
| — | r_hat (retry rate) | Added in V2: repeated attempts on same question |
| — | d_hat (trajectory slope) | Added in V2: trend of incorrectness over time |
| — | rep_hat (exact-answer repetition) | Added in V2: submitting identical answers repeatedly |

**Other differences:**
- Thesis proposes temporal smoothing via exponential smoothing — V2 has a stub (`SMOOTHING_ENABLED = False`) but does not use it
- Thesis does not mention Bayesian shrinkage — V2 applies `w_n = n / (n + 5)` to pull low-data scores toward class mean
- Thesis does not mention score clipping to [0, 1]

#### 3.3.2 Question Difficulty — FORMULA MISMATCH

**Thesis formula (4 components):**
`D_raw = alpha*c_tilde + beta*t_tilde + gamma*a_tilde + delta*f_tilde`

**Actual V2 formula (5 components):**
`D = 0.28*c_tilde + 0.12*t_tilde + 0.20*a_tilde + 0.20*f_tilde + 0.20*p_tilde`

**Missing from thesis:** `p_tilde` — first-attempt failure rate (fraction of students who got it wrong on first try).

#### 3.3.3 Collaborative Filtering (needs update)

Thesis describes CF as an alternative that "is still going to be implemented alongside the parameter-based approach as a secondary indicator."

**V2 reality:** CF IS implemented and enabled by default. Uses 5 normalized behavioral features, cosine similarity, k=3 nearest neighbours, threshold-based elevation detection. Toggleable in Settings. Shows diagnostic panel in In Class View when enabled.

Comparison table in thesis is accurate structurally but the "justification for current approach" framing needs updating — CF is no longer just proposed, it's live.

### 3.4 UI Design

#### 3.4.1 Design Principles (mostly accurate)
- Student struggle and question difficulty as distinct signals — matches V2
- Lab assistant allocation — implemented in V2
- Avoiding raw data exposure — achieved via normalization
- Supporting decision-making — matches V2 leaderboard-first design

#### 3.4.2 Instructor Dashboard — FIGMA MOCKUPS NEED REPLACING

Three Figma mockups (Figs 8-10):
- Fig 8: Student struggle list + question difficulty list
- Fig 9: Lab assistant allocation view
- Fig 10: Assistant leaderboard

All explicitly labeled as "conceptual design rather than a fully implemented system."

**V2 reality:** All three concepts are implemented in the actual dashboard, but the UI looks different from Figma mockups. Screenshots of the real dashboard should replace these.

#### 3.4.3 Visual Encoding (accurate)
Threshold tables for struggle (None/Low/Medium/High with Green/Yellow/Orange/Red) and difficulty (Easy/Medium/Hard/Very Hard) match V2 implementation in `config.py`.

**Note:** V2 uses different label names — "On Track" instead of "None", "Minor Issues" instead of "Low", "Needs Help" instead of "High" for struggle.

---

## Missing from design chapter entirely

These V2 features have no design coverage in the thesis:

- **IRT difficulty model** — Rasch 1PL via joint MLE (see [[IRT Difficulty Logic]])
- **BKT mastery tracking** — HMM with 4 parameters (see [[BKT Mastery Logic]])
- **Improved struggle model** — 3-component: behavioral + mastery gap + difficulty-adjusted (see [[Improved Struggle Logic]])
- **Measurement confidence** — confidence scoring for incorrectness estimates
- **Mistake clustering** — TF-IDF + K-means + OpenAI labeling
- **Saved sessions** — CRUD, retroactive save, academic period filtering
- **Data analysis views** — 6 analysis charts
- **Lab assistant system** — join/assign/self-claim/mark-helped flow
- **Settings page** — model toggles, CF threshold, auto-refresh config
- **Sound effects** — event-triggered browser audio
- **Academic calendar** — period labeling for submissions

---

## Rewrite items

- [ ] Update struggle formula to 7 components with actual weights
- [ ] Add description of Bayesian shrinkage
- [ ] Update difficulty formula to 5 components with actual weights
- [ ] Add `p_tilde` (first-attempt failure rate) description
- [ ] Update CF section — change from "will be implemented" to "is implemented"
- [ ] Replace 3 Figma mockups (Figs 8-10) with actual dashboard screenshots
- [ ] Update threshold label names (On Track/Minor Issues/Struggling/Needs Help)
- [ ] Add design sections for IRT, BKT, improved struggle, mistake clustering
- [ ] Address or remove temporal smoothing claims (not active in V2)
- [ ] Add lab assistant system design (session code, file-locked state, assignment flow)
- [ ] Remove "event-driven pipeline currently under exploration" or clarify status

## Open questions

- Should the new models (IRT, BKT, improved struggle) go in Ch3 Design or Ch4 Implementation?
- Should the design chapter describe the final system or the design-then-implementation evolution?
- The temporal smoothing was designed but not implemented — mention it as a design decision that was deferred?
