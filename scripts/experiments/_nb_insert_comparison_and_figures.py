"""One-shot notebook mutator: insert entity-level v1 vs v2 comparison cells
plus the IRT discrimination and incorrectness histogram cells into
notebooks/eval_main.ipynb.

Idempotent: cells are tagged with metadata['inserted_by'] so a re-run replaces
existing inserts instead of duplicating them.

Run from repo root:

    python scripts/experiments/_nb_insert_comparison_and_figures.py

This script is consumed once and can be deleted afterwards (the canonical
content lives in the notebook).
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NB_PATH = REPO / "notebooks" / "eval_main.ipynb"
TAG = "comparison_and_figures_2026_05_27"


def md(source: str) -> dict:
    return {
        "cell_type": "markdown",
        "metadata": {"inserted_by": TAG},
        "source": source.splitlines(keepends=True),
    }


def code(source: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {"inserted_by": TAG},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


SCORE_DELTA_MD = """## §5.4.3a — Per-snapshot score delta (v1 vs v2)

Aggregate ρ tells us v2 ranks the cohort better, but it hides _which_ students
move and by how much. The plots below show, for every snapshot, the v1 vs v2
predicted score (scaled to a shared 0–3 band axis) coloured by the LLM's true
band, and a histogram of the absolute per-snapshot delta. A snapshot near the
diagonal means the two models agree on severity; off-diagonal mass shows the
re-ranking that happens when an instructor flips the toggle.
"""

SCORE_DELTA_CODE = """# Per-snapshot score delta v1 vs v2 (struggle model).
# Uses v1_struggle / v2_struggle from cell §5.4.x re-derivation block above.

v1_pred_on_band = np.array(v1_struggle['pred']) * (N_BANDS - 1)   # rescale [0,1] -> [0,3]
v2_pred_on_band = np.clip(v2_struggle['pred'], 0, N_BANDS - 1)
y_arr_sd = np.array(v2_struggle['y'])
delta_abs = np.abs(v1_pred_on_band - v2_pred_on_band)

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# (a) Scatter — v1 vs v2 predicted score, coloured by LLM band
cmap = plt.get_cmap('RdYlBu_r')
band_colors = [cmap(i / (N_BANDS - 1)) for i in range(N_BANDS)]
for band_idx in range(N_BANDS):
    mask = (y_arr_sd == band_idx)
    axes[0].scatter(v1_pred_on_band[mask], v2_pred_on_band[mask],
                    c=[band_colors[band_idx]], alpha=0.55, s=28,
                    edgecolor='none', label=f'{band_idx} {STRUGGLE_BANDS[band_idx]}')
axes[0].plot([0, N_BANDS - 1], [0, N_BANDS - 1], '-', color='grey', linewidth=1.4, alpha=0.7,
             label='v1 = v2 (no change)')
axes[0].set_xlabel('v1 predicted band severity (live score × 3)')
axes[0].set_ylabel('v2 predicted band severity (OLS, clipped 0–3)')
axes[0].set_title('Per-snapshot prediction agreement\\ncoloured by LLM truth band')
axes[0].legend(loc='upper left', fontsize=9, framealpha=0.9)
axes[0].grid(True, alpha=0.3)
axes[0].set_xlim(-0.2, N_BANDS - 0.8)
axes[0].set_ylim(-0.2, N_BANDS - 0.8)

# (b) Histogram of |delta|
axes[1].hist(delta_abs, bins=40, color=COLOR_V2, edgecolor='black', linewidth=0.4)
axes[1].axvline(float(delta_abs.mean()), color='black', linestyle='--', linewidth=1.4,
                label=f'mean |Δ| = {delta_abs.mean():.2f} bands')
axes[1].axvline(float(np.median(delta_abs)), color='grey', linestyle=':', linewidth=1.4,
                label=f'median |Δ| = {np.median(delta_abs):.2f} bands')
