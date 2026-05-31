# 13 — Marking & Gap-to-A Checklist

Indicative marking of the **complete 125-page `Report/main.pdf`** (read end-to-end 2026-05-31) against the M.Sci. rubric in [[Marking Criteria]]. This is the **lens for the second pass** the author runs *after* Notes 00–12 are closed — not new edits to start now. Marks are indicative only; the official mark is the assessor's, and the rubric notes the mapping varies per project. ← [[00 Index]]

## Indicative marks

| Component (weight) | Band | Indicative | Why (against band wording) |
| --- | --- | --- | --- |
| Knowledge & Understanding (30%) | **A** | ~76% | "Comprehensive grasp … excellent understanding of research methods": IRT, BKT, RAG, empirical-Bayes shrinkage, OLS/TPE, κ/ρ — learnt and applied correctly |
| Cognitive Abilities (30%) | **high B → A−** | ~71% | Clear, well-framed original contribution + honest IRT anti-result; but B-band "publication if supplemented" fits — single-module, retrospective, LLM-rater-as-truth cap it under A |
| Practical Abilities (30%) | **A** | ~78% | "Very well planned and executed … contribution achieved and evaluated": designed, implemented **twice** (V1 Streamlit, V2 React/FastAPI), tested (FR/NFR), extensively evaluated |
| Transferable Skills (10%) | **high B → A−** | ~70% | Comprehensive 68-ref review + detailed methodology section (both A-band requirements present); dragged by empty *referenced* appendices and proofreading |

**Weighted ≈ 74–75%** — distinction-level, sitting right on the A boundary (A = ≥75%). The four items below are what stand between it and a clean, unarguable A.

## Gap-to-A items (the second pass)

1. **Empty appendices that the body cross-references — highest leverage.** Appendix **A** (Code Snippets), **D** (Formulae) and **E** (Formulae Derivation) are headings only in the compiled PDF. Worse, Ch4 promises "full derivation in Section 3 and **Appendix E**" in the struggle and difficulty maths recaps (≈ pp. 68–69) — a reader following the pointer hits a blank page. **Either fill them or delete the heading + every in-text pointer.** First confirm whether the latest `.tex` already has content the committed PDF lacks (the PDF showed as modified in `git status`); if so this is a stale-build check, not authoring. Formula content overlaps with [[04 Symbol, Data & Acronym Definitions]]; the broken-xref angle is the kind of integrity issue [[01 Integrity & Consistency Fixes]] handled, but this is a *fresh* finding for the second pass.
2. **Proofreading sweep.** Accumulated slips cost the "comprehensive, coherent" wording. Confirmed instances: "Or examined novice programmers'" (missing author name / "et al.", §2.2.1), "the parametrix model" (→ parametric, §3.4.4), "i.e.different models" (Fig 3.8 annotation), "This was approach allowed us" (§1.5/Table 1.1 area), "students who is needs help" (§5.5.2), "the to not want to" (§5.5.5 triangulation), "scenaro" (Fig B.11 caption text). Overlaps with [[05 Intros, Conclusions & Summaries]] ("finish abandoned sentences") and [[01 Integrity & Consistency Fixes]].
3. **Sharpen the contribution claim + name the publication scope (Cognitive band).** The contribution is currently under-sold. State the novel claim crisply and early (live, session-scale, instructor-facing struggle/difficulty validated against a scalable second-opinion rater, with a *documented negative finding*), and name precisely what a publication would additionally need (human-labelled or multi-module validation; a prospective intervention study). Turns a limitation into a controlled scope statement. → [[05 Intros, Conclusions & Summaries]], [[10 Related Work & Research-Gap Expansion]], [[03 Design Rationale & Missing Views]].
4. **Lift descriptive lit-review patches into analysis.** The research-gap synthesis (§2.6) is A-grade; parts of §2.1 and §2.5 read descriptively (the B-band's exact "descriptive in parts rather than analytical"). Re-cast 3–4 paragraphs to "X found A, but did not address B, which this project does." → [[06 Background Lit-Review Expansion]], [[10 Related Work & Research-Gap Expansion]].

## Do-not-lose strengths (protect in editing)

- The **IRT anti-result** (κ = −0.024, retained not promoted, framed as a positive of the systematic method) — this critical-maturity move is a mark-winner; keep it.
- The **evaluation rigour**: model-class bake-off (OLS vs Ridge/Lasso/ElasticNet/RF/GB), GroupKFold CV, Optuna TPE (τ 0.7→0.900, Δρ +0.160; K non-consequential), threshold training by κ-maximisation, and the **rater-fidelity ceiling** analysis (LLM-vs-human κ = +0.198 bounds the claim). Don't let any trim flatten this.
- The **negative-findings-on-equal-footing** framing and the **threats-to-validity / limitations** depth.

## Status

Reference note, not a task list to action now. Revisit once Notes 00–12 are ✅; this drives the post-00–12 marking pass.
