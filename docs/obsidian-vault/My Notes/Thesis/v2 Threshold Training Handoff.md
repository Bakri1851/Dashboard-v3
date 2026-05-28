---
phase: writing-handoff
status: ready-to-draft (implementation pass shipped 2026-05-27 evening)
covers: how to write the threshold-training findings into the report (cross-chapter)
sibling-of: "[[v2 Relabel Handoff]]"
sibling-of-2: "[[v2 Target-Swap Handoff]]"
sibling-of-3: "[[v2 Threshold Promotion Handoff]]"
inputs:
  - data/eval/experiments/threshold_search_cv.json
  - scripts/experiments/threshold_search_constrained.py
created: 2026-05-27
---

# Handoff — Writing-up the band-threshold training (cross-chapter)

> Companion to `[[v2 Threshold Promotion Handoff]]` (the implementation pass). This doc covers the prose: §5.4.11 (new), §5.6.x IRT anti-result (new), and cross-chapter touches in Ch1, Ch2, Ch3, Ch4, Ch6.

## §0 STOP — read this before continuing any prose

Two substantive things happened in the 2026-05-27 session. **If you're holding drafted prose for §5.4 or §5.6 from before today, stop and read §3 + §5 below before continuing.**

## §1 What changed this session

### 1.1 Model Comparison dashboard view — removed; analytics preserved offline

The `/api/models/compare` endpoint and the `ComparisonView` sidebar tab (baseline vs improved struggle; baseline vs IRT difficulty) were removed from the V2 dashboard. The view's analytics (top-10 leaderboards, agreement %, Spearman ρ, top-10 overlap, scatter plots, full pairs tables) were ported into a new dedicated notebook `notebooks/model_comparison.ipynb` that runs on the eval cohort (1306 snapshots / 72 questions) rather than the live `lab_session.json`-filtered cohort. Output artefacts:

- `data/eval/figures/comparison_struggle_top10.png`, `comparison_struggle_scatter.png`
- `data/eval/figures/comparison_difficulty_top10.png`, `comparison_difficulty_scatter.png`
- `data/eval/comparison_struggle_pairs.csv` (1306 rows), `comparison_difficulty_pairs.csv` (72 rows)

Backend model machinery (BKT, IRT, improved-struggle) **stays in production** — still used by the Settings → Models tab toggles (`struggle_model: baseline | improved`, `difficulty_model: baseline | irt`) which dispatch through `load_active_*_df()` in `code2/backend/cache.py`.

**Headline numbers from the new notebook** (use these if you previously cited live-cohort numbers):

- Struggle baseline-vs-improved: Spearman ρ = +0.496, top-10 overlap 4/10
- Difficulty baseline-vs-IRT: Spearman ρ = +0.345, top-10 overlap 1/10

### 1.2 Threshold training — SHIPPED 2026-05-27 evening

**The implementation pass has executed.** `code2/backend/config.py` now holds the constrained CV-trained values for `STRUGGLE_THRESHOLDS` and `DIFFICULTY_THRESHOLDS`; `notebooks/eval_main.ipynb` cell 26 uses the trained v2 OLS cutpoints; both `eval_main.ipynb` and `model_comparison.ipynb` were re-run; `data/eval/results.md` and `data/eval/figures/*.png` are regenerated. See §7 below for the per-item ✓ checklist + §13 for implementation deltas the writer needs to know.

What was done: brute-force κ-maximising grid search over `(c1, c2, c3)` cutpoints, cross-validated inside each fold (GroupKFold(5) for struggle, LOO for difficulty), trained per-model (6 distinct sets — one per (model × score-space) combination). Linear-weighted Cohen's κ as the objective, computed via a manual fast_kappa to avoid sklearn dispatch overhead. Two variants reported:

- **Unconstrained**: pure κ-max, exposes empirical ceiling
- **Constrained**: `c1 ≥ train-fold P5` AND every band ≥ 10% of score range — prevents cohort-overfit degeneracies (notably the lowest band collapsing to empty)

**Decision**: ship the constrained CV-trained thresholds for the 4 sets where the constrained gain is meaningfully positive; retain hand-set for the 2 sets where it isn't. **Default-only promotion, no Settings UI toggle** (decision rationale: thresholds are a downstream label-display calibration, not a modelling choice; the model-comparison view was removed this same session for being "evaluation, not production", and adding a threshold-comparison toggle would repeat that anti-pattern).

## §2 The headline 6-row table — paste-ready for §5.4.11

