# 11 — Evaluation Plots Review

Deep look at the Evaluation chapter's figures (the 2026-05-29 follow-up: "such as violin plots… just double check the plots"). **Decision:** add the **violin/box plots** only — **no confusion matrix, no IRT discrimination plot** (per the user). The rest is a double-check. No figure regeneration or `.tex` edit applied until approved. ← [[00 Index]]

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
- **Counts vs percentages (consistency, NEW):** the chapter mixes raw counts and percentages, and it reads messy — most glaring in the survey. Q5 (7/2/1) and Q6 (6/3/1) are reported as **counts out of ten**, but Q7 is converted to a "$70/10/20$" **percentage** split (§5.3.2 ~l103–105), and the **NFR2 row in Appendix C** (`detailed-test-results.tex`) mirrors the same mix (`7/2/1`, `6/3/1` vs `70/10/20`). With **n = 10** a percentage implies false precision (one respondent = 10 pp). **Recommended convention:** report the small-n survey Likert items as **raw counts (x of 10)** throughout §5.3.2, §5.5 (`sec:eval-survey`) and the NFR2 appendix row; reserve **percentages for the large-n quantities only** (e.g. the 92.5 % incorrectness fallback over 42,443 submissions, the LLM–human agreement κ). Also sweep the survey figure axes/labels (`fig:eval-survey-baseline`, `fig:eval-survey-interpretability-trust`) for the same mix. Convention is an **author decision**; once chosen, the prose/appendix edits are mechanical and **I apply gated**.

## Gated
The new plotting cell, any figure regeneration/re-copy, and the two `\includegraphics` insertions are previewed for approval before anything is applied to the notebook or `Report/`.
