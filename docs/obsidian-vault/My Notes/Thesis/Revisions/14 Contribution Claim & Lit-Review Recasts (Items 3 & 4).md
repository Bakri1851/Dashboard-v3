# 14 - Contribution Claim & Lit-Review Recasts (Items 3 & 4)

Author-writes briefs for the two prose Gap-to-A items from [[13 Marking & Gap-to-A Checklist]] (second-pass log, 2026-06-02). Items 1 (appendices) and 2 (proofreading) are closed; this note carries the proposed wording for **Item 3 (sharpen the contribution claim)** and **Item 4 (lift descriptive lit-review patches into analysis)**. Each location is a drop-down: expand it for the brief plus a copy-paste-ready LaTeX block. You write the final prose into `Report/`; nothing here has been applied. - [[00 Index]]

Both items target the **Cognitive band** (high-B -> A-), the one component holding the report off a clean A. The throughline to thread across the abstract, intro and conclusion is one claim:

> a live, session-scale, instructor-facing struggle- and difficulty-detection system, validated end-to-end against a scalable LLM second-opinion rater, with a documented negative finding (2PL IRT kappa = -0.024, retained not promoted).

## Figures to keep exact (do not paraphrase the numbers)

| Quantity | Value |
| --- | --- |
| Struggle Spearman rho | +0.588 |
| Difficulty Spearman rho | +0.468 |
| Struggle linear-weighted kappa | +0.384 |
| Difficulty linear-weighted kappa | +0.387 |
| 2PL IRT kappa | -0.024 (trained cutpoints) / -0.016 (hand-set) |
| IRT vs composite top-ten-hardest overlap | one question in ten |
| CF threshold tau | 0.7 -> 0.900, delta-rho = +0.160 |
| Shrinkage constant K | 5 -> 0, delta-rho = +0.009 (within per-fold SD) |
| OpenAI incorrectness fallback rate | 92.5% of 42,443 submissions |
| Rater fidelity ceiling (LLM vs human kappa) | +0.198 *(confirm against the results chapter before quoting the number)* |

---

## Item 3 - Sharpen the contribution claim

> [!example]- 3a. Abstract — `main.tex` ll.93-104 (insert after l.97)
> **Now:** para 1 (l.95-97) states the problem then lists system features; para 2 (l.99-102) goes straight to validation mechanics. The novel claim is never named crisply - it reads as "we built a dashboard".
> **Change:** insert one contribution sentence at the end of para 1 (after l.97), so para 2's mechanics land as evidence for a claim already stated. Leave l.102 (the IRT negative finding) as-is.
>
> ```latex
> The contribution is not the dashboard alone but a live, session-scale, instructor-facing capability for detecting student struggle and question difficulty, whose every tunable component is trained and tested end-to-end against a scalable large language model second-opinion rater, and reported together with a documented negative finding rather than only its successes.
> ```
>
> *Optional shorter alternative:* change l.96's verb "This thesis presents a real-time learning analytics dashboard" -> "This thesis contributes a real-time learning analytics dashboard" - a one-word lift that reframes the artefact as a contribution.

> [!example]- 3b. Introduction §1.3, Aims and Objectives — `introduction.tex` ll.43-62
> **Now:** primary aim (l.46) is framed as system-building; the closing sentence (l.62) is generic ("a full-fledged EdTech application"). Objective 5 (l.57) already names the training-against-rater work - leave it.
> **Change:** (i) widen the primary aim (l.46) to include validation + the concrete capability; (ii) replace the closing sentence (l.62) with a contribution statement that previews the conclusion.
>
> **Recast l.46:**
>
> ```latex
> The primary aim of this project was to design, implement and empirically validate a system that enables lab teachers and lab assistants to make more well-informed decisions during computer lab sessions, by detecting in real time which students are struggling and which questions are causing the most difficulty.
> ```
>
> **Replace l.62:**
>
> ```latex
> Together these objectives produced not only the deployed system but the central contribution of this thesis: a systematic, end-to-end validation of its struggle and difficulty scores against a scalable large language model second-opinion rater, reporting positive and negative findings on equal footing, including a documented negative result for the Item Response Theory difficulty model that is retained as a complementary view rather than promoted to the deployed scorer.
> ```

> [!example]- 3c. Conclusion §5.2, Key Findings and Contributions — `conclusion.tex` ll.22-44
> **Now:** strongest of the three, but it opens (l.24) on the *first contribution* (systematic validation) and never foregrounds that the thing validated is a live, session-scale, instructor-facing system.
> **Change:** add a two-sentence lead immediately after the `\subsection` heading (before l.24) naming the system as the overarching deliverable, with the two existing contributions (validation l.24, methodology l.36) substantiating it. No change to ll.24-44.
>
> ```latex
> This project delivers a live, session-scale, instructor-facing system that detects student struggle and question difficulty during a computer lab session; its novelty lies not in any single signal but in integrating them and validating the result end-to-end against a scalable second-opinion rater. The thesis makes two contributions, both substantiating that system rather than asserting it.
> ```

> [!example]- 3d. Publication-scope line (new) — end of §5.2 or lead of future work
> **Now:** the limitations are honest but scattered across future-work paragraphs (`conclusion.tex` ll.59-76; `results-and-evaluation.tex` l.70). No single sentence converts them into a controlled scope statement.
> **Change:** add one sentence that bounds the claim and names the route to a general result - turning the single-rater / single-module / retrospective limitations into the defined scope conditions of a stronger claim.
>
> ```latex
> The claim defended here is deliberately bounded by its evaluation design: validation against a single large language model rater on one module's retrospectively replayed data, where the rater's own agreement with human judgement ($\kappa = +0.198$) sets a ceiling on the achievable scores. Establishing the result as a general finding would additionally require validation against human-labelled ratings and across multiple modules, together with a prospective intervention study comparing dashboard-informed decisions against a control group on student outcomes; these are the scope conditions of a publication rather than gaps in the present contribution.
> ```
>
> *If the kappa = +0.198 figure cannot be confirmed quickly, drop the parenthetical and keep "the rater's own agreement with human judgement sets a ceiling on the achievable scores."*