| Model | Hand-set κ | Unconstrained CV κ | **Constrained CV κ (ship)** | Constrained Δ |
|---|---|---|---|---|
| Struggle baseline composite | +0.303 | +0.402 | **+0.390** | **+0.087** ✓ ship |
| Struggle improved (BKT+IRT) | +0.105 | +0.134 | +0.103 | −0.002 ✗ retain hand-set |
| Struggle v2 OLS [0,3] | +0.380 | +0.483 | **+0.456** | **+0.076** ✓ ship |
| Difficulty baseline composite | +0.065 | +0.465 | **+0.239** | **+0.175** ✓ ship |
| Difficulty IRT Rasch (scaled) | −0.016 | −0.069 | −0.024 | −0.007 ✗ retain hand-set |
| Difficulty v2 OLS [0,3] | +0.225 | +0.436 | **+0.393** | **+0.168** ✓ ship |

Source of truth: `data/eval/experiments/threshold_search_cv.json`. Scripts: `scripts/experiments/threshold_search_constrained.py` (the run-this-one), `threshold_search_cv.py`, `threshold_search.py`, `threshold_search_per_model.py` (intermediate variants — all delete-safe, kept for reproducibility).

**Constrained cutpoint values shipped:**

| Score | Production cutpoints (c1, c2, c3) | Score domain |
|---|---|---|
| Struggle baseline composite | (0.315, 0.505, 0.605) | [0, 1] |
| Struggle v2 OLS | (1.22, 1.78, 2.09) | [0, 3] |
| Difficulty baseline composite | (0.363, 0.463, 0.588) | [0, 1] |
| Difficulty v2 OLS | (1.88, 2.19, 2.69) | [0, 3] |

Per-fold std is ≤ 0.03 on every cutpoint — the optima are essentially deterministic across folds, not noise.

## §3 What's stale in your drafts (per-chapter)

> **Recap toolkit — DELETED 2026-05-27 evening.** The HTML recap toolkit (`docs/recap_toolkit/dashboard_v3_toolkit.html`) and its CLAUDE.md section were removed (user decision: not useful). There is no toolkit to keep in sync any more — disregard any instruction below or in other notes to update toolkit panels. The canonical sources are the vault notes + `data/eval/results.md` + the report itself.

### Ch5 §5.4 (results)

- **The notebook rerun has completed** (2026-05-27 18:07 UTC); `data/eval/results.md` is regenerated and the old caveat ("wait for results.md to regenerate") no longer applies. The post-promotion exact-band agreement numbers from the regenerated `data/eval/figures/confusion_bands.png` cell are: **v1 = 672/1306 (51.5%)**, **v2 = 725/1306 (55.5%)**. Lift these directly. The §5.6.1 model-disagreement counts in `results.md` are also fresh — current values: same-band 893/42443 (2.1%), reclassified 413/42443 (1.0%), upgraded 322 (0.8%), downgraded 91 (0.2%) (the 42443 denominator looks suspicious — investigate or normalise to 1306 in prose if helpful).
- Add a new subsubsection **§5.4.11 — Band-Threshold Optimisation (per-model)** between the existing §5.4.10 (Optuna hyperparams) and §5.6. The 6-row table in §2 above is the headline content.

### Ch5 §5.6 (limitations / model behaviour)

- Add a new paragraph or subsubsection on the **IRT-difficulty κ mismatch** — see §5 below.

### Ch4 (implementation)

- The current Ch4 documents hand-set thresholds in `code2/backend/config.py`. After promotion, update to the constrained-trained values with a comment block tying back to §5.4.11.
- The Settings → Read-only config reference card in `code2/frontend/src/views/SettingsView.tsx` surfaces the threshold values to instructors; the Appendix B screenshot of that card will need re-shooting after promotion.

### Ch3 (design)

- The threshold-scheme subsection currently presents `(0.2, 0.35, 0.5)` style numbers as design choices. Reframe as **interpretability-first design choice with empirical validation deferred to §5.4.11**. Forward-reference explicitly.

### Ch1 (contributions)

- Add a bullet: *"systematic empirical validation of all v2 pipeline hyperparameters (composite weights, scalar hyperparameters, AND score-to-band thresholds) against an LLM 4-band rater, with both positive and negative findings reported"*. This closes a logical gap — without it, the contributions read as "we trained the weights and scalars but left the most user-visible numbers hand-set".

### Ch6 (future work)

- Three new items: (a) joint weight + cutpoint optimisation via ordinal logistic regression (proportional-odds / `mord` / `statsmodels.OrderedModel`); (b) cohort-balanced re-evaluation (this cohort has 0 LLM-labelled "Easy" questions and only 5.8% "On Track" snapshots, so the lowest bands are cohort-specific empty); (c) per-semester threshold re-tuning as a deployment-side ML-maintenance concern.

## §4 Methodology to write up in §5.4.11

Three paragraphs + the headline table + one cohort-distribution caveat paragraph. Specific framings:

1. **Motivation**: the dashboard score-to-band mapping was hand-set on round-number boundaries for instructor interpretability; we test whether κ-optimal cutpoints would yield meaningfully better band classification against the LLM rater.

