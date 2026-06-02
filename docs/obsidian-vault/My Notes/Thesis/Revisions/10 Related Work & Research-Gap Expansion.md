# 10 - Related Work & Research-Gap Expansion

> **Status: closed 2026-06-01.** Applied to Report/: new §2.6 "Real-Time Classroom Support Systems" subsubsection + comparison table (`tab:rt-systems`), §2.7 reframed to the integration-gap narrative, and the themes-and-references appendix index. 6 CORE refs added to `.bib` (Diana, ClassAid, Kaliisa, Feng, Li, Tabib); the 8 deferred refs remain parked below for later enrichment.

High-leverage prior-art scan, now **web-verified** (two read-only verification sweeps, Feb-2026 literature included; every candidate below was resolved against a canonical DOI/arXiv record, with an adversarial second pass on the 2025/2026 items). Answers the supervisor's two follow-up questions: **(1) is anyone doing what we do?** and **(2) does Research Gaps (§2.7) need expanding?** <- [[00 Index]]

> **No-hallucination note:** all candidate references are still flagged **must-verify in Zotero** before any `.bib` entry; I do **not** edit `references.bib`. Verification here means each id was resolved against arXiv/DOI/DBLP/Semantic Scholar, but the canonical authority for the export is your Zotero + Better BibTeX. See [[07 Citations - wire orphans + Candidate References]] for the workflow. After validation + export, re-run `python scripts/sync_literature.py`.

> **Bib state checked 2026-06-01:** only the Lumilo/Holstein pair is already in `references.bib` (`holsteinIntelligentTutorsTeachers2017a` l471, `holsteinStudentLearningBenefits2018` l488). The other CORE refs are all absent and must be added in Zotero. §2.7 *Research Gaps* is at `requirements-specification.tex:317-339` (P-intro ~l319-321 with the integration-gap seed already at l321; P-lab ~l323-324; signal/detection gaps l326-332; delivery gap l334-339). §2.6 *Existing Systems* is ~l240-315.

---

## Verification verdicts at a glance

| Candidate | Verdict | Canonical id |
|---|---|---|
| Diana et al. (LAK 2017) | VERIFIED (DOI matches) | `10.1145/3027385.3027441` |
| Gao et al. (EDM 2024) | VERIFIED | `10.5281/zenodo.12729866` |
| OHQ (Penn Labs) | VERIFIED (software) | `https://ohq.io/` |
| Submitty (RPI) | VERIFIED (software) | `https://submitty.org/` |
| ClassAid (CHI 2026) | VERIFIED (both ids resolve) | `10.1145/3772318.3790824` / arXiv:2602.06734 |
| Li et al. (2025) | VERIFIED | arXiv:2512.18880 |
| Schwartz et al. (ECAI 2025) | VERIFIED | `10.3233/FAIA251230` / arXiv:2508.17353 |
| VizGroup (UIST 2024) | VERIFIED | `10.1145/3654777.3676347` / arXiv:2404.08743 |
| "Lumilo 2 (AIED 2024)" | **DROP** | mis-attributed: AIED 2025, demo track, Holstein/McLaren not authors, no DOI |
| "Konscia" | **FLAG name** | resolves to Holstein et al. 2019 JLA `10.18608/jla.2019.62.3`; confirm the product name |
| SPARK (Yang et al.) | **FLAG venue** | real arXiv:2601.22256; VL/HCC acceptance unconfirmed |
| Hoyl (Synthetic Responses) | **DROP** | Stanford EDS capstone, not peer-reviewed |

---

## (1) Is anyone doing what we do?

**Verdict: the full intersection is an unfilled niche, but every individual ingredient now has prior art.** All eight discovery angles independently reported that **no single recent system combines all six thesis ingredients** - live struggle-from-logs + an LLM-derived per-submission correctness signal + separate IRT/BKT difficulty ranking + cohort mistake-clustering + RAG-grounded feedback + mobile dispatch of a **human** assistant. The contribution must therefore be framed as the **integration plus the human-advisory dispatch loop**, not as per-component novelty; a per-component "no one does this" claim would not survive a viva.