axes[1].set_xlabel('|v1 − v2| score delta (band units, 0–3 scale)')
axes[1].set_ylabel('Snapshot count')
axes[1].set_title(f'Per-snapshot absolute score delta (n = {len(delta_abs):,})')
axes[1].legend(loc='upper right', fontsize=10)
axes[1].grid(True, alpha=0.3, axis='y')

fig.suptitle('Per-entity v1 vs v2 score delta — struggle model', fontsize=13)
_save('score_delta_v1_vs_v2_struggle')
plt.show()

n_large_shift = int((delta_abs >= 1.0).sum())
n_within_half = int((delta_abs <= 0.5).sum())
print(f'mean |delta|:                {delta_abs.mean():.3f} bands')
print(f'median |delta|:              {float(np.median(delta_abs)):.3f} bands')
print(f'snapshots with |delta| <=0.5: {n_within_half:,} ({n_within_half/len(delta_abs):.1%}) — broadly agree')
print(f'snapshots with |delta| >=1.0: {n_large_shift:,} ({n_large_shift/len(delta_abs):.1%}) — re-ranked by at least one band')
"""

RANK_SHIFT_MD = """## §5.6.1a — Leaderboard rank shift v1 → v2

The aggregate model-disagreement matrix above counts how many snapshots change
band, but a leaderboard is what an instructor sees in-class. The histogram
below shows, per snapshot, how its rank moves when the v1 toggle flips to v2
(positive = student becomes _more_ visible / climbs the struggle ranking;
negative = student drops down). The top-K overlap table answers the question
an instructor would actually ask: "if I flip the toggle, do I get a different
top-20?"
"""

RANK_SHIFT_CODE = """# Leaderboard rank shift v1 -> v2 (struggle model).
# Rank both models' predictions descending (higher = more struggling).
# Rank delta = v1_rank - v2_rank; positive => student climbs the v2 ranking.

# Use the same arrays from the §5.4.3a cells above
v1_scores = np.array(v1_struggle['pred'])
v2_scores = np.array(v2_struggle['pred'])
n = len(v1_scores)

v1_order = np.argsort(-v1_scores)
v2_order = np.argsort(-v2_scores)
v1_rank = np.empty(n, dtype=int)
v2_rank = np.empty(n, dtype=int)
v1_rank[v1_order] = np.arange(1, n + 1)
v2_rank[v2_order] = np.arange(1, n + 1)
rank_delta = v1_rank - v2_rank  # positive => student climbs the v2 ranking

fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# (a) Rank-shift histogram (symmetric around zero)
abs_cap = int(np.percentile(np.abs(rank_delta), 99))
bins = np.linspace(-abs_cap, abs_cap, 50)
axes[0].hist(np.clip(rank_delta, -abs_cap, abs_cap), bins=bins,
             color=COLOR_V2, edgecolor='black', linewidth=0.4)
axes[0].axvline(0, color='black', linestyle='--', linewidth=1.2, alpha=0.7,
                label='no change (v1 rank = v2 rank)')
axes[0].set_xlabel('Rank delta = v1 rank − v2 rank   (positive: climbs under v2)')
axes[0].set_ylabel('Snapshot count')
axes[0].set_title(f'Per-snapshot rank shift v1 → v2  (n = {n:,}, clipped to 99th pctile = ±{abs_cap})')
axes[0].legend(loc='upper right', fontsize=10)
axes[0].grid(True, alpha=0.3, axis='y')

# (b) Top-K overlap curve
ks = [10, 20, 50, 100, 200]
v1_top = {k: set(v1_order[:k].tolist()) for k in ks}
v2_top = {k: set(v2_order[:k].tolist()) for k in ks}
overlap_pcts = [len(v1_top[k] & v2_top[k]) / k for k in ks]
overlap_counts = [len(v1_top[k] & v2_top[k]) for k in ks]
axes[1].bar(range(len(ks)), overlap_pcts, color=COLOR_BAND, edgecolor='black', linewidth=0.6)
for i, (k, c, p) in enumerate(zip(ks, overlap_counts, overlap_pcts)):
    axes[1].text(i, p + 0.02, f'{c}/{k}\\n({p:.0%})', ha='center', fontsize=10)
