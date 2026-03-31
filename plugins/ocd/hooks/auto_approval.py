"""PreToolUse hook: enforce settings.json rules with inline guidance.

Two layers, fixed evaluation order:

1. Hardcoded blocks — CLAUDE.md rules that don't stick as prose. Block with
   inline redirection so the agent self-corrects without user intervention.

2. Dynamic settings.json enforcement — reads global (~/.claude/settings.json)
   and project (.claude/settings.json), merges allow/deny lists and allowed
   directories. Approves operations that settings would allow.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


# ===========================================================================
# Output helpers
# ===========================================================================


def approve() -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        },
        sys.stdout,
    )


def block(reason: str) -> None:
    json.dump({"decision": "block", "reason": reason}, sys.stdout)


# ===========================================================================
# Settings loader
# ===========================================================================


def load_settings_file(path: Path) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def merge_settings(global_settings: dict, project_settings: dict) -> dict:
    """Merge global and project settings. Union of allow/deny lists and
    additionalDirectories. Project values appear after global values."""
    global_perms = global_settings.get("permissions", {})
    project_perms = project_settings.get("permissions", {})

    merged_allow = list(global_perms.get("allow", []))
    for rule in project_perms.get("allow", []):
        if rule not in merged_allow:
            merged_allow.append(rule)

    merged_deny = list(global_perms.get("deny", []))
    for rule in project_perms.get("deny", []):
        if rule not in merged_deny:
            merged_deny.append(rule)

    merged_dirs = list(global_perms.get("additionalDirectories", []))
    for d in project_perms.get("additionalDirectories", []):
        if d not in merged_dirs:
            merged_dirs.append(d)

    return {
        "permissions": {
            "allow": merged_allow,
            "deny": merged_deny,
            "additionalDirectories": merged_dirs,
        }
    }


def load_merged_settings(project_dir: Path) -> dict:
    global_path = Path.home() / ".claude" / "settings.json"
    project_path = project_dir / ".claude" / "settings.json"
    return merge_settings(
        load_settings_file(global_path),
        load_settings_file(project_path),
    )


def get_project_dir() -> Path:
    import os
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())).resolve()


# ===========================================================================
# Path and rule matching
# ===========================================================================


def resolve_path(file_path: str, project_dir: Path) -> Path:
    p = Path(file_path)
    if not p.is_absolute():
        return (project_dir / p).resolve()
    return p.resolve()


def is_within_directory(abs_path: Path, directory: Path) -> bool:
    resolved = directory.resolve()
    return abs_path == resolved or resolved in abs_path.parents


def get_allowed_directories(project_dir: Path, settings: dict) -> set[Path]:
    """Build set of allowed directories from merged settings."""
    dirs = {project_dir}
    for d in settings.get("permissions", {}).get("additionalDirectories", []):
        expanded = Path(d).expanduser()
        if not expanded.is_absolute():
            expanded = (project_dir / expanded).resolve()
        else:
            expanded = expanded.resolve()
        dirs.add(expanded)
    return dirs


def is_within_allowed_dirs(abs_path: Path, project_dir: Path, settings: dict) -> bool:
    for directory in get_allowed_directories(project_dir, settings):
        if is_within_directory(abs_path, directory):
            return True
    return False


def is_tool_in_list(tool_name: str, rule_list: list) -> bool:
    """Check if a tool name appears as a blanket entry in a rule list."""
    return tool_name in rule_list


def match_bash_pattern(command: str, pattern_str: str) -> bool:
    """Match a command against a Bash(pattern) rule.

    Patterns:
        Bash(verb:*)     — command starts with verb
        Bash(verb *)     — command starts with "verb "
        Bash(path/*)     — command starts with path/
        Bash(verb)       — exact match on first word
        Bash(.claude/*)  — command starts with .claude/
    """
    inner = pattern_str
    if inner.endswith(":*"):
        prefix = inner[:-2]
        return command == prefix or command.startswith(prefix + " ")
    if inner.endswith("*"):
        prefix = inner[:-1]
        return command.startswith(prefix)
    return command.split()[0] == inner if command else False


def is_bash_allowed(command: str, settings: dict) -> bool:
    """Check if a Bash command matches any allow pattern in settings."""
    allow_list = settings.get("permissions", {}).get("allow", [])
    for rule in allow_list:
        if not isinstance(rule, str):
            continue
        if not rule.startswith("Bash(") or not rule.endswith(")"):
            continue
        inner = rule[5:-1]
        if match_bash_pattern(command, inner):
            return True
    return False


def is_bash_denied(command: str, settings: dict) -> bool:
    """Check if a Bash command matches any deny pattern in settings."""
    deny_list = settings.get("permissions", {}).get("deny", [])
    for rule in deny_list:
        if not isinstance(rule, str):
            continue
        if not rule.startswith("Bash(") or not rule.endswith(")"):
            continue
        inner = rule[5:-1]
        if match_bash_pattern(command, inner):
            return True
    return False


def is_path_denied(file_path: str, tool_name: str, settings: dict) -> bool:
    """Check if a file path matches any deny pattern for a tool."""
    deny_list = settings.get("permissions", {}).get("deny", [])
    for rule in deny_list:
        if not isinstance(rule, str):
            continue
        # Match patterns like Edit(path) or Write(path)
        for prefix in (tool_name + "(", ):
            if rule.startswith(prefix) and rule.endswith(")"):
                pattern = rule[len(prefix):-1]
                if _glob_match(file_path, pattern):
                    return True
        # Match bare tool name in deny list
        if rule == tool_name:
            return True
    return False


def _glob_match(path: str, pattern: str) -> bool:
    """Minimal glob match for deny rules — supports ** and * wildcards."""
    regex = re.escape(pattern)
    regex = regex.replace(r"\*\*", "DOUBLESTAR")
    regex = regex.replace(r"\*", "[^/]*")
    regex = regex.replace("DOUBLESTAR", ".*")
    regex = "^" + regex + "$"
    return bool(re.match(regex, path))


# ===========================================================================
# Layer 1 — Hardcoded blocks with inline redirection
# ===========================================================================


def split_compound_command(command: str) -> list[str] | None:
    """Split command on &&, ||, ;, | outside quotes.

    Returns list of individual commands if separators found, None otherwise.
    Tracks quote state character by character to avoid splitting inside strings.
    """
    parts = []
    current: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    i = 0
    while i < len(command):
        c = command[i]
        if escaped:
            current.append(c)
            escaped = False
            i += 1
            continue
        if c == "\\" and in_double:
            current.append(c)
            escaped = True
            i += 1
            continue
        if c == "'" and not in_double:
            in_single = not in_single
            current.append(c)
            i += 1
            continue
        if c == '"' and not in_single:
            in_double = not in_double
            current.append(c)
            i += 1
            continue
        if not in_single and not in_double:
            if command[i:i + 2] in ("&&", "||"):
                parts.append("".join(current).strip())
                current = []
                i += 2
                continue
            if c == ";":
                parts.append("".join(current).strip())
                current = []
                i += 1
                continue
            if c == "|" and command[i:i + 2] != "||":
                parts.append("".join(current).strip())
                current = []
                i += 1
                continue
        current.append(c)
        i += 1
    parts.append("".join(current).strip())
    parts = [p for p in parts if p]
    return parts if len(parts) > 1 else None


def check_hardcoded_blocks(command: str) -> str | None:
    """Return a blocking reason if command violates a hardcoded rule."""
    # cd / pushd / popd — directory changes break approval pipeline
    if re.match(r"^(cd|pushd|popd)\b", command):
        return (
            "Directory changes (cd/pushd/popd) are not allowed — working "
            "directory must remain project root for the entire session. "
            "Use absolute paths from project root instead. For git "
            "operations in other directories, use git -C <path>."
        )
    # cat — use Read tool instead
    if re.match(r"^cat\b", command):
        return (
            "Use the Read tool instead of cat. Read supports offset and "
            "limit parameters for partial file reads and handles errors "
            "natively — no redirect or exit-code wrapper needed."
        )
    return None


# ===========================================================================
# Layer 2 — Dynamic settings.json enforcement
# ===========================================================================


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


def check_bash_dynamic(command: str, settings: dict) -> None:
    # Deny rules take precedence
    if is_bash_denied(command, settings):
        return

    # Check command matches an allow pattern
    if is_bash_allowed(command, settings):
        approve()


# ===========================================================================
# Dispatch
# ===========================================================================


def main() -> None:
    hook_input = json.load(sys.stdin)
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    project_dir = get_project_dir()

    if tool_name == "Bash":
        command = tool_input.get("command", "").strip()
        if not command:
            return

        # Split compound commands and check each part independently
        parts = split_compound_command(command)
        if parts is not None:
            settings = load_merged_settings(project_dir)
            for part in parts:
                violation = check_hardcoded_blocks(part)
                if violation:
                    block(violation)
                    return
                if is_bash_denied(part, settings):
                    return
                if not is_bash_allowed(part, settings):
                    return
            approve()
            return

        # Single command — standard two-layer check
        violation = check_hardcoded_blocks(command)
        if violation:
            block(violation)
            return

        settings = load_merged_settings(project_dir)
        check_bash_dynamic(command, settings)
        return

    if tool_name in ("Edit", "Write"):
        settings = load_merged_settings(project_dir)
        check_edit_write(tool_name, tool_input, project_dir, settings)
        return


if __name__ == "__main__":
    main()
