"""PreToolUse hook: surface applicable conventions on Read/Edit/Write.

Non-blocking — allows the tool call and injects convention paths via
additionalContext so the agent is systematically aware of applicable
conventions whenever it touches a file.

On Read: informational — "these conventions govern this file"
On Edit/Write: directive — "read conventions and conform, refactor if needed"

Runs governance_match against the navigator database. If the database
doesn't exist (not initialized), allows silently.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _get_db_path() -> Path | None:
    """Resolve navigator database path."""
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    db_path = project_dir / ".claude" / "ocd" / "navigator" / "navigator.db"
    return db_path if db_path.exists() else None


def _build_context(file_path: str, conventions: list[str], is_mutation: bool) -> str:
    """Build the additionalContext message for the agent."""
    conv_list = "\n".join(f"  - {c}" for c in conventions)
    if is_mutation:
        return (
            f"Conventions apply to `{file_path}`:\n"
            f"{conv_list}\n\n"
            "Read each convention you haven't already loaded in this session. "
            "If this edit doesn't conform to the applicable conventions, "
            "immediately refactor to fix conformance before proceeding to other work."
        )
    return (
        f"Conventions govern `{file_path}`:\n"
        f"{conv_list}"
    )


def main() -> None:
    hook_input = json.load(sys.stdin)
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})

    if tool_name not in ("Read", "Edit", "Write"):
        return

    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    db_path = _get_db_path()
    if db_path is None:
        return

    from skills.navigator._governance import governance_match

    try:
        result = governance_match(str(db_path), [file_path])
    except Exception:
        return

    conventions = result.get("conventions", [])
    if not conventions:
        return

    is_mutation = tool_name in ("Edit", "Write")

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
                "additionalContext": _build_context(file_path, conventions, is_mutation),
            }
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
