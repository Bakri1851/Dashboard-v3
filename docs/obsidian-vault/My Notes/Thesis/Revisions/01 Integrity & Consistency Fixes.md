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

### I14 (HIGH, code+report). Trained v2 weights are NOT deployed — model_class guard mismatch
- **Discovered 2026-05-31 via the Ch4 audit workflow; adversarially re-verified.** The single most serious discrepancy found in the whole pass.
- **Code:** all three trained-weight loaders reject the JSONs. `code2/backend/struggle.py:56`, `code2/backend/difficulty.py:39`, `code2/backend/models/improved_struggle.py:51` each guard `if payload.get("model_class") != "LogisticRegression": return None`. But `scripts/optimise_v2_weights.py` (lines 304/382/491; docstring "ordinary least squares") writes `"model_class": "LinearRegression"` into every JSON. So all three trained weight sets are refused at load (`return None`), and `compute_student_struggle_scores(weights=None)` falls back to the v1 hand-set `config.STRUGGLE_WEIGHT_*` (struggle.py:310-317; caller cache.py:194-195 passes the None through). Strict `!=`, no `.lower()`/normalisation, no newer weights file — confirmed by two independent agents.
- **Impact:** the deployed struggle / difficulty / improved leaderboards run on **v1 hand-set weights**, not the trained OLS weights. The Optuna-tuned scalars τ≈0.90 and K=5 are a *separate* `runtime_config` path and ARE applied (unaffected). The evaluation scripts (`optimise_v2_weights.py`, CV Spearman ρ) measure the **trained** weights, so **deployed ≠ evaluated**.
- **Report claims the opposite (FALSE as written), 6 places:** design l524 ("these trained weights (v2) are the deployed default"), l1059, l1095; implementation l951 ("applied unconditionally; there is no runtime v1/v2 selector"), l1013, l1185.
- **RESOLVED 2026-05-31 — code fixed (author chose fix-the-code).** Guard changed `"LogisticRegression"` → `"LinearRegression"` in all three loaders (struggle.py:56, difficulty.py:39, models/improved_struggle.py:51, plus the matching warning strings). Runtime smoke test confirms all three now load the trained weights (struggle 7 keys; difficulty 5 keys; improved w_B/w_M/w_D = 0.268/−0.680/−0.052). **Deployment now matches the evaluated model, so the six report sentences (design l524/1059/1095, impl l951/1013/1185) are TRUE as written — no report edit needed.** Eval provenance confirmed: `optimised_struggle_weights_v2.json` `spearman_rho_mean`=0.5884, ci95 [0.490, 0.686] = the Ch5 headline ρ=+0.588 [+0.490, +0.686].

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

## Re-audit findings (2026-05-31, "make sure nothing is missed" pass — completeness critic verified against code)

> **APPLIED 2026-05-31 (verified by re-grep):** I13 (l151 Optuna phrasing), I15 (gpt-4o ×5 — only the intentional l1060 comparison still names gpt-4o-mini), I16 (router count → ten, models_cmp dropped), I17 (RAG_MIN_SUBMISSIONS + the "is does" typo) corrected in `Report/`; I18 reworded (V1 redistributes; deployed V2 applies trained weights and lets a missing signal contribute zero); Fig 3.6 lead-in now defines C1–C3 inline instead of promising an absent discussion. **I19 closed as no-fix** — `lab_state.py` uses the full 36-symbol alphabet, so the report's log₂(36⁶)≈31-bit claim is correct (the CLAUDE.md/memory "excludes O/0/I/1" note is the stale one).

### I15 (HIGH). OpenAI model: report says gpt-4o-mini, code uses gpt-4o
- **Where:** `implementation.tex` tech-stack table (~l70), l120, l595, l1285 (problems table), and the RAG generator l1060 ("gpt-4o-mini, the same model used for incorrectness scoring"); plus the architecture-diagram OpenAI node labelled gpt-4o-mini.
- **Truth (code-verified):** `config.py:13` `OPENAI_MODEL = "gpt-4o"` ("upgraded from gpt-4o-mini 2026-05-26 after re-label experiment showed +0.18 Spearman ρ gain on difficulty v2 training"); `incorrectness.py` and `rag.py` both call `config.OPENAI_MODEL` → **gpt-4o**. The report is internally inconsistent: the eval-label phase (impl l1019/1021) already says GPT-4o.
- **Fix:** replace "gpt-4o-mini" with "gpt-4o" for the deployed incorrectness scorer and the RAG generator (the eval-label text is already correct).

