"""Persisted blocks and topics (the `blocks` / `block_exchanges` tables).

A **block** groups exchanges that share a focus; its **summary** describes that
focus and its **topic** is a broader label shared across blocks (many summaries
→ one topic, e.g. "OAuth writeback", "stale-token re-auth" → topic `qbo-oauth`).
Membership is a set of `(parent_session, exchange)` pairs that may span sessions
(C.2); one exchange belongs to at most one block (unique index). Blocks persist
across runs so coalescing happens once, not per report.

Block time is the sum of per-exchange engaged seconds over resolved members.
Members whose session was pruned from `~/.claude/projects/` don't resolve in
`events` and contribute zero — tolerated, not an error (C.2).

The **`fill`** toggle governs unobserved compose pauses (`user_s` NULL or 0):
OFF (default) bills only measured compose time; ON credits each unobserved
pause one `avg_user_time_s`, estimating true human engagement (C-4).

Billability is **not** modeled here — the skill stores topics and offers
topic-filtered listing; the consuming project declares which topics bill and
passes them in via `billable_topics`.
"""

import sqlite3

from ._errors import InitError
from ._scope import resolve_session


def parse_members(spec: str, conn: sqlite3.Connection) -> list[tuple[str, int]]:
    """Parse `<session>:<exch>` / `<session>:<a>-<b>` comma-separated into pairs.

    Session tokens resolve via unique prefix (like other verbs). Ranges expand
    inclusively. Returns deduped `(full_session, exchange)` pairs in input order.
    """
    pairs: list[tuple[str, int]] = []
    seen: set[tuple[str, int]] = set()
    resolved: dict[str, str] = {}
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if ":" not in token:
            raise ValueError(
                f"member '{token}' must be <session>:<exchange> "
                f"(blocks may span sessions, so every member names its session)"
            )
        sess_tok, ex_part = token.rsplit(":", 1)
        sess_tok = sess_tok.strip()
        if sess_tok not in resolved:
            resolved[sess_tok] = resolve_session(conn, sess_tok)
        session = resolved[sess_tok]
        if "-" in ex_part:
            lo, hi = ex_part.split("-", 1)
            rng = range(int(lo), int(hi) + 1)
        else:
            rng = range(int(ex_part), int(ex_part) + 1)
        for ex in rng:
            pair = (session, ex)
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)
    return pairs


def create_block(
    conn: sqlite3.Connection, topic: str | None, summary: str | None,
    members: list[tuple[str, int]],
) -> int:
    """Insert a block and its members. Returns block_id. Members optional."""
    cur = conn.execute(
        "INSERT INTO blocks (topic, summary, created_at, updated_at) "
        "VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
        (topic, summary),
    )
    block_id = cur.lastrowid
    assert block_id is not None
    _add_members(conn, block_id, members)
    conn.commit()
    return block_id


def set_block(
    conn: sqlite3.Connection, block_id: int,
    topic: str | None = None, summary: str | None = None,
) -> None:
    """Update a block's topic and/or summary. Unset args are left unchanged."""
    if not _block_exists(conn, block_id):
        raise LookupError(f"no block with id {block_id}")
    sets, params = [], []
    if topic is not None:
        sets.append("topic = ?")
        params.append(topic)
    if summary is not None:
        sets.append("summary = ?")
        params.append(summary)
    if not sets:
        raise ValueError("set-block needs --topic and/or --summary")
    sets.append("updated_at = CURRENT_TIMESTAMP")
    params.append(block_id)
    conn.execute(f"UPDATE blocks SET {', '.join(sets)} WHERE block_id = ?", params)
    conn.commit()


def add_exchanges(
    conn: sqlite3.Connection, block_id: int, members: list[tuple[str, int]],
) -> None:
    """Add members to a block. Raises if any exchange already belongs elsewhere."""
    if not _block_exists(conn, block_id):
        raise LookupError(f"no block with id {block_id}")
    _add_members(conn, block_id, members)
    conn.execute(
        "UPDATE blocks SET updated_at = CURRENT_TIMESTAMP WHERE block_id = ?",
        (block_id,),
    )
    conn.commit()


def remove_exchanges(
    conn: sqlite3.Connection, block_id: int, members: list[tuple[str, int]],
) -> int:
    """Remove members from a block. Returns count actually removed."""
    removed = 0
    for session, ex in members:
        cur = conn.execute(
            "DELETE FROM block_exchanges WHERE block_id = ? AND parent_session = ? "
            "AND exchange = ?",
            (block_id, session, ex),
        )
        removed += cur.rowcount
    if removed:
        conn.execute(
            "UPDATE blocks SET updated_at = CURRENT_TIMESTAMP WHERE block_id = ?",
            (block_id,),
        )
    conn.commit()
    return removed


