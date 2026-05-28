"""Reframe the two eval_main.ipynb markdown cells that still describe the
removed v1/v2 weight toggle as an instructor-flippable switch. The toggles
were removed; v1 is now the offline evaluation baseline, v2 the deployed
model. Markdown-only edits — no re-execution needed.

Idempotent: exact-string replacements; running twice is a no-op once applied.
Run from repo root:
    python scripts/experiments/_nb_reframe_v1_baseline.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NB = REPO / "notebooks" / "eval_main.ipynb"

# (find, replace) pairs applied to markdown cell source text.
REPLACEMENTS = [
    (
        "A snapshot near the\ndiagonal means the two models agree on severity; off-diagonal mass shows the\n"
        "re-ranking that happens when an instructor flips the toggle.",
        "A snapshot near the\ndiagonal means the two models agree on severity; off-diagonal mass shows where\n"
        "the deployed v2 model re-ranks the cohort relative to the v1 hand-set\nbaseline.",
    ),
    (
        "below shows, per snapshot, how its rank moves when the v1 toggle flips to v2\n"
        "(positive = student becomes _more_ visible / climbs the struggle ranking;\n"
        "negative = student drops down). The top-K overlap table answers the question\n"
        "an instructor would actually ask: \"if I flip the toggle, do I get a different\n"
        "top-20?\"",
        "below shows, per snapshot, how its rank moves between the v1 hand-set baseline\n"
        "and the deployed v2 model (positive = student becomes _more_ visible / climbs\n"
        "the struggle ranking under v2; negative = student drops down). The top-K\n"
        "overlap table answers the practical question: does the deployed v2 model\n"
        "surface a different top-20 than the v1 baseline would have?",
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
    print(f"reframed {applied} markdown cell(s)")
    # Report any unapplied replacements (so a future drift is visible)
    blob = NB.read_text(encoding="utf-8")
    for i, (find, _) in enumerate(REPLACEMENTS):
        marker = find.split("\n")[0][:40]
        # crude check: the *replaced* text's first distinctive token should be present
        print(f"  replacement {i}: source phrase {'GONE (applied)' if find not in blob else 'STILL PRESENT'}")
    return 0 if applied == len(REPLACEMENTS) else 1


if __name__ == "__main__":
    sys.exit(main())