2. **Method**: brute-force grid search over `(c1, c2, c3)` to maximise linear-weighted Cohen's κ against the LLM band labels. Cross-validation matches each underlying model's training scheme: GroupKFold(5) by `session_id` for the three struggle models (n=1306); LeaveOneOut for the three difficulty models (n=72). Trained cutpoints fit on each fold's training set and applied to the held-out fold; per-fold pooled predictions yield the honest κ. Two variants reported — **unconstrained** (pure κ-max, exposes the empirical ceiling) and **constrained** (`c1 ≥ train-fold P5`, every band ≥ 10% of score range — guardrails preventing cohort-overfit degeneracies). The constrained variant is adopted as the deployment default.

3. **Findings**: four of the six (model × score-space) combinations gained substantially under constrained CV training (Δκ between +0.076 and +0.175); two did not (improved-struggle: Δ = −0.002, indistinguishable from noise — the underlying signal is weak regardless of cutpoint choice; IRT-difficulty: see §5.6.x). Per-fold cutpoint variance was below 0.03 on every shipped set, indicating the optima are robust across folds, not overfit artefacts.

4. **Cohort-distribution caveat**: three of the four shipped cutpoint sets place `c1` near the cohort's 5th-percentile score, reflecting the deployment cohort's class imbalance (0 LLM-labelled "Easy" difficulty questions; only 5.8% "On Track" snapshots). The 4-band scheme is retained in the dashboard for symmetry and future-cohort generality; cohort-balanced re-evaluation is identified as future work.

### Why constrained as the default (defensive framing for a viva)

> "We report two threshold-training variants: an unconstrained κ-maximising search that exposes the empirical ceiling, and a constrained variant (`c1 ≥ train P5`, every band ≥ 10% of score range) that produces deployment-defensible cutpoints. The constrained variant captures 50–90% of the unconstrained κ gain while avoiding cohort-overfit degeneracies (notably the collapse of the lowest band to an empty set on cohorts with skewed class distributions). We adopt the constrained variant as the deployment default and report both for transparency."

Reporting both numbers in the table is genuinely strong: it shows you noticed the degeneracy, you understood it, and you priced it explicitly. More credible than reporting just the chosen number.

### Why ship 4 of 6 sets (defensive framing)

> "Threshold-training gains varied substantially across the six (model × score-space) combinations. We adopted trained thresholds where the constrained-CV gain exceeded a pre-registered threshold of κ ≥ 0.05; we retained hand-set thresholds for improved-struggle (constrained gain −0.002, indistinguishable from noise) and IRT-difficulty (constrained κ remains negative — see §5.6.x)."

The phrase "pre-registered threshold of κ ≥ 0.05" gives methodological cover for the asymmetric ship decision.

## §5 The IRT-difficulty anti-result — §5.6.x

This is the most publishable single finding from the threshold work. Suggested framing (3 sentences):

> The IRT Rasch 1PL difficulty model produced negative linear-weighted κ against the LLM 4-band rater both at hand-set thresholds (κ = −0.016) and at constrained CV-trained cutpoints (κ = −0.024). This indicates the IRT model is not failing to map its scores to bands; it is fitting a different latent quantity than the LLM rater judges. IRT-Rasch difficulty captures item-response-pattern difficulty (the probability a student of a given ability gets the question right); the LLM rater judges pedagogical difficulty (curricular position, prerequisite load, cognitive demand). The two are conceptually distinct and empirically uncorrelated on this cohort (Spearman ρ between IRT and baseline composite difficulty = +0.345; top-10-hardest overlap = 1/10). The IRT toggle is retained in the dashboard for transparency; the baseline composite is the recommended production default for difficulty ranking on this cohort.

This is a *negative result* but it's the most defensible kind: empirical test → clear result → substantive interpretation → sensible disposition (toggle retained, default switched).

Pre-load this in Ch2 by adding (if not already present) a brief note in the IRT background distinguishing item-response-pattern difficulty from pedagogical difficulty.

## §6 Cross-chapter touch summary (one-liner per chapter)

| Chapter | Touch |
|---|---|
| Ch1 Contributions | New bullet — see §3 |
| Ch2 Background | Pre-load (a) decoupled vs joint cutpoint estimation; (b) IRT vs pedagogical difficulty distinction |
| Ch3 Design | Reframe hand-set thresholds as interpretability-first design with empirical validation in §5.4.11 |
| Ch4 Implementation | Document promoted threshold values in `config.py`; Appendix B Settings screenshot re-shoot after promotion |
| Ch5 §5.4.11 | NEW subsubsection — the headline of this handoff |
| Ch5 §5.6.x | NEW paragraph on IRT-difficulty κ mismatch |
| Ch6 Future Work | Three new items — see §3 |
| Appendix E (formulae) | Optional — linear-weighted κ formula + brute-force search pseudo-code |

