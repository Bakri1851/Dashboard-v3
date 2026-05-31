# 03 — Design Rationale & Missing Views (author writes)

The supervisor's core note: Ch3 "reads like a user manual" — it says *what* each thing is, not *why* it was chosen. Add engineering rationale, backed by literature not preference. **Dropped per your instruction: the overview-then-drill-down and general dashboard-design rationale (and Shneiderman/Few).** ← [[00 Index]]

## R1. Visual encoding / four-band colour scheme — rationale (supervisor named this)
- **Where:** `design-and-architecture.tex` Visual Encoding subsection (l1019–1050, Tables `tab: struggle table` / `tab: difficulty table`).
- **Write:** *why* four bands (not three or five); *why* the green→amber→orange→red traffic-light progression (perceptual ordering, instructor familiarity); and that the boundaries were hand-set for interpretability then calibrated against the rater (cross-ref §5.4.5). Note the colour scheme was not formally accessibility-tested → see the colour-blindness caveat in [[08 Examiner-Expected Sections]].
- **Cite:** composite-indicator normalisation/banding → `oecdHandbookConstructingComposite2008` (orphan, see [[07 Citations — wire orphans + Candidate References]]).

## R2. Tabular / leaderboard layout — rationale (supervisor named this)
- **Where:** Instructor Views subsection (l955–981).
- **Write:** *why* a ranked tabular leaderboard rather than a chart-heavy layout — it maps directly to the instructor's task (prioritise who to help next), supports at-a-glance scanning under time pressure, and keeps two parallel signals (struggle vs difficulty) side by side. Frame as an engineering decision tied to the in-lab use context, not preference.

## R3. Web app for the lab-assistant interface — rationale (supervisor pt 4)
- **Where:** Lab Assistant View subsection (l983–1017, around l985).
- **Write:** *why* a web app rather than a native mobile app: zero install on assistants' own devices, cross-platform (any phone/tablet), instant updates, simpler deployment for a single-process backend, and the same shared-state coordination path as the instructor app. Frame as accessibility + deployment simplicity.

## R4. Cosine vs Euclidean similarity — add the citation
- **Where:** Student Similarity Measure paragraph (~l498). The justification already exists ("robust to differences in overall activity levels"); it just lacks a source.
- **Cite:** `manningIntroductionInformationRetrieval2006` (already in `.bib`, cited elsewhere) for the cosine-similarity / vector-space rationale.

## R5. OLS-vs-non-linear — short forward reference
- **Where:** Struggle Score Definition (l259–266).
- **Write:** one sentence that OLS was chosen for interpretable signed weights, with the model-class comparison deferred to §5.4.3 (`fig:eval-model-class-bakeoff`). Avoids the choice looking unmotivated in Ch3.

## R6. Collaborative-filtering concept paragraph (supervisor pt 7)
- **Where:** `design-and-architecture.tex` CF section, **before** the "Student Interaction Matrix" maths (~l470). (Note: the CF section *is* in Design at l468–577 — the audit finding that claimed otherwise was a faulty grep.)
- **Write:** a 3–4 sentence plain-language definition — CF infers a student's likely struggle from the behaviour of *similar* peers, where similarity is measured over their interaction feature vectors; relevant here because a struggling student often resembles peers who already crossed the help threshold, enabling earlier intervention. Reader should not have to consult the literature review to follow the maths.
- **Cite (at point of use):** cold-start / data-sparsity limitation → `korenCollaborativeFilteringTemporal2010` (orphan); k-NN CF basis already cited (`herlockerAlgorithmicFrameworkPerforming1999`, `resnickGroupLensOpenArchitecture1994`).

## R7. RAG section framing (supervisor pt 6 — corrected)
- **Where:** RAG Feedback Design section opening (l850–854).
- **Write:** an opening paragraph stating RAG is a **proof-of-concept** layer that grounds coaching suggestions in the session's *own* submission history (beyond the core struggle/difficulty models), evaluated qualitatively rather than against quantitative labels; and that **three or four** existing feedback/retrieval approaches were surveyed before this design (**confirm the exact count**).
- **Do NOT** attribute RAG to Charlotte — that attribution belongs to **Figure 3.2** (see [[02 Proposed Report Edits — structural]] S5).

## Missing view designs (supervisor pt 9) — add to Ch3

### R8. Settings view design (entirely absent from Ch3)
- **Where:** new subsection after Lab Assistant View (~l1017).
- **Write:** the Settings interface design and its configurable options — model-choice (baseline vs improved), collaborative-filtering toggle + similarity-threshold τ, BKT parameter sliders, temporal-smoothing toggle, theme/refresh — with the *rationale* (instructor control over which signals drive the board; Bloomberg-terminal-style power-user toggles, defaults safe). Cross-reference the deployed Settings screenshot now in Appendix B.

### R9. Student-Detail & Question-Detail interface designs (currently only narrative)
- **Where:** Instructor Views subsection.
- **Write:** a short interface-design statement for each drill-down target — what the **Student Detail** view shows (per-signal struggle breakdown, timeline, hardest questions, RAG card) and what the **Question Detail** view shows (difficulty + aggregated incorrectness, top strugglers, mistake clusters, RAG misconception bullets) — and *why* those elements answer the instructor's question. Cross-reference the Figma mockups (kept in Ch3) and the Appendix B screenshots.
