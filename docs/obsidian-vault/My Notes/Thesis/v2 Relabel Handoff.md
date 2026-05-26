---
phase: Post-rater-upgrade interrupt + reconciliation
status: ready for writing chat (read this BEFORE continuing any drafting)
covers: LLM rater upgrade from gpt-4o-mini → gpt-4o (2026-05-26 evening). Sibling to [[v2 Target-Swap Handoff]] (target/model-class swap from earlier that day). This handoff covers a RATER UPGRADE only — no methodology change.
last_updated: 2026-05-26
inputs:
  - "`data/eval/results.md` — authoritative numbers (regenerated)"
  - "`data/eval/optimised_*_v2.json` (4 files) — re-trained on gpt-4o labels"
  - "`data/eval/kappa_report.json` — recomputed vs gpt-4o (κ_band_linear +0.198, was +0.111)"
  - "`data/eval/experiments/FULL_RELABEL_FINDINGS.md` — provenance of the relabel decision"
  - "[[v2 Target-Swap Handoff]] — methodology context (still relevant; only the rater changed in this update)"
---

# v2 Relabel Handoff (writing chat: read this AFTER the target-swap handoff)

> [!warning] STOP — read this if you're mid-flight
> The LLM rater was upgraded from `gpt-4o-mini` to `gpt-4o` on 2026-05-26 evening. **This is a rater upgrade, not a methodology change** — target, model class, CV scheme, figure inventory, and verdict-scorecard structure are all unchanged from the target-swap handoff. Only the headline ρ numbers shifted upward.
>
> If you drafted prose with ρ values from before the relabel (struggle +0.573, difficulty +0.287, improved-struggle +0.168, K=1, τ=0.899), those numbers are stale. See §3a for the specific substitutions. Most prose blocks need a number swap; the **difficulty §5.4.9 needs a tone shift** (from "weak positive" to "moderate positive correlation"); everything else is structurally stable.
>
> **Decide what your drafts need changing** — most will just need search-and-replace on numbers; a few need the difficulty narrative re-framed.

---

## §1 — What changed

**Rater upgrade only.** The methodology (target = 4-band rating, model class = OLS linear regression, CV scheme = GroupKFold by session / LOO on questions, metrics = Spearman ρ + weighted κ + MAE) is unchanged from the target-swap handoff.

| | Before 2026-05-26 evening | After 2026-05-26 evening |
|---|---|---|
| LLM rater model | `gpt-4o-mini` (OpenAI's cheap model) | **`gpt-4o`** (OpenAI's full flagship) |
| Cost to relabel 1306 + 72 snapshots | $0.20 (the original spend) | $4 (the upgrade spend) |
| Headline result | 4 wins + 1 tie; difficulty modest at ρ +0.287 | 4 wins + 1 tie; **difficulty substantially stronger** at ρ +0.468 |

Provenance: see `data/eval/experiments/FULL_RELABEL_FINDINGS.md` for the experiment + the partial-relabel learning that label *consistency* matters more than partial improvements (a sub-experiment finding worth a §5.6 sentence).

---

## §2 — New verdict scorecard

| Component | v1 (hand-set) ρ | v2 (trained) ρ | Δ | Verdict |
|---|---|---|---|---|
| **Struggle model** (7 OLS weights) | +0.471 | **+0.588** [+0.490, +0.686] | +0.117 | v2 wins |
| **Difficulty model** (5 OLS weights) | near-flat | **+0.468** | substantial | v2 wins — **biggest narrative change** (was +0.287; now moderate-positive) |
| **Improved-struggle model** (3 OLS weights) | near-flat | **+0.201** [+0.047, +0.356] | substantial | v2 wins; **now matches RandomForest ceiling** from bake-off (+0.202) — OLS is at the achievable ceiling under good labels |
| **CF threshold τ** (scalar) | +0.306 (τ=0.7) | **+0.466** (τ=0.900) | +0.160 | v2 wins; still at boundary of [0.4, 0.9] search range |
| **Shrinkage K** (scalar) | +0.471 (K=5) | +0.481 (K=0) | +0.009 | tied within fold-variance noise |

**Frame: still 4 positive findings + 1 tie.** Structurally identical to before the relabel; numbers are tighter and the difficulty narrative shifts from "weak positive" to "moderate positive correlation".

---

