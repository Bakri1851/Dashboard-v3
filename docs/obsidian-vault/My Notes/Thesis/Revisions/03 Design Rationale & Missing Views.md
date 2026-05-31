# 03 — Design Rationale & Missing Views (author writes)

The supervisor's core note: Ch3 "reads like a user manual" — it says *what* each thing is, not *why* it was chosen. Add engineering rationale, backed by literature not preference. **Dropped per your instruction: the overview-then-drill-down and general dashboard-design rationale (and Shneiderman/Few).** ← [[00 Index]]

> **Re-anchored 2026-05-31** against the live `Report/main-sections/design-and-architecture.tex` (**1282 lines, SHA a9896e02**). The note's original line numbers predated the Notes 01/02 edits and were off by ~250 lines; all anchors below are now correct. An earlier audit pass briefly mis-reported this chapter as structurally broken — that was tool-output corruption, **not** the file; the chapter is clean. Status legend: ✅ done · ⚙️ mechanical cite (author applies) · ✍️ author writes.

> [!tip] Drop-in drafts
> Each R-step below carries a collapsed `Drop-in draft` callout with copy-paste-ready LaTeX in *your* voice (British spelling, declarative, semicolons, no hedging). They are **starting points to adapt**, not final prose. `% TODO` marks any `\ref{}`/label or figure I could not verify — fill these before compiling.