axes[1].set_xticks(range(len(ks)))
axes[1].set_xticklabels([f'Top-{k}' for k in ks])
axes[1].set_ylabel('Fraction of v1 top-K also in v2 top-K')
axes[1].set_title('Top-K leaderboard overlap v1 ∩ v2')
axes[1].set_ylim(0, 1.05)
axes[1].grid(True, alpha=0.3, axis='y')

fig.suptitle('Leaderboard rank shift v1 → v2 — struggle model', fontsize=13)
_save('rank_shift_v1_vs_v2_struggle')
plt.show()

print(f'mean rank delta:    {rank_delta.mean():+.1f}')
print(f'median rank delta:  {float(np.median(rank_delta)):+.1f}')
print(f'mean |rank delta|:  {np.abs(rank_delta).mean():.1f}')
print(f'max  |rank delta|:  {int(np.abs(rank_delta).max())}')
for k in ks:
    print(f'top-{k:<3d} overlap:  {len(v1_top[k] & v2_top[k]):>3d}/{k} ({len(v1_top[k] & v2_top[k])/k:.0%})')
"""

DIFFICULTY_RANK_SHIFT_MD = """## §5.6.1b — Per-question difficulty rank shift v1 → v2

Same analysis on the difficulty model (per-question, n=72). With LOO CV and a
heavily-skewed cohort the per-question reordering is the more honest
diagnostic: even when ρ is modest, the top-K-hardest list is what an instructor
would act on.
"""

DIFFICULTY_RANK_SHIFT_CODE = """# Per-question difficulty rank shift v1 -> v2.
# Mirror of §5.6.1a, but for the difficulty model (n=72 questions, LOO CV).
# Lifts v2 predictions directly from optimised_difficulty_weights_v2.json's
# pooled_predictions (the LOO output of scripts/optimise_v2_weights.py) so
# we don't re-derive — and asserts ordering matches our matched_q iteration.

matched_q   = [q for q in diff_questions if q['question'] in llm_difficulty_labels]
v1_diff_pred = np.array([q['v1_difficulty_score'] for q in matched_q])
y_d = np.array([DIFFICULTY_BAND_INDEX[llm_difficulty_labels[q['question']]['band']]
                for q in matched_q])
v2_diff_pred = np.array(opt_difficulty['pooled_predictions'])
v2_pooled_y  = np.array(opt_difficulty['pooled_y'])

# Sanity check: our matched_q ordering must match the optimise script's, else
# v1 and v2 arrays are mis-aligned and the rank-shift result is garbage.
assert len(v2_diff_pred) == len(matched_q), (
    f'pooled_predictions has {len(v2_diff_pred)} entries but matched_q has {len(matched_q)}')
assert np.array_equal(v2_pooled_y, y_d), (
    'pooled_y from optimised_difficulty_weights_v2.json does not match the band '
    'sequence derived from iterating diff_questions in JSON order — the optimise '
    'script must use a different ordering. Falling back to re-derivation would '
    'restore correctness; bail here rather than plot misaligned ranks.')

n_q = len(matched_q)
v1_q_order = np.argsort(-v1_diff_pred)
v2_q_order = np.argsort(-v2_diff_pred)
v1_q_rank = np.empty(n_q, dtype=int); v1_q_rank[v1_q_order] = np.arange(1, n_q + 1)
v2_q_rank = np.empty(n_q, dtype=int); v2_q_rank[v2_q_order] = np.arange(1, n_q + 1)
q_rank_delta = v1_q_rank - v2_q_rank

fig, axes = plt.subplots(1, 2, figsize=(15, 6))
axes[0].hist(q_rank_delta, bins=30, color=COLOR_V2, edgecolor='black', linewidth=0.4)
axes[0].axvline(0, color='black', linestyle='--', linewidth=1.2, alpha=0.7)
axes[0].set_xlabel('Rank delta = v1 rank − v2 rank   (positive: harder under v2)')
axes[0].set_ylabel('Question count')
axes[0].set_title(f'Per-question rank shift v1 → v2  (n = {n_q})')
axes[0].grid(True, alpha=0.3, axis='y')