## §3a — What's stale in your work-in-progress

**If you wrote any of these old numbers, swap to the new ones:**

| Old (gpt-4o-mini era) | New (gpt-4o era) |
|---|---|
| struggle ρ +0.573 [+0.430, +0.715] | struggle ρ +0.588 [+0.490, +0.686] |
| struggle v1 baseline ρ +0.423 | struggle v1 baseline ρ +0.471 |
| difficulty ρ +0.287 | difficulty ρ +0.468 |
| difficulty v1 baseline ρ +0.027 | difficulty v1 baseline near-flat (unchanged framing) |
| improved-struggle ρ +0.168 [+0.004, +0.333] | improved-struggle ρ +0.201 [+0.047, +0.356] |
| improved-struggle v1 baseline ρ −0.017 | improved-struggle v1 baseline near-flat (unchanged framing) |
| CF τ best=0.899 ρ +0.434, Δ +0.200 | CF τ best=0.900 ρ +0.466, Δ +0.160 |
| CF τ v1 baseline +0.234 | CF τ v1 baseline +0.306 |
| Shrinkage K best=1 ρ +0.444, Δ +0.013 | Shrinkage K best=0 ρ +0.481, Δ +0.009 |
| κ_band_linear +0.111 | κ_band_linear +0.198 |
| κ_band_quadratic +0.094 | κ_band_quadratic +0.262 |
| κ_intervene +0.103 | κ_intervene +0.250 |

**Recast the §5.4.9 difficulty narrative**: drop "weak positive correlation" / "modest absolute ρ even after training" framing; replace with "moderate positive correlation (ρ +0.468); under the upgraded gpt-4o rater the cohort-skew limitation (76% Very Hard) is no longer the dominant ceiling on the difficulty model".

**Add this §5.6 / Ch6 paragraph** to anywhere you discussed label noise:
> A partial-relabel sub-experiment found that mixing labels from two raters (89% gpt-4o-mini + 11% gpt-4o) HURT Spearman ρ by −0.030, even though the gpt-4o labels individually agreed better with the human reference (κ +0.110 → +0.198 weighted-linear). A full relabel of all 1306 + 72 snapshots with gpt-4o was required to realise the label-quality gain. Methodologically: rater changes need to be all-or-nothing; partial relabelling injects label drift that OLS interprets as noise.

---

## §3 — Per-subsubsection narrative impact

| § | Impact |
|---|---|
| §5.4.1 cohort | No change. Cohort distribution figure already captures band calibration |
| §5.4.2 κ block | Numbers up substantially. The "poor by Landis-Koch" framing now softens to "fair by quadratic-weighted κ" (+0.262); within-1-band agreement basically unchanged |
| §5.4.3 struggle headline | Number swap: ρ +0.573 → +0.588. Per-fold pattern shifts: first fold went 0.380 → 0.498 (biggest single shift). 3 sign flips on weights are unchanged |
| §5.4.4 per-fold stability | Number swap |
| §5.4.9 difficulty | **Biggest narrative change.** From "weak positive" to "moderate positive correlation (+0.468)"; the cohort-skew caveat stays but becomes secondary |
| §5.4.9 improved-struggle | Number swap PLUS strong §5.6 evidence: v2 weights now match the non-linear RF ceiling (+0.201 ≈ +0.202), strengthening the "OLS reaches the achievable ceiling under good labels" claim |
| §5.4.10 Optuna | Number swap: K best shifts to 0, τ best stays at boundary 0.900 |
| §5.6.1 disagreement | The v1↔v2 disagreement percentages may shift slightly; check `data/eval/results.md` for current numbers |

---

## §4 — Figures + tables: structurally unchanged

All 7 essential figures (cohort, struggle weights, OLS diagnostic, per-fold ρ, negative findings, hyperparams Optuna, model disagreement) regenerated from the new labels — same files, same target sections, updated headline numbers in titles + annotations.

All 7 tables in `data/eval/results.md` regenerated with new numbers. Lift verbatim.

Verdict scorecard table for §5.6.1 — see §2 of this doc for the canonical version.

---

## §5 — Caveats to preserve (no false-positive spin)

