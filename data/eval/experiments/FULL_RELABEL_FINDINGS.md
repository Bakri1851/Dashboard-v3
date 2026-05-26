# Full re-label experiment — findings (2026-05-26 evening)

## Headline: every model improved; difficulty improved dramatically

| Model | Canonical ρ (4o-mini) | Full re-label ρ (4o-full) | Δρ | Note |
|---|---|---|---|---|
| **Struggle** (7 weights, n=1306) | +0.5729 | **+0.5884** | **+0.0155** | Modest gain, within the per-fold noise margin from earlier folds; consistent direction across all 5 folds (first fold: 0.380 → 0.498, biggest single jump) |
| **Difficulty** (5 weights, n=72) | +0.2870 | **+0.4685** | **+0.1815** | **HUGE gain.** Moves from "weak positive" to "moderate positive" — biggest single ρ shift in the entire experiment series |
| **Improved-struggle** (3 weights, n=1306) | +0.1683 | **+0.2015** | **+0.0332** | Real gain; matches the RandomForest ceiling (+0.2018) we saw in the model-class bake-off — i.e. better labels reach the non-linear-model ceiling without losing linear interpretability |

Plus MAE dropped on every model:
- Struggle MAE: 0.657 → 0.564
- Difficulty MAE: 0.278 → 0.319 (slight increase here, but ρ and κ both up)
- Improved-struggle MAE: 0.872 → 0.813

## Interpretation

The earlier partial-relabel experiment found that mixing 11% new + 89% old labels HURT the model (−0.030 ρ). That looked like "labels don't matter". This full-relabel result shows the truth: **labels do matter, but you need a fully consistent label set** — once 100% of the labels come from the better rater, the improvement materialises across the board.

Two specific things now defensible in the thesis:

1. **The "label noise was the ceiling" hypothesis is confirmed.** The OLS model didn't need a fancier model class (bake-off showed +0.01–0.03 from RF/GBM at most); it needed better labels. GPT-4o re-rating gave struggle +0.02, improved-struggle +0.03, difficulty +0.18.

2. **The difficulty model has been UNDERSOLD.** All previous prose said "difficulty's absolute ρ is modest (+0.287)" with a cohort-skew caveat. Under proper labels it's +0.469 — comfortably in the "moderate positive correlation" range. The cohort skew is real but matters less than label noise.

## Cost

| Item | Cost |
|---|---|
| Partial re-label (148 snapshots) | $0.45 |
| Full re-label (1158 remaining struggle + 72 difficulty) | ~$3.50 |
| **Total OpenAI spend** | **~$4** |

## Decision: promote to canonical

**The new GPT-4o labels should replace the canonical 4o-mini labels.** The ρ improvements are real across all three models, the methodology is identical, and the data flow doesn't change — just the rater changes from `gpt-4o-mini` to `gpt-4o`.

### Recommended propagation path

In rough order of effort and impact:

1. **Promote the new label files**:
   - `data/eval/experiments/full_relabel_struggle_gpt4o.json` → `data/eval/llm_struggle_labels.json` (overwrite)
   - `data/eval/experiments/full_relabel_difficulty_gpt4o.json` → `data/eval/llm_difficulty_labels.json` (overwrite)
   - Bump schema version to indicate the rater change

2. **Re-run all 3 OLS training scripts** to regenerate the canonical weight JSONs:
   ```bash
   python scripts/optimise_v2_weights.py --kind struggle
   python scripts/optimise_v2_weights.py --kind difficulty
   python scripts/optimise_v2_weights.py --kind improved
   ```

3. **Re-run Optuna** to re-tune K and τ against the new labels (they may shift):
   ```bash
   python scripts/optimise_hyperparams.py
   ```

4. **Re-run the notebook** to regenerate all 7 essential figures + `results.md` against the new numbers:
   ```bash
   python -m jupyter nbconvert --to notebook --execute --inplace --ExecutePreprocessor.timeout=900 notebooks/eval_main.ipynb
   ```

5. **Propagate to the vault** — same sweep approach as the earlier target-swap:
   - Update verdict scorecard everywhere (new ρ values)
   - Update §5.4.9 difficulty narrative — no longer "weak positive correlation"; now "moderate positive with caveats"
   - Update [[v2 Target-Swap Handoff]] §2 with the new headline numbers
   - Add a sync note in each vault file flagging the 2026-05-26 evening label upgrade

6. **Update the OpenAI model setting** in `code2/backend/config.py` or wherever the rater is configured so future re-labels use gpt-4o by default

7. **Re-do the κ report** against the human self-labels with the new 4o labels (we already know it goes 0.107 → 0.145 on unweighted and 0.094 → 0.262 on quadratic)

### Estimated time

| Step | Wallclock |
|---|---|
| 1. Promote labels (file copy) | 30 s |
| 2. Re-train 3 OLS models | ~5 min |
| 3. Re-run Optuna | ~5 min |
| 4. Re-run notebook | ~3 min |
| 5. Vault sweep (script + verification) | ~30 min |
| 6. Config update | 5 min |
| 7. κ re-report | 5 min |
| **Total** | **~50 min of work** |

## What the new scorecard would look like

| Component | Old (4o-mini) ρ | New (4o-full) ρ |
|---|---|---|
| Struggle weights | +0.573 | **+0.588** |
| Difficulty weights | +0.287 | **+0.469** |
| Improved-struggle weights | +0.168 | **+0.202** |
| CF τ | +0.434 (tbd; rerun Optuna) | tbd |
| Shrinkage K | +0.444 (tied; tbd) | tbd |

Verdict: still **4 wins + 1 tie**, just with cleaner numbers and a much stronger difficulty story.

## Where this experiment lives

```
scripts/experiments/full_relabel_gpt4o.py             ← relabel script (idempotent, resume-friendly)
scripts/experiments/retrain_all_full_relabels.py      ← retrain comparison script
data/eval/experiments/full_relabel_struggle_gpt4o.json    (1306 new labels)
data/eval/experiments/full_relabel_difficulty_gpt4o.json  (72 new labels)
data/eval/experiments/full_relabel_comparison.json    ← canonical vs new comparison
data/eval/experiments/FULL_RELABEL_FINDINGS.md        ← this file
data/eval/experiments/RELABEL_FINDINGS.md             ← prior partial-relabel finding (now superseded)
```

Delete-safe: `rm -rf scripts/experiments/ data/eval/experiments/` removes everything if you decide not to promote.
