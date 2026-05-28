"""Insert the two model-class bake-off figures into notebooks/eval_main.ipynb.

  1. model_class_bakeoff.png        — OLS vs 5 regression alternatives, 3 targets
  2. framing_regression_vs_classification.png — OLS (regression) vs 3 classifiers,
     on ranking (rho_expected) AND classification (weighted_kappa)

Reads the promoted canonical JSONs (data/eval/model_class_bakeoff.json,
data/eval/classifier_bakeoff.json). Idempotent: cells tagged with
metadata['inserted_by']; re-running replaces rather than duplicates.

Run from repo root:
    python scripts/experiments/_nb_insert_bakeoff_figures.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NB_PATH = REPO / "notebooks" / "eval_main.ipynb"
TAG = "bakeoff_figures_2026_05_27"


def md(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {"inserted_by": TAG},
            "source": source.splitlines(keepends=True)}


def code(source: str) -> dict:
    return {"cell_type": "code", "execution_count": None,
            "metadata": {"inserted_by": TAG}, "outputs": [],
            "source": source.splitlines(keepends=True)}


MODELCLASS_MD = """## §5.4.x — Model-class selection (regression alternatives)

Did the OLS choice for the v2 weights actually beat the alternatives, or would
a regularised / non-linear regressor have done better? Each model class is fit
against the same 4-band target under the same CV splits as
`scripts/optimise_v2_weights.py` (GroupKFold(5) by session for struggle +
improved; LOO for difficulty). Higher Spearman ρ is better. OLS is the deployed
choice; RandomForest / GradientBoosting are shown as a non-linear ceiling
reference — they produce no per-feature signed weights, so adopting them would
forfeit the interpretable weight-comparison story.
"""

MODELCLASS_CODE = """# Model-class bake-off — OLS vs regression alternatives, 3 targets.
import json as _json
mc = _json.loads((EVAL_DIR / 'model_class_bakeoff.json').read_text(encoding='utf-8'))['results']

target_keys = [('struggle', 'Struggle (n=1306)'),
               ('difficulty', 'Difficulty (n=72)'),
               ('improved_struggle', 'Improved-struggle (n=1306)')]

def _rho(entry):
    # struggle/improved store {mean,std,per_fold}; difficulty stores {pooled_rho}
    return entry.get('mean', entry.get('pooled_rho'))

# Stable model ordering (drop any model absent from a target)
model_order = ['OLS (baseline)', 'Ridge alpha=0.1', 'Ridge alpha=1.0',
               'Ridge alpha=10.0', 'Lasso alpha=0.01', 'ElasticNet a=0.01',
               'RandomForest', 'GradientBoosting']