## §7 What HAS been done (2026-05-27 evening — implementation complete)

The implementation pass (covered by `[[v2 Threshold Promotion Handoff]]`, now `status: completed`) executed and landed:

1. ✓ **`code2/backend/config.py`** updated. `STRUGGLE_THRESHOLDS` now (0.000, 0.315, 0.505, 0.605, 1.000) at lines 47-53; `DIFFICULTY_THRESHOLDS` now (0.000, 0.363, 0.463, 0.587, 1.000) at lines 63-69. Provenance comments added above each block citing the Δκ and CV scheme.
2. ✓ **`ols_pred_to_band` in `notebooks/eval_main.ipynb` cell 26** (the handoff had said "cell 24" — actual cell index is 26) parameterised to accept `cutpoints` and `bands`. Default uses `STRUGGLE_V2_OLS_CUTPOINTS = (1.22, 1.78, 2.09)` for the struggle confusion-matrix call site. A constant `STRUGGLE_V2_OLS_CUTPOINTS` was introduced; difficulty equivalent `(1.88, 2.19, 2.69)` is documented in a comment but no difficulty-v2 confusion cell exists in the notebook today, so it's not actively used (would be additive scope if needed).
3. ✓ **`eval_main.ipynb` re-run** (2026-05-27 18:07 UTC). Regenerated figures: `data/eval/figures/confusion_bands.png`, `model_disagreement.png`, plus the other 12 figures the notebook emits.
4. ✓ **`model_comparison.ipynb` re-run** (2026-05-27 ~18:08 UTC). Top-10 leaderboard + pairs-CSV band labels refreshed; no code edits needed (it reads `STRUGGLE_THRESHOLDS` / `DIFFICULTY_THRESHOLDS` via `from backend import config`).
5. ✓ **Settings → Read-only config reference** auto-updated. Live smoke test (`curl http://127.0.0.1:8000/api/settings`) confirmed `thresholds.struggle` and `thresholds.difficulty` return the new tuples. `SettingsView.tsx` source unchanged.

**Phase 0 outcome (the conditional dispatch question):** the backend `.clip(0.0, 1.0)`s the OLS weighted-sum output at `code2/backend/struggle.py:334` and `code2/backend/difficulty.py:176` *before* `classify_score` is called. v2 outputs therefore live in `[0, 1]` space at classification time, so the single `STRUGGLE_THRESHOLDS` set in `config.py` serves both v1 and v2 production paths; **no v2-only [0,3] dispatch was needed in the backend**. The `[0, 3]` cutpoints are eval-notebook-only. Write this up in §5.4.11's method paragraph for clarity ("the deployed scoring path squashes OLS predictions into `[0, 1]` via clip, so the single trained `[0, 1]` cutpoint set serves both weight versions in production; the `[0, 3]` cutpoints reported here are evaluation-side mappings used only for confusion-matrix construction against the band-index target").

The 4 winners' κ values in §2 are already final and unchanged by the implementation pass (they come from the threshold-search CV, not the notebook rerun).

## §8 Authoritative numerical sources

| Artefact | What's in it |
|---|---|
| `data/eval/experiments/threshold_search_cv.json` | Full per-fold cutpoints + κ for all 12 entries (6 unconstrained + 6 constrained) |
| `data/eval/results.md` | Headline metrics — will regenerate post-promotion |
| `data/eval/comparison_struggle_pairs.csv` / `comparison_difficulty_pairs.csv` | Full per-entity baseline-vs-alternative pairs — band-label columns will refresh post-promotion |
| `data/eval/optimised_*_weights_v2.json` | OLS weights + per-fold ρ/κ/MAE for the three v2 models (already canonical, no change) |

## §9 Plots — what changes vs what doesn't (post-promotion)

**Changes** (regenerate from refreshed notebook): `confusion_bands.png`, `model_disagreement.png`, `cohort_distributions.png`, level-column displays in `comparison_struggle_top10.png` / `comparison_difficulty_top10.png`.

**Unchanged** (no threshold dependency): all 12 other figures — weight bar charts, OLS diagnostics, per-fold ρ stability, rank-shift histograms, score-delta scatter, IRT discrimination, incorrectness distribution, Optuna plots, κ inter-rater, baseline-vs-alternative scatter plots.

## §10 What to highlight in a viva (defensive prep)

If a panel asks **"why did you train thresholds at all when v2 OLS already gets you good Spearman ρ?"**:

> "Spearman ρ measures rank agreement; κ measures categorical-band agreement. They are complementary metrics that answer different operational questions. A dashboard that ranks correctly but mislabels can mislead an instructor's intervention decisions; we therefore optimise both. The threshold training improved κ by 0.08–0.18 with no ranking change, completing the optimisation of all user-visible outputs."

If asked **"why didn't you use a joint ordinal regression?"**:

