# Ch4 – Implementation

Thesis chapter describing the system implementation. Currently describes V1 prototype only — needs near-complete rewrite for V2.

Related: [[Thesis Overview]], [[Report Sync]], [[Analytics Engine]], [[Instructor Dashboard]], [[Lab Assistant System]], [[UI System]], [[Data Loading and Session Persistence]]

**Source file:** `main sections/implementation.tex`
**Status:** Outdated (CRITICAL) — describes V1 prototype, not V2 full system

> **Sync note (2026-04-18):** "Current contents" below reflects the thesis state *before* the Phase 6 tex-skeleton additions (2026-04-12) that added 26 new subsection placeholders. For the current tex subsection tree and the active writing backlog, see [[Rewrite Queue#Phase 6 additions (2026-04-12)]] and the toolkit's Status panel §6 Source reconciliation.

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

### Instructor Dashboard (see [[Instructor Dashboard]], [[Lab App/Flows/Pages and UI Flow]])

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

## Rewrite items — mapped to skeleton subsection tree

### 4.1 – 4.2 Intro + Technology Stack

- [ ] Rewrite 4.1 intro — describe V2 as the full implementation, acknowledge V1 as prototyping phase only; remove "proof of concept" and "to be implemented" language
- [ ] Update 4.2 Technology Stack table — add OpenAI API (gpt-4o-mini), filelock, scikit-learn (TF-IDF/K-means/silhouette), scipy (L-BFGS-B for IRT)

### 4.x System Structure

- [ ] **Instructor System** — `app.py` → `instructor_app.main()`; session state init; deferred-actions pattern (`pending_*` flags applied before widgets); sidebar filters; routing to 6 views
- [ ] **Assistant System** — `lab_app.py` → `assistant_app`; URL `?aid=` identity persistence; 5s auto-refresh; 4 view states (no session / join / waiting / assigned)
- [ ] **Shared Runtime State** — `lab_session.json` managed by `lab_state.py`; filelock + atomic tmp-replace; fields stored (assistants dict, assignments dict, session code, session active flag)

### 4.x Data Pipeline

- [ ] **Endpoint Retrieval and Parsing** — `fetch_raw_data()` with `@st.cache_data(ttl=10)`; GET to PHP endpoint; JSON response with embedded XML; auto-detect JSON vs XML format
- [ ] **Data Normalisation and Structuring** — module filtering/renaming (excludes AI_TEST, 24COB231, 24WSC701); timestamp parsing; academic period labeling via `academic_calendar.py`; final DataFrame column schema

### 4.x Session Management

- [ ] **Live Session Lifecycle** — session start/end via sidebar; session code generation (6-char alphanumeric, excludes O/0/I/1); how pending flags defer state mutations until top of next run
- [ ] **Saved Session History and Restoration** — `data/saved_sessions.json` CRUD; save/load/delete via Previous Sessions view; filter by academic period

### 4.x Analytics Implementation

- [ ] **Incorrectness Scoring** — OpenAI gpt-4o-mini batch (size 50); `_incorrectness_cache` in-process dict avoids repeat API calls; fallback to 0.5 on API error; result is per-submission float in [0, 1]
- [ ] **Baseline Student Struggle Model** — 7 signals: n_hat (submission count), t_hat (time active), i_hat (mean incorrectness), r_hat (retry rate), A_raw (recent incorrectness), d_hat (trajectory slope), rep_hat (answer repetition); weights [0.10, 0.10, 0.20, 0.10, 0.38, 0.05, 0.07]; Bayesian shrinkage `w_n = n/(n+5)`; min-max normalisation; 4-level classification ("On Track / Minor Issues / Struggling / Needs Help")
- [ ] **Baseline Question Difficulty Model** — 5 signals: c_tilde (error rate), t_tilde (avg time), a_tilde (avg attempts), f_tilde (feedback rate), p_tilde (first-attempt failure rate); same 4-level classification
- [ ] **Collaborative Filtering** — cosine similarity on 5 normalised behavioral features; k=3 nearest neighbours; elevation detection (student score vs peer mean); toggleable via Settings; cold-start guard requires ≥k+1 active students
- [ ] **Mistake Clustering** — TF-IDF on raw student answer strings; K-means with auto-k via silhouette scoring; OpenAI labels each cluster; results displayed per-question in Question Detail view

### 4.x Advanced Model Implementation

- [ ] **Measurement Confidence** — length and extremity-based confidence weighting for incorrectness estimates; lives in `analytics.py`; computed but not yet surfaced in UI; mention as future display candidate
- [ ] **Item Response Theory (IRT) Difficulty** — `models/irt.py`; Rasch 1PL; joint MLE via scipy L-BFGS-B; estimates θ (student ability) and β (question difficulty); replaces baseline difficulty when "improved models" toggle enabled
- [ ] **Bayesian Knowledge Training (BKT) Mastery** — `models/bkt.py`; HMM with parameters P_init=0.3, P_learn=0.1, P_guess=0.2, P_slip=0.1; per-student per-question mastery sequence; configurable via Settings sliders
- [ ] **Improved Struggle Model** — `models/improved_struggle.py`; 3-component weighted sum: behavioral (0.45) + mastery gap (0.30) + difficulty-adjusted (0.25); uses BKT mastery gap; graceful degradation to baseline when BKT unavailable

### 4.x Lab Instructor System

- [ ] **In Class View** — summary cards (active students, avg struggle, top struggling student, hardest question); student + question leaderboards (max 15); score distributions; CF diagnostic panel; formula info expander
- [ ] **Student Detail View** — drill-down with struggle metrics, submission timeline, retry trend chart, similar students list (from CF), BKT mastery chart if improved models enabled
- [ ] **Question Detail View** — drill-down with mistake clusters, student attempt table, attempt timeline, IRT difficulty score if improved models enabled
- [ ] **Data Analysis View** — 6 chart types: module usage bar, top questions, user activity scatter, activity timeline, academic week heatmap, students by module
- [ ] **Comparison View** — model agreement summary cards (% agreement, avg delta); scatter plots baseline vs improved for struggle + difficulty; detailed comparison table; gated by `improved_models_enabled`
- [ ] **Settings View** — sound toggle, auto-refresh interval slider, CF toggle + k threshold, improved models master toggle, model selectors (IRT / BKT), BKT parameter sliders (P_init, P_learn, P_guess, P_slip)
- [ ] **Previous Sessions View** — load/delete saved sessions; filter by academic period; session metadata display (date, student count, module)

### 4.x Lab Assistant System

- [ ] **Session Join Flow** — enter session code + name; identity stored in URL `?aid=`; validation against `lab_session.json`; error state if code invalid
- [ ] **Waiting and Assignment States** — unassigned view (waiting screen); assigned view (student card with struggle summary, help-requested flag); transitions on filelock state change
- [ ] **Live Assistant Allocation** — instructor assigns via dropdown (any unassigned assistant → any student); assistant self-claim from list (toggleable by instructor); mark-helped clears assignment; all changes sync via filelock

### 4.x RAG Suggested Feedback (Phase 9)

> ⚠️ Stub — write after Phase 9 code is finalized

- [ ] Describe Dr. Batmaz's hybrid two-layer architecture (must credit in dissertation — Meeting 3, 2026-04-08)
- [ ] Layer 1: pandas pre-filter `df[df["user"] == student_id]` (SQL concept, pandas realisation)
- [ ] Layer 2: ChromaDB semantic search — `PersistentClient` at `data/rag_chroma/`, collection `session_{id}`, `where={"student_id": ...}` metadata filter
- [ ] Embedding model: `all-MiniLM-L6-v2` (local, ~90 MB first-run, no API cost)
- [ ] Generation: GPT-4o-mini, temperature 0, JSON array of 2–3 bullets ≤15 words each
- [ ] Caching: module-level `_suggestion_cache` + `st.session_state["cached_suggestions"]` — one OpenAI call per student per session
- [ ] Graceful degradation: missing deps → silent no-op; < 2 submissions → "Not enough data yet"; LLM failure → silent
- [ ] Privacy argument: two-layer student-scoped filter enforces NFR5

See [[RAG Pipeline - Two-Layer Retrieval]] and [[rag.py — RAG Engine and ChromaDB Interface]].

### Cross-cutting

- [ ] Remove all "to be implemented in later iteration" language (line 142 in tex)
- [ ] Add code snippets to Appendix A: incorrectness batch call, struggle score signature, lab state read/write, deferred actions pattern
- [ ] Add screenshots to Appendix B: all 6 instructor views + 4 assistant states

## Open questions

- Should the chapter describe the V1→V2 evolution, or just describe V2 as the final system?
- How much implementation detail is appropriate? Code snippets in chapter vs appendix?
- Should the improved models be in Ch3 (design) or Ch4 (implementation)?
