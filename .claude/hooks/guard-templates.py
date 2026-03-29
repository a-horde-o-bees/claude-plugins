"""Block direct edits to synced and propagated files in plugins/.

Two sync mechanisms produce these files:
1. OCD rules and convention templates — synced from .claude/ deployed copies
2. Propagated files — copied from ocd to other plugins by pre-commit hook

Edit canonical sources instead:
- Rules/conventions: edit deployed copies in .claude/
- plugin/__init__.py, plugin/__main__.py: edit in plugins/ocd/plugin/
"""

import json
import re
import sys

GUARDED_PATTERNS = [
    re.compile(r"^plugins/ocd/(rules|templates)/"),          # synced from .claude/
    re.compile(r"^plugins/(?!ocd/)[^/]+/rules/ocd-"),        # propagated rules
    re.compile(r"^plugins/(?!ocd/)[^/]+/plugin/(__init__|__main__)\.py$"),  # propagated plugin framework
]


def main() -> None:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    cwd = data.get("cwd", "")

    path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if path.startswith(cwd):
        path = path[len(cwd) :].lstrip("/")

    for pattern in GUARDED_PATTERNS:
        if pattern.match(path):
            result = {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": f"Synced or propagated file — edit the canonical source instead. Path: {path}",
                },
            }
            json.dump(result, sys.stdout)
            sys.exit(2)


if __name__ == "__main__":
    main()
