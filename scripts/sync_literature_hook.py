"""PostToolUse hook: re-run sync_literature.py when a citation-relevant file is edited.

Reads the Claude Code hook JSON from stdin, extracts the edited file path, and only
runs sync_literature.py if the path is one of:
- Report/references.bib (the bib file)
- Report/main-sections/*.tex (any chapter source)
- docs/obsidian-vault/My Notes/Literature/*.md (any literature note)

Silent on all errors so a hook failure never breaks the user's session.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

PATTERNS = [
    re.compile(r"Report/references\.bib$"),
    re.compile(r"Report/main-sections/[^/]+\.tex$"),
    re.compile(r"My Notes/Literature/[^/]+\.md$"),
]


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0

    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return 0

    normalised = file_path.replace("\\", "/")
    if not any(p.search(normalised) for p in PATTERNS):
        return 0

    project_root = Path(__file__).resolve().parent.parent
    try:
        subprocess.run(
            [sys.executable, "scripts/sync_literature.py"],
            cwd=project_root,
            check=False,
            timeout=60,
            capture_output=True,
        )
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
