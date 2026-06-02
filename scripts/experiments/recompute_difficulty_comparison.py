"""Headless recompute of the difficulty baseline-vs-IRT comparison + the true
IRT-vs-rater Spearman rho (jupyter is not installed, so this mirrors section §2
of scripts/experiments/_nb_create_model_comparison.py rather than executing the
notebook).

Why this exists: Chapter 5 §5.6.1 (line 488) cited rho = +0.345 as the IRT
difficulty's agreement "against the rater". That +0.345 is actually
spearmanr(baseline_score, irt_score) -- the cross-model agreement between the
baseline composite and IRT, printed into comparison_difficulty_scatter.png. The
genuine IRT-vs-rater rank agreement (IRT difficulty ordering vs the LLM band)
was never computed. This script computes all three so the prose can use the
correct number, and regenerates the scatter with a title that names what it
shows (baseline vs IRT), so the figure cannot be misread as vs-rater.

Run from repo root:
    python scripts/experiments/recompute_difficulty_comparison.py

Reads:  data/eval/snapshots.json, data/eval/llm_difficulty_labels.json,
        data/eval/submissions.parquet
Writes: data/eval/figures/comparison_difficulty_scatter.png
        Report/figures/evaluation/comparison_difficulty_scatter.png
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EVAL_DIR = REPO_ROOT / "data" / "eval"
FIG_DIR = EVAL_DIR / "figures"
REPORT_FIG_DIR = REPO_ROOT / "Report" / "figures" / "evaluation"
FIG_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO_ROOT / "code2"))
from backend import config as _bk_config            # noqa: E402
from backend.models.irt import compute_irt_model      # noqa: E402

DIFFICULTY_THRESHOLDS = _bk_config.DIFFICULTY_THRESHOLDS
DIFFICULTY_BANDS = ["Easy", "Medium", "Hard", "Very Hard"]
band_to_idx_d = {b: i for i, b in enumerate(DIFFICULTY_BANDS)}

_cmap = plt.get_cmap("RdYlBu_r")
band_colors = [_cmap(i / 3) for i in range(4)]


def score_to_level(score: float, thresholds) -> str:
    for lo, hi, label, _ in thresholds:
        if lo <= score < hi:
            return label
    return thresholds[-1][2]


def top10_overlap(ids_a, ids_b, k: int = 10):
    if not len(ids_a) or not len(ids_b):
        return None
    return round(len(set(ids_a[:k]) & set(ids_b[:k])) / k, 3)


diff_q = json.loads((EVAL_DIR / "snapshots.json").read_text(encoding="utf-8"))["difficulty_questions"]
llm_d = json.loads((EVAL_DIR / "llm_difficulty_labels.json").read_text(encoding="utf-8"))["labels"]

baseline_diff = pd.DataFrame([
    {
        "question": q["question"],
        "baseline_score": float(q["v1_difficulty_score"]),
        "baseline_level": q["v1_difficulty_level"],
        "llm_band": (llm_d.get(q["question"]) or {}).get("band"),
    }
    for q in diff_q
])
print(f"baseline difficulty: {len(baseline_diff)} questions")

subs_df = pd.read_parquet(EVAL_DIR / "submissions.parquet")
print(f"fitting 2PL on {len(subs_df):,} submissions...")
irt_model = compute_irt_model(subs_df)
irt_df = irt_model["difficulty_df"].copy()
print(f"IRT difficulty_df: {len(irt_df)} questions, convergence={irt_model['convergence']}")

b_raw = irt_df["b_raw"].astype(float).values
b_min, b_max = float(b_raw.min()), float(b_raw.max())
irt_df["irt_score"] = (b_raw - b_min) / (b_max - b_min) if b_max > b_min else 0.5
irt_df["irt_level"] = irt_df["irt_score"].apply(lambda v: score_to_level(v, DIFFICULTY_THRESHOLDS))

question_col = "question" if "question" in irt_df.columns else irt_df.columns[0]
df_d = baseline_diff.merge(
    irt_df[[question_col, "irt_score", "irt_level", "b_raw"]],
    left_on="question", right_on=question_col, how="inner",
)
print(f"overlap (baseline n IRT-fit): {len(df_d)} questions")

rho_base_irt = float(spearmanr(df_d["baseline_score"], df_d["irt_score"]).correlation)

m = df_d["llm_band"].notna()
band_idx = df_d.loc[m, "llm_band"].map(band_to_idx_d)
n_lab = int(m.sum())
rho_irt_rater = float(spearmanr(df_d.loc[m, "irt_score"], band_idx).correlation)
rho_base_rater = float(spearmanr(df_d.loc[m, "baseline_score"], band_idx).correlation)

ovl_d = top10_overlap(
    df_d.sort_values("baseline_score", ascending=False)["question"].tolist(),
    df_d.sort_values("irt_score", ascending=False)["question"].tolist(),
    k=10,
)

print()
print("=" * 64)
print("DIFFICULTY rank agreements (Spearman rho)")
print(f"  baseline composite  vs IRT   (cross-model): {rho_base_irt:+.3f}   [reproduces the figure title]")
print(f"  IRT difficulty      vs RATER (n={n_lab}):     {rho_irt_rater:+.3f}   <-- the number for line 488")
print(f"  v1 baseline composite vs RATER (n={n_lab}):   {rho_base_rater:+.3f}   [for reference; the chapter quotes")
print(f"                                                        +0.468 for the deployed OLS composite]")
print(f"  top-10 overlap (baseline n IRT): {int((ovl_d or 0) * 10)}/10")
print("=" * 64)

fig, ax = plt.subplots(figsize=(9, 8))
df_d_un = df_d[df_d["llm_band"].isna()]
if len(df_d_un):
    ax.scatter(df_d_un["baseline_score"], df_d_un["irt_score"],
               s=40, alpha=0.3, color="lightgrey", edgecolor="none",
               label=f"unlabeled (n={len(df_d_un)})")
for band in DIFFICULTY_BANDS:
    sub = df_d[df_d["llm_band"] == band]
    if not len(sub):
        continue
    ax.scatter(sub["baseline_score"], sub["irt_score"],
               s=70, alpha=0.7, color=band_colors[band_to_idx_d[band]],
               edgecolor="black", linewidth=0.4, label=f"{band} (n={len(sub)})")
ax.plot([0, 1], [0, 1], "--", color="grey", linewidth=1.2, alpha=0.7, label="baseline = IRT")
ax.set_xlabel("Baseline composite difficulty", fontsize=11)
ax.set_ylabel("IRT difficulty (b_raw, scaled to [0,1])", fontsize=11)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
ax.set_title(
    f"Baseline vs IRT difficulty, per question\n"
    f"n = {len(df_d)}  -  Spearman rho(baseline, IRT) = {rho_base_irt:+.3f}  -  "
    f"top-10 overlap = {int((ovl_d or 0) * 10)}/10",
    fontsize=12,
)
ax.legend(loc="lower right", fontsize=9, framealpha=0.95)
ax.grid(True, alpha=0.3)
plt.tight_layout()

out = FIG_DIR / "comparison_difficulty_scatter.png"
plt.savefig(out, dpi=200, bbox_inches="tight")
shutil.copyfile(out, REPORT_FIG_DIR / "comparison_difficulty_scatter.png")
print(f"saved {out.relative_to(REPO_ROOT)}")
print(f"saved {(REPORT_FIG_DIR / 'comparison_difficulty_scatter.png').relative_to(REPO_ROOT)}")