fig, axes = plt.subplots(1, 3, figsize=(16, 5.5), sharey=False)
for ax, (tk, title) in zip(axes, target_keys):
    models = mc[tk]['models']
    names = [m for m in model_order if m in models]
    vals = [_rho(models[m]) for m in names]
    # colour: OLS accent, non-linear (RF/GB) warn, linear-reg grey-blue
    colors = []
    for m in names:
        if m == 'OLS (baseline)':
            colors.append(COLOR_V2)
        elif m in ('RandomForest', 'GradientBoosting'):
            colors.append('#bdbdbd')
        else:
            colors.append(COLOR_BAND)
    ypos = np.arange(len(names))
    ax.barh(ypos, vals, color=colors, edgecolor='black', linewidth=0.5)
    for y, v in zip(ypos, vals):
        ax.text(v + (0.005 if v >= 0 else -0.005), y, f'{v:+.3f}',
                va='center', ha='left' if v >= 0 else 'right', fontsize=8)
    ax.set_yticks(ypos)
    ax.set_yticklabels([m.replace(' (baseline)', '\\n(deployed)') for m in names], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel('Spearman ρ vs 4-band rating')
    ax.set_title(title, fontsize=11)
    ax.grid(True, alpha=0.3, axis='x')

fig.suptitle('Model-class selection — OLS vs regression alternatives (deployed = lightcoral; '
             'non-linear = grey, no interpretable weights)', fontsize=12)
_save('model_class_bakeoff')
plt.show()

# Headline line for the writer
s_ols = _rho(mc['struggle']['models']['OLS (baseline)'])
s_rf  = _rho(mc['struggle']['models']['RandomForest'])
print(f'Struggle: OLS ρ={s_ols:+.3f} vs RandomForest ρ={s_rf:+.3f} '
      f'(OLS {\"wins\" if s_ols > s_rf else \"loses\"} by {abs(s_ols - s_rf):.3f})')
"""

FRAMING_MD = """## §5.4.x — Regression vs classification framing

The v2 weights are fit by **regression** (OLS on the band index 0–3). An
alternative is to frame the task as **classification** (predict the band
directly). The chart below compares OLS against three classifiers
(multinomial logistic regression, RandomForest, GradientBoosting) on two
metrics: Spearman ρ of the expected band (ranking quality — what the
leaderboard uses) and linear-weighted Cohen's κ of the arg-max band
(classification quality).

The pattern: OLS is competitive-to-best on **ranking**, while classifiers win
on raw **κ** (they optimise the categorical objective directly). However the
trained band-thresholds (§5.4.11) lift OLS's κ to a level that matches the best
classifier — so the deployed OLS-regression-plus-trained-thresholds pipeline
captures the classification gain while keeping interpretable signed weights and
the stronger ranking.
"""

FRAMING_CODE = """# Regression (OLS) vs classification framing — ranking (rho) + classification (kappa).
cf = _json.loads((EVAL_DIR / 'classifier_bakeoff.json').read_text(encoding='utf-8'))

cf_targets = [('struggle', 'Struggle'), ('difficulty', 'Difficulty'),
              ('improved', 'Improved')]
cf_models = ['OLS (baseline)', 'LogisticRegression (multinomial)',
             'RandomForestClassifier (n=200, d=5)',
             'GradientBoostingClassifier (n=200, d=3, lr=0.05)']
short = ['OLS\\n(regression)', 'Multinomial\\nlogit', 'RF\\nclassifier', 'GB\\nclassifier']
mcolors = [COLOR_V2, COLOR_BAND, '#9ecae1', '#bdbdbd']

fig, (axL, axR) = plt.subplots(1, 2, figsize=(15, 5.5))
x = np.arange(len(cf_targets))
w = 0.2
for j, (model, lab, col) in enumerate(zip(cf_models, short, mcolors)):
    rho_vals = [cf[tk][model]['rho_expected'] for tk, _ in cf_targets]
    kap_vals = [cf[tk][model]['weighted_kappa'] for tk, _ in cf_targets]
    axL.bar(x + (j - 1.5) * w, rho_vals, w, label=lab, color=col, edgecolor='black', linewidth=0.4)
    axR.bar(x + (j - 1.5) * w, kap_vals, w, label=lab, color=col, edgecolor='black', linewidth=0.4)

for ax, title, ylab in [(axL, 'Ranking quality — Spearman ρ (expected band)', 'Spearman ρ'),
                        (axR, 'Classification — linear-weighted κ (arg-max band)', 'Cohen κ')]:
    ax.set_xticks(x)
    ax.set_xticklabels([t for _, t in cf_targets])
    ax.set_ylabel(ylab)
    ax.set_title(title, fontsize=11)
    ax.legend(fontsize=8, loc='upper right')
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(0, color='black', linewidth=0.6)

fig.suptitle('Regression vs classification framing — OLS competitive on ranking; '
             'classifiers win raw κ (closed by trained thresholds, §5.4.11)', fontsize=12)
_save('framing_regression_vs_classification')
plt.show()

# Headline lines for the writer
for tk, t in cf_targets:
    ols_k = cf[tk]['OLS (baseline)']['weighted_kappa']
    best_clf = max((m for m in cf_models if m != 'OLS (baseline)'),
                   key=lambda m: cf[tk][m]['weighted_kappa'])
    print(f'{t}: OLS raw κ={ols_k:+.3f}  best-classifier κ={cf[tk][best_clf][\"weighted_kappa\"]:+.3f} '
          f'({best_clf.split(\" \")[0]})')
"""


def find_anchor(cells, predicate):
    for i, c in enumerate(cells):
        if predicate(c, ''.join(c.get('source', []))):
            return i
    return -1


def main() -> int:
    nb = json.loads(NB_PATH.read_text(encoding='utf-8'))
    cells = [c for c in nb['cells'] if c.get('metadata', {}).get('inserted_by') != TAG]
    n_before = len(cells)

    a = find_anchor(cells, lambda c, s: c['cell_type'] == 'markdown' and s.startswith('## Markdown export'))
    if a < 0:
        print('FAIL: could not find results.md export anchor', file=sys.stderr)
        return 1

    new_cells = [md(MODELCLASS_MD), code(MODELCLASS_CODE),
                 md(FRAMING_MD), code(FRAMING_CODE)]
    cells[a:a] = new_cells

    nb['cells'] = cells
    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'inserted {len(cells) - n_before} cells before results.md export (idx {a}); total {len(cells)}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