ks_q = [5, 10, 20]
v1_q_top = {k: set(v1_q_order[:k].tolist()) for k in ks_q}
v2_q_top = {k: set(v2_q_order[:k].tolist()) for k in ks_q}
overlap_q_pcts = [len(v1_q_top[k] & v2_q_top[k]) / k for k in ks_q]
overlap_q_counts = [len(v1_q_top[k] & v2_q_top[k]) for k in ks_q]
axes[1].bar(range(len(ks_q)), overlap_q_pcts, color=COLOR_BAND, edgecolor='black', linewidth=0.6)
for i, (k, c, p) in enumerate(zip(ks_q, overlap_q_counts, overlap_q_pcts)):
    axes[1].text(i, p + 0.02, f'{c}/{k}\\n({p:.0%})', ha='center', fontsize=10)
axes[1].set_xticks(range(len(ks_q)))
axes[1].set_xticklabels([f'Top-{k} hardest' for k in ks_q])
axes[1].set_ylabel('Fraction of v1 top-K also in v2 top-K')
axes[1].set_title('Top-K hardest-question overlap v1 ∩ v2')
axes[1].set_ylim(0, 1.05)
axes[1].grid(True, alpha=0.3, axis='y')

fig.suptitle('Per-question rank shift v1 → v2 — difficulty model', fontsize=13)
_save('rank_shift_v1_vs_v2_difficulty')
plt.show()

print(f'mean |rank delta| (questions): {np.abs(q_rank_delta).mean():.1f}')
print(f'max  |rank delta| (questions): {int(np.abs(q_rank_delta).max())}')
for k in ks_q:
    print(f'top-{k:<3d} hardest overlap: {len(v1_q_top[k] & v2_q_top[k]):>2d}/{k} ({len(v1_q_top[k] & v2_q_top[k])/k:.0%})')
"""

IRT_MD = """## §5.4.3 — IRT 2PL discrimination diagnostic (per question)

Two-parameter logistic IRT fit to the deployed submission stream. Each point
is one question; x-axis is logit-scale difficulty β_q (higher = harder),
y-axis is discrimination α_q (higher = better-separating). The dashed lines
mark Rasch-equivalent items (α = 1) and the low-discrimination cutoff
(α ≤ 0.5). Items in the red circles contribute little information to the
difficulty ranking — they are answered with roughly equal probability across
the student-ability spectrum.

Also written to `Report/figures/evaluation/eval-irt-discrimination.png` by
`scripts/experiments/extra_figures.py` for the LaTeX include path.
"""

IRT_CODE = """# IRT 2PL discrimination scatter (per question).
# Mirrors scripts/experiments/extra_figures.py::make_irt_discrimination().

from backend.models.irt import compute_irt_model

subs_df = pd.read_parquet(REPO_ROOT / 'data' / 'eval' / 'submissions.parquet')
print(f'loaded {len(subs_df):,} submissions; fitting 2PL...')
_irt = compute_irt_model(subs_df)
qdf = _irt['difficulty_df']
print(f'fitted: {len(qdf)} questions, convergence={_irt[\"convergence\"]}, log-likelihood={_irt[\"log_likelihood\"]:.1f}')

beta_q  = qdf['b_raw'].values
alpha_q = qdf['irt_discrimination'].values

fig, ax = plt.subplots(figsize=(10, 6.5))
ax.scatter(beta_q, alpha_q, s=60, c=COLOR_V2, alpha=0.65, edgecolor='black', linewidth=0.5)
ax.axhline(1.0, color='grey', linestyle='--', linewidth=1, alpha=0.7,
           label=r'Rasch-equivalent ($\\alpha = 1$)')
ax.axhline(0.5, color='grey', linestyle=':', linewidth=1, alpha=0.7,
           label=r'low-discrimination cutoff ($\\alpha \\leq 0.5$)')
