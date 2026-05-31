# 10 — Related Work & Research-Gap Expansion

High-leverage prior-art scan (verified via web search; every system below was fact-checked to be real, with fabrications dropped). Answers the supervisor's two follow-up questions: **(1) is anyone doing what we do?** and **(2) does Research Gaps (§2.7) need expanding?** ← [[00 Index]]

> ⚠️ **No-hallucination note:** all candidate references below are flagged **must-verify in Zotero** before any `.bib` entry. The 2025/2026 arXiv items especially must be confirmed (title, authors, venue, ID) before citing. I do **not** edit `references.bib`. See [[07 Citations — wire orphans + Candidate References]] for the workflow.

## (1) Is anyone doing what we do?

**Verdict: the *full intersection* is an unfilled niche, but every individual ingredient now has prior art.** So the contribution must be framed as the **integration + the human-advisory dispatch loop**, NOT as per-component novelty. A per-component "no one does this" claim would not survive a viva.

### Closest competitors (cite + distinguish)
1. **Diana et al. (LAK 2017) — the single closest system.** A real-time, instructor-facing dashboard for *interactive programming assignments* that predicts which students need help from live program-state logs **and dispatches by matching low-performers to high-performing peer tutors**. It closes the same monitor→rank→dispatch-a-human loop, in the same setting, eight years earlier — **must be cited and explicitly distinguished**. *We differ:* dispatches dedicated lab assistants via a mobile channel; LLM-derived per-submission correctness signal; separate question-difficulty ranking; 2PL IRT + BKT; mistake clustering; RAG. Diana has none of those.
2. **ClassAid (Zhang, Sun, Xia & Liang — CHI 2026) — most threatening on recency / LLM axis.** Live programming dashboard that assesses misconceptions and surfaces per-student + class analytics, LLM in the loop. *We differ:* it dispatches an **AI agent to the student**; we dispatch a **human assistant** and are explicitly advisory; no IRT/BKT, no cohort mistake-clustering, LLM used as feedback-agent not as a correctness *signal*.
3. **Lumilo / Lumilo 2 (Holstein, McLaren & Aleven — AIED 2018 / 2024) — already in the `.bib` but only cited in passing.** Real-time per-student detector state + BKT mastery on MR glasses — i.e. the "smart device for lab assistance" the thesis motivates in FR6. **Engage it as a competitor, not a progress dashboard.** *We differ:* platform-agnostic (generic logs + LLM, no instrumented ITS); separate difficulty ranking; mistake clustering; RAG; multi-assistant dispatch. **Reframe the FR6 smart-device claim — MR glasses already exist via Lumilo** (see [[01 Integrity & Consistency Fixes]] I4 and P6 below).
4. **Office-hours queue work (Gao et al. EDM 2024; OHQ Penn Labs; Submitty) — closest on the dispatch axis.** Prioritise *who a TA helps next* from a **self-declared queue** (FIFO / New-Student-First). *We differ:* struggle-**driven** dispatch from live logs reaches the shy student who never joins a queue — the thesis's core motivation; queue work is detection-free.

### The wider landscape (each ingredient has prior art — name a few, don't claim novelty)
- Real-time programming dashboards: Diana, VizGroup (UIST 2024), SPARK (VL/HCC 2025).
- LLM-in-the-loop orchestration: ClassAid.
- Live struggle on smart devices: Lumilo / Lumilo 2, Konscia.
- TA/help dispatch: Diana peer-matching, Gao et al., OHQ, Submitty.
- LLM + IRT difficulty estimation: SMART/DPKT-type work; Li et al. (warns LLMs misjudge human difficulty → motivates fusing the LLM signal with IRT/BKT rather than trusting the LLM alone).
- Struggle prediction over history (not live): Schwartz et al. (ECAI 2025).

## (2) Does §2.7 (Research Gaps) need expanding? — YES

The current §2.7 reads as "no one monitors labs live and dispatches help", which the verified work makes **falsifiable**. **Reframe from an *absence* argument to an *integration-gap* argument**, and actively position against the orchestration/dispatch literature it currently ignores. This also executes the author's own P1–P6 TODOs in the section.

