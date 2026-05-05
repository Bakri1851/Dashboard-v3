import json
import re
import sys

PATTERNS = [
    re.compile(r"Report/references\.bib$"),
    re.compile(r"Report/main-sections/[^/]+\.tex$"),
    re.compile(r"My Notes/Literature/[^/]+\.md$"),
]

data = json.load(sys.stdin)
fp = (data.get("tool_input") or {}).get("file_path", "")
print("raw       :", repr(fp))
norm = fp.replace("\\", "/")
print("normalised:", repr(norm))
for p in PATTERNS:
    print(f"pattern {p.pattern!r:50} -> {bool(p.search(norm))}")
