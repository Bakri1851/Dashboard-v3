# Thesis Overview

Master's thesis for the Dashboard v3 project. This note tracks the overall state of the dissertation and links to per-chapter analysis notes.

Related: [[Report Sync]], [[Rewrite Queue]], [[Evidence Bank]], [[Home]]

## Metadata

- **Title:** Online Dashboard For Lab Assistants To Better Support Students in Labs
- **Author:** Abubakar Othman (F221611)
- **Programme:** MSci Computer Science and Mathematics
- **Institution:** Loughborough University, Department of Computer Science
- **Supervisor:** Dr Firat Batmaz
- **Module Code:** 25COD290
- **Deliverable:** January 2026 (milestone); final submission May 2026
- **Source:** `c:\Users\Bakri\Downloads\Thesis\` (Overleaf export)

## Chapter completion status

| # | Chapter | Thesis Section | Status | Vault Note |
|---|---------|---------------|--------|------------|
| 1 | Introduction | `introduction.tex` | ✅ Written — small fixes remain (future-tense, risk table) | [[Ch1 – Introduction]] |
| 2 | Background and Requirements | `requirements specification.tex` | ✅ Written — small fixes remain (uncomment research gaps §2.1.7, FR/NFR status column) | [[Ch2 – Background and Requirements]] |
| 3 | Design and Modelling | `design and architecture.tex` | Draft — formulas outdated, Figma needs replacing; new skeleton sections added for Mistake Clustering, Advanced Model Design (IRT/BKT/improved struggle/confidence), Lab Assistant View | [[Ch3 – Design and Modelling]] |
| 4 | Implementation | `implementation.tex` | Outdated — describes V1 only; full skeleton tree now in place (26 new subsections across System Structure, Data Pipeline, Session Management, Analytics, Advanced Models, Instructor Views, Lab Assistant System); rewrite in progress | [[Ch4 – Implementation]] |
| 5 | Results and Evaluation | `results and evaluation.tex` | Empty — 5 headers, no content | [[Ch5 – Results and Evaluation]] |
| 6 | Conclusion | `conclusion.tex` | Empty — 2 headers, no content | [[Ch6 – Conclusion]] |
| - | Progress Report | `Progress Report.tex` | Commented out in main.tex (January milestone) | N/A |

## Appendix status

| Appendix | Title | Status |
|----------|-------|--------|
| A | Code Snippets | Empty |
| B | UI Screenshots | Empty |
| C | Detailed Test Results | Empty |
| D | Themes and References | Complete |
| E | Formulae | Empty |
| F | Formulae Derivation | Empty |

See [[Figures and Tables]] for full figure/table inventory.

## Bibliography

36 references in `references.bib` covering: learning analytics in HE, dashboards, real-time analytics, student struggle modelling, task difficulty modelling, collaborative filtering, LMS, instructor dashboards, early warning systems.

## Key concerns for final submission

1. **Ch4 Implementation is critically outdated** — describes V1 prototype, not V2 full system
2. **Ch5 and Ch6 are completely empty** — evaluation and conclusion must be written from scratch
3. **5 of 6 appendices are empty** — screenshots and test results are most urgent
4. **Formula mismatch** — thesis struggle model has 5 components, code has 7; difficulty has 4 vs 5
5. **Figma mockups** — 3 mockups in Ch3 should be replaced with actual dashboard screenshots
6. **Future-tense language** — thesis reads as proposal in many places, not a completed project
7. **Missing features** — IRT, BKT, improved struggle, mistake clustering, saved sessions, data analysis, lab assistant system, **Phase 9 RAG suggested feedback** — all implemented but not yet in thesis
8. **Phase 9 dissertation credit** — Dr. Batmaz's hybrid RAG architecture must be acknowledged in Ch4 and the literature review updated to cover ChromaDB + RAG

## Thesis source structure

```
Thesis/
  main.tex                          — master document
  references.bib                    — 36 citations
  title page/title.tex              — title page + logo
  main sections/
    introduction.tex                — Ch1
    requirements specification.tex  — Ch2
    design and architecture.tex     — Ch3
    implementation.tex              — Ch4
    results and evaluation.tex      — Ch5
    conclusion.tex                  — Ch6
    Progress Report.tex             — milestone report (commented out)
  appendices/
    code snippets.tex               — App A (empty)
    ui screenshots.tex              — App B (empty)
    detailed test results.tex       — App C (empty)
    themes and references.tex       — App D (complete)
    formulae.tex                    — App E (empty)
    formulae derivation.tex         — App F (empty)
  figures/                          — diagrams, screenshots, Figma mockups
```
