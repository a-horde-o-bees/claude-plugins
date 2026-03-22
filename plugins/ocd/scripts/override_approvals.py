"""PreToolUse hook: enforce settings.json rules with inline guidance.

Two layers, fixed evaluation order:

1. Hardcoded blocks — CLAUDE.md rules that don't stick as prose. Block with
   inline redirection so the agent self-corrects without user intervention.

2. Dynamic settings.json enforcement — reads global (~/.claude/settings.json)
   and project (.claude/settings.json), merges allow/deny lists and allowed
   directories. Approves operations that settings would allow.
"""

import json
import os
import re
import sys


# ===========================================================================
# Output helpers
# ===========================================================================


def approve():
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "allow",
            }
        },
        sys.stdout,
    )


def block(reason):
    json.dump({"decision": "block", "reason": reason}, sys.stdout)


# ===========================================================================
# Settings loader
# ===========================================================================


def load_settings_file(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def merge_settings(global_settings, project_settings):
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


def load_merged_settings(project_dir):
    global_path = os.path.expanduser("~/.claude/settings.json")
    project_path = os.path.join(project_dir, ".claude", "settings.json")
    return merge_settings(
        load_settings_file(global_path),
        load_settings_file(project_path),
    )


def get_project_dir():
    return os.path.realpath(
        os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
    )


# ===========================================================================
# Path and rule matching
# ===========================================================================


def resolve_path(file_path, project_dir):
    if not os.path.isabs(file_path):
        return os.path.realpath(os.path.join(project_dir, file_path))
    return os.path.realpath(file_path)


def is_within_directory(abs_path, directory):
    directory = os.path.realpath(directory)
    return abs_path.startswith(directory + os.sep) or abs_path == directory


def get_allowed_directories(project_dir, settings):
    """Build set of allowed directories from merged settings."""
    dirs = {project_dir}
    for d in settings.get("permissions", {}).get("additionalDirectories", []):
        expanded = os.path.expanduser(d)
        if not os.path.isabs(expanded):
            expanded = os.path.realpath(os.path.join(project_dir, expanded))
        else:
            expanded = os.path.realpath(expanded)
        dirs.add(expanded)
    return dirs


def is_within_allowed_dirs(abs_path, project_dir, settings):
    for directory in get_allowed_directories(project_dir, settings):
        if is_within_directory(abs_path, directory):
            return True
    return False


def is_tool_in_list(tool_name, rule_list):
    """Check if a tool name appears as a blanket entry in a rule list."""
    return tool_name in rule_list


def match_bash_pattern(command, pattern_str):
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


def is_bash_allowed(command, settings):
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


def is_bash_denied(command, settings):
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


def is_path_denied(file_path, tool_name, settings):
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


def _glob_match(path, pattern):
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


def strip_quoted_strings(command):
    """Remove single- and double-quoted strings for operator detection."""
    result = re.sub(r"'[^']*'", "", command)
    result = re.sub(r'"(?:[^"\\]|\\.)*"', "", result)
    return result


def check_hardcoded_blocks(command):
    """Return a blocking reason if command violates a hardcoded rule."""
    # cd / pushd / popd — directory changes break approval pipeline
    if re.match(r"^(cd|pushd|popd)\b", command):
        return (
            "Directory changes (cd/pushd/popd) are not allowed — working "
            "directory must remain project root for the entire session. "
            "Use absolute paths from project root instead. For git "
            "operations in other directories, use git -C <path>."
        )

    # Compound commands — separators bypass approval pattern matching
    stripped = strip_quoted_strings(command)
    if "&&" in stripped or "||" in stripped:
        return (
            "Compound operators (&&, ||) are not allowed — command "
            "separators bypass approval pattern matching because the "
            "matcher sees only the first command. Run each command as a "
            "separate Bash tool call. Independent commands can run in "
            "parallel."
        )
    if ";" in stripped:
        return (
            "Command separator (;) is not allowed — separators bypass "
            "approval pattern matching because the matcher sees only the "
            "first command. Run each command as a separate Bash tool call."
        )
    if re.search(r"(?<!\|)\|(?!\|)", stripped):
        return (
            "Pipes (|) are not allowed — command separators bypass "
            "approval pattern matching because the matcher sees only the "
            "first command. Run each command as a separate Bash tool call, "
            "or use dedicated tools (Grep instead of grep, Read instead "
            "of cat | head, etc.)."
        )

    return None


# ===========================================================================
# Layer 2 — Dynamic settings.json enforcement
# ===========================================================================


def check_edit_write(tool_name, tool_input, project_dir, settings):
    file_path = tool_input.get("file_path", "")
    if not file_path:
        return

    abs_path = resolve_path(file_path, project_dir)

    # Deny rules take precedence
    if is_path_denied(file_path, tool_name, settings):
        return
    if is_path_denied(abs_path, tool_name, settings):
        return

    # Check tool is in allow list and path is within allowed directories
    if is_tool_in_list(tool_name, settings.get("permissions", {}).get("allow", [])):
        if is_within_allowed_dirs(abs_path, project_dir, settings):
            approve()


def check_bash_dynamic(command, settings):
    # Deny rules take precedence
    if is_bash_denied(command, settings):
        return

    # Check command matches an allow pattern
    if is_bash_allowed(command, settings):
        approve()


# ===========================================================================
# Dispatch
# ===========================================================================


def main():
    hook_input = json.load(sys.stdin)
    tool_name = hook_input.get("tool_name", "")
    tool_input = hook_input.get("tool_input", {})
    project_dir = get_project_dir()

    if tool_name == "Bash":
        command = tool_input.get("command", "").strip()
        if not command:
            return

        # Layer 1: hardcoded blocks
        violation = check_hardcoded_blocks(command)
        if violation:
            block(violation)
            return

        # Layer 2: dynamic settings enforcement
        settings = load_merged_settings(project_dir)
        check_bash_dynamic(command, settings)
        return

    if tool_name in ("Edit", "Write"):
        settings = load_merged_settings(project_dir)
        check_edit_write(tool_name, tool_input, project_dir, settings)
        return


if __name__ == "__main__":
    main()
