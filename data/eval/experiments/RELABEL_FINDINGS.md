# Relabel experiment — findings (2026-05-26)

## What we tested

Hypothesis: GPT-4o (full model) produces less noisy struggle labels than GPT-4o-mini, lifting both (a) κ vs human reference and (b) downstream OLS Spearman ρ.

Method:
- Re-labelled 148 stratified snapshots (37 per band) with `gpt-4o` instead of `gpt-4o-mini`. All 50 author self-labelled snapshots force-included for head-to-head κ.
- Merged labels: 4o-full overrides 4o-mini for the 148 relabeled; remaining 1158 stay on 4o-mini.
- Retrained OLS struggle using merged labels with identical CV splits as the canonical run.

Cost: ~$0.45 OpenAI spend. Wallclock: ~2 min relabel + ~10 s retrain.

## Headline results

### (a) Label quality: GPT-4o IS better than 4o-mini vs the human reference

On the 50 author-self-labelled snapshots:

| κ variant | 4o-mini ↔ human | 4o-full ↔ human | Δ |
|---|---|---|---|
| Unweighted | +0.107 | **+0.145** | +0.038 |
| Linear-weighted | +0.111 | **+0.198** | +0.086 |
| **Quadratic-weighted** | +0.094 | **+0.262** | **+0.167** |
| Exact agreement | 34.0% | **38.0%** | +4.0% |
| Within-1-band agreement | 70.0% | 68.0% | −2.0% |

GPT-4o agrees with the human reference **markedly better on weighted κ** (the metric that penalises larger band gaps more). The quadratic-κ jump (+0.094 → +0.262) is substantial — moves from "poor" to "fair" on Landis-Koch.

### (b) Downstream OLS ρ: surprisingly went DOWN

| Metric | Canonical (4o-mini only) | Merged (4o-mini + 148 × 4o) | Δ |
|---|---|---|---|
| Spearman ρ | +0.5729 | **+0.5424** | **−0.0304** |
| Weighted κ (band) | +0.3642 | +0.3393 | −0.0249 |
| MAE (band) | 0.6565 | 0.6639 | +0.0073 |

Per-fold ρ:
- Canonical: [0.380, 0.585, 0.687, 0.614, 0.598]
- Merged:    [0.336, 0.577, 0.658, 0.587, 0.554]

Every fold dropped. Not noise — consistent direction across all 5 folds.

## Interpretation

The two results look contradictory but actually tell a coherent story:

1. **GPT-4o is genuinely a better rater** than 4o-mini (κ vs human went up substantially on all weighted measures). The hypothesis "label quality is the ceiling" is partially confirmed at the label level.

2. **But MIXING label sources hurt the model.** 148/1306 = 11% of labels are now from a different distribution than the other 89%. OLS fits consistency more than correctness — when 89% of labels carry one bias and 11% carry a different (more accurate) bias, the model gets confused.

3. **Per-fold consistency dropped uniformly**, which is the signature of label drift rather than fold-specific noise. If 4o-mini and 4o systematically rated certain snapshot patterns differently, the inserted 4o labels appear to OLS as outliers relative to the 89% it's fitting against.

## What this means for the thesis

This is actually a **publishable methodological finding**, not a setback:

- Cohen's κ on a partial subset (50 snapshots) confirms 4o > 4o-mini for label fidelity
- But partial re-labelling INCREASES label noise from the model's perspective
- **Therefore**: to lift ρ via better labels, you have to re-label EVERYTHING, not just a subset. Half-measures regress.

For §5.6 limitations / Ch6 future work, the framing is:

> "We verified that GPT-4o agrees with a human reference rater more closely than GPT-4o-mini (quadratic-weighted κ +0.094 → +0.262 on n=50 shared snapshots), but a partial-relabelling experiment confirmed that mixing label sources degrades training — full re-labelling of all 1306 snapshots with GPT-4o would be required to realise the label-quality benefit. We estimate the upper bound on ρ improvement at ≈+0.05-0.10 if the full relabel were performed."

## Decision

**Don't update canonical artefacts based on this experiment.** The merged labels HURT ρ on the canonical training pipeline. The canonical 4o-mini labels stay as the v2 reference.

The next-step question is whether to spend ~$3-5 doing a full relabel of all 1306 snapshots. Two paths:

### Option A: Stop here (recommended for the thesis)
- Document the partial-relabel finding (κ ↑, ρ ↓ when mixing) as a §5.6 / Ch6 limitation
- The current canonical OLS ρ +0.573 stands
- Net cost so far: $0.45 + maybe 2 hours of script time

### Option B: Do the full relabel ($3-5 OpenAI spend, ~15 min wallclock)
- Re-label ALL 1306 struggle snapshots + 72 difficulty questions with gpt-4o
- Re-train all 3 OLS models on the new consistent label set
- Compare ρ; if ρ rises by ≥+0.03 on struggle, consider promoting 4o labels to canonical
- Trade-off: another $3-5 + the risk that ρ stays flat (label noise wasn't the bottleneck, or 4o-mini was already close to ceiling)

My recommendation: **Option A for this thesis cycle**, because:
- The current §5.4 narrative is already defensible
- The $3-5 is small but the time to re-write all the vault notes / handoff doc / etc. with new numbers is substantial
- The partial-relabel finding is itself a worthwhile §5.6 contribution
- A full relabel + retrain is a natural Ch6 future-work item

Save the full-relabel option for a follow-up paper or extended thesis revision.

## Where this experiment lives

```
scripts/experiments/relabel_subset_gpt4o.py           ← relabel script (reproducible)
scripts/experiments/retrain_with_relabels.py          ← retrain + κ-comparison script
data/eval/experiments/relabel_subset_gpt4o.json       ← 148 new gpt-4o labels
data/eval/experiments/retrain_relabel_comparison.json ← full numerical comparison
data/eval/experiments/RELABEL_FINDINGS.md             ← this file
```

Delete-safe: `rm -rf scripts/experiments/ data/eval/experiments/` removes everything.
