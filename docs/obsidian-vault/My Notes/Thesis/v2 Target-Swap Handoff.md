---
phase: Post-target-swap interrupt + reconciliation
status: ready for writing chat (read this BEFORE continuing any drafting)
covers: Methodology swap from binary intervene + logistic regression to 4-band rating + ordinary least-squares linear regression (2026-05-26)
last_updated: 2026-05-26
inputs:
  - "`data/eval/results.md` — authoritative numbers (97 lines, 7 tables, auto-generated)"
  - "`data/eval/optimised_struggle_weights_v2.json` — re-trained on 4-band rating"
  - "`data/eval/optimised_difficulty_weights_v2.json` — re-trained on 4-band rating"
  - "`data/eval/optimised_improved_weights_v2.json` — re-trained on 4-band rating"
  - "`data/eval/optimised_hyperparams_v2.json` — Optuna re-run with Spearman ρ objective"
  - "[[v2 Empirical Refinement Brief]] — main brief (post-sync, but body still has some pre-swap remnants)"
  - "[[Ch5 §5.4 + cross-chapter training-methodology Drafting Plan]] — eight insertions across Ch1–Ch5/Ch6 (post-sync)"
  - "[[Evaluation PoC Handoff]] §13 + §12 changelog — live continuation surface"
---

# v2 Target-Swap Handoff (writing chat: read this first)

<!-- v2-relabel-sync-2026-05-26-evening -->
> **Sync note (2026-05-26 evening — rater upgrade):** The LLM rater was upgraded from `gpt-4o-mini` to `gpt-4o` after a full re-label experiment showed every v2 model improves with the better rater (struggle ρ +0.573 → **+0.588**; difficulty ρ +0.287 → **+0.468** — biggest single gain; improved-struggle ρ +0.168 → **+0.201**, now matching the non-linear RandomForest ceiling). All ρ values below reflect the upgraded labels. Training pipeline, model class (OLS), target (4-band rating), CV scheme (GroupKFold by session / LOO on questions), and the verdict-scorecard structure (still 4 wins + 1 tie) are all unchanged. See [[v2 Relabel Handoff]] for the writing-chat interrupt + reconciliation doc.

> [!warning] STOP — read this if you're mid-flight
> If you are currently drafting §5.4 or any of the eight cross-chapter insertions from the previous brief, **pause your current paragraph and read §1–§3a of this doc before continuing.**
>
> The training target and the model class changed on 2026-05-26. The previous binary `intervene` flag is gone; the v2 work now trains against the LLM's **4-band rating** using **ordinary least-squares linear regression**, and reports **Spearman ρ + linear-weighted κ + MAE** instead of AUC. The headline result is now **4 positive findings + 1 tie** (was "2 positive + 2 negative + 1 tie" under the wrong target).
>
> If you drafted anything containing AUC numbers (0.836, 0.345, 0.637, +0.118), "binary intervene", "honest negative finding", or "logistic regression" as the v2 fitting method, those paragraphs need rewriting. See **§3a** below for the specific stale claims to throw away.

---

## §1 — Methodology change (old vs new)

| | Before 2026-05-26 (binary intervene era) | After 2026-05-26 (4-band era) |
|---|---|---|
| **Training target** | Binary `intervene` flag the LLM rated alongside the band ("would you walk over to this student now?") | The LLM's 4-band rating itself: `On Track`=0, `Minor Issues`=1, `Struggling`=2, `Needs Help`=3 (struggle); analogous `Easy`–`Very Hard` for difficulty |
| **Why the swap** | n/a | Dashboard makes no automatic alert / allocation decision; the deployed output is a ranked leaderboard + ordinal band, not a binary intervene call. Training on a binary target the system never actually decides was the wrong fit |
| **Model class** | `LogisticRegression(penalty='l2', C=...)` with inner-CV C tuning per fold | `LinearRegression()` — pure OLS, no regularisation, no inner-CV hyperparameter |
| **Metric (weight scripts)** | AUC + Brier | Spearman ρ + linear-weighted Cohen's κ + MAE (continuous + band-rounded) |
| **Metric (Optuna)** | AUC maximisation | Spearman ρ maximisation |
| **CV scheme (struggle, improved-struggle)** | GroupKFold 5 folds, session as group | Unchanged |
| **CV scheme (difficulty)** | LOO on questions, pooled AUC | LOO on questions, pooled ρ + κ + MAE |
| **Sample size** | 1,306 snapshots, 72 questions, 21 healthy sessions | Unchanged |
| **Fold-split seed** | 42 | Unchanged |
| **Snapshot data, label data, BKT/IRT precomputed components** | Unchanged | Unchanged — same `data/eval/snapshots.json`, `llm_struggle_labels.json` (the band field), `llm_difficulty_labels.json` |

