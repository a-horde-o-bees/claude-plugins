"""Progressive disclosure data layer: projects, sessions, exchanges.

Returns plain Python data structures (dicts and lists) for JSON serialization.
Each layer surfaces only what's needed to navigate to the next:

- projects(): all projects with current-project marker
- sessions(): session metadata, filterable, default-lean with `show` opt-ins
- exchanges(): per-exchange rows, filterable, default-lean with `show` opt-ins

Filtering on `sessions` and `exchanges`:
- project_filter: substring match against project_name; empty = all projects
- session_id: exact session match (or unique prefix); takes precedence over project
- range_from/range_to: exchange-number bounds within the matched scope
- from_ts/to_ts: ISO timestamp bounds applied alongside any scope filter

Output verbosity is controlled by a `show` list. Defaults are lean — heavy or
domain-specific fields are opt-in. See SHOW_EXCHANGES / SHOW_SESSIONS for the
recognized values; unknown values raise ValueError.
"""

import sqlite3

from . import _db


SHOW_EXCHANGES = {"messages", "active", "breakdown", "metrics", "timeframes"}
SHOW_SESSIONS = {"timeframes", "bytes"}


def _validate_show(show: list[str] | None, allowed: set[str]) -> set[str]:
    if not show:
        return set()
    s = set(show)
    unknown = s - allowed
    if unknown:
        raise ValueError(
            f"unknown show values: {sorted(unknown)}; allowed: {sorted(allowed)}"
        )
    return s


def resolve_session(conn: sqlite3.Connection, prefix: str) -> str:
    """Resolve a session id by exact match or unique prefix; return full id."""
    matches = conn.execute(
        "SELECT DISTINCT parent_session FROM events "
        "WHERE parent_session LIKE ? ORDER BY parent_session",
        (prefix + "%",),
    ).fetchall()
    if not matches:
        raise LookupError(f"no session matching '{prefix}'")
    if len(matches) > 1:
        ids = ", ".join(r[0][:8] for r in matches[:5])
        raise LookupError(f"prefix '{prefix}' is ambiguous: {ids}")
    return matches[0][0]


def projects(conn: sqlite3.Connection) -> dict:
    """All projects with the current-project marker."""
    try:
        current = _db.current_project_name()
    except RuntimeError:
        current = ""
    rows = conn.execute(
        "SELECT DISTINCT project_name FROM events ORDER BY project_name"
    ).fetchall()
    return {
        "current": current,
        "projects": [r[0] for r in rows],
    }


def sessions(
    conn: sqlite3.Connection,
    project_filter: str = "",
    from_ts: str | None = None,
    to_ts: str | None = None,
    show: list[str] | None = None,
) -> dict:
    """Sessions in project(s) with optional date-range filter.

    Default row: {project, session, n_exchanges, n_purposed}.
    `show=["timeframes"]` adds first_ts, last_ts.
    `show=["bytes"]` adds bytes.
    """
    show_set = _validate_show(show, SHOW_SESSIONS)

    where_clauses = ["parent_message IS NULL"]
    params: list = []
    if project_filter:
        where_clauses.append("project_name LIKE ?")
        params.append(f"%{project_filter}%")

    rows = conn.execute(f"""
        SELECT project_name, parent_session,
               MAX(exchange) AS n_exchanges,
               MIN(ts) AS first_ts, MAX(ts) AS last_ts,
               SUM(CASE WHEN text IS NOT NULL AND label NOT LIKE 'tool_result%'
                        THEN LENGTH(text) ELSE 0 END) AS bytes,
               (SELECT COUNT(*) FROM exchanges x
                WHERE x.parent_session = events_with_gaps.parent_session
                  AND x.purpose IS NOT NULL) AS n_purposed
        FROM events_with_gaps
        WHERE {' AND '.join(where_clauses)}
        GROUP BY project_name, parent_session
        ORDER BY first_ts
    """, params).fetchall()

    sessions_list: list = []
    for proj, sess, n_ex, ft, lt, bts, n_p in rows:
        if from_ts and lt and lt < from_ts:
            continue
        if to_ts and ft and ft > to_ts:
            continue
        row: dict = {
            "project": proj,
            "session": sess,
            "n_exchanges": n_ex,
            "n_purposed": n_p,
        }
        if "timeframes" in show_set:
            row["first_ts"] = ft
            row["last_ts"] = lt
        if "bytes" in show_set:
            row["bytes"] = bts
        sessions_list.append(row)

    return {
        "filter": {
            "project": project_filter or "all",
            "from": from_ts,
            "to": to_ts,
        },
        "n_sessions": len(sessions_list),
        "sessions": sessions_list,
    }


