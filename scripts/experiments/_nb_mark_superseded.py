"""Signpost the v1-vs-v2 cells in notebooks/eval_main.ipynb after the v1-cut
decision (v2 is the premiere model; the methods bake-off is the §5.4
comparison). Markdown-only — no re-execution; figures untouched on disk.

Two tiers:
  * Cleanly v1-vs-v2 cells → full SUPERSEDED banner (not used in the report).
  * Entangled cells (v2 content mixed in) → a note that only the v1 portion
    is cut; the v2 content is retained for the report.

Idempotent: keyed on header text; re-running is a no-op once banners present.
Run from repo root:
    python scripts/experiments/_nb_mark_superseded.py
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
NB = REPO / "notebooks" / "eval_main.ipynb"

SUPERSEDED = (
    "> ⚠ SUPERSEDED 2026-05-27 — v1-vs-v2 comparison. v1 was cut from the "
    "evaluation (v2 is the premiere model; the model-class bake-off is the "
    "§5.4 comparison). Retained for provenance; NOT used in the report.\n\n"
)

# header-prefix → note to insert after the header line.
# Tier 1: cleanly v1-vs-v2 (full superseded banner).
FULL = {
    "## §5.4.3a — Per-snapshot score delta (v1 vs v2)": SUPERSEDED,
    "## §5.6.1 — Model disagreement matrix (v1 ↔ v2 bands on shared snapshots)": SUPERSEDED,
    "## §5.6.1a — Leaderboard rank shift v1 → v2": SUPERSEDED,
    "## §5.6.1b — Per-question difficulty rank shift v1 → v2": SUPERSEDED,
}
# Tier 2: entangled (v2 content kept; only v1 portion cut).
ENTANGLED = {
    "## §5.4.3 — Baseline check: v1 hand-set vs v2 trained weights (struggle)":
        "> ⓘ v1 cut from the report 2026-05-27 — present the **v2** trained weights only "
        "(v2-only chart or a table from `optimised_struggle_weights_v2.json`); the v1 bars "
        "are not shown.\n\n",
    "## §5.4.x — Predicted-vs-observed band scatter (v1 vs v2 side-by-side)":
        "> ⓘ v1 cut from the report 2026-05-27 — the report uses the **v2** panel only.\n\n",
    "## §5.4.8 — Confusion matrix: v1 / v2 predicted bands vs LLM bands":
        "> ⓘ v1 cut from the report 2026-05-27 — the report uses the **v2-vs-LLM** matrix only.\n\n",
    "## §5.4.9 — Negative findings: difficulty + improved model":
        "> ⓘ v1 cut from the report 2026-05-27 — the negative-weight findings are **v2 model "
        "behaviour** (kept); the v1 comparison bars are not shown.\n\n",
}


def already_noted(src: str) -> bool:
    return "SUPERSEDED 2026-05-27" in src or "v1 cut from the report 2026-05-27" in src


def main() -> int:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    applied = 0
    for cell in nb["cells"]:
        if cell["cell_type"] != "markdown":
            continue
        src = "".join(cell["source"])
        header = src.split("\n", 1)[0]
        note = FULL.get(header) or ENTANGLED.get(header)
        if not note or already_noted(src):
            continue
        # Insert the note right after the header line (+ its blank line).
        parts = src.split("\n", 1)
        rest = parts[1] if len(parts) > 1 else ""
        rest = rest.lstrip("\n")
        new = f"{parts[0]}\n\n{note}{rest}"
        cell["source"] = new.splitlines(keepends=True)
        applied += 1
    NB.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"signposted {applied} cell(s) ({len(FULL)} full + {len(ENTANGLED)} entangled targets)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
