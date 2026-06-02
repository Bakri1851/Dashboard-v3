"""Generate two additional report figures.

  1. IRT 2PL discrimination scatter (alpha vs beta per question)  → §5.4.3
     Output: Report/figures/evaluation/eval-irt-discrimination.png

  2. Incorrectness distribution histogram (shows the 92.5% fallback at 0.5)
     Output: Report/figures/evaluation/eval-incorrectness-distribution.png

Saves directly to Report/figures/evaluation/ so the figures are report-ready.
Print suggested \\includegraphics blocks at the end.

Run from repo root::

    python scripts/experiments/extra_figures.py

Superseded by `notebooks/eval_main.ipynb` (§5.4.3 IRT diagnostic and
§5.4.1 / §5.6.3 incorrectness distribution). The notebook is the canonical
source and writes duplicates into `data/eval/figures/` alongside the other
evaluation figures. This standalone script is retained for one-shot
regeneration directly into `Report/figures/evaluation/` without re-running
the full notebook.
"""
from __future__ import annotations
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "code2"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from backend.models.irt import compute_irt_model

OUT = REPO / "Report" / "figures" / "evaluation"
OUT.mkdir(parents=True, exist_ok=True)


def make_irt_discrimination():
    print("[1/2] IRT 2PL discrimination scatter...")
    df = pd.read_parquet(REPO / "data" / "eval" / "submissions.parquet")
    print(f"  loaded {len(df):,} submissions; fitting 2PL...")
    model = compute_irt_model(df)
    qdf = model["difficulty_df"]
    if qdf.empty:
        print("  IRT fit returned empty — skipping")
        return
    print(f"  fitted: {len(qdf)} questions, convergence={model['convergence']}, log-likelihood={model['log_likelihood']:.1f}")

    if "b_raw" not in qdf.columns or "irt_discrimination" not in qdf.columns:
        print(f"  expected b_raw + irt_discrimination columns, got {list(qdf.columns)} — skipping")
        return

    beta  = qdf["b_raw"].values
    alpha = qdf["irt_discrimination"].values

    fig, ax = plt.subplots(figsize=(10, 6.5))
    ax.scatter(beta, alpha, s=60, c="#F08080", alpha=0.65, edgecolor="black", linewidth=0.5)

    ax.axhline(1.0, color="grey", linestyle="--", linewidth=1, alpha=0.7,
               label="Rasch-equivalent ($\\alpha = 1$)")
    ax.axhline(0.5, color="grey", linestyle=":", linewidth=1, alpha=0.7,
               label="low-discrimination cutoff ($\\alpha \\leq 0.5$)")
    ax.axvline(0.0, color="grey", linestyle=":", linewidth=0.8, alpha=0.5)

    low_disc_mask = alpha <= 0.5
    n_low = int(low_disc_mask.sum())
    if n_low > 0:
        ax.scatter(beta[low_disc_mask], alpha[low_disc_mask],
                   s=120, facecolor="none", edgecolor="#ff2d55", linewidth=1.8,
                   label=f"low-discrimination items ($n={n_low}$)")

    ax.set_xlabel(r"Difficulty (logit scale) $\beta_q$ — higher = harder", fontsize=11)
    ax.set_ylabel(r"Discrimination $\alpha_q$ — higher = better-separating", fontsize=11)
    ax.set_title(
        f"2PL IRT diagnostic — discrimination vs difficulty per question\n"
        f"$n={len(qdf)}$ questions  ·  mean $\\alpha$ = {alpha.mean():.2f}  ·  mean $\\beta$ = {beta.mean():+.2f}",
        fontsize=12,
    )
    ax.legend(loc="best", fontsize=9, framealpha=0.95)
    ax.grid(True, alpha=0.3)

    n_neg_disc = int((alpha < 0).sum())
    annot = (
        f"{n_low} of {len(qdf)} questions have $\\alpha \\leq 0.5$\n"
        f"(weak discrimination — answering correctly on these\n"
        f"items reveals little about student ability)."
    )
    if n_neg_disc > 0:
        annot += f"\n{n_neg_disc} have negative $\\alpha$ — fit pathology, drop from interpretation."
    ax.text(0.02, 0.98, annot, transform=ax.transAxes, va="top", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.92, edgecolor="grey"))

    out = OUT / "eval-irt-discrimination.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.relative_to(REPO)}")