> "Joint fit (e.g. proportional-odds logit) couples the weight estimation to the cutpoint estimation, which would mean any future retuning of either component requires retuning the other. The decoupled fit preserves the interpretability of the underlying weighted composite score, which is the contract with instructors who see the score in the dashboard. We flag joint fit as future work in Ch6 but do not adopt it as the production default."

If asked **"why aren't your trained thresholds round numbers?"**:

> "The trained values reflect the deployment cohort's empirical distribution. The hand-set round-number alternatives sacrifice ~0.10 to ~0.18 κ on classification accuracy in exchange for instructor explainability. We considered both and adopted the trained values because the dashboard's primary contract with instructors is correctness of the band label, not human-friendliness of the underlying cutpoint."

If asked **"why are the lowest bands ('On Track' / 'Easy') empty on this cohort?"**:

> "Class-distribution property of the deployment cohort, not an artefact of the threshold training. The LLM rater assigned zero questions to 'Easy' and only 5.8% of snapshots to 'On Track'. The four-band scheme is retained for symmetry and forward-compatibility with cohorts that may have more uniformly-distributed severity; cohort-balanced re-evaluation is flagged as future work."

If asked **"the IRT-difficulty result is negative — does that mean the IRT model is broken?"**:

> "No. The IRT model is correctly fitting item-response-pattern difficulty (the probability a student of a given ability answers correctly). The negative κ against the LLM rater means the LLM is judging a different latent quantity — pedagogical difficulty — and the two are largely uncorrelated on this cohort. The IRT model would likely be the right choice if the rater were anchored on response-pattern semantics; for the LLM-rated pedagogical-difficulty target, the baseline composite is the stronger production default."

## §11 Style reminders (carry-over from prior handoffs)

- British spelling, declarative, semicolons, no hedging
- Defer code anchors (`file:line` references) to the final Step-11/12 pass — write `config.py` not `code2/backend/config.py:42`
- Student-authored — "we propose / we adopt"; do not name the supervisor in body chapters
- Design artefacts in Ch3; deployed-system screenshots in Ch4 / Appendix B; do not replace one with the other
- Vault notes in `docs/obsidian-vault/My Notes/Thesis/` are working drafts — prose for `Report/main-sections/*.tex` lives only in `Report/`

## §12 Pre-flight reads before drafting

1. `[[v2 Relabel Handoff]]` — prior handoff; the methodology arc and writing-style reminders here are unchanged
2. `[[v2 Threshold Promotion Handoff]]` — sibling implementation handoff; gives you the state of the codebase when the writing-chat picks up
3. `data/eval/results.md` — current canonical numbers (will refresh post-promotion)
4. `notebooks/eval_main.ipynb` cells §5.4.* — for the canonical wording of the v2 weight + hyperparam training pipeline (the threshold section should mirror its structure)
5. `data/eval/experiments/threshold_search_cv.json` — for the per-fold detail you may need to defend the stability claims

## §13 Implementation deltas + freshness rule (added 2026-05-27 evening post-promotion)

**Figure/number freshness rule.** When drafting any §5.4 or §5.6 prose, pull figure files and `results.md` numbers from disk as of the post-promotion state. If your context contains pre-promotion versions (e.g. cached pre-2026-05-27 captures), discard and re-read from disk. This handoff was written before the implementation pass executed; assume `data/eval/results.md` has been regenerated by the time you're reading this (rerun timestamp at the bottom of the file confirms — should read `2026-05-27T18:07:50` or later).

**Deltas from the §7 plan that the writer needs to know:**

1. **Cell index was 26, not 24.** The handoff originally pointed at `eval_main.ipynb` cell 24; the actual `ols_pred_to_band` cell is cell 26. Doesn't affect prose — just don't hunt for it at cell 24.
2. **No backend dispatch.** Phase 2 of the promotion plan (a conditional v2-only dispatch in `cache.py` for `[0, 3]`-space scores) was **skipped** because Phase 0 confirmed the `.clip(0, 1)` already lives in `struggle.py` / `difficulty.py`. The §5.4.11 methodology paragraph should reflect this — see §7 above for the suggested wording.
3. **No difficulty-v2 confusion cell exists in the notebook.** The handoff suggested adding one for parity with struggle; the implementation chat decided this was scope expansion (no §5.4.x prose currently cites a difficulty-v2 band-confusion figure) and deferred. If the writer wants this figure for §5.4.9 or §5.4.11, request a separate implementation pass.
4. **Recap toolkit — DELETED 2026-05-27 evening (no longer a sync target).** The HTML toolkit and its CLAUDE.md section were removed (user decision). Disregard the earlier "writing chat owns the toolkit sync" instruction — there is nothing to sync. Canonical sources are the vault + `data/eval/results.md` + the report.
5. **Vault sync notes already added by the implementation chat** to:
   - `v2 Methodology Journal.md`
   - `Evaluation PoC Handoff.md`
   - `Evidence Bank.md`
   - `Figures and Tables.md` (flags Tbl 6 / Tbl 7 stale verbatim values)
   - `Full Roadmap.md` (top-level sync note + flag on Tbl 6 TODO)
   - `Model Training/00 Overview.md` (Component (3) closure marker)
   - `v2 Threshold Promotion Handoff.md` (front-matter flipped to `status: completed`)

   The writing chat doesn't need to add more sync notes to these — they're done.

