#!/usr/bin/env python3
"""sync_literature.py

Keep Obsidian literature notes in sync with Zotero (`Report/references.bib`)
and the LaTeX thesis (`Report/**/*.tex`). Generates `Literature/coverage.md`.

Run from repo root after:
  - re-exporting `references.bib` from Better BibTeX
  - inserting `\\cite{}` calls in `.tex` files
  - adding/renaming literature notes

Idempotent. Non-destructive: only writes frontmatter, plus a one-time wrap of
the body of in-Zotero notes inside `%% Begin annotations %%` markers so the
Zotero Integration plugin's "Import & Replace" preserves the hand-written
summary on re-import.

No external dependencies — uses regex parsing only.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
BIB = REPO / "Report" / "references.bib"
TEX_DIR = REPO / "Report"
LIT_DIR = REPO / "docs" / "obsidian-vault" / "My Notes" / "Literature"
COVERAGE = LIT_DIR / "coverage.md"

CITEKEY_RX = re.compile(r"^@\w+\{\s*([^,\s]+)", re.MULTILINE)
CITE_RX = re.compile(r"\\cite[a-zA-Z]*\*?\{([^}]+)\}")
FM_RX = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)
CITED_IN_RX = re.compile(r"^Cited in:\s*(.+)$", re.MULTILINE)
WIKILINK_RX = re.compile(r"\[\[([^\]|]+?)(?:\|[^\]]+)?\]\]")
ANNOT_BEGIN = "%% Begin annotations %%"
ANNOT_END = "%% End annotations %%"


def parse_bib(bib_path: Path) -> set[str]:
    text = bib_path.read_text(encoding="utf-8", errors="replace")
    return set(CITEKEY_RX.findall(text))


def parse_tex(tex_root: Path) -> dict[str, list[str]]:
    """Return {citekey: ['relative/path.tex:line', ...]} de-duped by file:line."""
    raw: dict[str, list[str]] = defaultdict(list)
    for tex in sorted(tex_root.rglob("*.tex")):
        rel = tex.relative_to(REPO).as_posix()
        try:
            content = tex.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for i, line in enumerate(content.splitlines(), start=1):
            for m in CITE_RX.finditer(line):
                for raw_key in m.group(1).split(","):
                    key = raw_key.strip()
                    if key:
                        raw[key].append(f"{rel}:{i}")
    return {k: list(dict.fromkeys(v)) for k, v in raw.items()}


def parse_existing_note(text: str) -> tuple[dict[str, object], str]:
    """Parse YAML frontmatter and return (dict, body). Preserves only scalar keys."""
    m = FM_RX.match(text)
    if not m:
        return {}, text
    fm_text = m.group(1)
    body = text[m.end():]
    fm: dict[str, object] = {}
    current_list_key: str | None = None
    for raw in fm_text.splitlines():
        line = raw.rstrip()
        if not line:
            current_list_key = None
            continue
        if line.startswith("  - ") and current_list_key is not None:
            fm.setdefault(current_list_key, [])
            fm[current_list_key].append(line[4:].strip())  # type: ignore[union-attr]
            continue
        if line.endswith(":") and ":" in line:
            current_list_key = line[:-1].strip()
            fm[current_list_key] = []
            continue
        if ":" in line:
            k, _, v = line.partition(":")
            current_list_key = None
            fm[k.strip()] = v.strip()
    return fm, body


def parse_cited_in(body: str) -> list[str]:
    m = CITED_IN_RX.search(body)
    if not m:
        return []
    return [w.strip() for w in WIKILINK_RX.findall(m.group(1)) if w.strip()]


def render_frontmatter(fm: dict[str, object]) -> str:
    lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            if v:
                lines.append(f"{k}:")
                for item in v:
                    lines.append(f"  - {item}")
            else:
                lines.append(f"{k}: []")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def wrap_body_in_annotations(body: str) -> str:
    """One-time migration: place existing summary inside annotation markers.

    The Zotero Integration plugin preserves content between `%% Begin annotations %%`
    and `%% End annotations %%` on re-import. Putting the hand-written summary inside
    that block means future plugin imports keep it and append PDF highlights below.

    Idempotent: returns body unchanged if markers already present.
    """
    if ANNOT_BEGIN in body:
        return body
    stripped = body.strip("\n")
    if not stripped:
        return body
    lines = stripped.splitlines()
    if lines and lines[0].startswith("# "):
        h1 = lines[0]
        rest = "\n".join(lines[1:]).strip("\n")
    else:
        h1 = ""
        rest = stripped
    block = f"{ANNOT_BEGIN}\n## Summary\n\n{rest}\n{ANNOT_END}"
    if h1:
        return f"{h1}\n\n{block}\n"
    return block + "\n"


def sync_note(path: Path, in_zotero: set[str], tex_usage: dict[str, list[str]]) -> dict:
    citekey = path.stem
    text = path.read_text(encoding="utf-8")
    fm, body = parse_existing_note(text)

    cited_in_planned = parse_cited_in(body)
    cited_in_tex = tex_usage.get(citekey, [])
    is_zotero = citekey in in_zotero

    if cited_in_tex:
        status = "active"
    elif cited_in_planned:
        status = "planned"
    else:
        status = "stale"

    new_fm: dict[str, object] = dict(fm)
    new_fm["citekey"] = citekey
    new_fm["status"] = status
    new_fm["in_zotero"] = is_zotero
    new_fm["cited_in_tex"] = cited_in_tex
    new_fm["cited_in_planned"] = cited_in_planned
    new_fm["last_synced"] = str(date.today())

    new_body = body
    if status == "active" and ANNOT_BEGIN not in body:
        new_body = wrap_body_in_annotations(body)

    new_text = render_frontmatter(new_fm) + new_body
    if not new_text.endswith("\n"):
        new_text += "\n"

    changed = new_text != text
    if changed:
        path.write_text(new_text, encoding="utf-8")
    return {
        "changed": changed,
        "citekey": citekey,
        "status": status,
        "is_zotero": is_zotero,
        "cited_in_tex": cited_in_tex,
        "cited_in_planned": cited_in_planned,
    }


def _format_locations(locs: list[str], max_n: int = 4) -> str:
    if not locs:
        return "—"
    if len(locs) <= max_n:
        return ", ".join(f"`{loc}`" for loc in locs)
    head = ", ".join(f"`{loc}`" for loc in locs[:max_n])
    return f"{head}, …(+{len(locs) - max_n})"


def _format_planned(planned: list[str]) -> str:
    if not planned:
        return "—"
    return " · ".join(f"[[{p}]]" for p in planned)


def render_coverage(records: list[dict], in_zotero: set[str], tex_usage: dict[str, list[str]]) -> str:
    active = sorted([r for r in records if r["status"] == "active"], key=lambda r: r["citekey"])
    planned = sorted([r for r in records if r["status"] == "planned"], key=lambda r: r["citekey"])
    stale = sorted([r for r in records if r["status"] == "stale"], key=lambda r: r["citekey"])

    note_keys = {r["citekey"] for r in records}
    cited_keys = set(tex_usage.keys())
    unused_bib = sorted(in_zotero - cited_keys)
    broken_cite = sorted(cited_keys - in_zotero)
    no_note_for_bib = sorted(in_zotero - note_keys)

    chapter_map: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        for ch in r["cited_in_planned"]:
            chapter_map[ch].append(r)

    today = str(date.today())

    out: list[str] = []
    out.append("# Citation Coverage Index")
    out.append("")
    out.append("> [!info] Auto-generated by `scripts/sync_literature.py` — do not hand-edit. Re-run after changing `references.bib`, `\\cite{}` calls, or literature notes.")
    out.append("")
    out.append(f"**Last synced:** {today}")
    out.append("")
    out.append("## Summary")
    out.append("")
    out.append(f"- Active (cited in thesis): **{len(active)}**")
    out.append(f"- Planned (note + plan, no `\\cite{{}}` yet): **{len(planned)}**")
    out.append(f"- Stale (note but no plan, no cite): **{len(stale)}**")
    out.append(f"- In Zotero but not cited in thesis: **{len(unused_bib)}**")
    out.append(f"- Cited in thesis but missing bib entry (broken): **{len(broken_cite)}**")
    out.append(f"- In Zotero but no literature note: **{len(no_note_for_bib)}**")
    out.append("")

    out.append("## Active — cited in thesis")
    out.append("")
    out.append("| Citekey | Where cited (`file:line`) | Planned for |")
    out.append("|---|---|---|")
    for r in active:
        link = f"[[{r['citekey']}]]"
        out.append(f"| {link} | {_format_locations(r['cited_in_tex'])} | {_format_planned(r['cited_in_planned'])} |")
    if not active:
        out.append("| _none_ | | |")
    out.append("")

    out.append("## Planned — note + intent, no `\\cite{}` yet")
    out.append("")
    out.append("| Citekey | Planned for | In Zotero |")
    out.append("|---|---|---|")
    for r in planned:
        link = f"[[{r['citekey']}]]"
        zot = "✅" if r["is_zotero"] else "❌"
        out.append(f"| {link} | {_format_planned(r['cited_in_planned'])} | {zot} |")
    if not planned:
        out.append("| _none_ | | |")
    out.append("")

    out.append("## Stale — note but no plan, no cite")
    out.append("")
    if stale:
        for r in stale:
            out.append(f"- [[{r['citekey']}]]")
    else:
        out.append("_None — every note has either a `Cited in:` line or a `\\cite{}` call._")
    out.append("")

    out.append("## Issues")
    out.append("")
    out.append(f"### In Zotero but not cited in thesis ({len(unused_bib)})")
    out.append("")
    if unused_bib:
        for k in unused_bib:
            out.append(f"- `{k}`")
    else:
        out.append("_None — every bib entry is cited at least once._")
    out.append("")
    out.append(f"### Cited in thesis but missing bib entry — broken `\\cite{{}}` ({len(broken_cite)})")
    out.append("")
    if broken_cite:
        for k in broken_cite:
            locs = _format_locations(tex_usage.get(k, []))
            out.append(f"- `{k}` — {locs}")
    else:
        out.append("_None — every `\\cite{}` resolves to a bib entry._")
    out.append("")
    out.append(f"### In Zotero but no literature note ({len(no_note_for_bib)})")
    out.append("")
    if no_note_for_bib:
        for k in no_note_for_bib:
            out.append(f"- `{k}`")
    else:
        out.append("_None — every bib entry has a literature note._")
    out.append("")

    out.append("## By chapter / topic")
    out.append("")
    out.append("Citations grouped by the `Cited in:` line in each literature note.")
    out.append("")
    for chapter in sorted(chapter_map.keys()):
        entries = sorted(chapter_map[chapter], key=lambda r: r["citekey"])
        out.append(f"### [[{chapter}]] ({len(entries)})")
        out.append("")
        for r in entries:
            badge = {"active": "✅", "planned": "🟡", "stale": "⚪"}[r["status"]]
            out.append(f"- {badge} [[{r['citekey']}]]")
        out.append("")

    out.append("---")
    out.append(f"_Regenerated {today} by `scripts/sync_literature.py`._")
    return "\n".join(out) + "\n"


def main() -> int:
    if not BIB.exists():
        print(f"ERROR: {BIB} not found", file=sys.stderr)
        return 1
    if not LIT_DIR.exists():
        print(f"ERROR: {LIT_DIR} not found", file=sys.stderr)
        return 1

    in_zotero = parse_bib(BIB)
    tex_usage = parse_tex(TEX_DIR)
    print(f"Bib entries:        {len(in_zotero)}")
    print(f"Cite calls:         {sum(len(v) for v in tex_usage.values())} across {len(tex_usage)} unique keys")

    notes = sorted(
        p for p in LIT_DIR.glob("*.md")
        if p.stem not in ("index", "coverage") and not p.stem.startswith("_")
    )
    print(f"Literature notes:   {len(notes)}")

    records = []
    changed = 0
    wrapped = 0
    for note in notes:
        before = note.read_text(encoding="utf-8")
        rec = sync_note(note, in_zotero, tex_usage)
        records.append(rec)
        if rec["changed"]:
            changed += 1
            after = note.read_text(encoding="utf-8")
            if ANNOT_BEGIN in after and ANNOT_BEGIN not in before:
                wrapped += 1

    n_active = sum(1 for r in records if r["status"] == "active")
    n_planned = sum(1 for r in records if r["status"] == "planned")
    n_stale = sum(1 for r in records if r["status"] == "stale")
    print(f"Status:             {n_active} active · {n_planned} planned · {n_stale} stale")
    print(f"Notes updated:      {changed}")
    print(f"Annotation-wrapped: {wrapped} (one-time migration)")

    coverage = render_coverage(records, in_zotero, tex_usage)
    if not COVERAGE.exists() or COVERAGE.read_text(encoding="utf-8") != coverage:
        COVERAGE.write_text(coverage, encoding="utf-8")
        print(f"Wrote:              {COVERAGE.relative_to(REPO).as_posix()}")
    else:
        print(f"Unchanged:          {COVERAGE.relative_to(REPO).as_posix()}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
