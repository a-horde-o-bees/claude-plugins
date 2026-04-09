"""MCP server for friction discipline.

Agent-facing tools for logging, querying, and resolving process friction.
Friction is the signal that a system, tool, or process has a gap. Every
encounter is a Fix or Log decision — this server owns the Log path.

Entries live as timestamped bullets in `.claude/ocd/friction/{system}.md`,
one file per system the friction is *about*. Markdown is the storage
format — queue-not-archive lifecycle, human-inspectable, compatible with
existing logs.

Tools follow object_action naming: friction_log, friction_list,
friction_resolve, friction_systems. All return structured JSON.

Runs via stdio transport. Friction directory from FRICTION_DIR env var.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from ._helpers import _err, _ok

# --- Configuration ---

FRICTION_DIR = Path(os.environ.get("FRICTION_DIR", ".claude/ocd/friction"))

mcp = FastMCP(
    "ocd-friction",
    instructions="""Process friction queue. Reach for these tools when encountering a gap — a rule the system forced you to violate, a missing capability, a broken process step, unexpected state, or a runtime issue where investigating inline would derail the current task.

Every friction encounter is a Fix or Log decision. Make the choice actively — never default to logging.

Fix now when the current context is better equipped than a future session would be:
- The fix is clear from the current context and reconstructing that context later would be expensive
- The spider-web of related information informing the discovery would be lost to deferral
- The fix is simple enough that doing it now won't derail the current task

Log and continue when:
- The fix would derail current work — requires investigation, touches unrelated systems, or demands design decisions beyond current scope
- The friction is simple enough to describe and act on later without needing current context
- The fix depends on work outside the current task

Deciding question: is the current context better equipped than a future session would be? Complex friction rooted in a rich context web is worth fixing now — context won't regenerate cheaply. Simple friction with standalone context is fine to queue.

When logging: use friction_log immediately at the moment of encounter — do not wait until the task completes, context degrades. The `system` argument names the system the friction is *about*, not the workflow that surfaced it. Friction with navigator discovered during evaluate-governance goes to system='navigator', not 'evaluate-governance'.

When friction is fixed: use friction_resolve to clear the entry. Logs are a queue, not an archive — only unresolved friction remains.

