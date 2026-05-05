import json

cases = {
    "match": {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": r"c:\Users\Bakri\OneDrive - Loughborough University\Masters Year\Thesis\Dashboard v3\Report\main-sections\requirements-specification.tex"
        },
    },
    "skip": {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": r"c:\Users\Bakri\OneDrive - Loughborough University\Masters Year\Thesis\Dashboard v3\code\app.py"
        },
    },
}
for name, payload in cases.items():
    with open(f"hook_test_{name}.json", "w") as f:
        json.dump(payload, f)
    print(name, "->", repr(payload["tool_input"]["file_path"]))