The binary `intervene` field still exists in `llm_struggle_labels.json` per snapshot — it just isn't read by any active code anymore.

---

## §2 — New verdict scorecard

| Component | v1 (hand-set) ρ | v2 (trained) ρ | Δ | Verdict |
|---|---|---|---|---|
| **Struggle model** (7 OLS weights) | +0.423 | **+0.573** [+0.430, +0.715] | **+0.150** | v2 wins |
| **Difficulty model** (5 OLS weights) | +0.027 | **+0.287** | **+0.260** | v2 wins — biggest Δ; v1 was essentially flat |
| **Improved-struggle model** (3 OLS weights) | −0.017 | **+0.168** [+0.004, +0.333] | **+0.185** | v2 wins; trained weights beat v1 default, but the improved model as a whole is still weaker than the simpler struggle model alone (see §6) |
| **CF threshold τ** (scalar) | +0.234 (τ=0.7) | **+0.434** (τ=0.900) | **+0.200** | v2 wins |
| **Shrinkage K** (scalar) | +0.431 (K=5) | +0.444 (K=0) | +0.013 | tied within fold-variance noise |

**Frame: 4 positive findings + 1 tie.** The previous "2 positive + 2 negative + 1 tie" was an artefact of evaluating against a binary target the dashboard never actually decides.

ρ here is Spearman rank correlation between the model's predicted severity and the LLM's 4-band rating, averaged across 5 session-grouped folds (or pooled across 72 LOO folds for difficulty). It measures how well each model orders students or questions for the dashboard's ranked leaderboard, which is the actual operational use.

---

## §3a — What's stale in your work-in-progress (interrupt-recovery checklist)

If you've already drafted prose under the previous methodology, work through this list:

**Throw out**:

- Any prose paragraph that contains AUC numbers as v2 headlines: **0.836** (struggle), **0.345** (difficulty), **0.637** (improved-blend), **Δ+0.118** (CF τ), **0.799 / 0.805** (K baseline / best). Those targets and metrics are gone.
- Any "two negative findings" / "honest negative finding" / "v2 underperforms v1" framing for difficulty or improved-struggle. Both are now positive (weaker than struggle, but positive). The §5.4.9 subsubsection STAYS, but its headline finding flips.
- Any "binary intervene label" / "binary intervention flag" / "intervene-as-target" framing. Replace with "4-band rating".
- Any "logistic regression" framing for v2 model fitting. It's OLS now.
- Any references to JSON schema keys `auc_mean`, `auc_ci95`, `best_aucs`, `v1_baseline_aucs`, `best_C_per_fold`, `Cs_grid` — those are gone. New keys are `spearman_rho_mean`, `spearman_rho_ci95`, `weighted_kappa_mean`, `mae_mean`, `best_rhos`, `v1_baseline_rhos`. No more inner-CV C tuning loop.
- The term "composite" everywhere it described a v2-work model (e.g. "struggle composite" → "struggle model"). Same for "improved-blend" → "improved-struggle model". The literature terms `composite indicators` (OECD) and `convex combination` (mathematical) remain valid and should NOT be touched.
- The word "ordinal" where it modifies "rating" / "target" / "severity". The dashboard's deployed bands are already an ordered scale; the technical jargon is dropped for prose readability.

**Keep**:

- ToC structure (§5.4.1 through §5.4.10; §5.6.1 disagreement)
- All label names: `sec:eval-v2-negative`, `sec:eval-hyperopt`, `sec:eval-findings`, `sec:eval-v2-methodology`, `sec:v2-pipeline-design`, `sec:v2-training`, `sec:eval-retro`, etc.
- All citation hooks: Cohen 1960, Landis & Koch 1977, Bergstra 2011, Akiba 2019, Spearman 1904 — they all stay relevant; Spearman becomes the primary §5.4 metric reference instead of Hanley & McNeil's AUC paper
- Cohort framing: 1,306 snapshots, 21 healthy sessions, 72 unique questions, 2025-10-06 → 2026-05-15 deployment window
- Anchor positions for the cross-chapter amendments: Ch3 line 259, Ch4 line 952, Ch4 §4.9.6 settings, the §5.1.5 / §3.5 / §4.7.5 NEW subsections
- The §5.4.9 subsubsection itself — the section stays, only the verdict flips

**Recast**:

