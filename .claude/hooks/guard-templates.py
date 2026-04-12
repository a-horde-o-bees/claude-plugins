"""Block direct edits to deployed and propagated files.

Two categories of derived files should not be edited directly:
1. Deployed rules, conventions, patterns, and log templates — synced from plugin templates
2. Propagated files — copied from ocd to other plugins by pre-commit hook

Edit canonical sources instead:
- Rules/conventions/patterns: edit templates in plugins/ocd/{rules,conventions,patterns}/
- Log templates (_template.md): edit in plugins/ocd/logs/
- plugin/__init__.py, plugin/__main__.py: edit in plugins/ocd/plugin/

After editing templates, run /sync-templates to push changes to deployed
copies, or let the pre-commit hook do it automatically at commit time.
"""

import json
import re
import sys

GUARDED_PATTERNS = [
    re.compile(r"^\.claude/(rules|conventions|patterns)/"),    # deployed from templates
    re.compile(r"^\.claude/logs/[^/]+/_template\.md$"),  # deployed log templates
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
                    "permissionDecisionReason": f"Deployed or propagated file — edit the canonical source instead. Path: {path}",
                },
            }
            json.dump(result, sys.stdout)
            sys.exit(2)


if __name__ == "__main__":
    main()