## R1. Visual encoding / four-band colour scheme — rationale ✅ DONE 2026-05-31 (l1299–1302; modest version, no cite; typos fixed)
- **Where:** `\subsubsection{Visual Encoding of Metrics}` — **l1251–1280** (Tables `tab: struggle table` / `tab: difficulty table`, then the band-boundary paragraph at l~1278).
- **Already present:** the closing paragraph states the boundaries are hand-set at interpretable values and *later calibrated against the LLM rater alongside the weights*, with a forward-ref to `sec:eval-results`. So the *calibration* half of R1 is covered.
- **Write (the missing half):** frame the four bands as ordered **action levels** (On Track / Minor Issues / Struggling / Needs Help) — more than a binary help/no-help split, with intermediate "watch" levels — and the green→amber→orange→red ramp as the familiar traffic-light severity ordering, readable without a legend. Keep the accessibility caveat (redundant label + position, not colour alone → [[08 Examiner-Expected Sections]]). The exact number of bands is a **design judgement, not a derived optimum** — do not overclaim "four is the minimum".
- **Cite:** none — presented as a reasoned design/perceptual decision (user chose the modest framing, 2026-05-31). *Optional precedents if you ever want one:* `arnoldCourseSignalsPurdue2012a` (Purdue's three-colour stoplight) — **not used now**. `oecdHandbookConstructingComposite2008` is a composite-*construction* ref, not a fit here → leave to [[07 Citations — wire orphans + Candidate References]].

> [!example]- R1 — drop-in draft (adapt to your voice)
> ```latex
> % Add after the band-boundary paragraph in Visual Encoding of Metrics (l~1278)
> The scale is divided into four ordered bands --- On~Track, Minor~Issues, Struggling and
> Needs~Help --- so the board conveys more than a binary help/no-help split: the intermediate
> bands let an instructor watch a student who is slipping before they reach the point of needing
> help. The green--amber--orange--red ramp follows the familiar traffic-light convention, so
> severity is read from colour without a legend, and the same four-step scheme is reused for
> question difficulty (Easy--Very~Hard) for consistency. Colour is never the sole channel: each
> band also carries its textual label and fixed position, so the encoding stays legible without
> colour discrimination, although the palette was not formally accessibility-tested (see the
> accessibility statement, Section~\ref{sec:eval-accessibility}). % TODO: confirm/insert the Ch5 accessibility ref (Revisions 08 E7)
> ```

## R2. Tabular / leaderboard layout — rationale ✅ DONE 2026-05-31 (l1199–1202; abandoned "built around a" fragment cleared; typos + comma-splice fixed)
- **Where:** `\subsubsection{Instructor Views}` — insert **after l1196** (the paragraph that introduces the two ranked-list views from Fig.~`figma1`), before the allocation figure `figma2` (l1198).
- **⚠️ Abandoned fragment to clear first:** l1251 has a dangling half-sentence **`The instructor is built around a`**, orphaned at the end of *Lab Assistant View* just before *Visual Encoding*. It is the aborted start of this very R2 rationale, in the wrong subsection. **Delete it**, then place the full rationale at l1196. (Also a Note 05 abandoned-sentence item.)
- **Write:** *why* a ranked tabular leaderboard rather than a chart-heavy layout — it maps directly to the instructor's task (prioritise who to help next), supports at-a-glance scanning under time pressure, and keeps two parallel signals (struggle vs difficulty) side by side. Frame as an engineering decision tied to the in-lab use context, not preference.

> [!example]- R2 — drop-in draft (adapt to your voice)
> ```latex
> % Insert after l1196 (the "two key views" paragraph), before the figma2 figure.
> % First DELETE the abandoned fragment "The instructor is built around a" at l1251.
> The instructor view is built around a ranked table rather than a chart-led layout
> because the live-session task is one of prioritisation: deciding who to help next. A
> sorted leaderboard answers that question directly --- the most struggling student sits
> at the top --- whereas a scatter or heat-map would force the instructor to decode
> position into rank under time pressure. The tabular form also keeps the two signals
> side by side: struggle and difficulty are presented as parallel ranked lists, so the
> instructor moves between ``who is stuck'' and ``what is hard'' without switching visual
> idiom. Individual rows open into the per-student and per-question detail views for the
> cases that justify a closer look, leaving the default surface uncluttered.
> ```

## R3. Web app for the lab-assistant interface — rationale ✅ DONE 2026-05-31 (l1227–1230; your own version — no FastAPI leak, no "no functional gain" overclaim. Clean.)
- **Where:** `\subsubsection{Lab Assistant View}` — insert **after the opening paragraph at l1217** (which already says "mobile interface … handheld device" but does not defend the *web-app* choice), before the `figma4–6` assistant-views figure (l1219).
- **Write:** *why* a web app rather than a native mobile app: zero install on assistants' own devices, cross-platform (any phone/tablet), instant updates, and a single shared backend serving both surfaces via the same shared-state path (`lab_session.json`). Frame as accessibility + deployment simplicity.
- **⚠️ honesty/altitude (from R1's lesson):** (a) keep it **design-level** — don't name "FastAPI" or "single process" here; that's a V2 *implementation* detail (and untrue of V1, where the assistant ran as a separate Streamlit process on 8502). Say "a single backend". (b) **don't claim a native app gives "no functional gain"** — it genuinely could (push notifications on assignment vs the current ~5 s polling). Say native adds packaging/distribution cost for *little benefit here*, and note push as a possible future gain.

> [!example]- R3 — drop-in draft (adapt to your voice)
> ```latex
> % Insert after the Lab Assistant View opening paragraph (l1217), before the figma4--6 figure.
> The assistant interface is delivered as a responsive web application rather than a
> native mobile app. A web app installs nothing on the assistants' own devices and runs
> on any phone or tablet irrespective of platform, which matters when assistants rotate
> between sessions on whatever hardware they bring; changes ship to every device instantly
> without an app-store release; and a single backend serves both the instructor and
> assistant surfaces over the same file-locked shared state (\texttt{lab\_session.json}),
> rather than a separate mobile backend. A native build would add per-platform packaging
> and distribution for little benefit in this setting, where the assistant only needs a
> live list and a single assigned-student card; the main feature it would unlock --- push
> notifications on assignment, in place of the current short-interval polling --- is noted
> as possible future work rather than a requirement here.
> ```

## R4. Cosine vs Euclidean similarity — add the citation ✅ DONE 2026-05-31 (l734, manning cite attached; stray "s" + missing full stop fixed)
- **Where:** `\paragraph{Student Similarity Measure}` — **l731**. The justification already exists ("robust to differences in overall activity levels"); it just lacks a source.
- **Edit (author applies by hand):** append `\cite{manningIntroductionInformationRetrieval2006}` (already in `references.bib`) to the cosine-justification sentence at l731.

> [!example]- R4 — drop-in (one-line edit)
> ```latex
> % l731 --- append the citation to the END of the existing cosine sentence:
> ... making it robust to differences in overall activity levels between students \cite{manningIntroductionInformationRetrieval2006}.
> ```

## R5. OLS-vs-non-linear — short forward reference ✅ DONE
- **Where:** Struggle Score Definition — **l498–499**.
- **Status:** **already satisfied.** l498–499 already says the v1 weights were hand-set, re-fitted by OLS to give the deployed v2 default, that the v2 vectors are *signed and break the convex-combination constraint* (this also clears Note 04 **D3**), and forward-refs both `sec:v2-pipeline-design` and the model-class comparison in `sec:eval-results`. No action needed; *optionally* mirror one half-sentence in the Question Difficulty Model (l596) so the difficulty side reads symmetrically.

> [!example]- R5 — optional difficulty-side mirror (only if you want symmetry)
> ```latex
> % Optional --- one line in the Question Difficulty Model (l~596) mirroring the struggle side.
> % R5 is already DONE on the struggle side; add this only if the difficulty subsection lacks it.
> As with the struggle weights, the difficulty weights were initially hand-set for
> interpretability and then re-fitted by ordinary least squares against the rater labels;
> the trained vector is the deployed default (Section~\ref{sec:v2-pipeline-design}).
> ```

## R6. Collaborative-filtering concept paragraph ✅ DONE 2026-05-31 — concept para added (l704–705); cold-start cite intentionally OMITTED (koren = wrong topic, schafer not wanted; cold-start asserted without a source, as with R1). (supervisor pt 7)
- **Where:** `\subsubsection{Alternative Modelling Approach: Collaborative Filtering}` — **l701–807**.
- **Already present:** the `\paragraph{Motivation}` (l703–704) gives a plain-language lead-in ("rather than scoring each student in isolation, we explore similarity between students"), and cold-start is acknowledged in both the comparison table (l786, "Cold start: Requires ≥ k+1 active students") and the Justification paragraph (l796, "not reliable at the start of a session").
- **Write (optional sharpening):** if you want the reader to follow the maths without the lit review, expand the Motivation lead-in to 3–4 sentences making explicit that a struggling student often *resembles* peers who already crossed the help threshold, enabling earlier intervention.
- **⚠️ cite correction (2026-05-31):** **do NOT use `korenCollaborativeFilteringTemporal2010`** — that paper is about *temporal dynamics* (preference drift over time), not cold-start; it is a mismatch for the "not reliable at the start of a session" claim (same category of mis-cite as the R1 OECD one). **Use `schafer_2007_collaborative`** instead — a CF survey already in `references.bib` that explicitly covers the cold-start limitation. (Canonical dedicated cold-start ref = Schein et al. 2002, *not* in the bib; only validate in Zotero if you want the stronger source.)
- **Edit (author applies by hand):** append `\cite{schafer_2007_collaborative}` to the cold-start sentence at **l796** (ends "…not reliable at the start of a session."). k-NN CF basis already cited (`herlockerAlgorithmicFrameworkPerforming1999`, `resnickGroupLensOpenArchitecture1994`).
- **Status:** ⬜ NOT applied yet — saved file has zero koren/schafer cites at l796. (Bib housekeeping for Zotero: koren entry has `doy=` typo for `doi=` at references.bib:550 — fix in Zotero, not by hand.)

> [!example]- R6 — drop-in draft + one-line cite
> ```latex
> % Expand the CF \paragraph{Motivation} lead-in (l~703):
> Collaborative filtering infers a student's likely need for help not from their own
> behaviour in isolation but from the behaviour of peers with a similar interaction
> profile. A student who is beginning to struggle often resembles peers who have already
> crossed the help threshold; by borrowing the signal from those neighbours, the model can
> flag the student earlier than a purely self-referential score would. Similarity is
> measured over the same normalised interaction features used by the parametric model, so
> the two approaches operate on a common representation.
>
> % l796 --- append the citation at the cold-start point (schafer, NOT koren):
> ... whereas a collaborative filtering approach produces results that are not reliable at the start of a session \cite{schafer_2007_collaborative}.
> ```

## R7. RAG section framing ✅ DONE 2026-05-31 (l1088–1089, proof-of-concept framing added; "more serves"→"serves" typo fixed). Charlotte moot. Survey-count: author still to decide (see below).
- **Where:** `\subsection{Retrieval-Augmented Generation Feedback Design}` opening — **l1082–1086**.
- **Status check:** the opening is already *accurate* — it correctly says the design "grounds LLM output in the session's own submission history" and cites the hallucination-risk motivation. It is **not** generic/boilerplate (the earlier "trained on textbooks" report was tool corruption). Charlotte is **not** attributed here (she appears only in the Data-Endpoint figure caption, l364, which is correct) — so the "do not attribute RAG to Charlotte" item is **moot**.
- **Write (the genuine gap):** add the *framing* that RAG is a **proof-of-concept** layer (beyond the core struggle/difficulty models) evaluated **qualitatively** rather than against quantitative labels.
- **Open author decision — survey count:** the section makes **no** "three or four existing feedback approaches were surveyed" claim, and the deployed `rag.py` implements one design (it does not survey alternatives). So **do not invent a number.** Either (a) drop the survey-count framing entirely, or (b) add a 1–2 sentence survey of prior feedback/retrieval approaches and cite them — which overlaps [[10 Related Work & Research-Gap Expansion]]. Recommend (a) unless you want the related-work tie-in.

> [!example]- R7 — drop-in draft (proof-of-concept framing)
> ```latex
> % Add to the RAG opening (l~1084), after the "grounds LLM output ..." sentence:
> The retrieval-augmented layer is a proof-of-concept that sits above the struggle and
> difficulty models rather than a core contribution; it is evaluated qualitatively, by
> checking that its suggestions are grounded in the retrieved submissions, rather than
> against quantitative labels.
>
> % SURVEY COUNT --- DO NOT invent a number. Option (a): say nothing about "approaches surveyed".
> % Option (b), only if you add the prior-art tie-in (Revisions 10), adapt and cite REAL refs:
> % Several existing feedback approaches were considered --- \cite{...}, \cite{...} --- before
> % settling on retrieval grounded in the session's own submissions.
> ```

## Missing view designs (supervisor pt 9) — add to Ch3

### R8. Settings view design ✅ DONE 2026-05-31 — new `\subsubsection{Settings View}` inserted (l1268–1285) + `settings-view.png` figure (`fig: settings view`). Control list grounded in the real `SettingsView.tsx` (4 tabs: Appearance/Models/System/Advanced) and cross-checked against implementation.tex l1181, NOT the assumed draft list. (supervisor pt 9)
- **Where:** new `\subsubsection` under `\subsection{Interaction and UI Designs}` (l1175) — place it **immediately before `\subsubsection{Visual Encoding of Metrics}` (l1253)**, i.e. exactly where the abandoned l1251 fragment sits now (delete that fragment first).
- **Write:** the Settings interface design and its configurable options — model-choice (baseline vs improved), collaborative-filtering toggle + similarity-threshold τ, BKT parameter sliders, temporal-smoothing toggle, theme/refresh — with the *rationale* (instructor control over which signals drive the board; Bloomberg-terminal-style power-user toggles, defaults safe). Cross-reference the deployed Settings screenshot now in Appendix B. (Note: Settings is currently only mentioned in passing at l807 as "the Settings panel".)

> [!example]- R8 — drop-in draft (whole new subsubsection)
> ```latex
> % VERIFY the control list against the live Settings view before compiling --- ui-settings.png
> % is flagged stale in Revisions 12, so the deployed panel may differ from older screenshots.
> \subsubsection{Settings View}
> The Settings view collects the analytical choices that govern the two boards into one
> place, so the instructor decides which signals are trusted in a given session rather than
> the system imposing a fixed configuration. The available controls are:
> \begin{itemize}
>     \item \textbf{Model family} --- switch the struggle and difficulty scores between the
>           baseline parametric models and the improved, mastery-aware models (IRT, BKT and
>           the difficulty-adjusted struggle score);
>     \item \textbf{Collaborative filtering} --- enable or disable the peer-similarity
>           indicator and set the elevation threshold $\tau$ above which a peer counts as
>           struggling;
>     \item \textbf{Knowledge tracing} --- adjust the BKT parameters (prior mastery,
>           transition, guess and slip) that feed the mastery signal;
>     \item \textbf{Temporal smoothing} --- toggle the EWMA across refresh cycles and its
>           rate $\lambda$;
>     \item \textbf{Presentation} --- colour theme and refresh interval.
> \end{itemize}
> The defaults are chosen to be safe for an instructor who never opens the panel, while the
> toggles give a power user fine control in the spirit of a Bloomberg terminal. The deployed
> view is shown in Appendix~\ref{app:screenshots-settings}. % TODO: confirm Appendix B label; re-shoot ui-settings.png (Revisions 12)
> ```

### R9. Student-Detail & Question-Detail interface designs ✅ DONE 2026-05-31 (l1210–1217, \paragraph run-in headings; "rag suggestions"→"suggestions" fixed). NB: author kept the fuller element list rather than the lean trim — fine.
- **Where:** within `\subsubsection{Instructor Views}` — insert **after l1196**, following the R2 rationale (l1196 already says "the view also allows instructors to go over additional information" — these statements describe exactly that drill-down). The targets are referenced elsewhere only in passing (Student Detail l942, Question Detail l822/l1132).
- **Write:** a short interface-design statement for each drill-down target — what the **Student Detail** view shows (per-signal struggle breakdown, timeline, hardest questions, RAG card) and what the **Question Detail** view shows (difficulty + aggregated incorrectness, top strugglers, mistake clusters, RAG misconception bullets) — and *why* those elements answer the instructor's question. Cross-reference the Figma mockups (kept in Ch3) and the Appendix B screenshots.

> [!example]- R9 — drop-in draft (two design statements)
> ```latex
> % Insert in Instructor Views after l1196 (the "additional information" sentence), following the R2 rationale.
> \paragraph{Student Detail.} The Student Detail view answers a single question --- why is
> this student flagged? --- by decomposing the struggle score into its constituent signals:
> a per-signal breakdown shows which of submission rate, recent incorrectness, retries and
> the remaining signals are driving the score; a timeline tracks the score across the
> session; the student's hardest questions are listed; and a RAG card offers coaching
> prompts grounded in their own submissions for whoever attends the desk.
>
> \paragraph{Question Detail.} The Question Detail view answers the parallel question for
> tasks --- why is this question hard? --- pairing the difficulty score with the
> incorrectness aggregated over all attempts, the students currently most affected, the
> mistake clusters that group similar wrong answers (Section~\ref{sec: mistake clustering}),
> and RAG-generated misconception bullets the instructor can raise with the whole class.
> ```

## Mechanical citation edits — author applies by hand
Per your call (2026-05-31), these two are left for you to place rather than auto-applied:
- R4: append `\cite{manningIntroductionInformationRetrieval2006}` to the sentence ending "…activity levels between students." (l731).
- R6: append `\cite{korenCollaborativeFilteringTemporal2010}` to the sentence ending "…not reliable at the start of a session." (l805).
- Both keys pre-exist in `references.bib` (manning at l707, koren at l545); no `.bib` edit. Recompile (2 passes) afterwards to confirm no undefined cites.