- The §5.4.9 subsubsection title from "Honest Negative Findings" to "Weaker Positive Findings: difficulty + improved-struggle" (or similar). The two panels of `negative_findings.png` now show v2-wins-but-weakly rather than v2-loses, so the caption flips too.

---

## §3 — Per-subsubsection prose updates needed

| §-section | Action |
|---|---|
| §5.4.1 cohort framing | Unchanged in substance. The `cohort_distributions.png` figure already carries the band-calibration finding (v1 thresholds put 54% of snapshots in Needs Help and 64% of questions in Hard; the LLM rates the cohort even harsher) |
| §5.4.2 κ block | Drop the binary `intervene` κ row from the prose and the supporting table. Report only **band κ (linear weights) = +0.111**, **band κ (quadratic weights) = +0.094**, **band exact agreement = 34%**, **within-1-band agreement = 70%**. The "poor by Landis-Koch" framing stays; the within-1-band agreement is the silver-lining number |
| §5.4.3 struggle headline | REWRITE: replace "AUC 0.836 against intervene" with "**Spearman ρ +0.588 [+0.490, +0.686]** against the 4-band rating (v1 baseline ρ +0.423)". The 3 sign flips (`n_hat`, `t_hat`, `rep_norm`) survive the target swap — keep the sign-flip story. Add the new OLS diagnostic figure as supplementary evidence |
| §5.4.4 per-fold stability | REWRITE: per-fold Spearman ρ bars (0.380, 0.585, 0.687, 0.614, 0.598) instead of per-fold AUC bars. Mean ρ ± 95% CI on the same chart |
| §5.4.9 (recast) | TITLE flips to "Weaker Positive Findings". Difficulty: ρ +0.468 (v1 +0.027) — weak but positive; cohort skews 76% Very Hard so signal is constrained. Improved-struggle: ρ +0.201 (v1 −0.017) — trained weights beat v1, but model still weaker than struggle alone (+0.573). Both panels of `negative_findings.png` need new captions saying "v2 outranks v1, but…" |
| §5.4.10 Optuna | REWRITE: ρ-axis everywhere. **Shrinkage K**: best=1, ρ=+0.444 vs v1 K=5 ρ=+0.431, Δ +0.009 — tied within noise. **CF τ**: best=0.899 (at upper boundary), ρ=+0.434 vs v1 τ=0.7 ρ=+0.234, Δ +0.160 — substantial gain. Boundary caveat (finer τ search may yield more) stays |
| §5.6.1 disagreement | REWRITE: under the new v2 weights, **60.4% of snapshots reclassified** (789/1306), **58.2% downgraded** (760), **2.2% upgraded** (29). v2 sees students as systematically LESS severe than v1's thresholds suggested. This is a cohort-skew calibration finding: v1 thresholds over-flag on this cohort; v2-trained weights are better calibrated to the LLM band distribution |

---

## §4 — Figures inventory (Essential 7)

All 7 figures live at `data/eval/figures/*.png` at ≥200 DPI; copy each to `Report/figures/evaluation/` and reference with `\includegraphics`.

| # | File | Target § | Subject |
|---|---|---|---|
| 1 | `cohort_distributions.png` | §5.4.1 | 4-panel band-calibration finding — v1 struggle/difficulty bands vs LLM struggle/difficulty bands. Motivates why v2 matters |
| 2 | `weights_struggle_v1_vs_v2.png` | §5.4.3 HEADLINE | Paired bar chart, 7 signals, v1 vs v2 with per-fold std error bars. 3 sign flips (`n_hat`, `t_hat`, `rep_norm`) visible at a glance. The positive struggle headline |
| 3 | `ols_diagnostic_struggle.png` | §5.4.3 supplementary | Predicted band severity (OLS output) vs observed LLM band, with identity reference + binned-mean calibration curve. Visually demonstrates the OLS fit working — calibration curve tracks identity in middle bands, saturates at the extremes. Title shows ρ +0.566 (pooled re-derivation), R² +0.323, MAE 0.657. **Newly added 2026-05-26 on user review** |
| 4 | `per_fold_rho_struggle.png` | §5.4.4 | 5-bar per-fold Spearman ρ with mean horizontal line + 95% CI band + κ / MAE summary text-box. **Note rename from `per_fold_auc_struggle.png`** — the previous filename is no longer on disk |
| 5 | `negative_findings.png` | §5.4.9 | 2-panel: difficulty (left) + improved-struggle (right) v1 vs v2 weights. **Caption needs reframing** — both panels now show v2-outranks-v1-weakly rather than v2-loses (see §3a recast note) |
| 6 | `hyperparams_optuna.png` | §5.4.10 | 4-panel: shrinkage K trajectory + landscape (top + bottom left); CF τ trajectory + landscape (top + bottom right). ρ axis throughout |
| 7 | `model_disagreement.png` | §5.6.1 | v1↔v2 band confusion matrix; visually shows the 60.4% reclassification + downgrade direction |

