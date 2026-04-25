"""Block direct edits to deployed and propagated files.

Two categories of derived files should not be edited directly:
1. Deployed rules, conventions, and log templates — rectified from
   plugin templates at /checkpoint via the auto-init script
2. Propagated files — copied from canonical sources to other plugins
   by the pre-commit hook

Edit canonical sources instead:
- Project-wide rules: plugins/ocd/systems/rules/templates/
- System-scoped rules: plugins/ocd/systems/<system>/rules/
- Conventions: plugins/ocd/systems/conventions/templates/
- Log templates: plugins/ocd/systems/log/templates/<type>/
- Setup package (propagated to non-ocd plugins): plugins/ocd/systems/setup/
- Always-on primitives (propagated to every plugin's tools/): tools/ at project root

Deployed copies land on disk through the owning system's init() during
/checkpoint's auto-init step — not at commit time.
"""

import json
import re
import sys

GUARDED_PATTERNS = [
    re.compile(r"^\.claude/(rules|conventions)/"),    # deployed from templates
    re.compile(r"^logs/[^/]+/_(?:template|samples-template)\.md$"),  # deployed log templates
    re.compile(r"^plugins/(?!ocd/)[^/]+/systems/setup/[^/]+\.py$"),  # propagated setup package
    re.compile(r"^plugins/[^/]+/tools/(environment|errors)\.py$"),   # propagated always-on primitives
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
