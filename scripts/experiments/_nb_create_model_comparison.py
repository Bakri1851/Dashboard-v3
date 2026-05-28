"""One-shot generator for notebooks/model_comparison.ipynb.

Preserves the analytics from the removed Model Comparison dashboard view
(code2/frontend/src/views/ComparisonView.tsx and /api/models/compare) into
a standalone offline notebook. Run from repo root:

    python scripts/experiments/_nb_create_model_comparison.py

Idempotent: overwrites the notebook each run. Keep for re-generation;
delete when the notebook is stable.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NB_PATH = REPO / "notebooks" / "model_comparison.ipynb"


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


CELLS = [
    md("""# Model Comparison — offline preservation

This notebook preserves the analytics that the **Model Comparison** sidebar tab
in the React dashboard used to show. That view was removed on 2026-05-27
because comparing baseline vs improved model classes live in the dashboard
is evaluation work, not an instructor-facing operational tool — but the data
is still valuable as methodology evidence.

**What's compared:**

- **Struggle**: baseline composite (live `v1_struggle_score`) vs improved
  model (BKT mastery + IRT difficulty adjustment, the
  `improved_struggle_score` component)
- **Difficulty**: baseline composite (live `v1_difficulty_score`) vs IRT
  Rasch fit (`b_raw` from the 2PL fit, sign-flipped + normalised to
  match the baseline's [0, 1] scale)

**Cohort**: the evaluation cohort — 1306 struggle snapshots / 72 difficulty
questions — the same data used in `eval_main.ipynb` for the v2 weight
training. NOT the live `lab_session.json` cohort the dashboard used (which
was non-reproducible across re-runs).

**How to re-run**:

```
jupyter nbconvert --to notebook --execute --inplace notebooks/model_comparison.ipynb
```

Or regenerate the notebook structure from scratch:

```
python scripts/experiments/_nb_create_model_comparison.py
jupyter nbconvert --to notebook --execute --inplace notebooks/model_comparison.ipynb
```

Outputs (canonical artefacts):

- `data/eval/figures/comparison_struggle_top10.png`
- `data/eval/figures/comparison_struggle_scatter.png`
- `data/eval/figures/comparison_difficulty_top10.png`
- `data/eval/figures/comparison_difficulty_scatter.png`
- `data/eval/comparison_struggle_pairs.csv` (1306 rows)
- `data/eval/comparison_difficulty_pairs.csv` (≤72 rows)
"""),

    md("## Setup"),

    code("""from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import spearmanr

REPO_ROOT = Path.cwd().parent if Path.cwd().name == 'notebooks' else Path.cwd()
EVAL_DIR  = REPO_ROOT / 'data' / 'eval'
FIG_DIR   = EVAL_DIR / 'figures'
FIG_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(REPO_ROOT / 'code2'))
from backend import config as _bk_config

STRUGGLE_THRESHOLDS    = _bk_config.STRUGGLE_THRESHOLDS
DIFFICULTY_THRESHOLDS  = _bk_config.DIFFICULTY_THRESHOLDS

# Level ORDER (severity) maps a level label to an integer index used by the
# agreement summary (upgraded = improved sees higher index than baseline).
STRUGGLE_LEVEL_ORDER   = {lbl: i for i, (_, _, lbl, _) in enumerate(STRUGGLE_THRESHOLDS)}
DIFFICULTY_LEVEL_ORDER = {lbl: i for i, (_, _, lbl, _) in enumerate(DIFFICULTY_THRESHOLDS)}

print(f'REPO_ROOT: {REPO_ROOT}')
print(f'STRUGGLE_THRESHOLDS:   {[(lo, hi, lbl) for lo, hi, lbl, _ in STRUGGLE_THRESHOLDS]}')
print(f'DIFFICULTY_THRESHOLDS: {[(lo, hi, lbl) for lo, hi, lbl, _ in DIFFICULTY_THRESHOLDS]}')
"""),

    code("""# Helpers shared between the two sections.

def score_to_level(score: float, thresholds) -> str:
    \"\"\"Map a [0, 1] composite score to a level label via the threshold tuples.\"\"\"
    for lo, hi, label, _ in thresholds:
        if lo <= score < hi:
            return label
    return thresholds[-1][2]