**Recommended structure (brief — author writes the prose, British/declarative/semicolon style):**
- **P-intro** (revise l293): execute the P1 TODO — broaden the methods inventory (KT/BKT §2.2.2, text-mining/clustering §2.3.2, RAG §2.4); declarative tense; add one sentence conceding real-time programming dashboards/orchestration tools now exist → set up integration framing.
- **P-lab** (keep l296, re-tense): retain the shy-student / hands-up / end-of-lab-data live-timing gap (still strong), but cite **Diana (LAK 2017)** and the office-hours-queue work as the nearest live-lab dispatch precedents that still rely on opt-in/arrival order.
- **P3** (split, sharpen): (a) LLM-as-judge as a per-submission **correctness signal** feeding struggle/difficulty (vs ClassAid's feedback-agent use; cite **Li et al.** that LLMs misjudge difficulty → motivates IRT/BKT fusion); (b) course-level vs live-session struggle (vs Estey/Piech and **Schwartz et al.** which predict from history); (c) CF in real-time labs (existing point, retained).
- **P4** (NEW): instructor-facing **aggregate interpretability** gap — IRT/BKT live *inside* ITSs (Lumilo) for adaptation, not surfaced to an instructor as a class-level mastery/difficulty view beside a live struggle ranking; live cohort mistake-clustering for whole-class teaching moments is absent from orchestration tools.
- **P5** (NEW — most important): real-time **orchestration & dispatch** gap. Prior live tools either surface awareness without routing a human (Lumilo, MM dashboard), dispatch an **AI agent** to the student (ClassAid), match **peers** (Diana), or order a **self-declared queue** (Gao, OHQ, Submitty). None route a **human lab assistant** off an **automatically-detected** struggle ranking via a **mobile** channel, **advisory** and instructor-in-the-loop. State this as the integration gap.
- **P6** (smart-device, reframed): drop the hardware-novelty framing (MR glasses precede this via Lumilo); reframe as a **lightweight, instrumentation-free** assistant channel needing no per-student sensors and no instrumented ITS; FR6's heavier wearable ambition → Ch6 future work.
- **P7** (NEW synthesis, executes the optional P6 TODO): live timing + interpretable struggle/difficulty + cohort mistake patterns + grounded LLM feedback + human assistant dispatch = one integrated affordance no prior system provides; forward-reference the Appendix-E4 comparison table.

## Comparison table (feeds [[08 Examiner-Expected Sections]] E4)
Recommended columns: System (year, venue) · Setting (in-lab live / course-level / offline) · Real-time? · Signal source (logs / LLM correctness / ITS detectors / sensors / self-declared queue) · Ranks struggle? · Ranks question difficulty separately? · Interpretable model (IRT/BKT/none) · Mistake clustering? · Acts on ranking — dispatch type (human assistant / AI agent / peer / awareness only) · Dispatch device (mobile / MR glasses / desktop) · LLM/RAG coaching? · Autonomy (advisory / autonomous) · Domain. Rows: this dashboard + Diana + ClassAid + Lumilo/Lumilo 2 + MM dashboard + office-hours queue (one combined row) + VizGroup/SPARK.

## Candidate references to validate in Zotero (all must-verify)
| Ref | Where | Priority |
|---|---|---|
| **Diana et al. (LAK 2017)**, DOI 10.1145/3027385.3027441 | §2.6 + §2.7 P-lab/P5 + E4 (the single closest system) | **mandatory** — well-established, definitely real |
| **Gao et al. (EDM 2024)** "Who should I help next?" | §2.7 P-lab/P5 + E4 | high |
| **OHQ (Penn Labs) + Submitty queue** (deployed tools, footnote URLs) | §2.7 P5 + E4 | high |
| **ClassAid (CHI 2026)**, arXiv:2602.06734 / DOI 10.1145/3772318.3790824 | §2.7 P3a/P5 + E4 | high — **verify carefully (2026)** |
| **Li et al.** "Can LLMs estimate student struggles?" arXiv:2512.18880 | §2.7 P3a | medium — **verify carefully** |
| **Schwartz et al. (ECAI 2025)** arXiv:2508.17353 | §2.7 P3b | medium — **verify carefully** |
| **VizGroup (UIST 2024)** arXiv:2404.08743 (opt. SPARK VL/HCC 2025) | §2.6/E4 | optional |
| Lumilo / Holstein 2018 (`holsteinStudentLearningBenefits2018`) | already in `.bib` — re-engage as competitor, no Zotero needed | — |

> After validation + `.bib` export, re-run `python scripts/sync_literature.py`.