---

## §4a — Reserve list (8 figures on disk; pull in if needed)

These figures are reproducible and live on disk; promote any by adding an `\includegraphics` line in the relevant `\subsubsection`. Listed in descending order of "most likely to earn its place later":

| File | Why on reserve | When to promote |
|---|---|---|
| `optuna_joint_importances.png` | Bar chart attributing the v2 hyperparameter gain to τ (~95%) vs K (~5%); one panel, very readable | Promote if a reviewer asks "why is τ the substantial gain and K not?" |
| `optuna_joint_contour.png` | 2D K×τ heatmap from the joint Optuna study; more elegant than the trajectory+landscape pair | Promote if §5.4.10 wants a single contour-style visualisation of the joint optimisation surface |
| `pred_vs_obs_v1_v2_struggle.png` | Side-by-side scatter (v1 left, v2 right) of predicted vs observed band; strong "v2 hugs the diagonal, v1 doesn't" comparison | Promote as alternative to (not addition to) `weights_struggle_v1_vs_v2.png` if a reviewer prefers the prediction view to the weight view |
| `confusion_bands.png` | v1-vs-LLM and v2-vs-LLM 4×4 confusion matrices side-by-side; diagnostic for "where does each model misclassify?" | Promote if §5.4 wants a per-model misclassification view in addition to the v1↔v2 disagreement view |
| `weight_heatmap_struggle.png` | 7 signals × 5 folds signed-weight heatmap; useful for showing weight stability across folds | Promote if a reviewer questions whether v2 weights are stable across folds (already partially answered by per-fold std in the weights table) |
| `residuals_struggle.png` | OLS residuals scatter + distribution; statistical-diagnostic plot | Promote only if §5.6 grows a residual-analysis discussion |
| `kappa.png` | 3-bar κ chart with Landis-Koch threshold overlay | Cuttable because only 3 numbers; the §5.4.2 table covers it. Promote if the κ section wants a visual |
| `optuna_joint_history.png` | Best-so-far trajectory of the joint Optuna study | Redundant with the top row of `hyperparams_optuna.png`; promote only if the joint-study framing becomes the §5.4.10 narrative |

---

## §5 — Tables inventory (lift verbatim from `data/eval/results.md`)

Convert each Markdown table to LaTeX `tabularx`. Suggested labels in parens.

| Table | Source | § | Suggested label |
|---|---|---|---|
| Cohort (4 rows) | `results.md` § Cohort | §5.4.1 | `tab:eval-cohort` |
| κ band (4 rows; band-only, intervene-κ dropped) | `results.md` §5.4.2 | §5.4.2 | `tab:eval-kappa` |
| Struggle v1-vs-v2 weights (7 rows × 5 cols with sign flags) | `results.md` §5.4.3 | §5.4.3 | `tab:eval-weights-struggle` |
| Per-fold ρ + κ + MAE (5 rows × 6 cols) | `results.md` §5.4.4 | §5.4.4 | `tab:eval-perfold-struggle` |
| Difficulty v1-vs-v2 weights (5 rows × 5 cols) | `results.md` §5.4.9 first | §5.4.9 | `tab:eval-weights-difficulty` |
| Improved-struggle v1-vs-v2 weights (3 rows × 5 cols) | `results.md` §5.4.9 second | §5.4.9 | `tab:eval-weights-improved` |
| Optuna hyperparams (2 rows × 7 cols) | `results.md` §5.4.10 | §5.4.10 | `tab:eval-hyperparams` |
| Verdict scorecard (5 rows × 5 cols) | §2 of this doc + [[Evaluation PoC Handoff]] §13 | §5.6.1 | `tab:eval-verdict-scorecard` |

---

## §6 — Two caveats the writing chat MUST preserve (no hedging, no false-positive spin)

1. **The improved-struggle model is still weaker than the struggle model alone.** v2 improved-struggle ρ +0.201 ≪ v2 struggle ρ +0.588. The trained blend weights beat the v1 default blend weights, but the underlying model premise (combining behavioural + BKT mastery-gap + IRT-adjusted exposure) doesn't actually rank better than the simpler 7-signal struggle model on this cohort — and the trained weights make that explicit by assigning NEGATIVE values to `w_M` (mastery-gap) and `w_D` (IRT-adjusted exposure). Practical recommendation for the dashboard's deployed default: stay on the basic struggle model rather than switching to improved-struggle. Honest framing in §5.4.9: "v2 weights beat v1 weights for this model, but the model itself is still beaten by the simpler one".