def agreement_summary(baseline_levels: pd.Series, improved_levels: pd.Series,
                      level_order: dict) -> dict:
    \"\"\"Match _agreement() in routers/models_cmp.py — upgraded/downgraded/unchanged.\"\"\"
    upgraded = downgraded = unchanged = 0
    for b, i in zip(baseline_levels, improved_levels):
        bi = level_order.get(b, -1); ii = level_order.get(i, -1)
        if bi < 0 or ii < 0: continue
        if ii > bi: upgraded += 1
        elif ii < bi: downgraded += 1
        else: unchanged += 1
    total = upgraded + downgraded + unchanged
    return {
        'upgraded': upgraded, 'downgraded': downgraded, 'unchanged': unchanged,
        'total': total,
        'agreement_pct': round(100.0 * unchanged / total, 1) if total else None,
    }

def top10_overlap(ids_a, ids_b, k: int = 10) -> float | None:
    if not len(ids_a) or not len(ids_b):
        return None
    return round(len(set(ids_a[:k]) & set(ids_b[:k])) / k, 3)

def _save(name: str) -> None:
    plt.tight_layout()
    p = FIG_DIR / f'{name}.png'
    plt.savefig(p, dpi=200, bbox_inches='tight')
    print(f'  saved {p.relative_to(REPO_ROOT)}')
"""),

    md("## §1 Struggle — baseline composite vs improved (BKT + IRT)"),

    md("""The **baseline** struggle score is the live dashboard's weighted composite of
seven behavioural signals (`n̂, t̂, ī, r̂, Â, d̂, rep`) — the value an
instructor sees in the deployed leaderboard with `struggle_model = baseline`.

The **improved** struggle score blends three components, each in [0, 1]:

$$
\\text{improved} = 0.45 \\cdot \\text{behavioural composite}
                 + 0.30 \\cdot \\text{mastery gap (from BKT)}
                 + 0.25 \\cdot \\text{difficulty-adjusted exposure (from 2PL IRT)}
$$

Both scores are pre-computed per snapshot and stored in `data/eval/snapshots.json`
(`v1_struggle_score` and `improved_components.improved_struggle_score`), so the
notebook does no re-computation — it just joins, ranks, and compares.

The LLM 4-band rating is loaded from `data/eval/llm_struggle_labels.json` and
used purely for the scatter colouring (it does not enter the baseline vs
improved comparison itself).
"""),

    code("""# Load the eval cohort + LLM labels (read-only).

snapshots = json.loads((EVAL_DIR / 'snapshots.json').read_text(encoding='utf-8'))['struggle_snapshots']
llm = json.loads((EVAL_DIR / 'llm_struggle_labels.json').read_text(encoding='utf-8'))['labels']

rows = []
for s in snapshots:
    imp = s.get('improved_components') or {}
    if 'improved_struggle_score' not in imp:
        continue  # snapshot wasn't scored with the improved model — drop it
    rows.append({
        'snapshot_id':       s['snapshot_id'],
        'user':              s['user'],
        'session_name':      s['session_name'],
        'baseline_score':    float(s['v1_struggle_score']),
        'baseline_level':    s['v1_struggle_level'],
        'improved_score':    float(imp['improved_struggle_score']),
        'improved_level':    score_to_level(float(imp['improved_struggle_score']), STRUGGLE_THRESHOLDS),
        'llm_band':          (llm.get(s['snapshot_id']) or {}).get('band'),
    })
df_s = pd.DataFrame(rows)
df_s['delta'] = df_s['improved_score'] - df_s['baseline_score']
df_s['abs_delta'] = df_s['delta'].abs()
print(f'snapshots with both scores: {len(df_s):,}')
print(f'with LLM label:             {df_s[\"llm_band\"].notna().sum():,}')
df_s.head(3)
"""),

    code("""# Top-10 leaderboards — baseline vs improved, side-by-side.
# Replicates the ComparisonView's two ModelCard columns.

baseline_top = df_s.sort_values('baseline_score', ascending=False).head(10)
improved_top = df_s.sort_values('improved_score', ascending=False).head(10)

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
for ax, top, title, score_col, level_col in [
    (axes[0], baseline_top, 'Baseline composite — top 10 most struggling',
     'baseline_score', 'baseline_level'),
    (axes[1], improved_top, 'Improved (BKT + IRT) — top 10 most struggling',
     'improved_score', 'improved_level'),
]:
    ax.axis('off')
    headers = ['#', 'user', 'session', 'score', 'level']
    cells = [[f'{i+1}', r['user'][:8], r['session_name'][:22],
              f'{r[score_col]:.3f}', r[level_col]]
             for i, (_, r) in enumerate(top.iterrows())]
    tab = ax.table(cellText=cells, colLabels=headers, loc='center',
                   cellLoc='left', colLoc='left')
    tab.auto_set_font_size(False); tab.set_fontsize(10); tab.scale(1, 1.4)
    ax.set_title(title, fontsize=12, pad=10, weight='bold')

