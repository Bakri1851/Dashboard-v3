"""Regenerate the two struggle-weight figures with human-readable tick labels.

The eval notebook labels these bars with the raw feature keys
(n_hat, t_hat, i_norm, r_norm, A_norm, d_hat, rep_norm), but Chapter 5 §5.4.2
refers to them by their human names ("recent incorrectness carries the largest
weight at +0.314", "retry rate", "mean incorrectness", "active time",
"answer-repetition"). A reader cannot map the prose to the bars. This script
re-plots both figures identically in every other respect (same data, palette,
sizing, dpi) but swaps the tick labels for the human names taken verbatim from
the config.py weight comments.

jupyter is not installed, so this regenerates the PNGs directly rather than
executing notebooks/eval_main.ipynb. The two set_xticklabels / set_yticklabels
lines in that notebook are patched separately so a future full re-run matches.

Run from repo root:
    python scripts/experiments/relabel_weight_figures.py

Reads:  data/eval/optimised_struggle_weights_v2.json
Writes: data/eval/figures/{weights_struggle_v2,weight_heatmap_struggle}.png
        Report/figures/evaluation/{weights_struggle_v2,weight_heatmap_struggle}.png
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = REPO_ROOT / "data" / "eval"
FIG_DIR = EVAL_DIR / "figures"
REPORT_FIG_DIR = REPO_ROOT / "Report" / "figures" / "evaluation"
FIG_DIR.mkdir(parents=True, exist_ok=True)

COLOR_OK = "#10a15d"
COLOR_WARN = "#ff2d55"
plt.rcParams.update({
    "font.size": 12, "axes.titlesize": 12, "axes.labelsize": 12,
    "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 11,
    "figure.titlesize": 13,
})

STRUGGLE_SIGNALS = ["n_hat", "t_hat", "i_norm", "r_norm", "A_norm", "d_hat", "rep_norm"]

STRUGGLE_LABELS = {
    "n_hat": "Submission count",
    "t_hat": "Time active",
    "i_norm": "Mean incorrectness",
    "r_norm": "Retry rate",
    "A_norm": "Recent incorrectness",
    "d_hat": "Improvement slope",
    "rep_norm": "Answer repetition",
}
LABELS = [STRUGGLE_LABELS[s] for s in STRUGGLE_SIGNALS]

opt = json.loads((EVAL_DIR / "optimised_struggle_weights_v2.json").read_text(encoding="utf-8"))


def _save(name: str) -> None:
    plt.tight_layout()
    out = FIG_DIR / f"{name}.png"
    plt.savefig(out, dpi=200, bbox_inches="tight")
    shutil.copyfile(out, REPORT_FIG_DIR / f"{name}.png")
    print(f"  saved {out.relative_to(REPO_ROOT)}")
    print(f"  saved {(REPORT_FIG_DIR / f'{name}.png').relative_to(REPO_ROOT)}")


v2_vals = np.array([opt["weights"][s] for s in STRUGGLE_SIGNALS])
v2_std = np.array([opt["weights_per_fold_std"][s] for s in STRUGGLE_SIGNALS])

fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(STRUGGLE_SIGNALS))
colors = [COLOR_OK if v >= 0 else COLOR_WARN for v in v2_vals]
bars = ax.bar(x, v2_vals, 0.6, yerr=v2_std, capsize=4, color=colors)
ax.axhline(0, color="black", linewidth=0.6)
for bar, val in zip(bars, v2_vals):
    ax.text(bar.get_x() + bar.get_width() / 2,
            val + 0.012 if val >= 0 else val - 0.025,
            f"{val:+.3f}", ha="center", fontsize=9)
ax.set_xticks(x)
ax.set_xticklabels(LABELS, rotation=25, ha="right")
ax.set_ylabel("Signed weight (L1-normalised)")
rho_mean = opt["spearman_rho_mean"]
rho_lo, rho_hi = opt["spearman_rho_ci95"]
ax.set_title(f"v2 OLS-trained struggle weights (7 signals)\n"
             f"Spearman rho = {rho_mean:+.3f} [{rho_lo:+.3f}, {rho_hi:+.3f}]  (4-band target, GroupKFold(5))")
ax.grid(True, alpha=0.3, axis="y")

neg = [STRUGGLE_LABELS[s] for s, v in zip(STRUGGLE_SIGNALS, v2_vals) if v < 0]
note = "Negative-weight signals: " + ", ".join(neg) if neg else "All weights positive"
ax.text(0.02, 0.02, note, transform=ax.transAxes, va="bottom", fontsize=10,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9, edgecolor="grey"))
_save("weights_struggle_v2")
plt.close(fig)

fold_weights = np.array([
    [f["weights_convex"][s] for s in STRUGGLE_SIGNALS]
    for f in opt["per_fold"]
])

fig, ax = plt.subplots(figsize=(10, 6))
vmax = np.abs(fold_weights).max()
im = ax.imshow(fold_weights.T, cmap="RdYlGn", aspect="auto", vmin=-vmax, vmax=vmax)
ax.set_xticks(range(len(opt["per_fold"])))
ax.set_xticklabels([f"fold {i}" for i in range(len(opt["per_fold"]))])
ax.set_yticks(range(len(STRUGGLE_SIGNALS)))
ax.set_yticklabels(LABELS)
for i in range(fold_weights.shape[1]):  # signal
    for j in range(fold_weights.shape[0]):  # fold
        val = fold_weights[j, i]
        color = "white" if abs(val) > vmax * 0.5 else "black"
        ax.text(j, i, f"{val:+.3f}", ha="center", va="center", fontsize=10, color=color)
ax.set_title("Per-fold weight stability - v2 struggle (convex normalised)")
fig.colorbar(im, ax=ax, label="Signed weight (L1-norm)")
_save("weight_heatmap_struggle")
plt.close(fig)
