"""Hardcoded block rules and Edit/Write path checking."""

from __future__ import annotations

import re
from pathlib import Path

from ._matching import _strip_env_assignments, is_path_denied, is_tool_in_list
from ._output import approve
from ._paths import is_within_allowed_dirs, resolve_path


def check_hardcoded_blocks(command: str) -> str | None:
    """Return a blocking reason if command violates a hardcoded rule."""
    stripped = _strip_env_assignments(command)
    # cd / pushd / popd — directory changes break approval pipeline
    if re.match(r"^(cd|pushd|popd)\b", stripped):
        return (
            "Directory changes (cd/pushd/popd) are not allowed — working "
            "directory must remain project root for the entire session. "
            "Use absolute paths from project root instead. For git "
            "operations in other directories, use git -C <path>."
        )
    # cat — use Read tool instead
    if re.match(r"^cat\b", stripped):
        return (
            "Use the Read tool instead of cat. Read supports offset and "
            "limit parameters for partial file reads and handles errors "
            "natively — no redirect or exit-code wrapper needed."
        )
    return None


def check_edit_write(tool_name: str, tool_input: dict, project_dir: Path, settings: dict) -> None:
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    abs_path = resolve_path(file_path, project_dir)

    # Deny rules take precedence — check both original and resolved paths as strings
    if is_path_denied(file_path, tool_name, settings):
        return
    if is_path_denied(str(abs_path), tool_name, settings):
        return

    # Check tool is in allow list and path is within allowed directories
    if is_tool_in_list(tool_name, settings.get("permissions", {}).get("allow", [])):
        if is_within_allowed_dirs(abs_path, project_dir, settings):
            approve()
