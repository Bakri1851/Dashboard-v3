---
title: Future Work Inventory
date: 2026-04-10
type: thesis-planning
status: authoritative
---

# Future Work Inventory

This note is the single, deduplicated record of every unimplemented requirement, deferred feature, known limitation, and stretch goal identified by crawling the entire Obsidian vault. Items from multiple source files are merged into one row. Code status was verified against the live codebase on 2026-04-10; vault notes that pre-dated recent commits have been corrected.

**Note on temporal smoothing:** vault notes describe this as a "stub, disabled". The actual codebase (`config.py:72`, `instructor_app.py:675–689`) shows `SMOOTHING_ENABLED = True` with active EMA application at every refresh cycle (commit `8decf66`). Code status is therefore **Implemented**.

**Note on confidence indicator:** `models/measurement.py` computes `incorrectness_confidence` and `views.py:349–354` renders it via `render_confidence_indicator()`. Code status is **Implemented and displayed**. This item is excluded from the "computed-but-hidden" category.

---

## Full Inventory Table

| # | Item | Category | Source Files | Code Status | Report Status |
|---|------|----------|-------------|-------------|---------------|
| 1 | FR6 — smart device push notifications (phones, smartwatches, smart glasses) for high-struggle alerts | Unimplemented Requirements | Ch2, Ch6, Coding Roadmap Phase 8 | Not started | Mentioned (Ch2 FR6, Ch6 placeholder) |
| 2 | FR7 — full assistant ranking with student satisfaction feedback loop (not just helped-count) | Unimplemented Requirements | Ch2, Ch6 | Partially implemented (helped-count only, no satisfaction survey) | Mentioned (Ch2 FR7) |
| 3 | Supervised weight optimisation — replace hand-tuned α, β, γ, δ, η with logistic regression / gradient boosting once ground-truth struggle labels are collected | Model & Algorithm Extensions | Evaluation Strategy, Ch5 | Not started (PCA-based justification used for current weights) | Not mentioned explicitly — Should be in Ch6 |
| 4 | IRT calibration with larger datasets and MLE convergence diagnostics | Model & Algorithm Extensions | Ch3, IRT Difficulty Logic | Partially implemented (`models/irt.py` uses MLE; no convergence checks) | Not mentioned — Should be in Ch6 |
| 5 | BKT parameter estimation from per-module data (current p_learn, p_slip, p_guess are fixed defaults) | Model & Algorithm Extensions | BKT Mastery Logic, Ch3 | Partially implemented (BKT implemented with defaults; no fitting) | Not mentioned — Should be in Ch6 |
| 6 | BKT mastery direct visualisation — per-student mastery badge / progress bar in instructor dashboard and lab assistant app | UI & Feature Completeness | Ch3, Next Steps Phase 6, Coding Roadmap Phase 6 | Computed (`bkt.compute_all_mastery()`), mastery_summary only consumed internally by improved_struggle — never rendered | Not mentioned — Should be in Ch6 |
| 7 | Predictive / forward-looking struggle alerts — forecast who will struggle on the next question based on trajectory | Model & Algorithm Extensions | Ch6 (placeholder) | Not started | Mentioned (Ch6 future work placeholder) |
| 8 | RAG-based coaching suggestions for lab assistants — hybrid two-layer pipeline (pandas pre-filter by student_id → ChromaDB semantic search → GPT-4o-mini coaching hints) | Integrations | RAG Architecture, Full Roadmap Phase 9, [[rag.py — RAG Engine and ChromaDB Interface]] | **Implemented** (Phase 9, 2026-04-14) | Not yet written — needs Ch4 implementation section and Ch5 evaluation entry |
| 9 | Event-driven pipeline — replace interval polling (10 s cache, 5 s assistant app) with WebSockets or SSE for sub-second updates | Infrastructure & Architecture | Ch3, Architecture Overview, Ch6 | Not started (Ch3 describes it as "under exploration") | Mentioned (Ch3 design note) |
| 10 | Automated test suite — pytest coverage for analytics, models, lab_state; CI/CD integration | Infrastructure & Architecture | Ch6 (placeholder), Evidence Bank | Not started | Mentioned (Ch6 future work placeholder) |
| 11 | Session export — CSV and PDF download of struggle/difficulty scores, leaderboard, and charts | UI & Feature Completeness | Ch6 (placeholder), Evidence Bank | Not started | Mentioned (Ch6 future work placeholder) |
| 12 | In-app help system for instructor dashboard — Quick Tour, Help Centre, Model Guide, contextual tooltips, reliability indicators (Phase 10) | UI & Feature Completeness | Coding Roadmap Phase 10, Full Roadmap | Designed (sub-tasks fully specified), not started | Not mentioned — Should be in Ch6 |
| 13 | In-app help system for lab assistant app — join guide, student list explainer, action button guide (Phase 11) | UI & Feature Completeness | Coding Roadmap Phase 11, Full Roadmap | Designed, not started | Not mentioned — Should be in Ch6 |
| 14 | Baseline vs improved model comparison UI — side-by-side scatter and table for struggle and difficulty (Phase 5) | UI & Feature Completeness | Coding Roadmap Phase 5, Next Steps | Not started (`comparison_view` does not exist) | Not mentioned |
| 15 | User studies in real classroom settings with instructors and students | Evaluation & Validation | Ch6 (placeholder), Ch5 | Not conducted | Mentioned (Ch6 future work placeholder) |
| 16 | Longitudinal multi-session evaluation — track impact of temporal smoothing and difficulty signals across sessions | Evaluation & Validation | Ch6 (placeholder) | Not conducted | Mentioned (Ch6 future work placeholder) |
| 17 | Statistical validation — significance testing and confidence intervals on model agreement metrics | Evaluation & Validation | Ch6 (placeholder), Ch5 | Not conducted | Mentioned (Ch6 future work placeholder) |
| 18 | Comparative evaluation against existing LA systems (SAM, EMODA, Edsight, edInsight) | Evaluation & Validation | Ch6 (placeholder), Ch5 | Not conducted | Mentioned (literature review only) |
| 19 | LMS integration — consume data from Moodle/Canvas rather than custom PHP endpoint | Integrations | Ch6 (placeholder) | Not started | Mentioned (Ch6 future work placeholder) |
| 20 | Network / social learning analysis beyond k-NN collaborative filtering (graph-based, social network analysis) | Model & Algorithm Extensions | Ch6 (placeholder) | Not started (CF implemented with k=3 cosine similarity only) | Mentioned (Ch6 future work placeholder) |

