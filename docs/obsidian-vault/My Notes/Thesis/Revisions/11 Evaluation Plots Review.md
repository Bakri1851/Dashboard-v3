# 11 — Evaluation Plots Review

Deep look at the Evaluation chapter's figures (the 2026-05-29 follow-up: "such as violin plots… just double check the plots"). **Decision:** do not add the **violin/box plots** only — **no confusion matrix, no IRT discrimination plot** (per the user). The rest is a double-check. No figure regeneration or `.tex` edit applied until approved. ← [[00 Index]]

## Inventory (verified)
- Ch5 references **16** figures via `\includegraphics{figures/evaluation/...}`.
- `notebooks/eval_main.ipynb` is the **canonical source** (saves to `data/eval/figures/` via `_save(name)`); `Report/figures/evaluation/` holds the copies actually compiled into the PDF; `scripts/experiments/extra_figures.py` writes two figures straight into `Report/figures/evaluation/`.
- `data/eval/figures/` holds **~29** generated plots → **~13 are currently unused**.
- **Generated but unused** (do *not* add the two the user excluded): `confusion_bands.png` ❌excluded, `eval-irt-discrimination.png` ❌excluded, `kappa.png`, `pred_vs_obs_v1_v2_struggle.png`, `pred_vs_obs_v2_struggle.png`, `weights_struggle_v1_vs_v2.png`, `negative_findings_v2.png`, `score_delta_v1_vs_v2_struggle.png`, `residuals_struggle.png`, `model_disagreement.png`, `rank_shift_v1_vs_v2_struggle.png`, `rank_shift_v1_vs_v2_difficulty.png`, `hyperparams_optuna.png`, `optuna_joint_history.png`, `comparison_*_top10.png` (the top-10s are LaTeX tables, not images).

## The addition — violin/box plots of score-per-band (G1)
**Goal:** show how cleanly the deployed continuous score separates the four LLM bands — monotonic medians with controlled overlap is the visual case for the ranking quality that ρ summarises numerically.

