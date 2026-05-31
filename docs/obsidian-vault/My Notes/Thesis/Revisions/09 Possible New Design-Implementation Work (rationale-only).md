# 09 — Possible New Design/Implementation Work (rationale-only)

**No features are built this pass.** Per your direction, the action is to *amend the relevant sections to explain why we did, or deferred,* each — not to implement. If any is later promoted to actual building, that is a separate, explicitly-approved pass. ← [[00 Index]]

## P1. Incorrectness-scorer robustness (highest-leverage)
- **Context:** §5.6.3 flags that the OpenAI scorer returns the 0.5 fallback on **92.5%** of submissions (see [[01 Integrity & Consistency Fixes]] I9), yet recent incorrectness is the strongest struggle signal (η=0.38 / trained +0.314). This caps every downstream model.
- **Rationale to write (not build):** explain *why* the current design uses a midpoint fallback (most submissions lack AI feedback because students opt out of the LLM tutor), why this is a degraded-signal limitation rather than a bug, and *why* a more robust scorer (retry/backoff, structured-output validation, or a local fallback model) is named as the **highest-leverage future improvement** — above retraining any weights/thresholds. Surface the 92.5% figure in Ch3 where the signal is introduced, and frame the fix in Future Work (Ch6 already has a stub).

## P2. Joint weight + threshold optimisation (ordinal logistic regression)
- **Context:** weights (§5.4.3) and thresholds (§5.4.5) are trained in two separate passes; the deployed-composite recalibration exists because the promoted cutpoints were fit on a different score scale. `conclusion.tex` l53–57 already proposes proportional-odds ordinal logistic regression and carries the unresolved mord/statsmodels FLAG.
- **Rationale to write:** explain *why* the two-pass approach was used (separable, interpretable, each independently validated) and *why* a single joint ordinal-logistic fit would remove the scale-mismatch failure mode — as Future Work. Resolve the FLAG per [[07 Citations — wire orphans + Candidate References]] (either add refs for mord/statsmodels or reword generically as "a proportional-odds ordinal logistic regression"). No implementation.

## P3. Cross-session struggle aggregation
- **Context:** the only direct survey feature request (Q11, §5.5.5) — a view of how often a student is flagged across multiple labs, not just within one. Already named in Ch6 future work.
- **Rationale to write:** explain *why* the dashboard is scoped to a single live session (the deployed design persists no per-snapshot history beyond the live window) and *why* cross-session aggregation is deferred (needs persistent per-snapshot storage and session-grouped re-evaluation). No implementation.

## Related open decision
- **τ deployment** (from [[01 Integrity & Consistency Fixes]]): Optuna suggests `cf_threshold` 0.7→0.90. Decide whether to change the deployed `config.py` default (a small, low-risk config change — not a feature) or to report it only as a finding. If you want the config changed, that is a separate approved edit.
