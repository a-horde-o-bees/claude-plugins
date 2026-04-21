"""Block direct edits to deployed and propagated files.

Two categories of derived files should not be edited directly:
1. Deployed rules, conventions, patterns, and log templates — rectified
   from plugin templates at /checkpoint via the auto-init script
2. Propagated files — copied from ocd to other plugins by pre-commit hook

Edit canonical sources instead:
- Project-wide rules: plugins/ocd/systems/rules/templates/
- System-scoped rules: plugins/ocd/systems/<system>/rules/
- Conventions: plugins/ocd/systems/conventions/templates/
- Patterns: plugins/ocd/systems/patterns/templates/
- Log templates: plugins/ocd/systems/log/templates/<type>/
- Framework files (propagated to non-ocd plugins): plugins/ocd/systems/framework/

Deployed copies land on disk through the owning system's init() during
/checkpoint's auto-init step — not at commit time.
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
