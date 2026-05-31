# 05 — Intros, Conclusions & Summaries (author writes)

Supervisor pts 11–14, 16: don't end sections/chapters abruptly on a figure; open each top-level section with a short framing paragraph (but check the existing ones first); summarise big tables; finish the abandoned sentences. ← [[00 Index]]

## Chapter-intro audit (keep / tweak / add) — supervisor pt 12
Check each chapter opener before adding — some already have one:
- **Ch1 Introduction** — opens straight into "Problem"; add a 2–3 sentence chapter framing, and fix the garbled first sentence (see [[01 Integrity & Consistency Fixes]] I10).
- **Ch2 Background** — has a top line but the four sub-sections jump straight into subsubsections; **add x.0 intros** to §2.2 Modelling Student Behaviour (struggle vs difficulty as complementary targets), §2.3 Data-Driven Personalisation (CF + text mining as complementary), §2.4 Retrieval-Augmented Feedback (RAG grounding to prevent hallucination), §2.5 Existing Systems (why survey them; course-level vs session-level gap).
- **Ch3 Design** — has an opener (l2); a new **§3.1 System Walkthrough** subsection (storyboard `fig:storyboard`) and the stakeholder context diagram (`fig:context-stakeholders`) were added at the top but sit nearly bare (one lead-in sentence each) — see *System Walkthrough + context-figure framing* below.
- **Ch4 Implementation** — has a strong Overview but the chapter-intro TODO at l3 is unresolved; **write the 2–3 sentence intro** (V1 Streamlit → V2 React/FastAPI framing).
- **Ch5 Evaluation** — opens well at section level, but **add x.0 intros** to §5.2 Functional Testing, §5.4 Results, §5.5 Survey, §5.6 Discussion (each currently jumps into its first subsubsection).
- **Ch6 Conclusion** — opens fine; no change.

## System Walkthrough + context-figure framing
The Walkthrough storyboard and the stakeholder context diagram open Ch3 and need surrounding prose so they read as argument, not decoration. **Decision: keep both; they are complementary, not redundant** — the storyboard is the *usage scenario*, the context diagram is the *component model* the chapter references (and the supervisor-requested context diagram).
- **§3.1 System Walkthrough** — now structured as **five per-step figures**, each under a run-in `\paragraph{}` heading: **Monitor** (`fig:storyboard`), **Detect** (`fig:sb-detect`), **Dispatch** (`fig:sb-dispatch`), **Cross the room** (`fig:sb-cross`), **Helped** (`fig:sb-helped`). Each step currently carries a **DRAFT scenario sentence** (tagged `% DRAFT` in the source) — refine or replace in your voice; keep them scenario-level (defer mechanism to later sections). **Flesh out each step:** under (or beside) each of the five walkthrough figures, write a short discussion — a couple of sentences on what that step shows and why it matters — so every figure is accompanied by real prose and the full-page figures don't sit half-empty; this expands the single placeholder sentence currently above each one. Optionally expand the lead-in into a fuller framing paragraph (why a concrete in-lab scenario opens the chapter; it motivates the monitor-and-dispatch contribution).
- **System Architecture — Figure 3.6** (context diagram `fig:context-stakeholders`): currently has only a one-line lead-in, so **write its accompanying discussion** (same treatment as the walkthrough figures). Add a sentence or two that *distinguishes* it from the storyboard — the storyboard shows how the system is used; the context diagram names the three system components (C1 quiz/AI platform, C2 instructor dashboard, C3 assistant view), their read-only data flow, and the human-in-the-loop dispatch + "helps in person" return path. State that C1–C3 are the reference labels used through the rest of the chapter (ties to the component cross-references, [[02 Proposed Report Edits — structural]] S3).
- **Bridge**: one sentence linking them — the storyboard motivates; the context diagram formalises the components the architecture and analytics sections then build on.

## Section/chapter closers — supervisor pt 11 / 14
- **Evaluation chapter** (`results-and-evaluation.tex`, after `fig:eval-incorrectness-distribution` l523) — chapter ends on a figure. **Add a 3–4 sentence closing synthesis**: headline ρ=+0.588 (struggle), the rater-fidelity ceiling, and the case for advisory (not autonomous) use.
- **Implementation chapter** (`implementation.tex`, end l1431) — ends on the problems table with only a TODO. **Add a 0.5–1 page chapter summary**: decisions carried V1→V2 (shared analytical core, filelock coordination), the major V2 gains (FastAPI scalability, React responsiveness, prewarm), and readiness for evaluation.
- **Design §3.5 Model Training Pipeline** (after `fig:v2-pipeline-design` l847) — ends on a figure. **Add 2–4 sentences**: how Phase 4 outputs (trained weights, calibrated thresholds) load at V2 runtime, then bridge into the RAG section.
- **Implementation §4.9 Instructor Views** (after `fig:ui-progression` l1286) — ends on a figure. **Add 2–3 sentences** on the session-progression view's role before the Lab Assistant section.
- **Design chapter end** (l1051) — ends after the visual-encoding tables. **Add 2–3 sentences** summarising the layered information architecture.

## Big-table summaries — supervisor pt 13
- **Problems table** (`implementation.tex` §4.11, `tab:problems` l1382–1423): expand the one-line intro (l1385) to say *why* these eight problems mattered, and **add a post-table summary** drawing out the lessons (concurrency, cold-start, graceful degradation as recurring themes).

## Finish abandoned sentences / mid-thought TODOs — supervisor pt 16
- `results-and-evaluation.tex` **l338**: "Results suggest that the bayesian shrinkage offers no real gain to the modelling % only part of conclusion add to it" → complete it (shrinkage gives no real gain; K could be dropped from future tuning) and delete the inline comment.
- `results-and-evaluation.tex` **l290**: threshold-bias sentence trails off without punctuation → finish it (why the cohort skew may generalise across modules — students only enter the log when they attempt a submission).
- `results-and-evaluation.tex` **after `tab:eval-hyperparams` l322**: add the Optuna summary paragraph (K negligible Δρ≈+0.009, hand-set near-optimal; τ substantial Δρ≈+0.160, 0.7 too permissive).
- `results-and-evaluation.tex` **l87–98**: after the prewarm timing list, add interpretation — ~650 s cold-start is once-per-deployment, steady-state 5 s polling meets NFR1 (sub-millisecond in-memory lookups thereafter).
- **Research Gaps §2.6** (`requirements-specification.tex` l288–307): resolve the four embedded TODOs, fix the trailing fragment, split into coherent paragraphs (AI/struggle/CF gaps; BKT instructor-facing + mistake clustering; smart-device assistant channel), and add an optional synthesis paragraph tying the gaps to the thesis motivation.

## Background composite-metric definition + glossary — supervisor pt 16
- `requirements-specification.tex` §2.2.2/2.2.3: add a paragraph framing struggle/difficulty as weighted composites of sub-metrics (time-on-task, attempts, correctness), weights set by manual tuning or supervised learning, normalised to [0,1]/[−1,+1], with EWMA temporal decay.
- §2.2.4 l141–144: add a short glossary line — *weight* = coefficient in the weighted sum; *hyperparameter* = tuning parameter of the learning algorithm or a threshold boundary; *parameter* = learnable coefficient.

## Impl → Design back-references — FC-02
- Where Ch4 describes each deployed view, add "as designed in §3.7, Figure [figma-N]" so the conceptual design and deployed implementation are traceable (currently zero such back-references).