def exchanges(
    conn: sqlite3.Connection,
    threshold_s: float,
    project_filter: str = "",
    session_id: str = "",
    range_from: int | None = None,
    range_to: int | None = None,
    from_ts: str | None = None,
    to_ts: str | None = None,
    show: list[str] | None = None,
) -> list[dict]:
    """Exchanges with metrics + messages, filtered by scope and date.

    Scope precedence: session_id > project_filter > all (empty filter = all).

    Default row: {project, session, exchange, purpose}.
    `show=["timeframes"]` adds exchange_start, exchange_end.
    `show=["active"]` adds active_s.
    `show=["breakdown"]` adds active_s, user_s, agent_s.
    `show=["metrics"]` adds active_s, user_s, agent_s, total_s, idle_s.
    `show=["messages"]` adds messages: [...].

    Buckets combine — overlapping buckets union their fields.
    """
    show_set = _validate_show(show, SHOW_EXCHANGES)
    want_timeframes = "timeframes" in show_set
    want_active = bool(show_set & {"active", "breakdown", "metrics"})
    want_breakdown = bool(show_set & {"breakdown", "metrics"})
    want_wall = "metrics" in show_set
    want_messages = "messages" in show_set

    if session_id:
        session = resolve_session(conn, session_id)
    else:
        session = ""

    where_clauses = ["exchange > 0"]
    params: dict = {"threshold_s": threshold_s}

    if session:
        where_clauses.append("parent_session = :session")
        params["session"] = session
    elif project_filter:
        where_clauses.append("project_name LIKE :proj")
        params["proj"] = f"%{project_filter}%"

    if range_from is not None:
        where_clauses.append("exchange >= :rf")
        params["rf"] = range_from
    if range_to is not None:
        where_clauses.append("exchange <= :rt")
        params["rt"] = range_to

    if from_ts:
        where_clauses.append("ts >= :ft")
        params["ft"] = from_ts
    if to_ts:
        where_clauses.append("ts <= :tt")
        params["tt"] = to_ts

    metadata = conn.execute(f"""
        WITH params AS (SELECT :threshold_s AS threshold_s)
        SELECT
            project_name, parent_session, exchange,
            MIN(ts) AS exchange_start, MAX(ts) AS exchange_end,
            MAX(CASE WHEN label = 'user_msg' AND parent_message IS NULL
                     THEN gap_s END) AS user_msg_gap_s,
            SUM(CASE WHEN NOT (label = 'user_msg' AND parent_message IS NULL)
                      AND gap_s <= (SELECT threshold_s FROM params)
                      AND gap_s IS NOT NULL
                     THEN gap_s ELSE 0 END) AS agent_time_s,
            SUM(CASE WHEN gap_s > (SELECT threshold_s FROM params)
                     THEN gap_s ELSE 0 END) AS idle_s,
            SUM(CASE WHEN gap_s IS NOT NULL THEN gap_s ELSE 0 END) AS total_s
        FROM events_with_gaps
        WHERE {' AND '.join(where_clauses)}
        GROUP BY project_name, parent_session, exchange
        ORDER BY parent_session, exchange
    """, params).fetchall()

    if not metadata:
        return []

    sess_exchange_pairs = [(r[1], r[2]) for r in metadata]
    sessions_seen = sorted({p[0] for p in sess_exchange_pairs})

    msgs_by_pair: dict = {}
    purposes_by_pair: dict = {}
    for sess in sessions_seen:
        exs = [p[1] for p in sess_exchange_pairs if p[0] == sess]
        placeholders = ",".join("?" for _ in exs)
        if want_messages:
            msg_rows = conn.execute(f"""
                SELECT exchange, label, text
                FROM events_with_gaps
                WHERE parent_session = ?
                  AND exchange IN ({placeholders})
                  AND text IS NOT NULL
                  AND parent_message IS NULL
                  AND (label = 'user_msg' OR label LIKE 'assistant%')
                ORDER BY exchange, ts, file, line
            """, [sess, *exs]).fetchall()
            for ex, label, text in msg_rows:
                msg_type = "user" if label == "user_msg" else "assistant"
                msgs_by_pair.setdefault((sess, ex), []).append(
                    {"type": msg_type, "message": text}
                )
        purpose_rows = conn.execute(f"""
            SELECT exchange, purpose FROM exchanges
            WHERE parent_session = ? AND exchange IN ({placeholders})
              AND purpose IS NOT NULL
        """, [sess, *exs]).fetchall()
        for ex, purpose in purpose_rows:
            purposes_by_pair[(sess, ex)] = purpose

    out: list[dict] = []
    for proj, sess, ex, ts, te, ug, at, idle, total in metadata:
        if ug is None or ug > threshold_s:
            user_s: int | None = None
        else:
            user_s = round(ug)
        agent_s = round(at)
        active_s = (user_s or 0) + agent_s

        row: dict = {
            "project": proj,
            "session": sess,
            "exchange": ex,
            "purpose": purposes_by_pair.get((sess, ex)),
        }
        if want_timeframes:
            row["exchange_start"] = ts
            row["exchange_end"] = te
        if want_active:
            row["active_s"] = active_s
        if want_breakdown:
            row["user_s"] = user_s
            row["agent_s"] = agent_s
        if want_wall:
            row["total_s"] = round(total)
            row["idle_s"] = round(idle)
        if want_messages:
            row["messages"] = msgs_by_pair.get((sess, ex), [])
        out.append(row)
    return out
