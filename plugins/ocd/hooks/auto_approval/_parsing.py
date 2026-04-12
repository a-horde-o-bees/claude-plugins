"""Compound command splitting and loop expansion for Bash commands."""

from __future__ import annotations

import re


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