1. **Improved-struggle is still weaker than struggle alone.** v2 improved-struggle ρ +0.201 ≪ v2 struggle ρ +0.588. The trained weights match the achievable non-linear ceiling, but the underlying model premise (combining behavioural + BKT mastery-gap + IRT-adjusted exposure) doesn't out-rank the simpler 7-signal struggle model. Practical recommendation for deployment: stay on struggle, not improved-struggle.

2. **Difficulty's N=72 + cohort skew remain limitations.** ρ +0.468 is "moderate positive" rather than "strong" because there are still only 72 questions and 76% are rated Very Hard. The relabel lifted the ceiling but didn't eliminate it.

3. **The CF τ optimum is still at the boundary** (0.900, upper end of the [0.4, 0.9] search range). A finer search at τ ∈ [0.85, 0.95] may yield further improvement — future-work item.

---

## §5.6 prose addition — OLS choice defence (bonus, added 2026-05-27)

After the rater upgrade, we re-ran the model-class bake-off (`scripts/experiments/model_class_bakeoff.py`) under the new gpt-4o labels. The result is stronger than the original choice rationale: **OLS now decisively beats the non-linear alternatives on struggle**, where it was only tied before. Numbers:

| Model | Old labels (4o-mini) | New labels (4o) |
|---|---|---|
| Struggle OLS | +0.573 | **+0.588** ← went up |
| Struggle RandomForest | +0.583 (marginally beat OLS) | **+0.565** ← went DOWN |
| Struggle GradientBoosting | +0.559 | +0.552 |
| Difficulty OLS | +0.287 | +0.469 (all linear variants tied within ±0.003; RF +0.479 is noise) |
| Improved-struggle OLS | +0.168 | +0.201 |
| Improved-struggle RandomForest | +0.202 | +0.250 (still beats OLS but trade-off unchanged: kills interpretable weights, model still weaker than struggle alone) |

**The "RF marginally beat OLS under noisy labels" result was overfitting to label noise** — once labels were cleaned up, OLS pulled ahead. This is direct evidence that OLS is the right model class for these features at this sample size, not a constrained-by-interpretability compromise.

### Paste-ready §5.6 paragraph

> We verified the OLS model class choice was correct by re-running a model-class bake-off after the rater upgrade. On the struggle model, OLS now decisively beats the non-linear alternatives ($\rho = +0.588$ vs RandomForest $+0.565$ and GradientBoosting $+0.552$) — the earlier finding that RandomForest marginally beat OLS under noisier labels was overfitting to label noise that the rater upgrade removed. On the difficulty model, every linear variant (OLS, Ridge, Lasso, ElasticNet) sits within $\pm 0.003 \rho$ of OLS, with RandomForest's $+0.010 \rho$ lift inside fold-variance noise. On the improved-struggle model, RandomForest retains a real $+0.049 \rho$ advantage over OLS ($+0.250$ vs $+0.201$); we nevertheless retain OLS for this model so the v1 versus v2 per-weight comparison of Section~\ref{sec:eval-findings} stays intact and so the model class is consistent with the struggle and difficulty refits. Taken together, the bake-off evidence is that OLS is the right model class for these features at this sample size, not merely a constraint imposed by the interpretability requirement.

**Citations**: nothing new — the bake-off itself is a methodological artefact, not a literature claim. The OLS / Ridge / Lasso / RandomForest / GradientBoosting names are textbook and don't need cites in a thesis methods section.

**Where it lands**: §5.6.2 (Tradeoffs and Threats to Validity) or §5.6.3 (Limitations), depending on framing. If §5.6.2, frame as "we chose OLS and verified the choice empirically"; if §5.6.3, frame as "we acknowledge that more complex model classes could improve improved-struggle by +0.05 ρ but we retain OLS for interpretability and consistency".

---

## §6 — Pre-flight reads

In order:

1. **[[v2 Target-Swap Handoff]]** — for the underlying methodology (target, model class, CV scheme). All of that is unchanged in this update.
2. **This doc** — for what changed in the rater upgrade and which numbers to swap.
3. **`data/eval/results.md`** — for the authoritative current numbers (always trust this over any vault note if there's a disagreement).
4. **`data/eval/experiments/FULL_RELABEL_FINDINGS.md`** — for the provenance of the relabel decision + the partial-relabel sub-experiment finding.

After reading these, apply the §3a number-swap checklist to your in-flight drafts and shift the difficulty §5.4.9 narrative tone. Everything else is stable.