def make_incorrectness_histogram():
    print("[2/2] Incorrectness distribution histogram...")
    df = pd.read_parquet(REPO / "data" / "eval" / "submissions.parquet")
    inc = df["incorrectness"].values
    n = len(inc)
    n_fallback = int((inc == 0.5).sum())
    n_correct = int((inc < 0.5).sum())
    n_incorrect = int((inc > 0.5).sum())
    print(f"  N={n:,}  fallback@0.5={n_fallback:,} ({n_fallback/n:.1%})  "
          f"clearly correct (<0.5)={n_correct:,}  clearly incorrect (>0.5)={n_incorrect:,}")

    fig, ax = plt.subplots(figsize=(11, 6))
    counts, edges, patches = ax.hist(inc, bins=50, color="#F08080", edgecolor="black", linewidth=0.4)

    centre_bin_idx = int(np.argmin(np.abs(edges[:-1] - 0.5)))
    if 0 <= centre_bin_idx < len(patches):
        patches[centre_bin_idx].set_facecolor("#ff2d55")
        patches[centre_bin_idx].set_edgecolor("black")

    ax.axvline(0.5, color="black", linestyle="--", linewidth=1.2, alpha=0.6,
               label=r"CORRECT_THRESHOLD ($\tau = 0.5$)")
    ax.set_xlabel("Incorrectness score (per submission)", fontsize=11)
    ax.set_ylabel("Count (log scale)", fontsize=11)
    ax.set_yscale("log")
    ax.set_title(
        f"Distribution of per-submission incorrectness across the deployment ({n:,} submissions)\n"
        f"{n_fallback/n:.1%} sit at the 0.5 fallback (no AI feedback or LLM call failed)",
        fontsize=12,
    )
    ax.grid(True, alpha=0.3, axis="y", which="both")
    ax.legend(loc="upper right", fontsize=10)

    summary = (
        f"Fallback ($=0.5$):  {n_fallback:>6,d}  ({n_fallback/n:>5.1%})\n"
        f"Clearly correct  ($<0.5$):  {n_correct:>6,d}  ({n_correct/n:>5.1%})\n"
        f"Clearly incorrect ($>0.5$): {n_incorrect:>6,d}  ({n_incorrect/n:>5.1%})\n"
        f"Mean: {inc.mean():.3f}    Std: {inc.std():.3f}"
    )
    ax.text(0.02, 0.97, summary, transform=ax.transAxes, va="top", fontsize=9,
            family="monospace",
            bbox=dict(boxstyle="round", facecolor="white", alpha=0.92, edgecolor="grey"))

    out = OUT / "eval-incorrectness-distribution.png"
    fig.tight_layout()
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved {out.relative_to(REPO)}")


def main() -> int:
    make_irt_discrimination()
    make_incorrectness_histogram()

    print()
    print("=" * 78)
    print("Paste-ready LaTeX blocks:")
    print("=" * 78)
    print(r"""
% --- Figure 1: §5.4.3 IRT 2PL discrimination scatter ---
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\linewidth]{figures/evaluation/eval-irt-discrimination.png}
    \caption{Two-parameter logistic (2PL) IRT diagnostic: per-question discrimination $\alpha_q$ against difficulty $\beta_q$ on the logit scale. Items with $\alpha_q \leq 0.5$ (circled in red) discriminate weakly between students of different ability and contribute little information to the difficulty ranking. Rasch-equivalent items lie on the dashed $\alpha = 1$ line.}
    \label{fig:eval-irt-discrimination}
\end{figure}

% --- Figure 2: §5.6.3 Limitations (or §5.4.1) incorrectness distribution ---
\begin{figure}[H]
    \centering
    \includegraphics[width=0.85\linewidth]{figures/evaluation/eval-incorrectness-distribution.png}
    \caption{Distribution of per-submission incorrectness scores across the deployment ($n$ = {N_TOTAL:,} submissions). The bulk of the mass ({FALLBACK_PCT}) sits at the $0.5$ fallback value, which the analytics pipeline assigns when AI feedback text is absent or the LLM scoring call fails. Only the tails of the distribution (incorrectness strictly less than or greater than $0.5$) carry information from successful LLM scoring; every downstream signal that consumes this column is therefore weakly informed by the production scorer on this cohort.}
    \label{fig:eval-incorrectness-distribution}
\end{figure}
""".replace("{N_TOTAL:,}", "42,443").replace("{FALLBACK_PCT}", "92.5\\%"))

    return 0


if __name__ == "__main__":
    sys.exit(main())