2. **Difficulty's absolute ρ is modest, not strong.** ρ +0.468 is "moderate positive correlation" in textbook terms. v2 wins clearly over v1's +0.027 (which was effectively no signal), but N=72 questions with 76% in the Very Hard band gives limited rank-resolution to recover. Honest framing in §5.4.9: "v2 outranks v1 by a meaningful margin, but the difficulty model as a whole has lower absolute quality than the struggle model".

---

## §7 — Existing briefs / drafting-plan sections that need writing-chat attention

| Vault note | What to revisit |
|---|---|
| [[v2 Empirical Refinement Brief]] | §3 §5.4.9 prose blocks were drafted under the old binary-target framing and have sync notes at the top of the file. The §4 methodology preamble references OLS now but some §3 subsubsection blocks may have residual AUC numbers — cross-check against the values in §2/§3 of this doc |
| [[Ch5 §5.4 + cross-chapter training-methodology Drafting Plan]] | Insertion 4 (Ch5 §5.4 methodology preamble) needs the OLS + 4-band framing; Insertion 7 (Ch5 §5.1.5 V2 Training Methodology) needs Spearman ρ in place of AUC. The eight-insertion structure itself is correct |
| [[Evaluation PoC Handoff]] §13 verdict scorecard | Already updated — references "4 v2 wins + 1 tie" |
| [[Evaluation PoC Handoff]] §12 changelog | Already has new entry for the swap. Add a new changelog entry when you next paste prose into Report/*.tex |
| [[Evidence Bank]] §2026-05-25 evidence table | Already updated with new metric names |
| [[Full Roadmap]] top "Phase 0-8 v2 evaluation additions" block | Already updated; verdict scorecard table reflects new findings |
| [[Future Work Inventory]] item #1 (supervised weight optimisation) | Already updated: closed as "Done 2026-05-25" with the new headline numbers |
| [[v2 Methodology Journal]] §8.3 verdict scorecard | Already updated |
| [[Figures and Tables]] §2026-05-25 figure inventory | Captions reference Spearman ρ now; cross-check filenames if you paste into Ch5 |
| [[Ch5 – Results and Evaluation]] verdict scorecard at top | Already updated |

---

## §8 — Authoritative numbers source

If any number in this doc disagrees with `data/eval/results.md`, **trust `results.md`** — it's auto-generated by the notebook on each Run All and reflects what the trained JSONs actually contain.

| Artefact | Path | What it carries |
|---|---|---|
| Results markdown | `data/eval/results.md` | 97-line auto-generated table set: cohort, κ, all three weight comparisons, per-fold metrics, Optuna scorecard, disagreement |
| Struggle weights JSON | `data/eval/optimised_struggle_weights_v2.json` | v2 weights + per-fold std + per-fold metrics + summary stats |
| Difficulty weights JSON | `data/eval/optimised_difficulty_weights_v2.json` | Same shape, LOO pooled |
| Improved-struggle weights JSON | `data/eval/optimised_improved_weights_v2.json` | Same shape, 3 blend weights |
| Hyperparam Optuna JSON | `data/eval/optimised_hyperparams_v2.json` | Best K + best τ + per-trial trajectories + v1 baselines |

**Regeneration order** if anyone needs to refresh: `scripts/optimise_v2_weights.py` for each of `--kind struggle / difficulty / improved`, then `scripts/optimise_hyperparams.py`, then Restart & Run All on `notebooks/eval_main.ipynb`. Total wallclock ~12 min.

---

## §9 — Pre-flight reads for the writing chat

In order:

1. **This handoff doc** (§0 through §9) — reframes whatever you were doing
2. **`data/eval/results.md`** — authoritative numbers, lift tables verbatim
3. **[[v2 Empirical Refinement Brief]]** (post-sync version) — main brief, structure unchanged
4. **[[Ch5 §5.4 + cross-chapter training-methodology Drafting Plan]]** (post-sync version) — eight insertions, structure unchanged
5. **[[Evaluation PoC Handoff]] §13** (verdict scorecard) + **§12 changelog** (provenance)
6. (Optional) **[[v2 Methodology Journal]] §8.3** — cross-reference for the verdict scorecard

After reading these, return to your in-progress paragraph and apply the §3a checklist. Anything that survives the checklist is safe to keep; everything else needs rewriting against the numbers in §2 and the framing in §3 / §6.