**Two figures (one per target):**
- **Struggle** (n = 1306) → lands in §5.4.2 (Struggle Model Outputs and Quality), beside `ols_diagnostic_struggle`.
- **Difficulty** (n = 72) → lands in §5.6.1 (the difficulty discussion). With n = 72, prefer a **box+strip (jittered points) plot** over a violin (a violin's KDE is misleading at small n); a violin is fine for the 1306-snapshot struggle plot.

**Data — already in the notebook, small new cell:**
- x = LLM band; y = deployed **min-max [0,1] composite** score.
- Struggle: `matched = [s for s in snapshots if s['snapshot_id'] in llm_struggle_labels]`; `y = _v2_score(s['v1_features'], opt_struggle['weights'], STRUGGLE_SIGNALS)`; `band = llm_struggle_labels[s['snapshot_id']]['band']`; order bands by `STRUGGLE_BANDS` / `STRUGGLE_BAND_INDEX`.
- Difficulty: analogous with `diff_questions`, `llm_difficulty_labels`, `_v2_score(..., opt_difficulty['weights'], DIFFICULTY_SIGNALS)`, `DIFFICULTY_BANDS`.
- **Overlay the trained band cutpoints** as horizontal lines — struggle (0.102, 0.203, 0.326), difficulty (0.288, 0.388, 0.531) — so the reader sees how §5.4.5's thresholds slice the distributions; this visually links the score, the bands and the κ result in one figure.
- Save via the notebook's `_save('score_by_band_struggle')` / `_save('score_by_band_difficulty')`, then copy into `Report/figures/evaluation/` like the others.

**Captions (number + short title only, per [[02 Proposed Report Edits — structural]] S4):** e.g. "Deployed struggle score by LLM band" / "Deployed difficulty score by LLM band"; put the interpretation (monotonic medians, overlap, where the cutpoints fall) in the body paragraph after the figure, not the caption.

**Caveat to state in the body:** the difficulty cohort has no "Easy" band and the struggle cohort few "On Track" (the §5.4.1 / §5.6.3 skew) — so the lowest violin/box will be sparse or empty; acknowledge it rather than letting it look like a plotting error.

## The double-check (G2)
- **Report ↔ canonical sync:** confirm every referenced `Report/figures/evaluation/*.png` matches the latest `data/eval/figures/` version (the notebook is source-of-truth; the Report copies are manual and can drift — `weight_heatmap_struggle.png` shows as modified in *both* trees in `git status`, so a re-copy pass is warranted). Check mtimes / re-run the notebook and re-copy.
- **Hardcoded numbers:** `eval-incorrectness-distribution.png` caption injects "42,443" and "92.5%" via a string-replace in `extra_figures.py` (l180) — keep in lockstep with the §5.6.3 prose fix ([[01 Integrity & Consistency Fixes]] I9). If the cohort/window is restated (I8), re-check these.
- **In-plot titles vs LaTeX captions:** several plots bake a title + annotation box *into the PNG* (notably `eval-incorrectness-distribution`, and the excluded IRT plot). Once LaTeX captions are trimmed to number+title (S4), the in-image title duplicates the caption — decide whether to strip in-plot titles (cleaner) or keep them; be consistent across the chapter.
- **Orphaned copies:** decide use-or-drop for the unused PNGs sitting in `Report/figures/evaluation/` (`kappa.png`, `pred_vs_obs_*`, `weights_struggle_v1_vs_v2.png`, `negative_findings_v2.png`, plus the excluded `confusion_bands.png` / `eval-irt-discrimination.png`) so the repo doesn't carry orphaned figures an examiner might find.
- **Numbers spot-check (done, consistent):** trained struggle weights (`A_norm` +0.314, `t_hat`/`rep_norm` flipped negative), per-fold ρ {0.498, 0.508, 0.666, 0.636, 0.633}, difficulty ρ +0.468, cohort 1306 / 72 / 21-of-23 — all match `data/eval/results.md`. Note the abstract/conclusion ρ=+0.469 typo is tracked separately in [[01 Integrity & Consistency Fixes]] I2.
- **Counts vs percentages (consistency, NEW):** the chapter mixes raw counts and percentages, and it reads messy — most glaring in the survey. Q5 (7/2/1) and Q6 (6/3/1) are reported as **counts out of ten**, but Q7 is converted to a "$70/10/20$" **percentage** split (§5.3.2 ~l103–105), and the **NFR2 row in Appendix C** (`detailed-test-results.tex`) mirrors the same mix (`7/2/1`, `6/3/1` vs `70/10/20`). With **n = 10** a percentage implies false precision (one respondent = 10 pp). **Recommended convention:** report the small-n survey Likert items as **raw counts (x of 10)** throughout §5.3.2, §5.5 (`sec:eval-survey`) and the NFR2 appendix row; reserve **percentages for the large-n quantities only** (e.g. the 92.5 % incorrectness fallback over 42,443 submissions, the LLM–human agreement κ). Also sweep the survey figure axes/labels (`fig:eval-survey-baseline`, `fig:eval-survey-interpretability-trust`) for the same mix. Convention is an **author decision**; once chosen, the prose/appendix edits are mechanical and **I apply gated**. **DONE 2026-05-31 — convention chosen: raw counts.** Prose converted across §5.3.2 (Q7) and §5.5 (Q2, Q3, Q7, Q9, triangulation paragraph); NFR2 appendix row already in counts; large-n percentages (cohort/incorrectness/CI) left as percentages. Report compiles clean. **RESOLVED 2026-06-01:** the three survey figure PNGs already plot **raw counts** - `survey_main.ipynb` sets `ax.set_xlabel("Number of respondents (n=N)")` - so the axes match the counts prose; no regeneration needed.

## Gated
The new plotting cell, any figure regeneration/re-copy, and the two `\includegraphics` insertions are previewed for approval before anything is applied to the notebook or `Report/`.

## Outcome - audit applied 2026-06-01

**Violin/box plots: DROPPED** (user, 2026-06-01). The score-vs-band separation they would show is already carried by `ols_diagnostic_struggle` (predicted vs observed band) and `cohort_distributions`; redundant in a 16-figure chapter. The double-check below is the deliverable.

**Double-check (G2): every chapter number traced to `data/eval/*.json`.** One substantive error, three minor; everything else verified correct.

1. **(Substantive) IRT difficulty ρ mislabelled "against the rater" - §5.6.1 lines 488 + 490.** The cited ρ=+0.345 is `spearmanr(baseline_score, irt_score)` (cross-model; the title of `comparison_difficulty_scatter.png`), not IRT-vs-rater; no IRT-vs-rater ρ existed in `data/eval`. Recomputed via `scripts/experiments/recompute_difficulty_comparison.py`: **IRT-vs-rater ρ = -0.034** (n=72); baseline-vs-IRT +0.345 (reproduced, confirms pipeline); v1-baseline-vs-rater +0.414. The true -0.034 (essentially no rank agreement) strengthens the anti-result and matches the negative κ (-0.016 / -0.024). Scatter in-figure title clarified to ρ(baseline, IRT).
2. **Fig-15 mis-citation - line 488.** `fig:eval-negative-findings` (a v1-vs-v2 weights bar chart, no IRT, no ρ) was cited as the ρ source; it is the figure's only in-text `\ref`, so reposition rather than delete or it orphans.
3. **On-Track % inconsistency - line 164 ("6%") vs line 556 ("5.8%").** Same quantity (76/1306 = 5.82%). Figure 5.1 (cohort) displays it as "76 (6%)", so the figure rounds to 6%; harmonised **both lines to 6%** (line 556 5.8% -> 6%) to match the figure rather than introduce a figure/prose mismatch. Applied 2026-06-01.
4. **Weights figure + heatmap tick labels** used raw keys (`A_norm`, `t_hat`, ...); regenerated with human names via `scripts/experiments/relabel_weight_figures.py`. Note `d_hat` = improvement-trajectory slope (not IRT difficulty); `A_norm` = recent incorrectness = +0.314, so the prose label is correct.

**Verified correct (no action):** Table 2 thresholds (all six rows = `threshold_search_cv.json` constrained κ); deployed κ +0.384/+0.387 + cutpoints (= `threshold_search_v2composite.json`; correct-by-design against Table 2's StandardScaler-fit +0.456/+0.393, as §5.4.4 explains); model-class bake-off +0.588 / +0.479 / +0.250 (= `model_class_bakeoff.json`); struggle ρ +0.588, inter-rater κ 0.198/0.262/38%/68%; all survey counts; cohort LLM 47.3% Needs Help / 5.8% On Track / 72.2% Very Hard (`results.md`'s "76% Very Hard" is the stale value; `pooled_y` = 52/72 = 72.2%, so the chapter's 72% is right).

**Figures regenerated into `Report/figures/evaluation/`:** `weights_struggle_v2.png`, `weight_heatmap_struggle.png`, `comparison_difficulty_scatter.png` (jupyter unavailable, so via standalone scripts, not notebook execution). Notebook source patched for consistency: `eval_main.ipynb` tick-label lines; `_nb_create_model_comparison.py` now also prints IRT-vs-rater + baseline-vs-rater ρ and clarifies the scatter title. **No `\cite{}` changes, so `sync_literature.py` not re-run and `references.bib` untouched.**

**Prose: briefs delivered to author** (three edits - line 164 number; lines 488/490 ρ value + Fig-15 reposition). No `.tex` edited by me, per the gating/author-writes rule.