---

## Ch6 Candidates

These eight items are the most academically significant and should be included in Ch6 §6.3. Each addresses a known limitation, extends the contribution in a meaningful direction, or remains genuinely novel within the learning analytics literature.

### 1. Supervised weight optimisation (item #3)
The struggle model's five weighting parameters (α, β, γ, δ, η) are currently set by PCA-guided trial-and-error, a principled but unsupervised approach. Once ground-truth struggle labels can be collected from instructors or students, supervised optimisation — logistic regression, gradient boosting, or Bayesian hyperparameter search — would place the model on firmer empirical ground. This is the single most significant methodological limitation of the current work.

### 2. User studies in real classroom settings (item #15)
The system has not been deployed in an actual lab session with live instructors and students. Without this, claims about educational impact cannot be substantiated beyond functional correctness. A controlled field study comparing instructor attention allocation with and without the dashboard would be the most direct validation.

### 3. BKT mastery direct visualisation (item #6)
Per-student mastery probabilities are computed at every refresh cycle when improved models are enabled, yet no instructor or assistant view exposes this data. Surfacing a mastery badge or progress bar would close the model-to-decision loop and give instructors granular evidence to complement the aggregate struggle score.

### 4. RAG-based coaching suggestions (item #8) — ✅ Implemented
A hybrid two-layer retrieval-augmented generation pipeline (pandas pre-filter by student_id, ChromaDB semantic search over embedded Q&A + feedback, GPT-4o-mini coaching hints) was implemented in Phase 9 (2026-04-14). Architecture by Dr. Batmaz — must be credited in the dissertation. Now in Ch6 future work candidates only if further extensions are proposed (e.g., improved embedding models, multi-session retrieval, user evaluation of suggestion quality).

**Data labelling for weight optimisation** (deferred future work): ~500 hand-labelled submissions needed to fit `STRUGGLE_WEIGHT_*` and `DIFFICULTY_WEIGHT_*` in `config.py:17-48` against ground truth using supervised ML (logistic regression / Optuna). Not in scope for this implementation phase.

### 5. Event-driven pipeline (item #9)
The current polling architecture introduces up to ten seconds of latency between a submission event and its appearance in the dashboard. Replacing interval-based polling with WebSockets or Server-Sent Events is an engineering investment that would meaningfully improve real-time responsiveness — a non-functional requirement the current system only partially satisfies.

### 6. FR6 smart device notifications (item #1)
Push notifications to assistants' mobile devices or smartwatches when a high-struggle student is unassigned represent a "Should Have" requirement that was explicitly scoped out of the current implementation. The infrastructure for identifying high-struggle, unassigned students already exists; the notification delivery layer alone is missing.

### 7. Longitudinal multi-session evaluation (item #16)
The exponential moving average smoothing mechanism was designed to carry information across refresh cycles within a session; its value over multi-session timescales (e.g., whether difficulty scores stabilise across repeat attempts at the same lab) has not been tested. A longitudinal study would provide the strongest empirical argument for the temporal components of both models.

### 8. Predictive alerts (item #7)
Moving from reactive monitoring to forward-looking risk prediction — identifying students likely to struggle on an upcoming question based on their trajectory — would represent a genuine extension of the contribution rather than an incremental improvement. Sequence models (e.g., LSTM over submission histories) or DKT (Deep Knowledge Tracing) could be explored in this direction.