fig.suptitle('§1 — Top 10 most struggling students  ·  baseline vs improved',
             fontsize=13, y=1.02)
_save('comparison_struggle_top10')
plt.show()
"""),

    code("""# Agreement summary + Spearman ρ + top-10 overlap — matches the view's stats strip.

agree_s = agreement_summary(df_s['baseline_level'], df_s['improved_level'], STRUGGLE_LEVEL_ORDER)
baseline_order = df_s.sort_values('baseline_score', ascending=False)['user'].tolist()
improved_order = df_s.sort_values('improved_score', ascending=False)['user'].tolist()
rho_s = float(spearmanr(df_s['baseline_score'], df_s['improved_score']).correlation)
ovl_s = top10_overlap(baseline_order, improved_order, k=10)

print('AGREEMENT SUMMARY (improved vs baseline, per-snapshot levels)')
print(f'  total compared:  {agree_s[\"total\"]:,}')
print(f'  unchanged:       {agree_s[\"unchanged\"]:,}  ({agree_s[\"agreement_pct\"]}%)')
print(f'  upgraded   (improved sees as more struggling): {agree_s[\"upgraded\"]:,}')
print(f'  downgraded (improved sees as less struggling): {agree_s[\"downgraded\"]:,}')
print()
print(f'Spearman ρ (baseline vs improved scores): {rho_s:+.3f}')
print(f'Top-10 overlap (baseline ∩ improved by user): {int((ovl_s or 0) * 10)}/10  ({ovl_s})')
"""),

    code("""# Scatter — baseline (x) vs improved (y), coloured by LLM band where available.
# Matches the view's ScatterChart with our 4-band colour ramp.

STRUGGLE_BANDS = ['On Track', 'Minor Issues', 'Struggling', 'Needs Help']
band_to_idx = {b: i for i, b in enumerate(STRUGGLE_BANDS)}
cmap = plt.get_cmap('RdYlBu_r')
band_colors = [cmap(i / 3) for i in range(4)]

fig, ax = plt.subplots(figsize=(9, 8))
df_unlabeled = df_s[df_s['llm_band'].isna()]
if len(df_unlabeled):
    ax.scatter(df_unlabeled['baseline_score'], df_unlabeled['improved_score'],
               s=18, alpha=0.2, color='lightgrey', edgecolor='none',
               label=f'unlabeled (n={len(df_unlabeled):,})')
for band in STRUGGLE_BANDS:
    sub = df_s[df_s['llm_band'] == band]
    if not len(sub): continue
    ax.scatter(sub['baseline_score'], sub['improved_score'],
               s=28, alpha=0.6, color=band_colors[band_to_idx[band]],
               edgecolor='none', label=f'{band} (n={len(sub):,})')
ax.plot([0, 1], [0, 1], '--', color='grey', linewidth=1.2, alpha=0.7,
        label='baseline = improved')
ax.set_xlabel('Baseline composite score', fontsize=11)
ax.set_ylabel('Improved (BKT + IRT) score', fontsize=11)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title(f'§1 — Baseline vs improved struggle, per snapshot\\n'
             f'n = {len(df_s):,}  ·  Spearman ρ = {rho_s:+.3f}  ·  '
             f'top-10 overlap = {int((ovl_s or 0) * 10)}/10',
             fontsize=12)
ax.legend(loc='lower right', fontsize=9, framealpha=0.95)
ax.grid(True, alpha=0.3)
_save('comparison_struggle_scatter')
plt.show()
"""),

    code("""# Full pairs table — every snapshot, sorted by |delta| descending.
# Matches the view's PairsTable (which only showed biggest disagreements on
# screen but had the full data behind it).

pairs_s = df_s.sort_values('abs_delta', ascending=False).reset_index(drop=True)
out_csv = EVAL_DIR / 'comparison_struggle_pairs.csv'
pairs_s.to_csv(out_csv, index=False)
print(f'wrote {len(pairs_s):,} rows to {out_csv.relative_to(REPO_ROOT)}')
print()
print('Top 30 biggest disagreements (|delta| descending):')
display_cols = ['user', 'session_name', 'baseline_score', 'baseline_level',
                'improved_score', 'improved_level', 'delta', 'llm_band']
