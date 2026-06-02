# 09 — Possible New Design/Implementation Work (rationale-only)

✅ **Verified 2026-06-01 — already covered in the report; effectively no new writing required.** No features built (per direction). On checking the live report, the deferred-work rationale this note calls for is **already present and comprehensive** in `conclusion.tex` §6 *Future Work*, which covers all three items below plus four more. ← [[00 Index]]

## Status of the three flagged items

**P1. Incorrectness-scorer robustness** — ✅ **done.**
- Future-work rationale at `conclusion.tex:68–71` ("Restoring the OpenAI incorrectness scorer to a non-fallback rate"): explains the 92.5% midpoint fallback, why it degrades the strongest single signal, and names a robust scorer (retry/backoff, structured-output validation, or a local fallback model) as the **highest-leverage** future change.
- The 92.5% figure is also already surfaced in Ch3 where the signal is introduced — `design-and-architecture.tex:516` ("returns its 0.5 fallback for 92.5% of submissions… in practice the most weakly informed of the seven").
- Nothing to add.

**P2. Joint weight + threshold optimisation (ordinal logistic)** — ✅ **done.**
- Future-work rationale at `conclusion.tex:55–57`: explains the two-pass weights/thresholds design and the score-scale mismatch it caused, and proposes a proportional-odds ordinal logistic regression (via `mord` or `statsmodels.OrderedModel`) to fit weights + cutpoints jointly.
- **`mord`/`statsmodels` FLAG resolved:** these are software libraries named in a *future-work proposal*, not methods the project actually used — naming the tool is standard and needs **no academic citation**. (If preferred, reword to "a proportional-odds ordinal logistic regression" without naming libraries; either is fine.) So the index's "+1 cite" is **not required**.

**P3. Cross-session struggle aggregation** — ✅ **done.**
- Future-work rationale at `conclusion.tex:49–53` ("Cross-session aggregation"): the most direct survey-driven request (Q11), with the why-deferred — it needs per-snapshot scoring persisted beyond the live window plus session-grouped aggregation.
- *Optional, minor:* one sentence in Ch3 stating the dashboard is single-session **by design** would pre-empt the "why not cross-session?" question, but the Future-Work paragraph already carries the rationale.

## Also already in the report (beyond this note's original three — good)
`conclusion.tex` §6 additionally covers cohort-balanced re-evaluation (`:59–62`), per-semester threshold re-tuning as a maintenance concern (`:64–66`), a prospective intervention study (`:73–76`), and smart-device integration / FR6 (`:78–82`). The deferred-work section is thorough.

## Related open decision — resolved
- **τ deployment:** ✅ resolved 2026-05-31 — `cf_threshold` is deployed at **0.90** (seeded from the Optuna-tuned JSON) and the report states 0.90 throughout (see [[01 Integrity & Consistency Fixes]] / [[00 Index]]). No config change outstanding; report it as a finding only.

## Definition of done
- ✅ Report already explains why each deferred item was deferred (§6 Future Work + the Ch3 92.5% mention).
- ⬜ *Optional:* reword the `mord`/`statsmodels` mention generically, or leave as-is (recommended).
- ⬜ *Optional:* add one "single-session by design" sentence in Ch3 for P3.
- Flip Note 09 in [[00 Index]] to ✅ (no blocking work remains).