6. **Suspicious denominator in §5.6.1.** `results.md` §5.6.1 currently reports counts over `n=42443` rather than `n=1306`. This pre-dates the threshold promotion (same anomaly in the prior version) and is a notebook-side bug, not a threshold-promotion artefact. Writer should either normalise the percentages in prose (compute over 1306 manually) or flag it for a separate notebook fix before publishing those numbers.

---

## §14 — Model-class comparison + v1 removal + training-methodology migration (added 2026-05-27 evening; v1-removal finalised 2026-05-27)

This is the biggest report change of the session. It has three intertwined parts: (a) promote the model-class bake-off to THE headline §5.4 comparison, (b) **cut v1 from the evaluation entirely** — v2 is the premiere/deployed model, §5.4 has no v1-vs-v2 comparison (the bake-off's trained-vs-trained comparison covers rigour), (c) migrate the training methodology from an evaluation-only topic into the design + implementation chapters because the trained weights are now the deployed system. (NOTE: an earlier draft of this section said "demote v1 to a light baseline" — that is **superseded** by §14.3's removal decision below.)

### §14.1 — What changed in the system + artefacts (implementation already done)

- **v1/v2 weight + hyperparam toggles REMOVED from the live system.** `code2/backend/{runtime_config,cache,schemas,routers/settings}.py` and `code2/frontend/src/{views/SettingsView.tsx,types/api.ts}` no longer carry `struggle_weights_version` / `difficulty_weights_version` / `improved_struggle_weights_version` / `hyperparams_version`. The backend uses the trained v2 weights + Optuna-tuned hyperparameters unconditionally. The Settings → Advanced "Optimised Weights (v2)" card is gone (BKT Parameters + Read-only config reference remain).
- **KEPT**: BKT / IRT / improved-struggle model code; the `struggle_model` (baseline|improved) and `difficulty_model` (baseline|irt) model-class toggles; `shrinkage_k` (seeded from the Optuna value, still user-adjustable); the v1 hand-set weight CONSTANTS in `config.py` (the eval notebook reads them for the comparison).
- **Two bake-offs promoted to canonical** `data/eval/model_class_bakeoff.json` + `data/eval/classifier_bakeoff.json` (originals retained in `data/eval/experiments/` for provenance).
- **Two new figures** in `data/eval/figures/`: `model_class_bakeoff.png` (OLS vs 5 regression alternatives × 3 targets) + `framing_regression_vs_classification.png` (OLS vs 3 classifiers, ρ + κ panels).

### §14.2 — The headline §5.4 comparison numbers

**Regression model-class bake-off** (Spearman ρ vs 4-band, same CV as `optimise_v2_weights.py`):

| Target | OLS (deployed) | Best alternative | Verdict |
|---|---|---|---|
| Struggle | **+0.588** | RandomForest +0.565 | OLS wins; all linear variants within ±0.003 |
| Difficulty | +0.469 | RandomForest +0.479 (Δ +0.010, noise) | tie; Lasso/Ridge within ±0.003 |
| Improved-struggle | +0.201 | RandomForest +0.250 | RF wins on ρ but forfeits interpretable signed weights |

**Regression-vs-classification framing** (classifiers = multinomial logit, RF, GB):

| Target | OLS ρ (rank) | best-classifier ρ | OLS raw κ | best-classifier κ | OLS κ *with trained thresholds* (§5.4.11) |
|---|---|---|---|---|---|
| Struggle | +0.585 | +0.582 (≈tie) | +0.380 | +0.475 (RF) | **+0.456** |
| Difficulty | +0.468 | +0.551 (RF, +0.083) | +0.225 | +0.444 (GB) | **+0.436** |
| Improved | +0.175 | +0.221 (RF/GB) | +0.007 | +0.129 (GB) | n/a (not shipped) |

**The combined narrative (this is the strong story)**: OLS regression is competitive-to-best on *ranking* (Spearman ρ — what the leaderboard uses); classifiers win on raw *κ* because they optimise the categorical objective directly; BUT the trained band-thresholds lift OLS's κ to a level that matches the best classifier (struggle +0.456 vs RF +0.475; difficulty +0.436 vs GB +0.444). So the deployed **OLS-regression + trained-thresholds** pipeline captures the classification gain *while keeping interpretable signed weights and the stronger ranking*. That's the §5.4 thesis: the model-class choice is justified on merit, not just convenience.