pairs_s.head(30)[display_cols]
"""),

    md("## §2 Difficulty — baseline composite vs IRT Rasch 1PL"),

    md("""The **baseline** difficulty score is the live dashboard's weighted composite
of five question-level signals (`c, t̃, ã, f, p`) — `v1_difficulty_score`
in the eval cohort, the value an instructor sees with
`difficulty_model = baseline`.

The **IRT** difficulty is `b_raw` from a 2PL fit on the full deployed
submission stream (`data/eval/submissions.parquet`), then min-max scaled
to [0, 1] to match the baseline's scale for the comparison plot. The 2PL
fit is the same one used by §5.4.3 in `eval_main.ipynb` — same 92 questions,
log-likelihood ≈ -2633.

Question overlap: the IRT fit covers any question with sufficient response
data (92 questions); the eval cohort covers questions present in the
labelled difficulty set (72 questions). The intersection is what's
plotted below.
"""),

    code("""# Compute baseline + IRT difficulty per question.

from backend.models.irt import compute_irt_model

# Baseline: lift directly from snapshots.json.
diff_q = json.loads((EVAL_DIR / 'snapshots.json').read_text(encoding='utf-8'))['difficulty_questions']
llm_d  = json.loads((EVAL_DIR / 'llm_difficulty_labels.json').read_text(encoding='utf-8'))['labels']

baseline_diff = pd.DataFrame([
    {
        'question': q['question'],
        'module':   q.get('module'),
        'baseline_score': float(q['v1_difficulty_score']),
        'baseline_level': q['v1_difficulty_level'],
        'llm_band':       (llm_d.get(q['question']) or {}).get('band'),
    }
    for q in diff_q
])
print(f'baseline difficulty: {len(baseline_diff)} questions')

# IRT: fit on submissions.parquet, take the difficulty_df.
subs_df = pd.read_parquet(EVAL_DIR / 'submissions.parquet')
print(f'fitting 2PL on {len(subs_df):,} submissions...')
irt_model = compute_irt_model(subs_df)
irt_df = irt_model['difficulty_df'].copy()
print(f'IRT difficulty_df: {len(irt_df)} questions, convergence={irt_model[\"convergence\"]}')

# Normalise b_raw to [0, 1] for comparison with baseline (which is in [0, 1]).
b_raw = irt_df['b_raw'].astype(float).values
b_min, b_max = float(b_raw.min()), float(b_raw.max())
irt_df['irt_score'] = (b_raw - b_min) / (b_max - b_min) if b_max > b_min else 0.5
irt_df['irt_level'] = irt_df['irt_score'].apply(lambda v: score_to_level(v, DIFFICULTY_THRESHOLDS))

# Inner-join on question text.
question_col = 'question' if 'question' in irt_df.columns else irt_df.columns[0]
df_d = baseline_diff.merge(irt_df[[question_col, 'irt_score', 'irt_level', 'b_raw',
                                    'irt_discrimination']],
                            left_on='question', right_on=question_col, how='inner')
df_d['delta'] = df_d['irt_score'] - df_d['baseline_score']
df_d['abs_delta'] = df_d['delta'].abs()
print(f'overlap (baseline ∩ IRT-fit): {len(df_d)} questions')
print(f'  baseline-only: {len(baseline_diff) - len(df_d)}')
print(f'  IRT-only:      {len(irt_df) - len(df_d)}')
df_d.head(3)
"""),

    code("""# Top-10 hardest leaderboards — baseline vs IRT, side-by-side.

baseline_top_d = df_d.sort_values('baseline_score', ascending=False).head(10)
irt_top_d      = df_d.sort_values('irt_score',      ascending=False).head(10)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
for ax, top, title, score_col, level_col in [
    (axes[0], baseline_top_d, 'Baseline composite — top 10 hardest',
     'baseline_score', 'baseline_level'),
    (axes[1], irt_top_d, 'IRT (2PL b_raw, scaled to [0,1]) — top 10 hardest',
     'irt_score', 'irt_level'),
]:
    ax.axis('off')
    headers = ['#', 'question', 'score', 'level']
    cells = [[f'{i+1}', r['question'][:46],
              f'{r[score_col]:.3f}', r[level_col]]
             for i, (_, r) in enumerate(top.iterrows())]
    tab = ax.table(cellText=cells, colLabels=headers, loc='center',
                   cellLoc='left', colLoc='left')
    tab.auto_set_font_size(False); tab.set_fontsize(9); tab.scale(1, 1.4)
    ax.set_title(title, fontsize=12, pad=10, weight='bold')

