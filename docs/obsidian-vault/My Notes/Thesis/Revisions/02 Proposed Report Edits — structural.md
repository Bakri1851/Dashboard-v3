# 02 — Proposed Report Edits (structural / mechanical)

Structural changes only (no new argument). Each is **previewed for approval before applying**. ← [[00 Index]]

> **✅ Fully applied to `Report/` (2026-05-31).** S1–S6 all complete. Final session built **S6a** (Appendix C — FR1–FR7 / NFR1–NFR6 verification tables in `detailed-test-results.tex`) and **S6b** (Appendix D — `themes-and-references.tex` rebuilt from a complete 68-key `\cite` census; the 4 orphaned CF keys wired into §2.3.1 instead of dropped — see `[[07 Citations — wire orphans + Candidate References]]`). Report compiles clean (MiKTeX, exit 0; zero undefined cites/refs); `sync_literature.py` re-run (195 cite calls / 68 unique keys).

## S1. Move live UI screenshots → Appendix B (supervisor pt 8)
- **From** `Report/main-sections/implementation.tex` **to** `Report/appendix-sections/ui-screenshots.tex` (currently a heading-only stub with `\label{app:ui-screenshots}` already in place).
- **Move these 15 figures:** `fig:v2-inclass`, `fig:ui-inclass-basic`, `fig:ui-inclass`, `fig:ui-studentdetail`, `fig:ui-questiondetail`, `fig:ui-dataanalysis`, `fig:ui-settings`, `fig:ui-previoussessions`, `fig:ui-progression`, `fig:asst-join`, `fig:asst-unassigned` (both subfigures), `fig:asst-assigned`, `fig:asst-dispatch`.
- **Keep inline:** `fig:arch-v2` (architecture diagram) and `fig:v2-live-session` (session-embedded sidebar) — these are not "live software screenshots" in the supervisor's sense.
- At each removal point leave a one-line cross-reference (e.g. "the deployed view is shown in Appendix~\ref{app:ui-screenshots}, Figure~X"). Drop the `\IfFileExists{…}{…}` placeholder scaffolding — all PNGs exist in `figures/implementation/`. Give each relocated figure a clean Appendix caption (view name + the cohort/session it was captured from).

## S2. Stickman bird's-eye context diagram (supervisor pt 1) — TikZ
- **New figure** near the top of the System Architecture subsection in `design-and-architecture.tex` (~after l119), styled to match the existing `fig:system architecture` TikZ.
- **Contents:** three stickman stakeholders — **student**, **lab assistant**, **lab coordinator / module leader** — each connected to a touchpoint: student → the formative-assessment environment (which feeds the data endpoint); assistant → mobile phone (assistant view); coordinator → computer (instructor dashboard). **Number every component (C1…Cn)** so later prose can cite "Component C3".
- I will deliver the **TikZ source as a preview here** for your approval before it goes into the chapter. (Supervisor also said: keep the existing technical architecture diagram, just add this simpler stakeholder view.)

## S3. Component-level cross-references (supervisor pt 2)
- Make the layer/box labels visible on `fig:system architecture` and confirm the phase labels on `fig:v2-pipeline-design` (it already has Phase 1–5).
- Rewrite whole-figure references to component references: data-ingestion prose → "Layer 2, Data Ingestion"; instructor-views prose → "Layer 3 (Instructor)"; file-lock prose → "the Shared session state box"; weight-fitting (`design-and-architecture.tex` ~l800) → "Phase 4 … produces the trained weights and calibrated thresholds"; figure-generation → "Phase 5".

## S4. Trim captions to number + short title (supervisor pt 10)
- **Evaluation** (`results-and-evaluation.tex`) captions at l149, l159, l166, l175, l188, l199, l210, l261, l309, l327, l452 — strip ρ/κ/MAE/CI/percentages and interpretive clauses.
- **Implementation** (`implementation.tex`) captions at l153, l199, l342, l407, l496 — reduce 40-word captions to short titles.
- **Design** (`design-and-architecture.tex`) l1033, l1046 — fix non-standard "Table Highlighting…" → "Struggle band thresholds and colour mapping" / "Difficulty band thresholds and colour mapping".
- Pure relocations (moving an existing sentence from caption to the paragraph after the figure) are mechanical; where the relocation needs *new* interpretive prose, that is briefed in [[05 Intros, Conclusions & Summaries]] instead.

## S5. Figure 3.2 technician credit (user)
- Add to the `fig:data entry` caption (`design-and-architecture.tex` ~l131): "Figure courtesy of the module technician, Charlotte Barnes." (credit by role + name, per the supervisor).

## S6. Appendix C + D tables and Lists (examiner navigability)
- **Appendix C** (`detailed-test-results.tex`, stub): assemble the FR1–FR7 and NFR1–NFR6 verification tables that §5.1 promises (`\ref{app:detailed-test-results}`), drawn from the qualitative results already in §5.2–5.3 and the prewarm timings (§5.3.1). Columns: requirement ID, description, test method (smoke/e2e), pass/fail, evidence. (table assembly from existing facts.)
- **Appendix D** (`themes-and-references.tex`): rebuild Table D from the **actually-cited** key set per chapter — the current CF row lists `schafer/dasilva/deschnes/li`, none of which the design/implementation CF sections use. Add rows for Knowledge Tracing (BKT/IRT), Text Mining/Mistake Clustering, RAG, Composite Indicators/Time-decay/Shrinkage, LLM-as-judge, Composite Model Training. Convert drifted underscore citekeys (l44, l46, l48) to the CamelCase forms used in chapters; every key grepped in `references.bib` first. Then re-run `python scripts/sync_literature.py`.
- **Lists:** add `\listoffigures` and `\listoftables` after the ToC in `main.tex` (30+ numbered floats).
