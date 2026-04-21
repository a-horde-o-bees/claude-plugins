"""CLI entry point for the auto_approval PreToolUse hook."""

from __future__ import annotations

import json
import sys

from . import *  # noqa: F403


def _dispatch() -> None:
    hook_input = json.load(sys.stdin)
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    project_dir = get_project_dir()

    if tool_name == "Bash":
        command = tool_input.get("command", "").strip()
        if not command:
            return

        leaves = expand_command(command)
        if not leaves:
            return

        # Layer 1 — hardcoded blocks fire first so they return a block
        # message regardless of allow-list state.
        for leaf in leaves:
            violation = check_hardcoded_blocks(leaf)
            if violation:
                block(violation)
                return

        # Layer 2 — settings.json deny then allow. Every leaf must pass;
        # a single denied or unapproved leaf drops the whole command.
        settings = load_merged_settings(project_dir)
        for leaf in leaves:
            if is_bash_denied(leaf, settings):
                return
            if not is_bash_allowed(leaf, settings):
                return
        approve()
        return

    if tool_name in ("Edit", "Write"):
        settings = load_merged_settings(project_dir)
        check_edit_write(tool_name, tool_input, project_dir, settings)
        return


def main() -> None:
    """Fail-open wrapper. Any unhandled exception surfaces a single stderr
    line and exits 0 — Claude Code's fallback (prompt user) takes over. The
    hook's job is auto-approval; it must never block a tool call by crashing.
    """
    try:
        _dispatch()
    except Exception as exc:
        sys.stderr.write(f"auto_approval hook error — {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    main()
