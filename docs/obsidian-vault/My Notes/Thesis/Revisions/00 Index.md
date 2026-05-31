# Revisions Roadmap — Index

Post-draft revision pass following the 2026-05-29 supervisor meeting, backed by two read-only audits of the whole report (verified against the `.tex` and `data/eval/` files — see `[[Meeting Log]]`). **Progress: Notes 01 and 02 are fully applied to `Report/` (report compiles clean, zero undefined cites/refs); Notes 03–12 are pending (see the Status column).** Every `Report/`/`.bib` edit is previewed in these notes and applied only after sign-off. Prose is *briefed* here for the author to write; mechanical edits are previewed for approval.

Related: [[Writing Roadmap]] · [[Full Roadmap]] · [[v2 Report Change List]] · [[Figures and Tables]] · [[Meeting Log]]

## Notes in this folder

| Status | Note                                                            | Scope                                                                                                                             | Author writes / I apply        |
| ------ | --------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------ |
| ✅      | [[01 Integrity & Consistency Fixes]]                            | **Do first.** Phantom benchmark, wrong figures, unmet headings, contradictions, leftover TODOs                                    | mostly I apply (review-gated)  |
| ✅      | [[02 Proposed Report Edits — structural]]                       | Screenshots→Appendix B, stickman TikZ, component cross-refs, caption trims, Fig 3.2 credit, Appendix C/D tables, lists of figures | I apply (review-gated)         |
| ⬜      | [[03 Design Rationale & Missing Views]]                         | Why-decisions + Settings / Student / Question design + CF concept                                                                 | author writes                  |
| ⬜      | [[04 Symbol, Data & Acronym Definitions]]                       | Data fields, parameters, Evaluation-Metrics subsection, nomenclature list                                                         | author writes                  |
| ⬜      | [[05 Intros, Conclusions & Summaries]]                          | Chapter-intro audit, section closers, chapter summaries, finish abandoned sentences                                               | author writes                  |
| ⬜      | [[06 Background Lit-Review Expansion]]                          | New/expanded Ch2 subsections (OLS, bake-off, shrinkage, thresholds, missing data)                                                 | author writes                  |
| ⬜      | [[07 Citations — wire orphans + Candidate References]]          | Wire 16 orphaned refs into prose; small new-ref set for Zotero                                                                    | author wires / validates       |
| ⬜      | [[08 Examiner-Expected Sections]]                               | Ethics, GDPR, reproducibility, comparison table, threats-to-validity, accessibility                                               | author writes                  |
| ⬜      | [[09 Possible New Design-Implementation Work (rationale-only)]] | Why-deferred rationale; no building this pass                                                                                     | author writes                  |
| ⬜      | [[10 Related Work & Research-Gap Expansion]]                    | Prior-art scan (closest = Diana LAK 2017); §2.7 reframe to integration-gap; comparison table                                      | author writes / validates refs |
| ⬜      | [[11 Evaluation Plots Review]]                                  | Eval-chapter plots: add violin/box of score-per-band (no confusion matrix / IRT plot); double-check existing figures              | author writes / I apply gated  |
| ⬜      | [[12 Screenshot Re-shoot TODO]]                                 | Stale deployed-UI screenshots (Settings confirmed stale) to re-capture before submission; same filenames → no .tex change         | author re-captures             |

**Legend:** ✅ done · 🟡 partly applied · ⬜ pending

## Supervisor point → note map

1 stickman diagram → 02 · 2 component cross-refs → 02 · 3 rationale → 03 · 4 web-app rationale → 03 · 5 define symbols → 04 · 6 RAG framing → 03 · 7 CF concept → 03 · 8 screenshots→appendix → 02 · 9 missing view designs → 03 · 10 caption trims → 02 · 11 sections ending on figures → 05 · 12 section intros → 05 · 13 problems-table summary → 05 · 14 implementation summary → 05 · 15 lit review for new content → 06/07 · 16 more detail / finish sentences → 05/01 · *(29 May follow-up)* prior art + research-gaps expansion → 10

## Priority order

1. **[[01 Integrity & Consistency Fixes]]** — credibility issues an examiner catches first (the phantom HistGB claim, the +0.469 figure, the unmet "Ethical Approval" heading, the smart-device contradiction). Do these before anything else.
2. **[[02 Proposed Report Edits — structural]]** — the supervisor's headline asks (stickman, screenshots→appendix, component cross-refs, caption trims).
3. **[[04]] + [[05]]** — definitions and the chapter/section intros & closers (high marks-per-effort).
4. **[[03]] + [[06]] + [[07]]** — rationale, background expansion, citation wiring.
5. **[[08]] + [[09]]** — examiner-expected sections and deferred-work rationale.

## Open decisions for the author

- **HistGB (high):** remove "and histogram gradient boosting" from abstract + conclusion (default, no implementation), **or** run the HistGB experiment. → [[01 Integrity & Consistency Fixes]]
- **Cohort window:** confirm the true range — Ch5 says 2 Feb–15 May 2026; `data/eval/results.md` says 2025-10-06→2026-05-15 (21/23 healthy sessions). Likely a Semester-1 tail excluded from evaluation; state which. → [[01 Integrity & Consistency Fixes]]
- **Ethics approval:** supply the Loughborough approval/exemption reference + date, or rename the §5.5.1 heading. → [[01]] / [[08 Examiner-Expected Sections]]
- **RAG count:** confirm how many existing approaches were surveyed ("three or four"). → [[03 Design Rationale & Missing Views]]
- **τ deployment:** Optuna suggests raising `cf_threshold` 0.7→0.90 — change the deployed `config.py` default, or only report it as a finding? → [[01]] / [[09 Possible New Design-Implementation Work (rationale-only)]]
- **New BibTeX:** validate the 6 candidate refs in Zotero before Better BibTeX export (I do **not** edit `references.bib`). → [[07 Citations — wire orphans + Candidate References]]

## If time permits (stretch)

- **Recent-work scouting (optional, end of pass):** run a deep-research web sweep on *"What's the 2024–2026 state-of-the-art in real-time struggle detection — am I missing recent work?"* as a scouting step for [[06 Background Lit-Review Expansion]] / [[10 Related Work & Research-Gap Expansion]]. Output is a leads list to chase in Zotero/Scholar — **scouting, not citable content**; validate any ref in Zotero before it enters `references.bib`. → run via `/deep-research`.
