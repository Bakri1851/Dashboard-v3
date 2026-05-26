---
title: Future Work Inventory
date: 2026-04-10
type: thesis-planning
status: authoritative
---

# Future Work Inventory

<!-- v2-relabel-sync-2026-05-26-evening -->
> **Sync note (2026-05-26 evening — rater upgrade):** The LLM rater was upgraded from `gpt-4o-mini` to `gpt-4o` after a full re-label experiment showed every v2 model improves with the better rater (struggle ρ +0.573 → **+0.588**; difficulty ρ +0.287 → **+0.468** — biggest single gain; improved-struggle ρ +0.168 → **+0.201**, now matching the non-linear RandomForest ceiling). All ρ values below reflect the upgraded labels. Training pipeline, model class (OLS), target (4-band rating), CV scheme (GroupKFold by session / LOO on questions), and the verdict-scorecard structure (still 4 wins + 1 tie) are all unchanged. See [[v2 Relabel Handoff]] for the writing-chat interrupt + reconciliation doc.

<!-- v2-target-swap-sync-2026-05-26 -->
> **Sync note (2026-05-26 — major methodology correction):** The original v2 work in this note was framed around training against a binary `intervene` flag from the LLM rater. The dashboard makes no automatic alert or allocation decision, so binary classification on intervene was the wrong target. **The v2 weights, hyperparameters, and Optuna study have all been re-trained against the LLM's 4-band rating** (`On Track` / `Minor Issues` / `Struggling` / `Needs Help`) using ordinary least-squares **linear regression** instead of logistic regression, with **Spearman ρ + weighted κ + MAE** replacing AUC as the evaluation metric. Under the corrected target the verdict scorecard becomes **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" — the previous negative findings for difficulty and improved-struggle were artefacts of the wrong target). Old AUC numbers below have been updated to the new ρ numbers; any remaining `composite`/`blend`/`ordinal`/`intervene-as-target` language has been removed. See `data/eval/results.md` for the authoritative current numbers.

This note is the single, deduplicated record of every unimplemented requirement, deferred feature, known limitation, and stretch goal identified by crawling the entire Obsidian vault. Items from multiple source files are merged into one row. Code status was verified against the live codebase on 2026-04-10; vault notes that pre-dated recent commits have been corrected.

**Note on temporal smoothing:** vault notes describe this as a "stub, disabled". The actual codebase (`config.py:72`, `instructor_app.py:675–689`) shows `SMOOTHING_ENABLED = True` with active EMA application at every refresh cycle (commit `8decf66`). Code status is therefore **Implemented**.

**Note on confidence indicator:** `models/measurement.py` computes `incorrectness_confidence` and `views.py:349–354` renders it via `render_confidence_indicator()`. Code status is **Implemented and displayed**. This item is excluded from the "computed-but-hidden" category.

---

## Full Inventory Table

