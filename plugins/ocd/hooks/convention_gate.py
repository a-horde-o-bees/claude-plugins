"""PreToolUse hook: surface applicable conventions on Read/Edit/Write.

Non-blocking — allows the tool call and injects convention paths via
additionalContext so the agent is systematically aware of applicable
conventions whenever it touches a file.

On Read: informational — "read conventions, awareness only"
On Edit/Write: directive — "read conventions and conform, refactor if needed"

Reads governance files directly from disk — no database dependency.
If convention files are missing or unreadable, allows silently.
"""

from __future__ import annotations

import json
import sys


def _build_context(file_path: str, conventions: list[str], is_mutation: bool) -> str:
    """Build the additionalContext message for the agent."""
    conv_list = "\n".join(f"  - {c}" for c in conventions)
    if is_mutation:
        return (
            f"Conventions apply to `{file_path}`:\n"
            f"{conv_list}\n\n"
            "Load any listed conventions not already in context. "
            "Conform this edit to all applicable conventions; "
            "refactor immediately if non-conformant."
        )
    return (
        f"Conventions govern `{file_path}`:\n"
        f"{conv_list}\n\n"
        "Load any listed conventions not already in context."
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

    try:
        from lib.governance import governance_match

        result = governance_match([file_path])
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
