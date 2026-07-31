#!/usr/bin/env python3
"""Pretty-print one session's conversation as markdown — user and agent messages
only, no tool calls — with a horizontal rule between messages.

    uv run ${CLAUDE_SKILL_DIR}/export_md.py --session ID_OR_PREFIX --out FILE.md \
        [--db ~/.claude/engaged-time/raw.db]

Reads the raw DB (ingest first). Keeps `user`/`assistant` records' text blocks;
drops tool_use / tool_result / thinking blocks, meta and command records, replays,
compact summaries, and sidechains. Consecutive records of one role merge into one
message, so the rules separate logical messages, not storage records.
"""
import argparse
import json
import pathlib
import sqlite3
import sys

import _paths


def session_markdown(conn: sqlite3.Connection, session_id: str) -> str:
    """Render one session as markdown. `session_id` may be a unique prefix."""
    ids = [s for (s,) in conn.execute(
        "SELECT DISTINCT session_id FROM raw WHERE session_id LIKE ? || '%'",
        (session_id,))]
    if not ids:
        sys.exit(f"no session matching {session_id!r} in the DB — ingest it first?")
    if len(ids) > 1:
        sys.exit(f"{session_id!r} is ambiguous: " + ", ".join(sorted(ids)))
    sid = ids[0]

    rows = conn.execute(
        "SELECT type, timestamp, json FROM raw"
        " WHERE session_id = ? AND type IN ('user', 'assistant')"
        "   AND is_replay = 0 AND is_meta = 0 AND is_compact_summary = 0"
        "   AND COALESCE(is_sidechain, 0) = 0"
        " ORDER BY timestamp, file, line", (sid,))

    messages: list = []  # [role, text] — mutable so same-role runs can merge
    first_ts = last_ts = None
    for rtype, ts, raw in rows:
        text = _text_of(json.loads(raw))
        if not text:
            continue  # tool-result-only user rows, block-less records
        first_ts = first_ts or ts
        last_ts = ts or last_ts
        role = "Agent" if rtype == "assistant" else "User"
        if messages and messages[-1][0] == role:
            messages[-1][1] += "\n\n" + text
        else:
            messages.append([role, text])

    head = f"# Session {sid}\n"
    if first_ts:
        head += f"\n_{len(messages)} messages · {first_ts} → {last_ts}_\n"
    body = "\n\n---\n\n".join(f"**{role}**\n\n{text}" for role, text in messages)
    return head + "\n" + body + "\n"


def _text_of(rec: dict) -> str:
    """The human-readable text of a conversation record: string content as-is,
    list content reduced to its text blocks (tool calls and thinking dropped)."""
    content = (rec.get("message") or {}).get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        return "\n\n".join(
            b["text"].strip() for b in content
            if isinstance(b, dict) and b.get("type") == "text" and b.get("text", "").strip())
    return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=_paths.db("raw.db"))
    ap.add_argument("--session", required=True, help="session id (or unique prefix)")
    ap.add_argument("--out", required=True, help="markdown file to write")
    a = ap.parse_args()
    conn = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    md = session_markdown(conn, a.session)
    conn.close()
    out = pathlib.Path(a.out).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md)
    n = md.count("\n---\n") + 1
    print(f"{out}: {n} messages")


if __name__ == "__main__":
    main()
