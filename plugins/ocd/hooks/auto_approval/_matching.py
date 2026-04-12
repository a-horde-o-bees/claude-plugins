"""Tool and Bash pattern matching against settings allow/deny rules."""

from __future__ import annotations

import re


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
