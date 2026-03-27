"""Block direct edits to template files in plugins/.

Templates are distribution artifacts synced from deployed copies by
the commit workflow. Edit deployed copies in .claude/ instead.
"""

import json
import re
import sys

TEMPLATE_PATTERN = re.compile(r"^plugins/[^/]+/(rules|templates)/")


def main() -> None:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    cwd = data.get("cwd", "")

    path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if path.startswith(cwd):
        path = path[len(cwd) :].lstrip("/")

    if TEMPLATE_PATTERN.match(path):
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Template file — edit the deployed copy in .claude/ instead. Path: {path}",
            },
        }
        json.dump(result, sys.stdout)
        sys.exit(2)


if __name__ == "__main__":
    main()
