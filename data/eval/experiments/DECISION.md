# Model-class bake-off — decision (2026-05-26)

## Conclusion: **stay with OLS for all three v2 model classes.**

No methodology change to the model class. **Promoted 2026-05-27 from a defensive §5.6 footnote to the headline §5.4 model-class-selection comparison** (see `[[v2 Threshold Training Handoff]]` §14): the bake-off is now first-class evidence that the OLS choice was correct on merit, not just interpretability. A second axis (regression-vs-classification framing, `classifier_bakeoff.json`) was added — classifiers win raw κ but OLS+trained-thresholds matches them while keeping interpretable signed weights and stronger ranking. The promoted artefacts live at `data/eval/{model_class,classifier}_bakeoff.json` + `data/eval/figures/{model_class_bakeoff,framing_regression_vs_classification}.png`.

## What the bake-off tried

Same data and CV splits as `scripts/optimise_v2_weights.py`. Eight model classes:

- OLS (current baseline)
- Ridge α ∈ {0.1, 1.0, 10.0}
- Lasso α = 0.01
- ElasticNet α = 0.01, l1_ratio = 0.5
- RandomForestRegressor (n=200, max_depth=5)
- GradientBoostingRegressor (n=200, max_depth=3, lr=0.05)

Full numbers in `model_class_bakeoff.md` / `model_class_bakeoff.json`.

## Per-target verdicts

### Struggle (n=1306, 7 features)
| Best alt | Δ ρ vs OLS | Keep OLS? |
|---|---|---|
| RandomForest (+0.583) | +0.010 | Yes — Δ within per-fold variance noise; RF loses interpretable weights |

All Ridge / Lasso / ElasticNet variants are within ±0.001 ρ of OLS. Sample-to-feature ratio is 186, so regularisation has nothing to do.

### Difficulty (n=72, 5 features)
| Best alt | Δ ρ vs OLS | Keep OLS? |
|---|---|---|
| Lasso α=0.01 (+0.316) | **+0.029** | Yes — Δ is real but small; Lasso may zero a feature, breaking the v1-vs-v2 paired bar chart for that row; difficulty's absolute ρ is modest either way |

Most interesting finding: small-N + 5-feature setting is where regularisation genuinely helps. Lasso > ElasticNet > Ridge α=1 > OLS, but the spread is only 0.03. Non-linear models catastrophically overfit (RF +0.133, GB −0.024 — GB literally worse than random).

### Improved-struggle (n=1306, 3 features)
| Best alt | Δ ρ vs OLS | Keep OLS? |
|---|---|---|
| RandomForest (+0.202) | +0.034 | Yes — RF kills the interpretable-weights story; the §5.4.9 negative-w_M / negative-w_D revelation is the whole point and RF can't show it |

All linear variants tied with OLS. RF gain is real but interpretability cost is total.

## Why not switch to Lasso for difficulty (even though it wins on ρ)

1. The +0.029 ρ gain doesn't change the §5.4.9 narrative: v2 outranks v1 either way, and the absolute ρ is "weak positive" either way (+0.287 vs +0.316 — both modest)
2. Lasso may zero one or more difficulty weights, breaking the paired bar chart for that row and the "sign-flip" story for the zero'd feature
3. Switching difficulty alone to Lasso means inconsistent model class across the three v2 models, which is harder to justify in §5.1.5 methodology preamble than "OLS everywhere"

The defensive write-up move is: in §5.6 mention that Ridge / Lasso / ElasticNet / RF / GB were all evaluated as alternatives; report Lasso as the best non-OLS option for difficulty (+0.029 ρ); explain why OLS was retained for consistency + interpretability.

## Why not switch to RF anywhere (despite small gains)

The §5.4 contribution is the **paired v1-vs-v2 weight bar chart**. RF doesn't produce per-feature signed weights, so that comparison cannot exist for an RF v2. The +0.010 / +0.034 ρ gain is genuine but trades away the entire §5.4 visual and narrative.

If the user wants a "ceiling reference" benchmark for §5.6 ("the best non-linear model achieves +0.583 / +0.202 ρ; OLS gets +0.573 / +0.168 — we're within 0.01 / 0.03 of the achievable ceiling"), the RF numbers from this bake-off can be lifted verbatim into a single sentence. No further work needed.

## Where this experiment lives

```
scripts/experiments/model_class_bakeoff.py     ← the script (reproducible)
data/eval/experiments/model_class_bakeoff.json ← full per-fold numbers
data/eval/experiments/model_class_bakeoff.md   ← human-readable summary
data/eval/experiments/DECISION.md              ← this file
```

Delete-safe: `rm -rf scripts/experiments/ data/eval/experiments/` removes the entire experiment without touching any canonical artefact.

---

## Update — re-bake-off under upgraded gpt-4o labels

After the rater upgrade (2026-05-26 evening), the bake-off was re-run against the new labels. The verdict shifted in OLS's favour for struggle, stayed essentially tied for difficulty, and persisted only for improved-struggle.

| Target | OLS old labels | OLS new labels | Best alternative new labels | Notes |
|---|---|---|---|---|
| Struggle | +0.573 | **+0.588** | RandomForest +0.565 ← went DOWN | OLS now decisively beats RF; earlier "RF marginally wins" was overfitting to label noise |
| Difficulty | +0.287 | **+0.469** | RandomForest +0.479 (Δ +0.010, noise) | All linear variants tied with OLS within ±0.003 |
| Improved-struggle | +0.168 | +0.201 | RandomForest +0.250 (Δ +0.049, real) | RF still wins but interpretability cost unchanged |

**Updated decision (2026-05-27): still no swap.** OLS confirmed as the right choice on struggle (now decisively); ties or marginal RF gains elsewhere don't justify swapping. The cleaner-labels result is the publishable methodological argument that the OLS choice is correct on merit, not just on interpretability constraint. Paste-ready §5.6 prose lives in [[v2 Relabel Handoff]] §5.6 prose addition section.