Use friction_list to review the queue before starting related work. Use friction_systems for an overview of where friction has accumulated.""",
)

# --- Entry parsing and formatting ---

_ENTRY_RE = re.compile(
    r"^- (?P<logged_on>\d{4}-\d{2}-\d{2}) — "
    r"(?P<what_happened>.*?); "
    r"expected (?P<expected>.*?); "
    r"workaround: (?P<workaround>.*)$"
)

_SAFE_SYSTEM_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_\-]*$")


@dataclass
class Entry:
    logged_on: str
    what_happened: str
    expected: str
    workaround: str

    def format(self) -> str:
        return (
            f"- {self.logged_on} — {self.what_happened}; "
            f"expected {self.expected}; workaround: {self.workaround}"
        )

    def to_dict(self, system: str, index: int) -> dict:
        return {
            "system": system,
            "index": index,
            "logged_on": self.logged_on,
            "what_happened": self.what_happened,
            "expected": self.expected,
            "workaround": self.workaround,
        }


def _validate_system(system: str) -> None:
    if not _SAFE_SYSTEM_RE.match(system):
        raise ValueError(
            f"Invalid system name: {system!r}. "
            "Use alphanumerics, underscore, or dash; no path separators."
        )


def _system_path(system: str) -> Path:
    _validate_system(system)
    return FRICTION_DIR / f"{system}.md"


def _parse_entries(content: str) -> list[Entry]:
    entries: list[Entry] = []
    for line in content.splitlines():
        if not line.strip():
            continue
        match = _ENTRY_RE.match(line)
        if match:
            entries.append(Entry(**match.groupdict()))
    return entries


def _read_entries(system: str) -> list[Entry]:
    path = _system_path(system)
    if not path.exists():
        return []
    return _parse_entries(path.read_text())


def _write_entries(system: str, entries: list[Entry]) -> None:
    path = _system_path(system)
    if not entries:
        if path.exists():
            path.unlink()
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    body = "\n".join(entry.format() for entry in entries) + "\n"
    path.write_text(body)


def _list_systems() -> list[str]:
    if not FRICTION_DIR.exists():
        return []
    return sorted(p.stem for p in FRICTION_DIR.glob("*.md"))


# ============================================================
# friction_* — friction queue operations
# ============================================================


@mcp.tool()
def friction_log(
    system: str,
    what_happened: str,
    expected: str,
    workaround: str,
) -> str:
    """Append a friction entry for a system. Auto-timestamps with today's date.

    Call immediately at the moment of friction — do not wait until the task completes.
    Context degrades; capture while it's rich.

    Args:
        system: The system the friction is *about*, not the workflow that surfaced it.
            Friction with navigator discovered during evaluate-governance uses 'navigator'.
            Alphanumerics, underscore, dash — no path separators.
        what_happened: Concise description of the gap, rule violation, tool miss, or breakdown.
        expected: What the agent expected to be the case or to work.
        workaround: What was done instead, or "none — blocked" if no workaround existed.

    Returns {logged_on, system, index, path} on success; {error} on invalid system name.
    """
    try:
        _validate_system(system)
        entries = _read_entries(system)
        entry = Entry(
            logged_on=date.today().isoformat(),
            what_happened=what_happened.strip(),
            expected=expected.strip(),
            workaround=workaround.strip(),
        )
        entries.append(entry)
        _write_entries(system, entries)
        return _ok({
            "logged_on": entry.logged_on,
            "system": system,
            "index": len(entries) - 1,
            "path": str(_system_path(system)),
        })
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_list(system: str | None = None, limit: int | None = None) -> str:
    """List unresolved friction entries. Optionally scope to one system.

    Use before starting related work to surface known gaps, and during review
    to decide what to fix next. Entries include a stable index within their system
    that friction_resolve consumes.

    Args:
        system: If provided, return entries only from this system. If omitted, return
            entries from all systems.
        limit: Optional cap on total entries returned. Most-recent-first across systems.

    Returns {total, entries: [{system, index, logged_on, what_happened, expected, workaround}]}.
    """
    try:
        if system is not None:
            _validate_system(system)
            systems = [system]
        else:
            systems = _list_systems()

        rows: list[dict] = []
        for sys_name in systems:
            for idx, entry in enumerate(_read_entries(sys_name)):
                rows.append(entry.to_dict(sys_name, idx))

        rows.sort(key=lambda r: r["logged_on"], reverse=True)
        if limit is not None and limit >= 0:
            rows = rows[:limit]

        return _ok({"total": len(rows), "entries": rows})
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_resolve(system: str, entry_index: int) -> str:
    """Remove a resolved friction entry by its index within a system.

    Call after the underlying cause is fixed and verified. Friction logs are a queue,
    not an archive — resolved entries leave the file. Deleting the last entry removes
    the system file entirely.

    Args:
        system: The system name whose entry should be cleared.
        entry_index: Zero-based index within that system's entries, as returned by
            friction_list. Indices may shift after a resolve — re-list before the next
            resolve in a batch.

    Returns {removed: entry_dict, remaining} on success; {error} if out of range.
    """
    try:
        _validate_system(system)
        entries = _read_entries(system)
        if entry_index < 0 or entry_index >= len(entries):
            return _ok({
                "error": (
                    f"entry_index {entry_index} out of range for system "
                    f"{system!r} ({len(entries)} entries)"
                ),
            })
        removed = entries.pop(entry_index)
        _write_entries(system, entries)
        return _ok({
            "removed": removed.to_dict(system, entry_index),
            "remaining": len(entries),
        })
    except Exception as e:
        return _err(e)


@mcp.tool()
def friction_systems() -> str:
    """List all systems with friction logs, with entry counts.

    Use for an overview of where friction has accumulated across the project.
    Systems with zero entries are not listed — empty files are pruned on resolve.

    Returns {total_systems, total_entries, systems: [{system, count}]}.
    """
    try:
        rows = []
        total_entries = 0
        for sys_name in _list_systems():
            count = len(_read_entries(sys_name))
            if count == 0:
                continue
            rows.append({"system": sys_name, "count": count})
            total_entries += count
        rows.sort(key=lambda r: r["count"], reverse=True)
        return _ok({
            "total_systems": len(rows),
            "total_entries": total_entries,
            "systems": rows,
        })
    except Exception as e:
        return _err(e)


if __name__ == "__main__":
    mcp.run()