ax.axvline(0.0, color='grey', linestyle=':', linewidth=0.8, alpha=0.5)

low_mask = alpha_q <= 0.5
n_low = int(low_mask.sum())
if n_low > 0:
    ax.scatter(beta_q[low_mask], alpha_q[low_mask],
               s=120, facecolor='none', edgecolor=COLOR_WARN, linewidth=1.8,
               label=f'low-discrimination items ($n={n_low}$)')

ax.set_xlabel(r'Difficulty (logit scale) $\\beta_q$ — higher = harder', fontsize=11)
ax.set_ylabel(r'Discrimination $\\alpha_q$ — higher = better-separating', fontsize=11)
ax.set_title(
    f'2PL IRT diagnostic — discrimination vs difficulty per question\\n'
    f'$n={len(qdf)}$ questions  ·  mean $\\\\alpha$ = {alpha_q.mean():.2f}  '
    f'·  mean $\\\\beta$ = {beta_q.mean():+.2f}',
    fontsize=12,
)
ax.legend(loc='best', fontsize=9, framealpha=0.95)
ax.grid(True, alpha=0.3)

n_neg = int((alpha_q < 0).sum())
annot = (f'{n_low} of {len(qdf)} questions have $\\\\alpha \\\\leq 0.5$\\n'
         f'(weak discrimination — answering correctly on these\\n'
         f'items reveals little about student ability).')
if n_neg > 0:
    annot += f'\\n{n_neg} have negative $\\\\alpha$ — fit pathology, drop from interpretation.'
ax.text(0.02, 0.98, annot, transform=ax.transAxes, va='top', fontsize=9,
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.92, edgecolor='grey'))

_save('eval-irt-discrimination')
plt.show()
"""

INC_MD = """## §5.4.1 / §5.6.3 — Per-submission incorrectness distribution

The `incorrectness` column drives the struggle model's i-signal. Its
distribution across the live deployment shows how heavily the analytics
pipeline relied on the 0.5 fallback value (assigned when AI feedback text was
missing or the LLM scoring call failed). The bulk of the mass sitting at
exactly 0.5 means most submissions are scored at the neutral midpoint rather
than from real LLM signal — this is a deployment-side limitation the i-signal
inherits.

Also written to `Report/figures/evaluation/eval-incorrectness-distribution.png`
by `scripts/experiments/extra_figures.py` for the LaTeX include path.
"""

INC_CODE = """# Per-submission incorrectness distribution.
# Mirrors scripts/experiments/extra_figures.py::make_incorrectness_histogram().

if 'subs_df' not in dir():
    subs_df = pd.read_parquet(REPO_ROOT / 'data' / 'eval' / 'submissions.parquet')

inc = subs_df['incorrectness'].values
n_total = len(inc)
n_fallback  = int((inc == 0.5).sum())
n_correct   = int((inc < 0.5).sum())
n_incorrect = int((inc > 0.5).sum())

fig, ax = plt.subplots(figsize=(11, 6))
counts, edges, patches = ax.hist(inc, bins=50, color=COLOR_V2, edgecolor='black', linewidth=0.4)
centre_bin_idx = int(np.argmin(np.abs(edges[:-1] - 0.5)))
if 0 <= centre_bin_idx < len(patches):
    patches[centre_bin_idx].set_facecolor(COLOR_WARN)
    patches[centre_bin_idx].set_edgecolor('black')

ax.axvline(0.5, color='black', linestyle='--', linewidth=1.2, alpha=0.6,
           label=r'CORRECT_THRESHOLD ($\\tau = 0.5$)')
ax.set_xlabel('Incorrectness score (per submission)', fontsize=11)
ax.set_ylabel('Count (log scale)', fontsize=11)
ax.set_yscale('log')
ax.set_title(
    f'Distribution of per-submission incorrectness across the deployment ({n_total:,} submissions)\\n'
    f'{n_fallback/n_total:.1%} sit at the 0.5 fallback (no AI feedback or LLM call failed)',
    fontsize=12,
)
ax.grid(True, alpha=0.3, axis='y', which='both')
ax.legend(loc='upper right', fontsize=10)

