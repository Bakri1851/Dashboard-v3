# Ch2 Survey-Motivating Literature — Drafting Plan

Companion to [[Ch5 – Results and Evaluation]] and [[Ch5 §5.5 Drafting Plan]] (not yet drafted). Built 2026-05-26 to give the survey findings of §5.5 a literature-review home in Ch2 so the findings *triangulate against* a prior literature base rather than appearing as raw primary data with no anchor.

## Why

Survey themes that recur across Q2–Q11 (instructor situational awareness, dashboard interpretability, algorithmic trust, surveillance ethics) all have a citable literature behind them. Ch2 currently touches on LA ethics in passing (line 25–26 `wilson_2017_learning, tzimas_2021_ethical`) and on instructor dashboards (§2.5.2 with `holstein*`) but does not pull these threads together at the level the survey findings warrant. This plan adds three paste-ready blocks to Ch2 that establish the prior-literature scaffolding §5.5 will cross-refer to.

## What stays in §5.5 vs what moves to Ch2

Survey **findings** (n=10 numbers, quoted free-text, themes) stay in §5.5 — they are primary data, not citable third-party claims. What moves to Ch2 are the **concepts** the findings echo, with citable literature behind them. §5.5 subsubsections then reference back to Ch2.

## Voice / convention

Match Ch2's voice — declarative, semicolon-joined, citation-heavy. Use the existing Ch2 paragraphs as the model (e.g. lines 230–248 are good templates for the new paragraphs).

## Citations needed (Phase 8 Zotero imports — all currently missing from `references.bib`)

| Bibkey | Reference | Used in |
|---|---|---|
| `sladeLearningAnalyticsEthical2013` | Slade & Prinsloo (2013) — "Learning Analytics: Ethical Issues and Dilemmas" | Block A |
| `pardoEthicalPrivacyPrinciples2014` | Pardo & Siemens (2014) — "Ethical and Privacy Principles for Learning Analytics" | Block A |
| `prinslooStudentVulnerabilityAgency2015` | Prinsloo & Slade (2015) — "Student vulnerability, agency, and learning analytics" | Block A |
| `leeTrustAutomationDesigning2004` | Lee & See (2004) — "Trust in Automation: Designing for Appropriate Reliance" | Block C |
| `verbertLearningAnalyticsDashboard2014` | Verbert et al. (2014) — "Learning analytics dashboard applications" (the systematic-review one) | Block B |

User runs `scripts/sync_literature.py` once these are in Zotero / `references.bib`.

---

## Block A — Ethics, privacy, and student agency (~140 words)

