# 08 — Data Protection (GDPR)

**Scope narrowed 2026-06-01:** this note now covers **only the GDPR / data-protection statement** — how the project complies through anonymised data and minimisation. The Loughborough ethics-approval reference is **out of scope** here (your steer); it is in any case **already covered** in the report — the NFR5 row of `appendix-sections/detailed-test-results.tex` records that ethical approval was granted through the University's LEON system. So nothing is missing on that front; this note is GDPR-only. The other "examiner-expected" candidates (reproducibility, comparison table, threats-to-validity, accessibility) are out of scope for this pass. ← [[00 Index]]

## The angle

A short, confident subsection showing the project was **data-protection-compliant by design**: it never held information that identifies a student, collected only what the analytics needed, and used the data solely for in-lab triage. Frame it around GDPR's core principles rather than a compliance checklist.

## Grounding — verified facts already in the report (build on these, don't contradict)

- **Data minimisation — only seven fields per record:** the parsed submission record carries `module, question, timestamp, student_answer, ai_feedback, session` and an **anonymised `user` code** ([implementation.tex:451](../../../../Report/main-sections/implementation.tex)). No name, email, or university ID number is ingested or stored.
- **Deliberately uncollected data:** demographic data and gaze patterns were available but **not used** ("we can get away without using… demographic data and gaze patterns", [requirements:20](../../../../Report/main-sections/requirements-specification.tex)).
- **No linkage:** "the anonymisation of student identifiers rules out grade linkage, and submission records cannot currently be mapped to individual lab seats" ([results:13](../../../../Report/main-sections/results-and-evaluation.tex)).
- **Anonymous survey:** "Participation was voluntary, anonymous, and the form recorded no personal identifiers" ([results:386](../../../../Report/main-sections/results-and-evaluation.tex)).
- **Instructor-facing only:** the dashboard is "never being surfaced to students themselves" ([results:423](../../../../Report/main-sections/results-and-evaluation.tex)); outputs are advisory, not decisional.
- **Privacy stated as a priority** in Ch2 ("protecting students' identities and data is a priority", [requirements:30](../../../../Report/main-sections/requirements-specification.tex)) and **NFR5 (Privacy & Ethics)** holds by construction (Appendix detailed-test-results).

## GDPR principles → how the project meets them (the content to write)

| GDPR principle | How the project satisfies it |
|---|---|
| **Lawfulness & purpose limitation** | Data used solely to surface struggling students / hard questions to instructors *during the lab* — not for grading, ranking, or any secondary purpose; outputs are advisory. |
| **Data minimisation** | Only the seven fields above; no names, emails, ID numbers, demographics, or biometric/gaze data. The incorrectness signal reads AI-feedback text, not student identity. |
| **Pseudonymisation (Art. 4(5))** | Students appear only as anonymised codes (e.g. `uo0752`). The system holds nothing that re-identifies them, and cannot link a code to a grade or a lab seat. |
| **Storage limitation** | Operates on the live/replayed session export; runtime artefacts live under `data/`. *(Confirm retention: caches such as `incorrectness_cache.json` persist — state that they hold no identifiers and are bound to the project.)* |
| **No automated decision-making with legal effect** | The dashboard recommends; the instructor decides (human-in-the-loop). No grade or sanction is produced automatically. |

## Honest limitation to include (keeps it consistent with §5.5 Q10)

The identifiers are **pseudonyms, not full anonymisation**: because a code persists across sessions, an instructor holding the class roster could in principle re-associate a repeat code with a person (the report already raises this — "even an anonymised student ID still lets the lecturer recognise the same struggler week after week", [results:437](../../../../Report/main-sections/results-and-evaluation.tex), and the reputation-effect risk at [results:444](../../../../Report/main-sections/results-and-evaluation.tex)). Treat this as a **deployment-policy** matter (informed consent, anonymisation review, a data-use scope statement) rather than a system flaw. Naming this *strengthens* the section — it shows GDPR-literate judgement rather than overclaiming "fully anonymous".

## Draft prose (adapt into Report/ — your voice; do not paste verbatim without a read)

> **Data Protection.** The system was built to be data-protection-compliant by design. It processes only the minimum needed to score struggle and difficulty: per submission, the module, question, timestamp, submitted answer, AI-feedback text, session, and an anonymised user code; no names, email addresses, university identification numbers, demographic attributes, or biometric data are collected or stored, and demographic and gaze data that some learning-analytics systems use were deliberately excluded. Students are represented throughout by pseudonymous codes, and the pipeline holds nothing that links a code to a grade, a timetable, or a lab seat, so no individual is identifiable from the data the system retains. The analytics serve a single purpose — helping instructors prioritise help within the live session — and never feed grading or any automated decision; every recommendation is advisory, with the instructor retaining the decision. The accompanying survey was voluntary and anonymous and recorded no personal identifiers. The one residual consideration is that the codes are pseudonyms rather than fully anonymous: because a code persists across weeks, an instructor with the class list could re-associate it with a student, so deployment should be accompanied by informed consent and a stated data-use scope.

## Placement

- **Primary home (recommended): extend the existing `\subsection{Graceful Degradation and Privacy}`** at `implementation.tex:1098` — it already states retrieval is local and that "no student identifier of any kind" is sent to the LLM (`:1103`–`:1105`); add the data-protection / anonymisation paragraph there so all privacy material sits together. (The data dictionary already calls `user` "the anonymised identifier", `design:381`.)
- Alternative home: a short **`\subsection{Data Protection}`** in the evaluation chapter near the survey's ethical-concerns discussion (§5.5), **or** repurpose the unmet `§5.5.1` heading flagged in [[01 Integrity & Consistency Fixes]] — rename it from "Ethical Approval" to **"Data Protection"** and fill it with this content. *(Confirm that heading still exists before renaming.)*
- ~1 paragraph (the draft above) plus, optionally, the principle→mechanism points as 3–4 sentences.

## To confirm before writing

1. **ID provenance:** are the user codes anonymised **at source** (platform/technician export) or hashed **in the pipeline**? The compliance claim holds either way (the system stores only the codes), but state it accurately.
2. **Retention:** confirm the persisted caches (`data/incorrectness_cache.json`, saved sessions) contain no identifiers and a one-line retention intent.
3. **Heading:** does the unmet `§5.5.1` "Ethical Approval" heading exist to rename, or add a fresh subsection?

## Definition of done

- ⬜ Author writes the Data-Protection subsection (from the draft above) into `Report/`.
- ⬜ Confirm the three points above.
- ⬜ Recompile clean; flip Note 08 in [[00 Index]] to ✅ (scope = GDPR only).