### Closest competitors (cite + distinguish)
1. **Diana et al. (LAK 2017) - the single closest historical system.** A real-time, instructor-facing dashboard for interactive programming assignments that predicts which students need help from live program-state logs. **Correction:** the *automatic peer-tutor matching* is a **separate** Diana & Eagle paper, not this LAK 2017 dashboard; cite LAK 2017 for the live prediction/visualisation and treat peer-matching as an adjacent strand. *We differ:* dispatch dedicated lab assistants via a mobile channel; LLM-derived per-submission correctness signal; separate question-difficulty ranking; 2PL IRT + BKT; mistake clustering; RAG.
2. **ClassAid (Zhang, Sun, Xia, Liang - CHI 2026) - most threatening on recency and orchestration.** An "Instructor-AI-Student Orchestration" dashboard; instructors monitor student-AI interaction live and switch AI-TA feedback modes (technical / heuristic / automatic / silent); evaluated with 54 students and 8 educators. **Correction:** it is **instructor-in-the-loop**, so the old "we are advisory, it is not" line is wrong. *We differ on the true axes:* it dispatches an **AI agent** to the student, we dispatch a **human assistant**; no separate IRT/BKT difficulty ranking; no cohort mistake-clustering; LLM used as a feedback-agent, not as a correctness *signal*.
3. **Lumilo / Holstein (AIED 2018; JLA 2019) - already in the `.bib`, re-engage as a competitor.** Real-time per-student detector state + BKT mastery on mixed-reality glasses - the "smart device for lab assistance" the thesis motivates in FR6. **Drop the FR6 hardware-novelty framing: MR glasses already exist via Lumilo** (see [[01 Integrity & Consistency Fixes]] I4 and P6 below). *We differ:* platform-agnostic (generic logs + LLM, no instrumented ITS); separate difficulty ranking; mistake clustering; RAG; multi-assistant dispatch.
4. **Closing the Loop (Phung et al. - SIGCSE 2026) - closest on the human-escalation axis.** A hybrid AI-hint system that escalates to a **human instructor** when a student rates a hint unhelpful (82 students, 673 hints, 22% escalated). *We differ:* escalation is **student-initiated and reactive**; ours is **proactive dispatch off an automatically-detected** struggle ranking; no difficulty ranking or clustering.
5. **Co-Orchestration / Balancing Agency (Yang et al. - CSCW 2026) - closest on real-time orchestration + KT.** A real-time co-orchestration dashboard that models mastery with **BKT** and alerts teachers to disengagement, suggesting **dynamic peer pairing**. *We differ:* it pairs **peers** in an algebra ITS; ours routes a **human assistant** in an open programming lab off an LLM-plus-IRT/BKT signal.
6. **Office-hours queue work (Gao et al. EDM 2024; OHQ Penn Labs; Submitty) - closest on the dispatch axis.** Prioritise *who a TA helps next* from a **self-declared queue** (Gao simulates FIFO vs New-Student-First; OHQ/Submitty are deployed tools). *We differ:* struggle-**driven** dispatch from live logs reaches the shy student who never joins a queue - the thesis's core motivation; queue work is detection-free.

### The wider landscape (each ingredient has prior art - name a few, do not claim novelty)
- Real-time programming dashboards: Diana, VizGroup (UIST 2024), SPARK (arXiv preprint, venue pending).
- LLM-in-the-loop orchestration: ClassAid, Closing the Loop, Co-Orchestration.
- Live struggle on smart devices: Lumilo, Holstein 2019 JLA, SensEmo (smartwatch affect).
- TA/help dispatch: Gao, OHQ, Submitty, VTutor (multi-screen monitoring), Sticky Help (attention allocation).
- LLM correctness signal: Duan et al. (KC-level labeling), Jukiewicz, Oli et al.
- LLM + IRT/BKT difficulty: Li et al. and Tabib et al. (both warn LLMs misjudge difficulty -> motivates fusing the LLM signal with IRT/BKT rather than trusting the LLM alone), SMART, Zotos et al., Sun (hierarchical BKT).
- Live mistake clustering: Strickroth et al. (ITiCSE 2024), McMining, SANN (Hoq et al.), Heickal & Lan.
- RAG feedback for tutors: YA-TA, KITE, Scholz et al., SteLLA.
- Struggle prediction over history (not live): Schwartz et al. (ECAI 2025).

---

## (2) Does §2.7 (Research Gaps) need expanding? - YES

