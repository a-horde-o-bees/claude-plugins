"""Block direct edits to deployed and propagated files.

Two categories of derived files should not be edited directly:
1. Deployed rules and log templates under `.claude/` — currently
   manually deployed (see plans/architecture-refactor.md). Conventions
   deployment is dormant; convention_gate hook removed.
2. Propagated files — copies of canonicals under project-root `shared/`
   bundled into each skill's matching subfolder by the pre-commit hook.
   `shared/scripts/X.py` lands in `<skill>/scripts/X.py`;
   `shared/_dependencies/X.md` lands in `<skill>/_dependencies/X.md`.
   The underscore-prefix folder marks install-source-only storage per
   markdown-dependency-resolution.

Edit canonical sources instead:
- Rule canonicals: shared/_dependencies/<name>.md
- Shared scripts (_environment.py, _deps.py): shared/scripts/<name>.py
- Conventions: plugins/ocd-old/systems/conventions/templates/ (source-only;
  no current deployment target)
- Log templates: plugins/ocd-old/systems/log/templates/<type>/
"""

import json
import re
import sys

GUARDED_PATTERNS = [
    re.compile(r"^\.claude/(rules|conventions)/"),    # deployed from templates
    re.compile(r"^logs/[^/]+/_(?:template|samples-template)\.md$"),  # deployed log templates
    re.compile(r"^plugins/[^/]+/skills/[^/]+/scripts/(_environment|_deps)\.py$"),  # propagated python canonicals
    re.compile(r"^plugins/[^/]+/skills/[^/]+/_dependencies/[^/]+\.md$"),  # propagated rule canonicals (seed storage)
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
