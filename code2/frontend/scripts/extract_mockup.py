"""Decompress the mockup bundle into plain-text source files.

The mockup at C:\\Users\\Bakri\\Downloads\\Alternative Dashboard _standalone_.html
uses a custom single-file bundler:

  - <script type="__bundler/manifest">{ "<uuid>": {data: base64, compressed: bool}, ... }</script>
  - <script src="<uuid>">...</script> tags are rewritten at runtime to blob URLs
    backed by the decoded manifest entries.
  - 'compressed' entries are gzip-compressed before base64 encoding.

This script reproduces the decode path server-side and writes each asset as a
file under mockup-extracted/ with a sensible extension guessed from content.

Run:
    python scripts/extract_mockup.py
"""
from __future__ import annotations

import base64
import gzip
import json
import re
import sys
from pathlib import Path


MOCKUP_HTML = Path(r"C:\Users\Bakri\Downloads\Alternative Dashboard _standalone_.html")
OUT_DIR = Path(__file__).resolve().parent.parent / "mockup-extracted"


def _guess_ext(body: bytes, hint: str | None = None) -> str:
    head = body[:256].decode("utf-8", errors="replace").lstrip()
    if head.startswith("<!"):
        return ".html"
    if head.startswith("{") or head.startswith("["):
        return ".json"
    if head.startswith("/*") or head.startswith("@"):
        return ".css"
    if head.startswith("<svg"):
        return ".svg"
    if "import React" in head or "React.createElement" in head or "window.T" in head:
        return ".jsx"
    if "function " in head or "const " in head or "var " in head or "=>" in head:
        return ".js"
    return ".txt"


def main() -> int:
    raw = MOCKUP_HTML.read_text(encoding="utf-8")
    m = re.search(r'<script type="__bundler/manifest">(.*?)</script>', raw, re.DOTALL)
    if not m:
        print("ERROR: manifest script tag not found", file=sys.stderr)
        return 1
    manifest = json.loads(m.group(1))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index: list[dict] = []

    for uuid, entry in manifest.items():
        b64 = entry["data"]
        compressed = entry.get("compressed", False)
        body = base64.b64decode(b64)
        if compressed:
            body = gzip.decompress(body)
        ext = _guess_ext(body)
        out = OUT_DIR / f"{uuid}{ext}"
        out.write_bytes(body)
        index.append({"uuid": uuid, "ext": ext, "size": len(body), "compressed": compressed})

    # Sort index by size descending so the biggest (component) files are easy to find.
    index.sort(key=lambda r: -r["size"])
    (OUT_DIR / "INDEX.json").write_text(json.dumps(index, indent=2), encoding="utf-8")

    print(f"Wrote {len(index)} assets to {OUT_DIR}")
    for r in index[:15]:
        print(f"  {r['ext']:6s} {r['size']:>10,}  {r['uuid']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