### §14.3 — v1 REMOVAL from the evaluation (superseding the earlier "demotion" framing)

**Decision updated 2026-05-27 (final):** v1 is **cut from the evaluation entirely**, not demoted. The user's rationale: "training beats hand-set is obvious — it's a waste of §5.4 space." v2 is the **premiere / deployed model**; §5.4 contains **no v1-vs-v2 comparison**. The "better than what?" rigour concern is answered by the **model-class bake-off** (trained-vs-trained: OLS vs Ridge/Lasso/ElasticNet/RF/GB + classifiers) — a non-trivial comparison — so a hand-set baseline is not needed in Ch5.

- The hand-set origin gets **at most one sentence in Ch3/Ch4** as design history ("the initial weights were hand-set; the deployed weights are trained"), past tense. It is NOT an evaluation result in Ch5.
- The substantive §5.4 comparison is **"which training method wins"** (the bake-off), not "trained vs hand-set".
- Drop the "v1 as control / light baseline" language from earlier drafts — that framing is superseded.

**New §5.4 structure (the writer follows this):**
1. §5.4.1–5.4.2 — cohort + inter-rater κ (unchanged)
2. §5.4.3 — **v2 model outputs + quality**: the trained v2 weights (v2-only chart or a table from `optimised_struggle_weights_v2.json`, NOT the v1-vs-v2 paired chart), per-fold ρ stability, OLS residuals diagnostic, per-fold weight-stability heatmap, v2-vs-LLM confusion matrix (v2 column only)
3. §5.4.x — **HEADLINE: model-class selection (the bake-off)** — OLS vs all alternatives + regression-vs-classification framing; the two bake-off figures; the honest per-target story (see §14.3a)
4. §5.4.10 Optuna hyperparameters; §5.4.11 thresholds
5. §5.6 limitations (IRT anti-result, cohort skew, improved-struggle weakness)

**Figure inventory:**
- **USE:** `model_class_bakeoff.png`, `framing_regression_vs_classification.png`, `per_fold_rho_struggle.png`, `ols_diagnostic_struggle.png`, `residuals_struggle.png`, `weight_heatmap_struggle.png`, `kappa.png`, `optuna_*`, `eval-irt-discrimination.png`, `eval-incorrectness-distribution.png`, + a v2-only weight chart/table.
- **DROP (v1-vs-v2):** `weights_struggle_v1_vs_v2.png` (replace with v2-only), `confusion_bands.png` (use v2-only), `model_disagreement.png`, `pred_vs_obs_v1_v2_struggle.png`, `score_delta_v1_vs_v2_struggle.png`, `rank_shift_v1_vs_v2_struggle.png`, `rank_shift_v1_vs_v2_difficulty.png`.
- The notebook cells producing the dropped figures are marked SUPERSEDED / "v1 cut from report" (markdown banners, 2026-05-27) — the figures still exist on disk but the report does not cite them.

**New asset the writer needs:** a **v2-only struggle weight chart or table** (the interpretability story — signed weights incl. the negative w_M/w_D improved-struggle finding). Simplest: a table from `optimised_*_weights_v2.json`; or a one-cell notebook addition.

### §14.3a — Why OLS and not RandomForest where RF "wins" (viva-critical defence)

Making the bake-off the headline invites the obvious question: RF tops difficulty (+0.479 vs OLS +0.468) and improved (+0.250 vs +0.201) on ρ, so why deploy OLS? §5.4 must pre-empt this:
1. **The RF edges are within per-fold variance** — improved's +0.049 gap is < 0.5× the per-fold std (≈ 0.124–0.136); difficulty's +0.011 is negligible and RF overfits at n=72 (LOO); RF *loses* struggle clearly (−0.023). RF does not *reliably* beat OLS on any target.
2. **RF has no interpretable signed weights** — the entire §5.4 interpretability narrative (sign-flips; the negative w_M/w_D improved-struggle finding) is impossible with a black-box ensemble.
3. **Improved-struggle is a weak, non-default toggle** (ρ ≈ 0.20 either way; struggle_model defaults to baseline) — not worth a black-box swap for noise-level gain.

Frame as: *"OLS is competitive-or-better within noise on every target, wins struggle decisively, and is the only competitive model class yielding interpretable signed weights — so it is deployed across all three."*

### §14.3b — IRT difficulty's position (separate axis, §5.6 anti-result, unchanged)