def delete_block(conn: sqlite3.Connection, block_id: int) -> bool:
    """Delete a block and its membership rows. Returns True when it existed."""
    conn.execute("DELETE FROM block_exchanges WHERE block_id = ?", (block_id,))
    cur = conn.execute("DELETE FROM blocks WHERE block_id = ?", (block_id,))
    conn.commit()
    return cur.rowcount > 0


def _block_exists(conn: sqlite3.Connection, block_id: int) -> bool:
    return conn.execute(
        "SELECT 1 FROM blocks WHERE block_id = ?", (block_id,)
    ).fetchone() is not None


def _add_members(
    conn: sqlite3.Connection, block_id: int, members: list[tuple[str, int]],
) -> None:
    for session, ex in members:
        try:
            conn.execute(
                "INSERT INTO block_exchanges (block_id, parent_session, exchange) "
                "VALUES (?, ?, ?)",
                (block_id, session, ex),
            )
        except sqlite3.IntegrityError:
            owner = conn.execute(
                "SELECT block_id FROM block_exchanges WHERE parent_session = ? "
                "AND exchange = ?",
                (session, ex),
            ).fetchone()
            owner_id = owner[0] if owner else "?"
            raise InitError(
                f"exchange {session[:8]}:{ex} already belongs to block {owner_id} "
                f"— one exchange maps to at most one block. Remove it there first."
            ) from None


def _metrics(
    conn: sqlite3.Connection, threshold_s: float, members: list[tuple[str, int]],
) -> dict[tuple[str, int], tuple[int | None, int]]:
    """Per-member (user_s, agent_s), mirroring `_scope.exchanges` time math.

    Members absent from `events` (pruned sessions) are simply missing from the
    returned map — callers treat that as a zero-contribution unresolved member.
    """
    by_session: dict[str, set[int]] = {}
    for session, ex in members:
        by_session.setdefault(session, set()).add(ex)

    out: dict[tuple[str, int], tuple[int | None, int]] = {}
    for session, exs in by_session.items():
        placeholders = ",".join("?" for _ in exs)
        rows = conn.execute(
            f"""
            WITH params AS (SELECT ? AS threshold_s)
            SELECT exchange,
                MAX(CASE WHEN label = 'user_msg' AND parent_message IS NULL
                         THEN gap_s END) AS ug,
                SUM(CASE WHEN NOT (label = 'user_msg' AND parent_message IS NULL)
                          AND gap_s <= (SELECT threshold_s FROM params)
                          AND gap_s IS NOT NULL
                         THEN gap_s ELSE 0 END) AS agent_s
            FROM events_with_gaps
            WHERE parent_session = ? AND exchange IN ({placeholders})
            GROUP BY exchange
            """,
            [threshold_s, session, *exs],
        ).fetchall()
        for ex, ug, agent_s in rows:
            user_s = None if (ug is None or ug > threshold_s) else round(ug)
            out[(session, ex)] = (user_s, round(agent_s or 0))
    return out


def _engaged(
    metrics: dict[tuple[str, int], tuple[int | None, int]],
    members: list[tuple[str, int]],
    avg_user_s: float,
    fill: bool,
) -> tuple[int, int, int]:
    """Sum (user_s, agent_s, n_resolved) over members under the fill policy.

    Unobserved compose pause = user_s NULL or 0. fill ON credits it
    `avg_user_s`; fill OFF credits 0.
    """
    user_total = agent_total = resolved = 0
    for member in members:
        m = metrics.get(member)
        if m is None:
            continue  # unresolved (pruned session) — zero contribution
        resolved += 1
        user_s, agent_s = m
        if user_s is not None and user_s > 0:
            user_total += user_s
        elif fill:
            user_total += round(avg_user_s)
        agent_total += agent_s
    return user_total, agent_total, resolved


def _candidate_block_ids(
    conn: sqlite3.Connection, project_filter: str, session_id: str,
) -> list[int] | None:
    """Block ids whose membership intersects the scope. None means 'all blocks'."""
    if session_id:
        session = resolve_session(conn, session_id)
        rows = conn.execute(
            "SELECT DISTINCT block_id FROM block_exchanges WHERE parent_session = ?",
            (session,),
        ).fetchall()
        return [r[0] for r in rows]
    if project_filter:
        rows = conn.execute(
            """
            SELECT DISTINCT be.block_id
            FROM block_exchanges be
            JOIN (SELECT DISTINCT parent_session, project_name FROM events) e
              ON e.parent_session = be.parent_session
            WHERE e.project_name LIKE ?
            """,
            (f"%{project_filter}%",),
        ).fetchall()
        return [r[0] for r in rows]
    return None  # all