fig.suptitle('§2 — Top 10 hardest questions  ·  baseline vs IRT',
             fontsize=13, y=1.02)
_save('comparison_difficulty_top10')
plt.show()

# Agreement summary + stats.
agree_d = agreement_summary(df_d['baseline_level'], df_d['irt_level'], DIFFICULTY_LEVEL_ORDER)
rho_d = float(spearmanr(df_d['baseline_score'], df_d['irt_score']).correlation)
ovl_d = top10_overlap(
    df_d.sort_values('baseline_score', ascending=False)['question'].tolist(),
    df_d.sort_values('irt_score',      ascending=False)['question'].tolist(),
    k=10,
)
print()
print('AGREEMENT SUMMARY (IRT vs baseline, per-question levels)')
print(f'  total compared:  {agree_d[\"total\"]}')
print(f'  unchanged:       {agree_d[\"unchanged\"]}  ({agree_d[\"agreement_pct\"]}%)')
print(f'  upgraded   (IRT harder): {agree_d[\"upgraded\"]}')
print(f'  downgraded (IRT easier): {agree_d[\"downgraded\"]}')
print(f'Spearman ρ: {rho_d:+.3f}')
print(f'Top-10 overlap: {int((ovl_d or 0) * 10)}/10  ({ovl_d})')
"""),

    code("""# Difficulty scatter — baseline (x) vs IRT (y), coloured by LLM difficulty band.

DIFFICULTY_BANDS = ['Easy', 'Medium', 'Hard', 'Very Hard']
band_to_idx_d = {b: i for i, b in enumerate(DIFFICULTY_BANDS)}

fig, ax = plt.subplots(figsize=(9, 8))
df_d_un = df_d[df_d['llm_band'].isna()]
if len(df_d_un):
    ax.scatter(df_d_un['baseline_score'], df_d_un['irt_score'],
               s=40, alpha=0.3, color='lightgrey', edgecolor='none',
               label=f'unlabeled (n={len(df_d_un)})')
for band in DIFFICULTY_BANDS:
    sub = df_d[df_d['llm_band'] == band]
    if not len(sub): continue
    ax.scatter(sub['baseline_score'], sub['irt_score'],
               s=70, alpha=0.7, color=band_colors[band_to_idx_d[band]],
               edgecolor='black', linewidth=0.4, label=f'{band} (n={len(sub)})')
ax.plot([0, 1], [0, 1], '--', color='grey', linewidth=1.2, alpha=0.7,
        label='baseline = IRT')
ax.set_xlabel('Baseline composite difficulty', fontsize=11)
ax.set_ylabel('IRT difficulty (b_raw, scaled to [0,1])', fontsize=11)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
ax.set_title(f'§2 — Baseline vs IRT difficulty, per question\\n'
             f'n = {len(df_d)}  ·  Spearman ρ = {rho_d:+.3f}  ·  '
             f'top-10 overlap = {int((ovl_d or 0) * 10)}/10',
             fontsize=12)
ax.legend(loc='lower right', fontsize=9, framealpha=0.95)
ax.grid(True, alpha=0.3)
_save('comparison_difficulty_scatter')
plt.show()
"""),

    code("""# Full pairs table for difficulty.

pairs_d = df_d.sort_values('abs_delta', ascending=False).reset_index(drop=True)
out_csv_d = EVAL_DIR / 'comparison_difficulty_pairs.csv'
pairs_d.to_csv(out_csv_d, index=False)
print(f'wrote {len(pairs_d)} rows to {out_csv_d.relative_to(REPO_ROOT)}')
print()
print('All pairs sorted by |delta| (IRT − baseline):')
display_cols = ['question', 'module', 'baseline_score', 'baseline_level',
                'irt_score', 'irt_level', 'delta', 'llm_band',
                'b_raw', 'irt_discrimination']
pairs_d[display_cols]
"""),
]


def main() -> int:
    nb = {
        "cells": CELLS,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    NB_PATH.parent.mkdir(parents=True, exist_ok=True)
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {NB_PATH.relative_to(REPO)} ({len(CELLS)} cells)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
