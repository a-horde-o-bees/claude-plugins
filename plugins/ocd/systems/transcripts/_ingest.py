"""Event collection from Claude Code JSONL transcripts.

Walks a parent session JSONL plus any nested *.jsonl files in the matching
session directory, extracts events with normalized labels, resolves the
spawning parent_message for nested events by temporal containment, and
ingests via INSERT OR IGNORE on (file, line). JSONL lines are append-only
in Claude Code transcripts, so re-runs only insert newly-appended lines.

`sync` is the auto-ingest entry point: walks ~/.claude/projects/ (filtered
by an optional project name substring) and ingests anything new. Each verb
in the CLI calls sync before querying so the DB is current at every read.
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from tools import environment


@dataclass
class Event:
    ts: datetime
    label: str
    ref: str | None
    file: str
    line: int
    project_name: str
    parent_session: str
    text: str | None = None
    uuid: str | None = None
    parent_message: str | None = None
    tool_use_label: str | None = None


def parse_ts(ts: str) -> datetime:
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def extract_text(e: dict) -> str | None:
    """Pull chat-relevant text from a user or assistant event. None if absent."""
    msg = e.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        s = content.strip()
        return s or None
    if isinstance(content, list):
        parts: list[str] = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                parts.append(c.get("text", ""))
            elif isinstance(c, str):
                parts.append(c)
        joined = "\n".join(parts).strip()
        return joined or None
    return None


def event_label(e: dict) -> tuple[str, str | None]:
    """Return (label, tool_use_id-or-ref) for a JSONL event."""
    t = e.get("type")
    if t == "assistant":
        msg = e.get("message") or {}
        content = msg.get("content", [])
        if isinstance(content, list):
            for c in content:
                if isinstance(c, dict) and c.get("type") == "tool_use":
                    return f"tool_use:{c.get('name')}", c.get("id")
            kinds = [c.get("type", "?") for c in content if isinstance(c, dict)]
            return f"assistant[{','.join(kinds)}]", None
        return "assistant", None
    if t == "user":
        if "toolUseResult" in e:
            msg = e.get("message") or {}
            content = msg.get("content", [])
            ref = None
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("type") == "tool_result":
                        ref = c.get("tool_use_id")
                        break
            tur = e.get("toolUseResult")
            interrupted = isinstance(tur, dict) and tur.get("interrupted")
            return ("tool_result_interrupted" if interrupted else "tool_result"), ref
        return ("sidechain_user_msg" if e.get("isSidechain") else "user_msg"), None
    if t == "system":
        return f"system:{e.get('subtype', '?')}", None
    if t == "attachment":
        a = e.get("attachment") or {}
        return f"attachment:{a.get('type', '?')}", None
    return t or "?", None


def collect_events(
    jsonl_path: Path, project_name: str, parent_session: str,
) -> list[Event]:
    rows: list[Event] = []
    file_str = str(jsonl_path)
    with open(jsonl_path) as f:
        for line_no, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                e = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = e.get("timestamp")
            if not ts:
                continue
            label, ref = event_label(e)
            text = None
            if label.startswith("assistant") or label in ("user_msg", "sidechain_user_msg"):
                text = extract_text(e)
            rows.append(Event(
                ts=parse_ts(ts), label=label, ref=ref,
                file=file_str, line=line_no,
                project_name=project_name,
                parent_session=parent_session,
                text=text,
                uuid=e.get("uuid"),
            ))
    return rows


def process_transcript(parent: Path) -> list[Event]:
    """Collect parent + nested events, resolve tool_use_label and parent_message."""
    project_name = parent.parent.name
    parent_session = parent.stem
    parent_events = collect_events(parent, project_name, parent_session)

    nested_dir = parent.with_suffix("")
    nested_events: list[Event] = []
    if nested_dir.is_dir():
        for nf in sorted(nested_dir.rglob("*.jsonl")):
            nested_events.extend(collect_events(nf, project_name, parent_session))

    tool_use_names: dict[str, str] = {}
    for r in parent_events + nested_events:
        if r.label.startswith("tool_use:") and r.ref:
            tool_use_names[r.ref] = r.label.split(":", 1)[1]
    for r in parent_events + nested_events:
        if r.label.startswith("tool_result") and r.ref:
            r.tool_use_label = tool_use_names.get(r.ref)

    spawn_candidates = sorted(
        (r for r in parent_events + nested_events
         if r.label in ("tool_use:Task", "tool_use:Agent") and r.uuid),
        key=lambda r: r.ts,
    )
    nested_by_file: dict[str, list[Event]] = {}
    for r in nested_events:
        nested_by_file.setdefault(r.file, []).append(r)
    for evs in nested_by_file.values():
        first_ts = min(e.ts for e in evs)
        spawning_uuid: str | None = None
        for cand in spawn_candidates:
            if cand.ts <= first_ts:
                spawning_uuid = cand.uuid
            else:
                break
        for e in evs:
            e.parent_message = spawning_uuid

    return parent_events + nested_events


def insert_events(conn: sqlite3.Connection, events: list[Event]) -> int:
    """Insert events into the DB; return count of newly added rows."""
    before = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    conn.executemany(
        """
        INSERT OR IGNORE INTO events
            (file, line, project_name, parent_session, ts,
             label, text, tool_use_label, ref, parent_message, uuid)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (e.file, e.line, e.project_name, e.parent_session, e.ts.isoformat(),
             e.label, e.text, e.tool_use_label, e.ref, e.parent_message, e.uuid)
            for e in events
        ],
    )
    conn.commit()
    after = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    return after - before


def discover_transcripts(path: Path) -> list[Path]:
    """Resolve path to one or more parent JSONL files."""
    if path.is_file() and path.suffix == ".jsonl":
        return [path]
    if path.is_dir():
        return sorted(path.glob("*.jsonl"))
    raise ValueError(f"Not a JSONL file or project directory: {path}")


def sync(conn: sqlite3.Connection, project_filter: str = "") -> int:
    """Ingest any new lines from ~/.claude/projects/, returning rows added.

    Walks every project directory (optionally filtered by name substring),
    discovers parent JSONL files, processes them with their nested subagent
    transcripts, and inserts via INSERT OR IGNORE. Unchanged transcripts
    skip every existing row at insert time, so re-running is cheap.
    """
    base = environment.get_claude_home() / "projects"
    if not base.exists():
        return 0
    total_added = 0
    for project_dir in sorted(base.iterdir()):
        if not project_dir.is_dir():
            continue
        if project_filter and project_filter not in project_dir.name:
            continue
        for parent in discover_transcripts(project_dir):
            events = process_transcript(parent)
            total_added += insert_events(conn, events)
    return total_added