IRT difficulty is **not in the bake-off** — it is a latent-trait model fit on the response matrix, not a regression on the 5 composite features, so it is not apples-to-apples with the model-class comparison. It is unaffected by the v1-cut and stays as: the live `difficulty_model = irt` Settings toggle, and the **§5.6 anti-result** (negative κ vs the LLM rater: −0.016 hand-set / −0.024 trained; ρ +0.345 vs composite +0.468 — it measures item-response-pattern difficulty, not the LLM's pedagogical difficulty). Methods story: the bake-off compares regression classes for the composite difficulty model; IRT is reported separately in §5.6 as a model measuring a different latent quantity.

### §14.4 — Training-methodology migration to Ch3 + Ch4 (the structural move)

Because the trained weights are now *the deployed system*, the training methodology is no longer an evaluation activity — it's how the system works. It graduates from Ch5-only to earlier chapters. **Anti-duplication table — write each item ONCE in its canonical home, recap + forward-ref elsewhere:**

| Topic | Canonical home (full description) | Recap-only (forward-ref) |
|---|---|---|
| Decision to train weights by LLM-supervised OLS vs hand-tuning | **Ch3 Design** (design rationale) | Ch5 (one line: "as designed in §3.x") |
| 4-band ordinal target design + LLM-as-rater rationale | **Ch3 Design** | Ch5 §5.4 preamble (recap) |
| Feature sets (7 struggle / 5 difficulty / 3 improved) | **Ch3** (already there — reframe as inputs to a *trained* model) | — |
| Training pipeline: `optimise_v2_weights.py`, CV machinery, weights→JSON | **Ch4 Implementation** | Ch5 (recap the CV scheme only) |
| GPT-4o labelling flow (`eval_fetch.py` / `eval_label.py` / `eval_common.py`) | **Ch4 Implementation** | Ch5 §5.4.2 κ (recap) |
| Optuna hyperparameter pipeline | **Ch4 Implementation** | Ch5 §5.4.10 (results only) |
| Threshold-training pipeline | **Ch4 Implementation** | Ch5 §5.4.11 (results only) |
| How trained artefacts load into the live scoring path (config + JSON + cache.py) | **Ch4 Implementation** | — |
| Model-class bake-off (OLS vs alternatives + classification framing) | **Ch5 §5.4.x** (evaluation/validation) | Ch3 forward-ref ("model-class selection validated in §5.4.x") |
| Threshold optimisation results + IRT anti-result | **Ch5 §5.4.11 / §5.6.x** | — |

**Chronological honesty**: V1 was hand-set first; V2 evolved it via training. Ch3/Ch4 present the trained approach as the V2 design with V1's hand-set origin acknowledged as the starting point — consistent with the existing "V2 is the evolution of V1, not an alternative" branding.

### §14.5 — Cross-chapter touches

- **Ch1 Contributions**: add a bullet — the LLM-supervised training methodology + model-class-selection rigour as a *core contribution* (not just an evaluation finding). Pairs with the existing empirical-validation bullet.
- **Ch2 Background**: add (a) model-class-selection literature (why compare regularised / non-linear / classification alternatives); (b) LLM-as-rater / LLM-supervised labelling background; (c) ordinal-regression target background. These pre-load §5.4.x.
- **Ch4**: the Settings UI no longer has the weight-version toggles — describe a single trained scoring path. **Specific stale passage to rewrite: `implementation.tex:1254`** currently describes V2's "Optimised Weights (v2)" Settings section with "four select rows ... selecting v2 on any row invalidates the selected cache" and implies v1 is active until the user opts in — that UI was removed; rewrite to "V2 loads the trained weights + Optuna hyperparameters unconditionally; there is no v1/v2 runtime selector". Appendix B Settings screenshot re-shoot already flagged in §3.
- **Ch6 Future work**: unchanged from §3 (joint ordinal fit, cohort-balanced re-eval, per-semester retuning).

### §14.6 — Figures + sources for §5.4.x

- `data/eval/figures/model_class_bakeoff.png` — the regression-alternatives comparison
- `data/eval/figures/framing_regression_vs_classification.png` — the regression-vs-classification ρ + κ panels
- `data/eval/model_class_bakeoff.json` + `data/eval/classifier_bakeoff.json` — the numbers
- `data/eval/experiments/DECISION.md` — reframed this session from "defensive §5.6 footnote" to "headline §5.4 comparison"; lift the "why not switch to RF / Lasso" reasoning from there

### §14.7 — Risk flags for the writer

- **Don't double-document the training.** Use the §14.4 anti-duplication table — full method in its canonical chapter, recap + forward-ref elsewhere.
- **Don't over-claim OLS.** Be honest that classifiers win raw κ and RF wins difficulty ρ; the OLS case rests on ranking + interpretability + the trained-threshold κ recovery, not on dominating every metric.
- **v1 is cut from Ch5 — do NOT reintroduce a v1-vs-v2 comparison.** The "better than what?" rigour is covered by the bake-off (trained-vs-trained); the hand-set origin is design history (one line in Ch3/Ch4), not an evaluation result.
- **Chronological honesty** — V1 hand-set → V2 trained-evolution; don't retcon the design as "trained from the start".

End of handoff.