summary = (
    f'Fallback ($=0.5$):  {n_fallback:>6,d}  ({n_fallback/n_total:>5.1%})\\n'
    f'Clearly correct  ($<0.5$):  {n_correct:>6,d}  ({n_correct/n_total:>5.1%})\\n'
    f'Clearly incorrect ($>0.5$): {n_incorrect:>6,d}  ({n_incorrect/n_total:>5.1%})\\n'
    f'Mean: {inc.mean():.3f}    Std: {inc.std():.3f}'
)
ax.text(0.02, 0.97, summary, transform=ax.transAxes, va='top', fontsize=9,
        family='monospace',
        bbox=dict(boxstyle='round', facecolor='white', alpha=0.92, edgecolor='grey'))

_save('eval-incorrectness-distribution')
plt.show()

print(f'N = {n_total:,}')
print(f'fallback @ 0.5:      {n_fallback:,} ({n_fallback/n_total:.1%})')
print(f'clearly correct:     {n_correct:,} ({n_correct/n_total:.1%})')
print(f'clearly incorrect:   {n_incorrect:,} ({n_incorrect/n_total:.1%})')
"""


def find_anchor(cells: list, predicate) -> int:
    for i, c in enumerate(cells):
        src = ''.join(c.get('source', []))
        if predicate(c, src):
            return i
    return -1


def strip_existing_inserts(cells: list) -> list:
    return [c for c in cells if c.get('metadata', {}).get('inserted_by') != TAG]


def main() -> int:
    nb = json.loads(NB_PATH.read_text(encoding='utf-8'))
    cells = strip_existing_inserts(nb['cells'])
    n_before = len(cells)

    # Anchor 1: after the predicted-vs-observed scatter cell
    a1 = find_anchor(cells, lambda c, s: c['cell_type'] == 'code' and
                     'Predicted-vs-observed band scatter for v1 vs v2 side-by-side' in s)
    if a1 < 0:
        print('FAIL: could not find predicted-vs-observed scatter anchor', file=sys.stderr)
        return 1

    # Anchor 2: after the v1↔v2 disagreement matrix cell
    a2 = find_anchor(cells, lambda c, s: c['cell_type'] == 'code' and
                     'cm_v1v2 = confusion_matrix(v1_bands_arr, v2_bands_arr' in s)
    if a2 < 0:
        print('FAIL: could not find disagreement matrix anchor', file=sys.stderr)
        return 1

    # Anchor 3: before the results.md markdown export header
    a3 = find_anchor(cells, lambda c, s: c['cell_type'] == 'markdown' and
                     s.startswith('## Markdown export'))
    if a3 < 0:
        print('FAIL: could not find results.md export anchor', file=sys.stderr)
        return 1

    # Insert in reverse order so earlier indices stay valid
    insertions = [
        (a3,     [md(IRT_MD), code(IRT_CODE),
                  md(INC_MD), code(INC_CODE)]),
        (a2 + 1, [md(RANK_SHIFT_MD), code(RANK_SHIFT_CODE),
                  md(DIFFICULTY_RANK_SHIFT_MD), code(DIFFICULTY_RANK_SHIFT_CODE)]),
        (a1 + 1, [md(SCORE_DELTA_MD), code(SCORE_DELTA_CODE)]),
    ]
    for idx, new_cells in insertions:
        cells[idx:idx] = new_cells

    nb['cells'] = cells
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'inserted {len(cells) - n_before} cells; total now {len(cells)}')
    print(f'  after a1 (scatter)        idx {a1 + 1}: score_delta_v1_vs_v2_struggle')
    print(f'  after a2 (disagreement)   idx {a2 + 1}: rank_shift_v1_vs_v2_struggle + difficulty')
    print(f'  before a3 (results.md)    idx {a3}: IRT + incorrectness')
    return 0


if __name__ == '__main__':
    sys.exit(main())
