"""Block direct edits to deployed and propagated files.

Two categories of derived files should not be edited directly:
1. Deployed rules, conventions, and log templates — managed by each
   system's setup handler
2. Propagated files — copies of canonicals under project-root `shared/`
   bundled into each skill's matching subfolder by the pre-commit hook.
   `shared/scripts/X.py` lands in `<skill>/scripts/X.py`;
   `shared/dependencies/X.md` lands in `<skill>/dependencies/X.md`.

Edit canonical sources instead:
- Project-wide rules: plugins/ocd-old/systems/rules/templates/
- Conventions: plugins/ocd-old/systems/conventions/templates/
- Log templates: plugins/ocd-old/systems/log/templates/<type>/
- Shared canonicals (propagated to every skill's matching subfolder that has its own copy): shared/ at project root

Deployed copies land on disk through the owning system's setup install,
not at commit time.
"""

import json
import re
import sys

GUARDED_PATTERNS = [
    re.compile(r"^\.claude/(rules|conventions)/"),    # deployed from templates
    re.compile(r"^logs/[^/]+/_(?:template|samples-template)\.md$"),  # deployed log templates
    re.compile(r"^plugins/[^/]+/skills/[^/]+/scripts/(_environment|_deps)\.py$"),  # propagated python canonicals
    re.compile(r"^plugins/[^/]+/skills/[^/]+/dependencies/(process-flow-notation|file-decomposition|dependency-resolution)\.md$"),  # propagated rule canonicals
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
