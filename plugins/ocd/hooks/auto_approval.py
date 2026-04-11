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

import plugin


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
    return plugin.get_project_dir()


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


_ENV_ASSIGN_RE = re.compile(
    r'^\s*'                                    # leading whitespace
    r'[A-Za-z_][A-Za-z0-9_]*='                 # NAME=
    r'(?:'
    r'"(?:[^"\\]|\\.)*"'                       # "double-quoted"
    r"|'[^']*'"                                # 'single-quoted'
    r'|\$\([^)]*\)'                            # $(command substitution)
    r'|[^\s"\';|&<>]*'                         # bare token (no meta chars)
    r')'
    r'(?:\s+|$)'                               # trailing whitespace
)


def _strip_env_assignments(command: str) -> str:
    """Strip leading NAME=value env assignments so pattern matching sees
    the actual command verb.

    Bash permits `VAR=value ... cmd` as a command prefix that sets env
    vars for the invocation. Without stripping, the first "word" would
    be `VAR=value` and allow patterns targeting `cmd` would never match.
    Handles double/single-quoted values and `$()` command substitutions.
    """
    while True:
        m = _ENV_ASSIGN_RE.match(command)
        if not m:
            return command.lstrip()
        command = command[m.end():]


def match_bash_pattern(command: str, pattern_str: str) -> bool:
    """Match a command against a Bash(pattern) rule.

    Patterns:
        Bash(verb:*)     — command starts with verb
        Bash(verb *)     — command starts with "verb "
        Bash(path/*)     — command starts with path/
        Bash(verb)       — exact match on first word
        Bash(.claude/*)  — command starts with .claude/

    Leading NAME=value env assignments are stripped before matching so
    `VAR=x python3 ...` matches Bash(python3:*) just like plain python3.

    Absolute-path executables (e.g., /usr/bin/python3, .venv/bin/python3 resolved
    to an absolute path) are normalized to basename before matching :* and exact-
    match patterns. So Bash(python3:*) matches /usr/bin/python3 the same as plain
    python3. Path-prefix patterns (Bash(path/*)) match literally with no
    normalization — they're meant for matching literal paths, not executable names.
    """
    inner = pattern_str

    if not command:
        return False

    stripped = _strip_env_assignments(command)
    if not stripped:
        return False

    # Build candidates: env-stripped command and (if first word is absolute path)
    # the basename-normalized version
    candidates = [stripped]
    first_word = stripped.split()[0]
    if first_word.startswith("/"):
        basename = first_word.rsplit("/", 1)[-1]
        if basename:
            normalized = basename + stripped[len(first_word):]
            candidates.append(normalized)

    if inner.endswith(":*"):
        prefix = inner[:-2]
        return any(c == prefix or c.startswith(prefix + " ") for c in candidates)
    if inner.endswith("*"):
        # Path-prefix pattern — match literally against env-stripped command
        prefix = inner[:-1]
        return stripped.startswith(prefix)
    # Exact first-word match
    return any(c.split()[0] == inner for c in candidates)


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


_LOOP_OPEN_WORDS = ("for", "while", "until")
_LOOP_CLOSE_WORD = "done"
_LOOP_BODY_OPEN_WORD = "do"


def _is_word_at(command: str, i: int, word: str) -> bool:
    """Return True if `word` starts at position i as a standalone token."""
    end = i + len(word)
    if command[i:end] != word:
        return False
    if i > 0:
        prev = command[i - 1]
        if prev.isalnum() or prev == "_":
            return False
    if end < len(command):
        nxt = command[end]
        if nxt.isalnum() or nxt == "_":
            return False
    return True