The current §2.7 reads as "no one monitors labs live and dispatches help", which the verified work makes **falsifiable**. **Reframe from an *absence* argument to an *integration-gap* argument**, and actively position against the orchestration/dispatch literature it currently ignores. The survey evidence makes this defensible: Kaliisa et al. (LAK 2024 Best Paper) find learning-analytics dashboards have shown **no strong achievement gains**, and Feng et al. (2023 meta-analysis) find teacher **awareness** is necessary but not sufficient - **action** is the open problem. This also executes the author's own P1-P6 TODOs in the section.

### Deliverable 3 brief - §2.7 reframe (author writes prose; British / declarative / semicolons / plain hyphens; gated before->after diff for every `Report/` edit)
- **P-intro (l319-321):** retain the methods-inventory sentence; add one sentence conceding that real-time programming dashboards and orchestration tools now exist (Diana, VizGroup, ClassAid) and one citing the survey evidence that passive dashboards have not delivered achievement gains (Kaliisa 2024) -> the opportunity is integration plus action, not a new component. Keep the existing "the gap ... lie at their intersection" seed at l321.
- **P-lab (l323-324):** keep the shy-student / hands-up / end-of-lab-data live-timing gap; cite Diana (LAK 2017) and the office-hours-queue work (Gao 2024, OHQ, Submitty) as the nearest live-lab dispatch precedents that still rely on opt-in or arrival order.
- **P3 (l326-329), split + sharpen:** (a) LLM-as-judge as a per-submission **correctness signal** feeding struggle/difficulty (contrast ClassAid's feedback-agent use; cite Li 2025 and Tabib 2025 that LLMs misjudge difficulty -> motivates IRT/BKT fusion); (b) course-level vs live-session struggle (Estey already cited at `estey_2017_automatically`; add Schwartz 2025 as history-based prediction); (c) CF in real-time labs (existing point, retained).
- **P4 (NEW, after l331):** instructor-facing **aggregate interpretability** gap - IRT/BKT live inside ITSs (Lumilo, Co-Orchestration) drive adaptation, not surfaced to an instructor as a class-level mastery/difficulty view beside a live struggle ranking; live cohort mistake-clustering for whole-class teaching moments is near-absent (Strickroth 2024 is the closest, and clusters to generate feedback rather than for instructor-facing diagnosis).
- **P5 (NEW, most important):** real-time **orchestration and dispatch** gap. Prior live tools surface awareness without routing a human (Lumilo, MM dashboard, VizGroup), dispatch an **AI agent** (ClassAid), escalate on **student request** (Closing the Loop), match **peers** (Diana, Co-Orchestration), or order a **self-declared queue** (Gao, OHQ, Submitty). None route a **human lab assistant** off an **automatically-detected** struggle ranking via a **mobile** channel, advisory and instructor-in-the-loop. Cite Feng 2023 for "awareness is necessary but not sufficient - action is the open problem".
- **P6 (smart-device, reframed, l334-337):** drop the hardware-novelty framing (MR glasses precede this via Lumilo / Holstein 2019); reframe as a **lightweight, instrumentation-free** assistant channel needing no per-student sensors and no instrumented ITS; cite Pitts 2025 that human-in-the-loop beats full automation. FR6's heavier wearable ambition -> Ch6 future work.
- **P7 (NEW synthesis, l339):** live timing + interpretable struggle/difficulty + cohort mistake patterns + grounded LLM feedback + human-assistant dispatch = one integrated affordance no prior system provides; forward-reference the Appendix E4 table.

### Deliverable 2 brief - expand §2.6 (Existing Systems)

> **Structure decided 2026-06-01:** this is a **dedicated subsubsection** placed **last in §2.6**, immediately before `\subsection{Research Gaps}` (l317), titled **"Real-Time Classroom Support Systems"**. The §2.6 intro generalisation (l242-244, "course-level... after the fact") is rescoped to the older classes. Because the systems are now reviewed here, the §2.7 **P5** descriptive paragraph is dropped; §2.7 keeps only the gap framing (P-intro / P3a / P6 / P7).
>
> **Trimmed to in-bib sources 2026-06-01 (interest of time):** the authored subsubsection + comparison table use ONLY refs already in `.bib` - Diana (`dianaInstructorDashboardRealtime2017`), ClassAid (`zhangClassAidRealtimeInstructorAIStudent2026`), Lumilo (`holsteinIntelligentTutorsTeachers2017a`, `holsteinStudentLearningBenefits2018`), the MM dashboard (`leecultura_2023_multimodal`), and Feng (`fengEffectivenessFunctionsClassroom2023`) for the orchestration-meta-analysis framing. The comparison table is a **self-contained compact inline table** (`tab:rt-systems`, 5 rows: this work + Diana + ClassAid + Lumilo + MM dashboard) - **no Appendix E4 split, no forward-ref**, so nothing dangles. The 8 deferred refs (VizGroup, Holstein-2019, Gao, OHQ, Submitty, Closing-the-Loop, Co-Orchestration, Strickroth) and the fuller appendix table remain optional for later. Prose authored and handed to the user 2026-06-01; compiles clean against the current `.bib`.

Add a new subsubsection after "Instructor Facing Dashboards" (the MM dashboard sits at l266-275), e.g. **"Real-Time Programming Dashboards"**, with 2-3 short declarative paragraphs:
- **Diana et al. (LAK 2017):** a real-time instructor dashboard for interactive programming assignments that predicts which students need help from live program-state logs; the same group's separate work matches low performers to high-performing peer tutors. State plainly it is the earliest system to close a monitor-then-act loop in this setting.
- **VizGroup (UIST 2024):** an LLM-assisted, event-driven dashboard surfacing real-time collaboration analytics and alerts to instructors in large programming classes.
- **ClassAid (CHI 2026):** an instructor-AI-student orchestration system; instructors monitor student-AI interaction live and switch AI-TA feedback modes - note its instructor-in-the-loop design explicitly.
- Close with the limitation that motivates §2.7: these surface awareness or route AI agents/peers, but none rank struggle from an automatically-derived per-submission correctness signal and dispatch a human assistant.
- Keep the MM dashboard (`leecultura_2023_multimodal`) and at-risk material as-is; the surveys (Kaliisa, Feng) belong in §2.7, not §2.6.

---

## Deliverable 4 - Appendix E4 comparison-table skeleton (feeds [[08 Examiner-Expected Sections]] E4)

Author the final cells; the values below are a verified starting point (Y / N / partial). The table is wide - use a landscape `longtable` or a `\resizebox{\textwidth}` `tabular`. The **"This dashboard"** row is the only one Y across struggle-rank + separate-difficulty + IRT/BKT + clustering + human-assistant + mobile + advisory; that single visual contrast *is* the contribution.

**Columns:** System (year, venue) | Setting (live-lab / course / offline) | Real-time? | Signal source | Ranks struggle? | Ranks difficulty separately? | Interpretable model | Mistake clustering? | Dispatch type | Dispatch device | LLM/RAG coaching? | Autonomy | Domain.

**Row values (verify before publishing):**
- **This dashboard** | live-lab | Y | logs + LLM correctness | Y | Y | IRT + BKT | Y | human assistant | mobile | Y (RAG) | advisory | programming labs
- **Diana (LAK '17)** | live-lab | Y | program-state logs | Y (predicts need) | N | none | N | peer (separate work) | desktop | N | advisory | programming
- **ClassAid (CHI '26)** | live-class | Y | LLM + interaction | partial | N | none | N | AI agent | desktop | Y (LLM) | advisory (instructor-controlled) | programming
- **VizGroup (UIST '24)** | live-class | Y | logs + LLM events | N (collab patterns) | N | none | N | awareness only | desktop | partial | advisory | programming
- **Lumilo + Holstein '19** | live-class | Y | ITS detectors + BKT | partial (detector state) | N | BKT | N | awareness only | MR glasses | N | advisory | ITS (maths)
- **Closing the Loop (SIGCSE '26)** | live | Y | student escalation + LLM | N (reactive) | N | none | N | human instructor (escalation) | desktop | Y (LLM hints) | advisory | programming / data sci
- **Co-Orchestration (CSCW '26)** | live-class | Y | BKT + rules | partial | N | BKT | N | peer pairing | desktop/tablet | N | advisory | algebra ITS
- **MM dashboard** | live-class | Y | sensors (eye/wrist/cam) | partial | N | none | N | awareness only | desktop | N | advisory | general
- **Office-hours queue (Gao / OHQ / Submitty)** | live | Y | self-declared queue | N (arrival order) | N | none | N | human TA (queue) | desktop/mobile | N | n/a | programming
- **Strickroth (ITiCSE '24)** | live-coding | Y | submission clustering | N | N | none | Y (clusters) | awareness / feedback | desktop | N | advisory | programming

Minimal LaTeX scaffold to adapt (author fills cells, places in the appendix per [[08 Examiner-Expected Sections]]):
```latex
\begin{landscape}
\begin{longtable}{p{2.6cm}*{12}{c}}
\caption{Comparison of real-time classroom struggle/dispatch systems.}\label{tab:e4-comparison}\\
\hline
System & Setting & RT & Signal & Strug. & Diff. & Model & Clust. & Dispatch & Device & LLM/RAG & Auto. \\
\hline
\endhead
This dashboard & live-lab & Y & logs+LLM & Y & Y & IRT+BKT & Y & human & mobile & Y & advis. \\
% ... one row per system above ...
\hline
\end{longtable}
\end{landscape}
```

---

## CORE candidate references - wire into §2.6 / §2.7 / E4 (all must-verify in Zotero)

Proposed BibTeX below uses **descriptive** keys; the final `\cite{}` keys come from your Better BibTeX export. Add by DOI/arXiv id in Zotero (it fetches canonical metadata), then diff against these.

### Bib status (updated 2026-06-01 - refs added to Zotero)

**In `references.bib` now (7), use these real Better BibTeX keys:**

| Paper | `\cite{}` key | §2.7 use |
|---|---|---|
| Diana (LAK 2017) | `dianaInstructorDashboardRealtime2017` | §2.6 + P-lab |
| ClassAid (CHI 2026) | `zhangClassAidRealtimeInstructorAIStudent2026` | §2.6 + P3a + P5 |
| Kaliisa (LAK 2024) | `kaliisaHaveLearningAnalytics2024` | P-intro + P5 |
| Feng (C&E 2023) | `fengEffectivenessFunctionsClassroom2023` | P5 |
| Li et al. (2025) | `liCanLLMsEstimate2025` | P3a |
| Tabib & Deedar (2025) | `tabibTrustworthyDifficultyAssessments2025` | P3a |
| Pitts (2025) | `pitts_a` | **already in `.bib` and already cited at l327**; reuse at P6 |

These 7 are enough to author the **§2.7 reframe core** (P-intro / P3a / P5 / P6).

**Still to add to Zotero (9)** - needed for the §2.6 expansion (VizGroup) and the full E4 table / office-hours-queue point (Gao, OHQ, Submitty): VizGroup, Gao, OHQ, Submitty, Closing-the-Loop (Phung), Co-Orchestration (Yang), Strickroth, Schwartz, Holstein-2019-JLA.

**Diana et al. 2017** - LAK '17 dashboard [§2.6 + §2.7 P-lab + E4]
```bibtex
@inproceedings{diana2017instructor,
  title     = {An Instructor Dashboard for Real-Time Analytics in Interactive Programming Assignments},
  author    = {Diana, Nicholas and Eagle, Michael and Stamper, John C. and Grover, Shuchi and Bienkowski, Marie A. and Basu, Satabdi},
  booktitle = {Proceedings of the Seventh International Learning Analytics and Knowledge Conference (LAK '17)},
  pages     = {272--279},
  year      = {2017},
  publisher = {ACM},
  doi       = {10.1145/3027385.3027441}
}
```

**ClassAid (Zhang et al.) 2026** - CHI '26 [§2.6 + §2.7 P3a/P5 + E4]
```bibtex
@inproceedings{zhang2026classaid,
  title     = {ClassAid: A Real-time Instructor-AI-Student Orchestration System for Classroom Programming Activities},
  author    = {Zhang, Gefei and Sun, Guodao and Xia, Meng and Liang, Ronghua},
  booktitle = {Proceedings of the 2026 CHI Conference on Human Factors in Computing Systems (CHI '26)},
  year      = {2026},
  address   = {Barcelona, Spain},
  doi       = {10.1145/3772318.3790824},
  note      = {arXiv:2602.06734}
}
```

**VizGroup (Tang et al.) 2024** - UIST '24 [§2.6 + §2.7 P4/P5 + E4]
```bibtex
@inproceedings{tang2024vizgroup,
  title     = {VizGroup: An AI-Assisted Event-Driven System for Real-Time Collaborative Programming Learning Analytics},
  author    = {Tang, Xiaohang and Wong, Sam and Pu, Kevin and Chen, Xi and Yang, Yalong and Chen, Yan},
  booktitle = {Proceedings of the 37th Annual ACM Symposium on User Interface Software and Technology (UIST '24)},
  year      = {2024},
  publisher = {ACM},
  doi       = {10.1145/3654777.3676347},
  note      = {arXiv:2404.08743}
}
```

**Closing the Loop (Phung et al.) 2026** - SIGCSE '26 [§2.7 P5 + E4]
```bibtex
@inproceedings{phung2026closing,
  title     = {Closing the Loop: An Instructor-in-the-Loop AI Assistance System for Supporting Student Help-Seeking in Programming Education},
  author    = {Phung, Tung and Choi, Heeryung and Wu, Mengyan and Brooks, Christopher and Gulwani, Sumit and Singla, Adish},
  booktitle = {Proceedings of the 57th ACM Technical Symposium on Computer Science Education (SIGCSE TS '26)},
  year      = {2026},
  publisher = {ACM},
  doi       = {10.1145/3770762.3772612},
  note      = {arXiv:2510.14457}
}
```

**Co-Orchestration (Yang et al.) 2026** - CSCW '26 (confirm venue) [§2.7 P4/P5 + E4]
```bibtex
@inproceedings{yang2026balancing,
  title     = {Balancing Teacher and Student Agency: Co-Orchestration Tool Design Supporting Real-Time Dynamic Pairing},
  author    = {Yang, Kexin Bella and Liu, Menghan and Xu, Liyi and Rummel, Nikol and Aleven, Vincent},
  booktitle = {Proceedings of the ACM on Human-Computer Interaction (CSCW '26)},
  year      = {2026},
  note      = {arXiv:2605.18761; CSCW 2026 venue to confirm}
}
```

**Gao et al. 2024** - EDM '24 office-hours queue [§2.7 P-lab/P5 + E4]
```bibtex
@inproceedings{gao2024who,
  title     = {Who Should I Help Next? Simulation of Office Hours Queue Scheduling Strategy in a CS2 Course},
  author    = {Gao, Zhikai and Silva de Oliveira, Gabriel and Babalola, Damilola and Lynch, Collin and Heckman, Sarah},
  booktitle = {Proceedings of the 17th International Conference on Educational Data Mining (EDM 2024)},
  pages     = {484--490},
  address   = {Atlanta, Georgia},
  year      = {2024},
  doi       = {10.5281/zenodo.12729866}
}
```

**OHQ (Penn Labs)** - deployed software [§2.7 P5 + E4]
```bibtex
@misc{pennlabs_ohq,
  title        = {Office Hours Queue (OHQ)},
  author       = {{Penn Labs}},
  organization = {University of Pennsylvania},
  howpublished = {\url{https://ohq.io/}},
  note         = {Open-source software; \url{https://github.com/pennlabs/office-hours-queue}}
}
```

**Submitty (RPI / RCOS)** - deployed software [§2.7 P5 + E4]
```bibtex
@misc{submitty,
  title        = {Submitty: Open-Source Course Management with Office Hours Queue},
  author       = {{Submitty Development Team}},
  organization = {Rensselaer Center for Open Source, Rensselaer Polytechnic Institute},
  howpublished = {\url{https://submitty.org/}},
  note         = {Office-hours-queue feature}
}
```

**Lumilo** - ALREADY in `.bib` (`holsteinIntelligentTutorsTeachers2017a`, `holsteinStudentLearningBenefits2018`); no Zotero action, re-engage as competitor [§2.6/§2.7 P6 + E4].

**Holstein, McLaren, Aleven 2019** - JLA (the "Konscia" item; confirm product name) [§2.7 P6 + E4]
```bibtex
@article{holstein2019codesigning,
  title   = {Co-Designing a Real-Time Classroom Orchestration Tool to Support Teacher-AI Complementarity},
  author  = {Holstein, Kenneth and McLaren, Bruce M. and Aleven, Vincent},
  journal = {Journal of Learning Analytics},
  volume  = {6},
  number  = {2},
  pages   = {27--52},
  year    = {2019},
  doi     = {10.18608/jla.2019.62.3}
}
```

**Li et al. 2025** - LLMs misjudge difficulty [§2.7 P3a]
```bibtex
@article{li2025can,
  title   = {Can LLMs Estimate Student Struggles? Human-AI Difficulty Alignment with Proficiency Simulation for Item Difficulty Prediction},
  author  = {Li, Ming and Chen, Han and Xiao, Yunze and Chen, Jian and Jiao, Hong and Zhou, Tianyi},
  journal = {arXiv preprint arXiv:2512.18880},
  year    = {2025}
}
```

**Tabib & Deedar 2025** - GPT-4o 37.75% vs LightGBM 86% on difficulty [§2.7 P3a]
```bibtex
@article{tabib2025toward,
  title   = {Toward Trustworthy Difficulty Assessments: Large Language Models as Judges in Programming and Synthetic Tasks},
  author  = {Tabib, H. M. Shadman and Deedar, Jaber Ahmed},
  journal = {arXiv preprint arXiv:2511.18597},
  year    = {2025}
}
```

**Schwartz et al. 2025** - ECAI '25, history-based struggle prediction [§2.7 P3b]
```bibtex
@inproceedings{schwartz2025detecting,
  title     = {Detecting Struggling Student Programmers using Proficiency Taxonomies},
  author    = {Schwartz, Noga and Fairstein, Roy and Segal, Avi and Gal, Kobi},
  booktitle = {Proceedings of the 28th European Conference on Artificial Intelligence (ECAI 2025)},
  series    = {Frontiers in Artificial Intelligence and Applications},
  volume    = {413},
  pages     = {3551--3558},
  publisher = {IOS Press},
  year      = {2025},
  doi       = {10.3233/FAIA251230}
}
```

**Strickroth et al. 2024** - ITiCSE '24, live-coding error grouping (fill full author list in Zotero) [§2.7 P4 + E4]
```bibtex
@inproceedings{strickroth2024scalable,
  title     = {Scalable Feedback for Student Live Coding in Large Courses Using Automatic Error Grouping},
  author    = {Strickroth, Sven and others},
  booktitle = {Proceedings of the 2024 Conference on Innovation and Technology in Computer Science Education (ITiCSE '24)},
  pages     = {499--505},
  year      = {2024},
  publisher = {ACM},
  doi       = {10.1145/3649217.3653620}
}
```

**Kaliisa et al. 2024** - LAK '24 Best Paper, LADs show no strong achievement gains [§2.7 P-intro/P5]
```bibtex
@inproceedings{kaliisa2024have,
  title     = {Have Learning Analytics Dashboards Lived Up to the Hype? A Systematic Review of Impact on Students' Achievement, Motivation, Participation and Attitude},
  author    = {Kaliisa, Rogers and Misiejuk, Kamila and L{\'o}pez-Pernas, Sonsoles and Khalil, Mohammad and Saqr, Mohammed},
  booktitle = {Proceedings of the 14th Learning Analytics and Knowledge Conference (LAK '24)},
  pages     = {295--304},
  address   = {Kyoto, Japan},
  year      = {2024},
  publisher = {ACM},
  doi       = {10.1145/3636555.3636884}
}
```

**Feng et al. 2023** - Computers & Education, orchestration meta-analysis [§2.7 P5]
```bibtex
@article{feng2023effectiveness,
  title   = {Effectiveness of the functions of classroom orchestration systems: A systematic review and meta-analysis},
  author  = {Feng, Shuo and Zhang, Lishan and Wang, Shuwen and Cai, Zhihui},
  journal = {Computers and Education},
  volume  = {203},
  pages   = {104864},
  year    = {2023},
  doi     = {10.1016/j.compedu.2023.104864}
}
```

**Pitts et al. 2025** - HCI+NLP '25 survey, human-in-the-loop > automation [§2.7 P6]
```bibtex
@inproceedings{pitts2025survey,
  title     = {A Survey of LLM-Based Applications in Programming Education: Balancing Automation and Human Oversight},
  author    = {Pitts, Griffin and Hridi, Anurata Prabha and Lekshmi-Narayanan, Arun Balajiee},
  booktitle = {Proceedings of the Fourth Workshop on Bridging Human-Computer Interaction and Natural Language Processing (HCI+NLP)},
  pages     = {255--262},
  year      = {2025},
  publisher = {Association for Computational Linguistics},
  doi       = {10.18653/v1/2025.hcinlp-1.21}
}
```

---

## PARKED / OPTIONAL references (verified; in Note 10 only, promote into §2.3/§2.4/§2.7 if wanted)

Add by DOI/arXiv id in Zotero. Grouped by where each could be promoted:

- **LLM correctness signal:** Duan, Kankaria, Kartik, Lan 2026, KC-level correctness labeling (arXiv:2602.17542); Jukiewicz 2025, LLM-grading comparison of 18 models (arXiv:2509.26483); Oli, Banjade, Olney, Rus 2024, gaps/misconceptions in code explanations (ITS '24, `10.1007/978-3-031-64299-9_21`); Policar, Spendl, Curk, Zupan 2025, bioinformatics grading (Bioinformatics, `10.1093/bioinformatics/btaf196`).
- **Difficulty / IRT:** SMART (Scarlatos, Fernandez, Ormerod, Lottridge, Lan - EMNLP '25, `10.18653/v1/2025.emnlp-main.1274`); Zotos, van Rijn, Nissim 2025, model-uncertainty for difficulty (EDM '25, arXiv:2412.11831); DPKT (Yang, Sun, Li, Xu, Wei - Scientific Reports 2025, `10.1038/s41598-025-96540-3`).
- **BKT instructor view:** Sun 2025, hierarchical BKT in undergraduate engineering (arXiv:2506.00057).
- **Mistake clustering:** McMining (Al-Hossami, Bunescu 2025, arXiv:2510.08827); Hoq et al. SANN (EDM '25, `10.5281/zenodo.15870203`); Heickal & Lan, code-edit embedding (AIED '25, arXiv:2502.19407); Mitton et al. 2026, dialogue misconceptions (arXiv:2602.02414).
- **RAG for tutors:** YA-TA (Yang et al. 2024, arXiv:2409.00355); KITE (Jain et al., BEA '26, arXiv:2605.12988); Scholz et al. (ECTEL '25, arXiv:2507.00406); SteLLA (Qiu et al., IEEE BigData '24, arXiv:2501.09092).
- **Dashboard explanations / monitoring:** Deriyeva & Paassen 2025 (arXiv:2511.11671); VTutor (Chen et al., L@S '25, `10.1145/3698205.3733948`); Sticky Help (Jin et al., LAK '26, `10.1145/3785022.3785128`).
- **Surveys:** Pacheco et al. 2025 (Frontiers in Education, `10.3389/feduc.2025.1672901`); Long et al. 2025 (Frontiers in Education, `10.3389/feduc.2025.1648661`).
- **Wearable (FR6 reframe support):** Kazakou & Koutromanos 2025, AR-glasses acceptance (`10.1007/s10639-025-13687-2`); SensEmo (Choksi et al., MASS '24, `10.1109/MASS62621.2024.10723643`).

---

## DROPPED / FLAGGED (recorded so they are not re-proposed)

- **DROP "Lumilo 2 (AIED 2024)"** - mis-attributed: it is AIED **2025** (interactive-event/demo track), Holstein and McLaren are **not** listed authors, and it has no DOI. Use the original Lumilo (already in `.bib`) plus Holstein et al. 2019 JLA for the wearable precedent.
- **DROP Hoyl "Synthetic Student Responses"** - Stanford EDS capstone, not peer-reviewed (arXiv:2602.00034 / `10.25740/hh553ky5049`); year is 2025 not 2026.
- **FLAG SPARK (Yang, Zhang, Oney, Wang)** - real arXiv preprint **2601.22256**, but VL/HCC acceptance is **unconfirmed** (conference is later in 2026). Use only as "arXiv preprint, venue pending", or omit from E4.
- **FLAG "Konscia" name** - the citable artifact is Holstein et al. 2019 JLA (`10.18608/jla.2019.62.3`); confirm whether "Konscia" is the correct product label before using that name in prose.

> After validation + `.bib` export, re-run `python scripts/sync_literature.py` and check `Literature/coverage.md` for new/broken-cite diagnostics.