---

## Item 4 - Lift descriptive lit-review patches into analysis

Pattern to apply (borrowed from the A-grade §2.6, e.g. ll.361-364 "X has been studied as A ... but not as B"): turn "X did Y. Z found W." into "X found A, but did not address B, which this project does." **Leave §2.6 untouched.**

> [!example]- 4a. §2.1 Learning Analytics in Higher Education — `requirements-specification.tex` ll.13-30
> **Now:** ll.13-16 are definitional (l.16 duplicates l.15's clause - delete it). The data-sources paragraph (ll.18-22) and outputs/limitations paragraph (ll.24-30) describe findings without turning them on the project's gap.
> **Change:** keep the opening definitions (ll.13-15); delete redundant l.16; recast the two body paragraphs into the analytical voice. All citation keys preserved.
>
> **Recast the data-sources paragraph (ll.18-22):**
>
> ```latex
> Learning analytics draws on a range of data sources: Vieira et al. survey Massive Open Online Courses (MOOCs), clickstream records of interactions such as clicks and time spent, and course content \cite{vieira_2018_visual}. They find that, although combining data types is argued to serve learning outcomes more effectively, the majority of studies still rely on a single source \cite{vieira_2018_visual}. What this body of work does not address is the live computer-lab session: the source that matters there is neither retrospective clickstream nor demographic or gaze data, but the stream of code submissions a student produces while working, which this project takes as its primary signal.
> ```
>
> **Recast the outputs/limitations paragraph (ll.24-30):**
>
> ```latex
> The outputs of learning analytics have proven valuable for pedagogical decision-making, from tailoring recommendations to students' behavioural profiles \cite{vieira_2018_visual} to confirming, in the VITAL project, that flipped-classroom delivery worked because students engaged with materials before face-to-face sessions \cite{gelan_2018_affordances}. Wilson et al. caution, however, that such systems read observable behaviours such as clicks and time online rather than the cognitive processes beneath them \cite{wilson_2017_learning}, and that moving analytics beyond the controlled setting raises privacy concerns \cite{wilson_2017_learning,tzimas_2021_ethical}. This project addresses the first limitation directly by inferring struggle from submission behaviour as the session unfolds, when an instructor can still act, and respects the second by operating only on in-session submission data without demographic or biometric profiling.
> ```

> [!example]- 4b. §2.5 Existing Systems (LMS + Instructor dashboards) — `requirements-specification.tex` ll.246-255
> **Now:** the LMS paragraphs (ll.247-249) describe then bolt on limitations; the Instructor-Facing Dashboards paragraphs (ll.253-255) describe then trail off ("and students struggle", l.255). The recast also clears grammar slips ("A limitation ... are", "A notable learning management systems is", "long-time planning").
> **Change:** recast the LMS block (ll.247-249) into a tight describe-then-gap pair, and the dashboards block (ll.253-255) into the "report progress, not struggle" gap turn. All citation keys preserved; the figure at l.257 is untouched.
>
> **Recast the LMS block (ll.247-249), under the existing `\subsubsection{Learning Management System}`:**
>
> ```latex
> A learning management system administers, tracks and delivers educational courses and materials \cite{wikipediacontributors_2019_learning_management_systems}; such systems hold the largest share of the learning-systems market, almost every higher-education institution has adopted one, and Moodle is the most widely used \cite{wikipediacontributors_2019_learning_management_systems}. They were designed to surface training and learning gaps through analytical reporting, but that reporting has two properties that matter here: it is reviewed after an activity has finished, so a student who struggled in a lab may already have left without timely help, and it is pitched at the level of the course. Course-level reporting is well suited to curriculum design and long-term planning; it is not suited to the live lab, where support is only useful before the student moves on. It is precisely this gap that the present work targets.
> ```
>
> **Recast the Instructor-Facing Dashboards block (ll.253-255):**
>
> ```latex
> Learning management systems commonly incorporate dashboards that visualise student progress so that teachers can locate knowledge gaps \cite{kiatxin_development}; the dashboard has become the central output of learning analytics. Existing examples such as Blocks: Progress Bar report active time, assignment progress, marks and submission counts \cite{kiatxin_development,holsteinIntelligentTutorsTeachers2017a,holsteinStudentLearningBenefits2018}, and a visual component such as a progress bar makes a student's position legible at a glance. What they report, however, is how far a student has progressed, not whether a student is struggling, and they do so at the course level rather than the live lab. This project keeps the dashboard as the natural home for learning analytics but reorients it from progress tracking towards real-time struggle and difficulty within the session itself.
> ```

---

## Author checklist

- [ ] 3a abstract: insert contribution sentence after l.97 (or apply the one-word l.96 lift)
- [ ] 3b intro: recast primary aim (l.46) + replace closing sentence (l.62)
- [ ] 3c conclusion: insert two-sentence lead before l.24
- [ ] 3d publication-scope line: place at end of §5.2 / lead of future work; confirm kappa = +0.198 first
- [ ] 4a §2.1: delete redundant l.16; recast ll.18-22 and ll.24-30
- [ ] 4b §2.5: recast LMS block (ll.247-249) and dashboards block (ll.253-255)
- [ ] rebuild and check no new overfull boxes or broken cites

All proposed wording uses British spelling, plain hyphens, declarative voice with semicolons, and the exact figures above. Line numbers are current as of 2026-06-02; re-confirm at edit time since earlier edits in the same file shift them.