def list_blocks(
    conn: sqlite3.Connection,
    threshold_s: float,
    avg_user_s: float,
    project_filter: str = "",
    session_id: str = "",
    topic: str = "",
    billable_topics: set[str] | None = None,
    fill: bool = False,
) -> dict:
    """List blocks in scope with members and computed engaged time.

    `topic` restricts to one topic; `billable_topics` restricts to a set (the
    project's billable policy). Time is reported as user_s / agent_s /
    combined_s under the `fill` policy.
    """
    ids = _candidate_block_ids(conn, project_filter, session_id)

    where = []
    params: list = []
    if ids is not None:
        if not ids:
            return _empty_block_result(project_filter, session_id, topic, billable_topics, fill)
        where.append(f"block_id IN ({','.join('?' for _ in ids)})")
        params.extend(ids)
    if topic:
        where.append("topic = ?")
        params.append(topic)
    if billable_topics:
        where.append(f"topic IN ({','.join('?' for _ in billable_topics)})")
        params.extend(sorted(billable_topics))
    clause = f"WHERE {' AND '.join(where)}" if where else ""

    block_rows = conn.execute(
        f"SELECT block_id, topic, summary, created_at, updated_at FROM blocks "
        f"{clause} ORDER BY block_id",
        params,
    ).fetchall()

    blocks_out: list[dict] = []
    total_combined = 0
    for block_id, btopic, summary, created, updated in block_rows:
        member_rows = conn.execute(
            "SELECT parent_session, exchange FROM block_exchanges "
            "WHERE block_id = ? ORDER BY parent_session, exchange",
            (block_id,),
        ).fetchall()
        members = [(s, e) for s, e in member_rows]
        metrics = _metrics(conn, threshold_s, members)
        user_s, agent_s, resolved = _engaged(metrics, members, avg_user_s, fill)
        combined = user_s + agent_s
        total_combined += combined
        blocks_out.append({
            "block_id": block_id,
            "topic": btopic,
            "summary": summary,
            "members": [f"{s}:{e}" for s, e in members],
            "n_members": len(members),
            "n_resolved": resolved,
            "user_s": user_s,
            "agent_s": agent_s,
            "combined_s": combined,
            "created_at": created,
            "updated_at": updated,
        })

    return {
        "filter": {
            "project": project_filter or ("session" if session_id else "all"),
            "topic": topic or None,
            "billable_topics": sorted(billable_topics) if billable_topics else None,
            "fill": "on" if fill else "off",
        },
        "n_blocks": len(blocks_out),
        "total_combined_s": total_combined,
        "blocks": blocks_out,
    }


def _empty_block_result(project_filter, session_id, topic, billable_topics, fill) -> dict:
    return {
        "filter": {
            "project": project_filter or ("session" if session_id else "all"),
            "topic": topic or None,
            "billable_topics": sorted(billable_topics) if billable_topics else None,
            "fill": "on" if fill else "off",
        },
        "n_blocks": 0,
        "total_combined_s": 0,
        "blocks": [],
    }


def topic_summary(
    conn: sqlite3.Connection,
    threshold_s: float,
    avg_user_s: float,
    project_filter: str = "",
    session_id: str = "",
    fill: bool = False,
) -> dict:
    """Distinct topics in scope with block counts and combined engaged time.

    The "evaluate first" view: a curator reads this to see the topic
    vocabulary (and spot near-duplicates like `oauth` vs `qbo-oauth`) before
    deciding which topics bill.
    """
    listing = list_blocks(
        conn, threshold_s, avg_user_s,
        project_filter=project_filter, session_id=session_id, fill=fill,
    )
    agg: dict[str, dict] = {}
    for block in listing["blocks"]:
        topic = block["topic"] or "(untagged)"
        entry = agg.setdefault(topic, {"topic": topic, "n_blocks": 0,
                                       "n_member_exchanges": 0, "combined_s": 0})
        entry["n_blocks"] += 1
        entry["n_member_exchanges"] += block["n_members"]
        entry["combined_s"] += block["combined_s"]
    topics = sorted(agg.values(), key=lambda t: t["combined_s"], reverse=True)
    return {
        "filter": listing["filter"],
        "n_topics": len(topics),
        "topics": topics,
    }
