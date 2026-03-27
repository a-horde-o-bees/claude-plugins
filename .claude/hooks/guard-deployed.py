"""Block edits to deployed files in .claude/.

Deployed rules and conventions are copies managed by plugin init.
Edit templates in plugins/ instead.
"""

import json
import sys

GUARDED_PREFIXES = (
    ".claude/rules/",
    ".claude/ocd/",
    ".claude/blueprint/",
)


def main() -> None:
    data = json.load(sys.stdin)
    tool_input = data.get("tool_input", {})
    cwd = data.get("cwd", "")

    path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if path.startswith(cwd):
        path = path[len(cwd):].lstrip("/")

    if any(path.startswith(p) for p in GUARDED_PREFIXES):
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Deployed file — edit the template in plugins/ instead. Path: {path}",
            },
        }
        json.dump(result, sys.stdout)
        sys.exit(2)


if __name__ == "__main__":
    main()