def split_compound_command(command: str) -> list[str] | None:
    """Split command on &&, ||, ;, | outside quotes and outside loops.

    Quote state is tracked character by character; separators inside
    strings are preserved. Loop structure (for/while/until ... do ...
    done) is also respected — separators between a loop's `do` and its
    matching `done` are treated as internal structure, not statement
    boundaries, so a loop remains a single block even when it contains
    multiple statements. Nested loops track depth via the keyword pair
    for/while/until <-> done. Command-start position is required for
    the keyword check so that `for`/`done` appearing inside argument
    values aren't misinterpreted.

    Returns list of individual commands if separators found, None otherwise.
    """
    parts = []
    current: list[str] = []
    in_single = False
    in_double = False
    escaped = False
    depth = 0
    at_cmd_start = True
    i = 0
    while i < len(command):
        c = command[i]
        if escaped:
            current.append(c)
            escaped = False
            i += 1
            at_cmd_start = False
            continue
        if c == "\\" and in_double:
            current.append(c)
            escaped = True
            i += 1
            at_cmd_start = False
            continue
        if c == "'" and not in_double:
            in_single = not in_single
            current.append(c)
            i += 1
            at_cmd_start = False
            continue
        if c == '"' and not in_single:
            in_double = not in_double
            current.append(c)
            i += 1
            at_cmd_start = False
            continue
        if in_single or in_double:
            current.append(c)
            i += 1
            continue

        if c.isspace():
            current.append(c)
            i += 1
            continue

        # Loop keyword detection at command-start position.
        if at_cmd_start:
            matched_loop_open = False
            for word in _LOOP_OPEN_WORDS:
                if _is_word_at(command, i, word):
                    depth += 1
                    current.append(word)
                    i += len(word)
                    at_cmd_start = False
                    matched_loop_open = True
                    break
            if matched_loop_open:
                continue
            if _is_word_at(command, i, _LOOP_CLOSE_WORD):
                depth = max(0, depth - 1)
                current.append(_LOOP_CLOSE_WORD)
                i += len(_LOOP_CLOSE_WORD)
                at_cmd_start = False
                continue
            if _is_word_at(command, i, _LOOP_BODY_OPEN_WORD):
                # `do` starts a new command position inside the loop body
                current.append(_LOOP_BODY_OPEN_WORD)
                i += len(_LOOP_BODY_OPEN_WORD)
                # at_cmd_start stays True — next non-whitespace is a command
                continue

        # Separator handling — split only at depth 0.
        two = command[i:i + 2]
        if two in ("&&", "||"):
            if depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(two)
            i += 2
            at_cmd_start = True
            continue
        if c == ";":
            if depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(c)
            i += 1
            at_cmd_start = True
            continue
        if c == "|" and two != "||":
            if depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(c)
            i += 1
            at_cmd_start = True
            continue

        current.append(c)
        i += 1
        at_cmd_start = False

    parts.append("".join(current).strip())
    parts = [p for p in parts if p]
    return parts if len(parts) > 1 else None


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


_FOR_LOOP_RE = re.compile(
    r'^\s*for\b.+?\bdo\b\s+(.+?)\s*;?\s*\bdone\b\s*$',
    re.DOTALL,
)
_WHILE_LOOP_RE = re.compile(
    r'^\s*while\b.+?\bdo\b\s+(.+?)\s*;?\s*\bdone\b\s*$',
    re.DOTALL,
)
_UNTIL_LOOP_RE = re.compile(
    r'^\s*until\b.+?\bdo\b\s+(.+?)\s*;?\s*\bdone\b\s*$',
    re.DOTALL,
)


def _extract_loop_body(command: str) -> str | None:
    """If command is a for/while/until loop, return the body captured
    between `do` and `done`. Returns None if not a loop.

    The body is returned as a single string — splitting and further
    parsing happen via recursion in expand_command, which lets nested
    loops unfold naturally because each inner loop is itself a command
    that matches the same loop regex on the next recursion.
    """
    for pattern in (_FOR_LOOP_RE, _WHILE_LOOP_RE, _UNTIL_LOOP_RE):
        m = pattern.match(command)
        if m:
            return m.group(1).strip()
    return None


def expand_command(command: str) -> list[str]:
    """Expand a bash command into individual leaf commands for pattern checking.

    - Control-flow constructs (for/while/until loops) have their body
      captured between outer `do` and outer `done`, then recursively
      expanded. Nested loops fall out of the recursion naturally: each
      inner loop is itself a command that re-enters this function.
    - Compound commands joined by `&&`, `||`, `;`, `|` are split via
      `split_compound_command`, which is loop-aware — separators inside
      a loop body are treated as internal structure, so loops mixed
      with sibling statements at the same level split cleanly into
      parallel blocks for independent expansion.
    - Leaves are individual commands matched against allow/deny patterns.
    - A loop is allowed when every command in its body matches an allow
      pattern.
    """
    body = _extract_loop_body(command)
    if body is not None:
        return expand_command(body)

    parts = split_compound_command(command)
    if parts is not None:
        result: list[str] = []
        for part in parts:
            result.extend(expand_command(part))
        return result

    stripped = command.strip()
    return [stripped] if stripped else []


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


if __name__ == "__main__":
    main()