### I16 (HIGH). Router count: "eleven … models_cmp" → ten, no models_cmp
- **Where:** `implementation.tex` l189 and l237 — "Eleven routers … live, student, question, analysis, sessions, settings, models_cmp, lab, rag, meta and cf".
- **Truth (code-verified):** `main.py:42` imports and l202–211 include exactly **ten** routers (analysis, cf, lab, live, meta, question, rag, sessions, settings, student). There is **no `models_cmp` router** anywhere in code2; `routers/classes.py` exists but is not imported/included.
- **Fix:** "Eleven" → "ten"; drop `models_cmp`; use the actual ten-router list. (Optionally note `classes.py` is an unused stub.)

### I17 (MEDIUM). RAG constant name: RAG_MIN_SUGGESTIONS → RAG_MIN_SUBMISSIONS
- **Where:** `implementation.tex` l1247 "fewer than RAG_MIN_SUGGESTIONS = 2 submissions".
- **Truth:** `config.py:206` defines `RAG_MIN_SUBMISSIONS = 2`; no `RAG_MIN_SUGGESTIONS` exists. The value (2) is right; the same section uses the correct name at l1055 — internal inconsistency.
- **Fix:** l1247 `RAG_MIN_SUGGESTIONS` → `RAG_MIN_SUBMISSIONS`.

### I18 (MEDIUM). Improved-struggle "redistribution observed in production" — deployed V2 does not redistribute
- **Where:** `results-and-evaluation.tex` ~l147 (robustness) states the case-2 weight redistribution (w_M absorbed into w_B) "was observed in production" on the 25COA122 fallback.
- **Truth:** after the I14 fix the deployed v2 improved model loads TRAINED weights (w_B,w_M,w_D)=(0.268,−0.680,−0.052) and, in v2_mode, EXPLICITLY SKIPS graceful redistribution (`improved_struggle.py:134-168`). The (0.45,0.30,0.25) defaults and the redistribution table describe **V1** only. Impl frames them as V1 (l959) and says trained weights deploy (l953–956), so the impl is defensible, but the eval "observed in production" sentence describes the deployed system, where redistribution does not run.
- **Fix:** scope the "observed in production" redistribution claim to V1 (or note the deployed v2 uses trained weights without redistribution).

### I19 (LOW, verify). Session-code entropy: 36-symbol alphabet vs documented exclusion of O/0/I/1
- **Where:** `implementation.tex` l540 — "string.ascii_uppercase + string.digits, log2(36^6) ≈ 31 bits".
- **Truth:** CLAUDE.md/MEMORY say the code excludes O/0/I/1 (a 32-symbol alphabet → log2(32^6)=30 bits). Verify `generate_session_code()`; if it excludes confusables, the 36-symbol/31-bit derivation is wrong (should be 32/30).

### Still-pending from earlier: I13 NOT applied
- The l151 Optuna fix (`requirements-specification.tex` l151: "find optimal weights for our composite metrics" → "tune the scalar hyperparameters that govern these composite models") was **not applied** by the author — re-audit confirms l151 still has the old phrasing. Re-flag.

### Verified ACCURATE by the completeness critic (no action — recorded for confidence)
All named constants (LEADERBOARD_MAX_ITEMS=15, DATA_ANALYSIS_TOP_QUESTIONS=10/USERS=20, AUTO_REFRESH_OPTIONS, LAB_CODE_LENGTH=6, CLUSTER_* , OPENAI_BATCH_SIZE=20, SCORING_PER_RUN_CAP=500); V2 cache TTLs (df 60s, struggle/difficulty 900s, improved/irt 600s); V1 caching (10s, 300s); BKT params + bounds + min-obs=50; 2PL IRT bounds/identifiability/IRT_MAX_ITER=100; measurement-confidence formula (base 0.7, min-length 20, floor 0.2); CF k=3 + 5-feature vector; per-module difficulty normalisation; threshold κ representations; Optuna deltas. Runtime/data figures (prewarm latencies, 92.5% fallback, 100-trial joint study) are log-derived and not statically checkable.

## Verify-on-apply
After approved edits: `pdflatex main && bibtex main && pdflatex main && pdflatex main` from `Report/`; confirm zero undefined-reference/citation warnings.
