# 01 — Integrity & Consistency Fixes (DO FIRST)

These are correctness/credibility issues an examiner notices immediately. All verified against the `.tex` and `data/eval/` files. Most are mechanical and will be applied **only after you approve the previews**. ← [[00 Index]]

## HIGH — must resolve

### I1. Phantom benchmark: "histogram gradient boosting"
- **Where:** abstract `Report/main.tex` ~l128; `Report/main-sections/conclusion.tex` ~l40 ("benchmarked against random forest, gradient boosting, and histogram gradient boosting").
- **Problem:** `data/eval/model_class_bakeoff.json` ran **OLS, Ridge×3, Lasso, ElasticNet, RandomForest, GradientBoosting** — **no HistGradientBoosting**. The Results figure (`fig:eval-model-class-bakeoff`) names only random forest + gradient boosting. So the abstract and conclusion overclaim.
- **Decision:** **(default, no implementation)** delete "and histogram gradient boosting" from both sentences; **or** run a HistGB variant in the bake-off and add it to the figure + Results text. Note the bake-off *does* include Ridge/Lasso/ElasticNet (matches Results), so only HistGB is phantom.

### I2. Wrong rounded figure: difficulty ρ
- **Where:** `main.tex` l129 and `conclusion.tex` l16, l41 say **+0.469**; `results-and-evaluation.tex` l183, l443 say **+0.468**.
- **Truth:** `model_class_bakeoff.json` difficulty OLS `pooled_rho = 0.4684530` → rounds to **+0.468**. `results.md` l54 also says +0.468.
- **Fix:** standardise to **+0.468** in the abstract and conclusion.

### I3. Unmet "Ethical Approval" heading
- **Where:** `results-and-evaluation.tex` l342 — `\subsubsection{Instrument, Audience and Ethical Approval}`; body l344–346 only notes voluntary/anonymous.
- **Fix:** add the Loughborough ethics approval/exemption reference + date under the heading, **or** rename the heading to drop "Ethical Approval". (See [[08 Examiner-Expected Sections]] for the fuller ethics statement.)

### I4. Contradicted claim: smart-device integration "delivered"
- **Where:** `introduction.tex` l48 ("The project has smart device integration, sending who to help to lab assistant's phones"); contradicted by FR6 scoped out (`results-and-evaluation.tex` l82) and future work (`conclusion.tex` l81–84). Stale comment at l55 ("update this once smart devices are implemented") confirms it.
- **Fix:** re-tense l48 to the delivered **mobile web route** (or state it as an aim), and delete the l55 comment.

### I5. Leftover TODO / FLAG / draft blocks still in source
- `main.tex` l1–29 (read-through TODO); `implementation.tex` l3, l1427; `requirements-specification.tex` l292–306; `conclusion.tex` FLAGs l55–56 and l60–62; every appendix stub's TODO; and the `\begin{comment}` "Lazy Lab Assistants" block in `introduction.tex` l21–30.
- **Fix:** resolve each (the conclusion FLAGs tie to I-items below and [[07 Citations — wire orphans + Candidate References]]) and delete the comment blocks before submission.

## MEDIUM — number traceability & polish

### I6. Difficulty κ chain reads as three different numbers
- Values in play (all verified): **+0.225** (`results.md` l55, original-scale OLS fit) → **+0.393** (`results-and-evaluation.tex` Table 5.8 l277, trained StandardScaler) → **+0.387** (l286, deployed min-max recalibration).
- **Fix:** add one bridging sentence stating +0.225 is the original-scale fit, superseded by the recalibrated deployed **+0.387**, so the underlying data file does not read as contradicting the headline.

### I7. Optuna K = 0 vs K = 1
- Independent study tuned **`shrinkage_k = 0`** (verified in `optimised_hyperparams_v2.json` `best_values`; matches Table 5.9 + conclusion l30). The joint study reports **K = 1** (`results-and-evaluation.tex` l302).
- **Fix:** add a clause stating the joint (K=1) and independent (K=0) optima differ by one integer step and both fall within per-fold noise — otherwise it reads as a contradiction.

### I8. Cohort window mismatch
- Ch5 l5: "2 February 2026 to 15 May 2026"; `results.md` l17: "2025-10-06 → 2026-05-15"; 21/23 healthy sessions.
- **Fix (author confirms):** state the true window. Likely the data file spans the full academic year and the evaluation excludes a Semester-1 tail — say which, so the date range and the 23-session count agree. (Also `results.md` l56 says 76% Very Hard vs Ch5's 72% — reconcile in passing.)

### I9. Use the exact 92.5% fallback figure
- `results-and-evaluation.tex` l515, l521 say "the majority of submissions"; `scripts/experiments/extra_figures.py` hardcodes **FALLBACK_PCT = 92.5%** of the 42,443 submissions.
- **Fix:** replace "the majority" with the exact **92.5%**, and surface it in the design chapter where the incorrectness signal (weight η=0.38 / trained +0.314) is introduced — it currently hides until Ch5.

### I10. Grammar in the first paragraphs of the Introduction
- `introduction.tex` l4: "working simultaneously on different questions **are their own pace**" → "**at** their own pace". l18: doubled verb "The central problem **is addressed** in this project **is therefore**" → "The central problem **addressed** in this project **is** therefore…".

### I11. Abstract acronyms unexpanded
- `main.tex` l127–130 uses **OLS, TPE, 2PL** without expansion (RAG/IRT/BKT are expanded). Expand on first use; also see the document-level acronym list in [[04 Symbol, Data & Acronym Definitions]].

### I12. Min-max normalisation: degenerate-cohort value (0 vs 0.5)
- **Where:** `design-and-architecture.tex` l448 — "When $x_{\min} = x_{\max}$, the normalised value is conventionally set to $0$."
- **Truth (code-verified):** the deployed V2 normaliser `code2/backend/analytics.py:50` returns **0.5** (the neutral midpoint), not 0, with a documented rationale — it preserves the signal's weight contribution when a signal is uniform across the cohort, and the ranking is unchanged either way. The "0" is the V1 convention (`code/learning_dashboard/`), stale for the evaluated V2 system.
- **Fix:** change "$0$" to "$0.5$ (the neutral midpoint)" plus a short rationale clause. One-line gated before→after, delivered with the Ch3 brief in [[05 Intros, Conclusions & Summaries]].

### I13. §2.2.4 Optuna "finds weights" vs tunes scalar hyperparameters
- **Where:** `requirements-specification.tex` l151 (§2.2.4) — "use … Optuna's TPE to efficiently search the hyperparameter space and find optimal weights for our composite metrics".
- **Truth (code-verified):** the composite **weights** are learned by OLS regression (`scripts/optimise_v2_weights.py`, `sklearn LinearRegression`), not by Optuna. Optuna's TPE tuned only the **scalar hyperparameters** K and τ (`scripts/optimise_hyperparams.py` — two TPE studies: `shrinkage_k` ∈ {0..50}, `cf_threshold` ∈ [0.4, 0.9], objective 5-fold CV Spearman ρ). Optuna does not "find the weights".
- **Fix:** "find optimal weights for our composite metrics" → "tune the scalar hyperparameters that govern these composite models". Gated before→after, delivered with the Ch2 brief in [[05 Intros, Conclusions & Summaries]]. The preceding sentence (l142) already credits supervised learning with refining the weights.

## Verify-on-apply
After approved edits: `pdflatex main && bibtex main && pdflatex main && pdflatex main` from `Report/`; confirm zero undefined-reference/citation warnings.
