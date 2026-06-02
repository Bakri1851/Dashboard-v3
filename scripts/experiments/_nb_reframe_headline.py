"""Move the §5.4 HEADLINE designation from the v1-vs-v2 weight chart (cell 9)
to the model-class bake-off cells. Markdown-only — no re-execution.

- Cell 9: drop "(HEADLINE)"; reframe as a baseline check (training beat
  hand-setting) that feeds into the model-class selection headline.
- Bake-off cells (model-class selection + regression-vs-classification):
  mark as the primary/headline §5.4 model-class comparison.

Idempotent exact-string replacements. Run from repo root:
    python scripts/experiments/_nb_reframe_headline.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NB = REPO / "notebooks" / "eval_main.ipynb"

REPLACEMENTS = [
    (
        "## §5.4.3 — v1 vs v2 weights: STRUGGLE model (HEADLINE)\n"
        "\n"
        "Paired bars: v1 hand-set weights vs v2 OLS-trained weights. Error bars on v2 from per-fold std (5 folds, session-grouped GroupKFold). Target: 4-band rating (`On Track` ... `Needs Help`). Sign-flipped signals indicate where the trained model disagrees with the hand-set direction — these survive the target swap from binary intervene to the 4-band rating.",
        "## §5.4.3 — Baseline check: v1 hand-set vs v2 trained weights (struggle)\n"
        "\n"
        "Paired bars: v1 hand-set weights vs v2 OLS-trained weights. Error bars on v2 from per-fold std (5 folds, session-grouped GroupKFold). Target: 4-band rating (`On Track` ... `Needs Help`). Sign-flipped signals indicate where the trained model disagrees with the hand-set direction. This is the **baseline** result — it establishes that empirical training improves on hand-setting; the **headline** model-class comparison (which model family to train) is the bake-off at §5.4.x below.",
    ),
    (
        "## §5.4.x — Model-class selection (regression alternatives)\n",
        "## §5.4.x — Model-class selection (regression alternatives) — HEADLINE comparison\n",
    ),
]


def main() -> int:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    applied = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        new = src
        for find, repl in REPLACEMENTS:
            if find in new:
                new = new.replace(find, repl)
        if new != src:
            cell["source"] = new.splitlines(keepends=True)
            applied += 1
    NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    blob = NB.read_text(encoding="utf-8")
    print(f"reframed {applied} cell(s)")
    print(f"  cell 9 '(HEADLINE)' on v1-vs-v2 gone: {'§5.4.3 — v1 vs v2 weights: STRUGGLE model (HEADLINE)' not in blob}")
    print(f"  bake-off marked HEADLINE: {'Model-class selection (regression alternatives) — HEADLINE comparison' in blob}")
    return 0 if applied == len(REPLACEMENTS) else 1


if __name__ == "__main__":
    sys.exit(main())