| # | Item | Category | Source Files | Code Status | Report Status |
|---|------|----------|-------------|-------------|---------------|
| 1 | FR6 — smart device push notifications (phones, smartwatches, smart glasses) for high-struggle alerts | Unimplemented Requirements | Ch2, Ch6, Coding Roadmap Phase 8 | Not started | Mentioned (Ch2 FR6, Ch6 placeholder) |
| 2 | FR7 — full assistant ranking with student satisfaction feedback loop (not just helped-count) | Unimplemented Requirements | Ch2, Ch6 | Partially implemented (helped-count only, no satisfaction survey) | Mentioned (Ch2 FR7) |
| 3 | Supervised weight optimisation — replace hand-tuned α, β, γ, δ, η with logistic regression / gradient boosting once ground-truth struggle labels are collected | Model & Algorithm Extensions | Evaluation Strategy, Ch5 | ✅ **Done 2026-05-25** — LLM second-opinion labels (GPT-4o-mini, n=1306) replaced the instructor-flagging prerequisite. All four weight vectors refit with OLS + GroupKFold CV; 4 positive findings (struggle weights, difficulty weights, improved-struggle weights, CF τ) + 1 tie (K). Toggleable in V2 Settings; defaults stay v1. See [[Evaluation PoC Handoff]] §13 and [[v2 Empirical Refinement Brief]]. | Ch5 §5.4 brief delivered; writing chat to draft |
| 3b | Missing-feedback fallback in incorrectness scoring — when `ai_feedback` is absent or the OpenAI call fails, incorrectness defaults to 0.5 (sitting exactly on the binary `CORRECT_THRESHOLD`). If most submissions lack feedback, this dominates the signal, attenuates struggle scores, inflates difficulty scores, and contaminates mistake clustering. Three fix paths: (a) direct LLM grading on `(question, target, student_answer)` instead of inferring from tutor feedback text; (b) embedding-based semantic similarity to the target answer (cheap, deterministic, no API); (c) confidence-weighted aggregation using existing `incorrectness_confidence` from `models/measurement.py` to down-weight low-confidence/missing-feedback submissions in the struggle aggregate. (c) is the smallest viable change. | Model & Algorithm Extensions | Ch3 §3.3.1 (acknowledged as limitation), Ch5 §5.5 (to discuss), Ch6 §6.3 (to propose), `analytics.py:112-149` (current fallback), `models/measurement.py` (confidence already computed) | Not started — substantial signal attenuation suspected on current data | Not mentioned — must be added to Ch3 §3.3.1 (1 sentence ack), Ch5 §5.5 (limitations paragraph), Ch6 §6.3 (future work bullet) |
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

### 1. Supervised weight optimisation (item #3) — ✅ Done 2026-05-25
Originally framed as the single most significant methodological limitation. **Closed during the Phase 4 v2 evaluation pipeline** (with a major target-swap correction on 2026-05-26). GPT-4o second-opinion labels (n=1306 struggle, n=72 difficulty) replaced the instructor-flagging prerequisite; OLS + GroupKFold CV refit the seven struggle weights, five difficulty weights, and three improved-struggle weights against the LLM's 4-band rating; Optuna TPE refit the shrinkage K and CF threshold τ against the same target. Final scorecard: **4 positive findings + 1 tie** — struggle weights (ρ +0.588 vs v1 +0.423), difficulty weights (ρ +0.468 vs v1 +0.027), improved-struggle weights (ρ +0.201 vs v1 −0.017), CF τ (Δ +0.160 ρ; best τ=0.900), and the shrinkage K within fold-variance noise (Δ +0.009 ρ; best K=1). All four artefacts toggleable in V2 React Settings (defaults stay v1). Verdict scorecard at [[Evaluation PoC Handoff]] §13. Residual future-work flavour now narrower — see new item #4a (LLM-rater limitation) and #4b (BKT priors + boundary τ) below.

### 1a. LLM-rater limitation (residual from item #3)
The v2 weights are trained against GPT-4o second-opinion labels rather than instructor flags; Cohen's κ between the LLM rater and the author at n=50 is poor by Landis–Koch (0.10–0.11 across binary intervene and the linear/quadratic-weighted band variants), though within-1-band agreement is 70%. Replacing the LLM rater with instructor flags (requires ethics extension) or a multi-rater consensus would let the v2 weights claim agreement with human judgement, not just with one model's judgement. Reported as a §5.6 methodological limitation.

### 1b. Optuna hyperparameter boundary + deferred BKT priors (residual from item #3)
The CF threshold τ optimum (0.899) landed at the upper boundary of the [0.4, 0.9] search range; a finer search at τ ∈ [0.85, 0.95] may yield further improvement. Four BKT priors (p_init, p_learn, p_guess, p_slip) and the BKT mastery threshold were originally on the optimisation grid but are pinned to `config.py` defaults in `optimised_hyperparams_v2.json` because each trial requires ~30 minutes of BKT refits; running a TPE study over them (perhaps with reduced fold count) is the natural follow-on. Reported as a §5.4.10 caveat.

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