**Anchor**: extend the existing ethics paragraph in [`requirements-specification.tex:25`](../../../../Report/main-sections/requirements-specification.tex#L25–L26). The current text mentions privacy in one sentence with two citations (`wilson_2017_learning`, `tzimas_2021_ethical`); replace with the expanded version below.

**Paste-ready prose** (replaces the current two-line ethics passage at line 25–26):

```latex
Learning analytics also raises ethical concerns that go beyond the technical safeguards of anonymisation and access control. Slade and Prinsloo argue that the asymmetry of power between an institution that collects analytics and the students it observes raises distinct questions about consent, transparency, and the right to opt out, and they frame learning analytics as a moral practice rather than a purely technical one \cite{sladeLearningAnalyticsEthical2013}. Pardo and Siemens distil six ethical and privacy principles for the design of learning-analytics systems, including transparency about what is collected, student access to the same data the institution sees, and minimisation of the data that is retained beyond its immediate analytical purpose \cite{pardoEthicalPrivacyPrinciples2014}. Prinsloo and Slade further develop the argument that students themselves are vulnerable subjects of analytics and that the design of analytics systems must protect their agency, not merely their identity \cite{prinslooStudentVulnerabilityAgency2015}. These concerns recur in the survey findings of Section~\ref{sec:eval-survey}, where a minority of respondents reported discomfort with being scored under a per-student struggle metric and raised concerns about visibility of their difficulties to instructors; the dashboard's existing privacy invariants address the most cited technical concerns, but the comfort dimension is shown to be a residual ethical concern that technical privacy guarantees do not fully resolve.
```

---

## Block B — Instructor situational awareness in real-time labs (~150 words)

**Anchor**: extend the Holstein-citing paragraph in [`requirements-specification.tex:228`](../../../../Report/main-sections/requirements-specification.tex#L228). The current paragraph mentions Holstein in passing alongside Kiatxin progress-bar dashboards; the new version reframes the paragraph around the *situational-awareness gap* that Holstein documents directly.

**Paste-ready prose** (replaces the current paragraph at line 228, keeping the existing flow into the Piwik figure at line 230):

```latex
Existing learning dashboards, such as Blocks: Progress Bar, report on student progress rather than student struggle at the live lab level \cite{kiatxin_development}. Dashboards like these show user active time, assignment progress, learning progress, marks, and assignment submissions \cite{kiatxin_development}. Holstein, McLaren, and Aleven argue that the problem facing an instructor in a live classroom is not the absence of data but the absence of situational awareness; in their study of a real-time instructor-facing dashboard alongside an intelligent tutoring system, they found that instructors with the dashboard redirected attention more effectively than instructors without, identifying students who would otherwise have been missed and adjusting their classroom strategy mid-session \cite{holsteinIntelligentTutorsTeachers2017a,holsteinStudentLearningBenefits2018}. Verbert and colleagues' systematic review of learning-analytics dashboards reaches a similar conclusion: dashboards are most useful when they shorten the loop between observation and intervention, and least useful when they offload course-level analysis on which the instructor cannot act in the moment \cite{verbertLearningAnalyticsDashboard2014}. The survey of Section~\ref{sec:eval-survey} corroborates this picture; a majority of respondents reported difficulty identifying which students need help in a typical lab, and the free-text responses converged on staff shortage, quieter students, and help-seeking reluctance as the three principal barriers. Visual components such as the progress bar aid in the understanding of student progress, removing all the complexity that is going on behind the scenes; although these are useful, they do not directly surface students who are struggling in ways the instructor would otherwise miss.
```

---

## Block C — Dashboard interpretability and trust in algorithmic decision aid (~140 words)

**Anchor**: extend the MM-dashboard limitations paragraph in [`requirements-specification.tex:246`](../../../../Report/main-sections/requirements-specification.tex#L246–L248). The current paragraph notes that teachers lacked the knowledge to interpret the MM dashboard's metrics; the new version frames this as a special case of the broader algorithmic-trust literature.

**Paste-ready prose** (replaces the limitations paragraph at line 246–248):

```latex
However, the dashboards do come with a range of issues. For the MM dashboard to work, students must have a range of sensors, which are uncommon for them \cite{leecultura_2023_multimodal}. Teachers also report no experience with some of the hardware required for the MM dashboard to work. Although this is a key problem, it was not the MM dashboard's main issue; the main issue was that teachers may lack the knowledge to understand and interpret the dashboard results, as the majority of users reported unfamiliarity with the measurements provided. The importance of the metrics was also questioned \cite{leecultura_2023_multimodal}. The issue is not specific to the MM dashboard. Lee and See's foundational work on trust in automation establishes that user reliance on an automated decision aid is a function of perceived competence, perceived intent, and the user's ability to interpret the aid's reasoning, and that miscalibrated trust --- either over-reliance on an opaque system or under-reliance on a competent one --- is the dominant failure mode of decision-support systems \cite{leeTrustAutomationDesigning2004}. In educational contexts the lesson is that an interpretable composite score with a clear rationale is more likely to earn calibrated trust than an opaque model with higher headline accuracy; this motivates the linear, additive struggle composite of Chapter~\ref{sec:design} over a black-box alternative, and is corroborated by the trust ratings reported in Section~\ref{sec:eval-survey}. The study also noted that hands-on training may be required to help teachers use the system efficiently \cite{leecultura_2023_multimodal}.
```

---

## What §5.5 then references

Each survey subsubsection in §5.5 cross-refs the new Ch2 blocks rather than restating literature claims:

| §5.5 subsubsection | New Ch2 cross-ref |
|---|---|
| 5.5.2 Baseline Perception of Lab Support (Q2 + Q3 + Q4) | Block B (situational awareness) |
| 5.5.3 Dashboard Interpretability and Trust (Q5 + Q6 + Q7) | Block C (interpretability + trust) |
| 5.5.4 Student Comfort and Ethical Concerns (Q8 + Q9 + Q10) | Block A (ethics + privacy) |
| 5.5.5 Change Requests and Triangulation (Q11) | Triangulation pointer back to Blocks A/B/C |

This makes §5.5 lighter (it doesn't restate literature) and more defensible (each finding has a prior-literature anchor).

---

## Pre-paste checklist for the user

1. Phase 8 Zotero imports needed for 5 new bibkeys (see citations table above); after import, run `python scripts/sync_literature.py` to bring them into `references.bib`.
2. After pasting Block A, line 27–31 of the ethics passage already in Ch2 (the smart-device-integration paragraph) follows naturally; check the join.
3. After pasting Block B, the next paragraph at the existing line 230 is the Piwik figure block; check the join.
4. After pasting Block C, the existing Block C bridges into the "early warning systems" subsubsection at line 251; check the join.
5. After pasting, run `pdflatex Report/main.tex` twice and check the log for unresolved `\cite{}` warnings on the five new bibkeys (will warn until Phase 8 imports complete).

## Post-paste audit checklist (for me)

1. Confirm British spelling throughout; "tradeoff" not "trade-off".
2. Confirm `\ref{sec:eval-survey}` resolves (it does — the label exists on §5.5 in [`results-and-evaluation.tex:92`](../../../../Report/main-sections/results-and-evaluation.tex#L92)).
3. Confirm `\ref{sec:design}` resolves (Ch3 chapter-level label, confirmed).
4. Confirm no V1/V2 conflations in the new prose.
5. Confirm voice match — long sentences with semicolons, declarative, no hedging.
