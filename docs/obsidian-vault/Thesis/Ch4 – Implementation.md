# Ch4 – Implementation

Thesis chapter describing the system implementation. Currently describes V1 prototype only — needs near-complete rewrite for V2.

Related: [[Thesis Overview]], [[Report Sync]], [[Analytics Engine]], [[Instructor Dashboard]], [[Lab Assistant System]], [[UI System]], [[Data Loading and Session Persistence]]

**Source file:** `main sections/implementation.tex`
**Status:** Outdated (CRITICAL) — describes V1 prototype, not V2 full system

---

## Current contents

### 4.1 Scope of Implementation

States: "Version 1 was implemented to ensure end-to-end functionality worked as planned and to experiment with data visualisation rather than to deploy the whole system proposed."

Key V1-only language:
- "At this stage, the implementation focuses on fundamental indicators"
- "Version 1 therefore serves as the foundation for what the dashboard will eventually become"
- "proof of concept and testing of the data"

### 4.2 Technology Stack (partially accurate)

Table lists: PHP endpoint, JSON/XML format, Python processing, Streamlit dashboard, Plotly visualization. These are still correct for V2. But the "Purpose and Justification" column says "Version 1 has simple indicators for student struggle based on thresholds" — this is no longer true.

**Missing from stack:** OpenAI API (gpt-4o-mini), filelock, scikit-learn (TF-IDF, K-means, silhouette), scipy (L-BFGS-B for IRT).

### 4.3 Data Pipeline (accurate foundation, incomplete)

5-step pipeline described: retrieval, parsing, structuring, metric computation, dashboard update. This is correct as a high-level description but:
- Step 4 says "A naive metric approach was used, where thresholds are used for the attempt amount of a question" — V2 uses 7-signal struggle, 5-signal difficulty, OpenAI scoring
- No mention of incorrectness scoring via OpenAI
- No mention of normalization pipeline in `data_loader.py`
- No mention of academic period labeling

### 4.4 Dashboard Implementation (outdated)

Describes "a live visual overview of student activity" with "simple, predictable indicators." States: "Most advanced features, such as model-driven prioritisation, assistant allocation and smart device notifications, are to be implemented in the later iteration."

**All of these are now implemented except smart device notifications.**

---

## What V2 actually implements (for rewrite reference)

### Data Pipeline (see [[Data Pipeline]], [[Data Loading and Session Persistence]])
- `fetch_raw_data()` — GET to PHP endpoint, 10s cache TTL
- Auto-detect JSON vs XML format
- JSON parsing with embedded XML extraction (submissions, AI feedback)
- Module filtering (excludes AI_TEST, 24COB231, 24WSC701), module renaming
- Timestamp parsing, academic period labeling
- Saved session persistence (CRUD in `data/saved_sessions.json`)

### Analytics Engine (see [[Analytics Engine]], [[Student Struggle Logic]], [[Question Difficulty Logic]])
- **Incorrectness scoring** — OpenAI gpt-4o-mini, batch size 50, in-process cache
- **Student struggle** — 7 signals: n_hat, t_hat, i_hat, r_hat, A_raw, d_hat, rep_hat; Bayesian shrinkage; 4-level classification
- **Question difficulty** — 5 signals: c_tilde, t_tilde, a_tilde, f_tilde, p_tilde; 4-level classification
- **Collaborative filtering** — cosine similarity, k=3 nearest neighbours, elevation detection; toggleable
- **Mistake clustering** — TF-IDF + K-means (auto k via silhouette) + OpenAI cluster labeling

### Advanced Models (see [[IRT Difficulty Logic]], [[BKT Mastery Logic]], [[Improved Struggle Logic]])
- **IRT difficulty** — Rasch 1PL via joint MLE; alternative to baseline difficulty
- **BKT mastery** — HMM with P(L0)=0.3, P(T)=0.1, P(G)=0.2, P(S)=0.1; per-student per-question
- **Improved struggle** — 3-component: behavioral (0.45) + mastery gap (0.30) + difficulty-adjusted (0.25); graceful degradation
- **Measurement confidence** — length/extremity-based confidence for incorrectness estimates (computed but not displayed)

### Instructor Dashboard (see [[Instructor Dashboard]], [[Dashboard Pages and UI Flow]])
6 views:
1. **In Class** — summary cards, student/question leaderboards (max 15), score distributions, CF panel, formula info
2. **Student Detail** — drill-down with metrics, submission timeline, retry trend, similar students (CF)
3. **Question Detail** — drill-down with mistake clusters, student table, attempt timeline
4. **Data Analysis** — 6 chart types (module usage, top questions, user activity, activity timeline, academic week, students by module)
5. **Settings** — sound, auto-refresh, CF toggle/threshold, improved models toggle, model selectors
6. **Previous Sessions** — load/delete saved sessions, filter by academic period

### Lab Assistant System (see [[Lab Assistant System]])
- Shared state via `data/lab_session.json` with filelock
- Session code (6-char alphanumeric, excludes O/0/I/1)
- Assistant join/leave, instructor assign/unassign, self-claim (toggleable), mark-helped
- 4 assistant views: no session, join, waiting/unassigned, assigned with student card

### UI and UX (see [[UI System]])
- Sci-fi neon theme (Orbitron headings, Share Tech Mono body)
- Sound effects for navigation/refresh/selection/join/assignment
- Auto-refresh (configurable 5-300s)
- Desktop and mobile CSS variants

---

## Rewrite items

- [ ] Rewrite 4.1 Scope — describe V2 as the full implementation, acknowledge V1 as prototyping phase
- [ ] Update 4.2 Technology Stack table — add OpenAI API, filelock, scikit-learn, scipy
- [ ] Rewrite 4.3 Data Pipeline — describe full normalization, OpenAI scoring, academic period labeling
- [ ] Rewrite 4.4 Dashboard — describe all 6 instructor views and 4 assistant views
- [ ] Add new section: Analytics Implementation (struggle, difficulty, CF, clustering)
- [ ] Add new section: Advanced Models (IRT, BKT, improved struggle)
- [ ] Add new section: Lab Assistant System (session management, assignment flow, file-locked state)
- [ ] Add new section: Configuration and Extensibility (model toggles, config-driven thresholds)
- [ ] Remove all "to be implemented in later iteration" language
- [ ] Remove "proof of concept" framing
- [ ] Add code snippets to Appendix A referencing key implementation functions
- [ ] Add screenshots to Appendix B showing actual dashboard

## Open questions

- Should the chapter describe the V1→V2 evolution, or just describe V2 as the final system?
- How much implementation detail is appropriate? Code snippets in chapter vs appendix?
- Should the improved models be in Ch3 (design) or Ch4 (implementation)?
