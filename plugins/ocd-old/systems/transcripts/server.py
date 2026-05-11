"""MCP server for transcripts operations.

Agent-facing tools for navigating Claude Code session transcripts:
project discovery, session enumeration, per-exchange retrieval with
metrics and chat content, persistent per-exchange purpose summaries,
plus a read-only SQL escape hatch and live schema introspection.

Tool naming follows the input-shape distinction described in the
problem log `Verb naming convention not formally captured.md`:
`_list` for unfiltered enumeration, `_query` for filtered structural
retrieval (named typed-field criteria), `_get`/`_set` for single-keyed
operations, `_describe` for introspection. This deliberately diverges
from the current `mcp-server.md` convention pending the audit that log
triggers — the substantive distinction (filter-by-typed-fields vs
text-pattern matching) survives whichever naming the audit lands on.

Runs via stdio transport. Database path resolved internally via
`_init._db_path()` — no DB_PATH env var, since transcripts deploys to a
plugin-local path under the project's `.claude/` tree.

When the transcripts database is absent or its schema is divergent, the
server starts in dormant mode — it registers zero tools and its
instructions reduce to a one-line pointer at the setup skill.
Re-registering tools after init requires a Claude Code restart.
"""

from __future__ import annotations

import sqlite3
from typing import Any

from mcp.server.fastmcp import FastMCP

from . import _db, _ingest, _init, _purposes, _scope, _settings, _stats
from ._server_helpers import _err, _ok


_READY = False
_DB_PATH_STR = ""
try:
    _DB_PATH = _init._db_path()
    _DB_PATH_STR = str(_DB_PATH)
    _READY = _init.ready(_DB_PATH)
except Exception:
    _READY = False


_FULL_INSTRUCTIONS = """Claude Code session transcripts — projects, sessions, exchanges (user_msg + agent response groups). Reach for transcripts when the agent needs to inspect prior conversations, build time reports, extract chat slices, or persist per-exchange purpose summaries that survive future syncs.

Hierarchy: project → session → exchange. Default scope on `sessions_query` and `exchanges_query` is the current project; widen via `all_projects=true` or `project=...` filter.

Output verbosity is opt-in via `show` lists — defaults are lean (no chat content, no metrics, no timeframes). Pull what you need: `show=["messages"]` for chat replay, `show=["active"]` for engaged time, `show=["breakdown"]` for active + user/agent split, `show=["metrics"]` for the full hierarchy including idle/total.

Purposes are workflow artifacts persisted on the `exchanges` annotations table. When you read an exchange's content and would benefit from re-finding it later, write a one-line Purpose Statement-style summary via `purposes_set`. Purposes survive ingest and only `reset` wipes them.

For ad-hoc analyses not covered by the curated tools, `sql_query` accepts read-only SELECT statements against the live schema. Call `schema_describe` first to get table/view structure plus the gap_s and exchange-model semantics needed to write correct queries."""

_DORMANT_INSTRUCTIONS = "Transcripts is dormant — run /ocd:setup to enable."


mcp = FastMCP(
    "transcripts",
    instructions=_FULL_INSTRUCTIONS if _READY else _DORMANT_INSTRUCTIONS,
)


def _connect() -> sqlite3.Connection:
    """Open a read-write connection to the deployed transcripts DB."""
    conn = _db.get_connection(_DB_PATH_STR)
    _settings.init_settings(conn)
    return conn


def _connect_readonly() -> sqlite3.Connection:
    """Open a read-only connection to the deployed transcripts DB.

    Used by `sql_query` so the SQL the agent passes cannot mutate state
    regardless of what statement it tries — read-only is enforced at the
    connection level, not by SQL parsing.
    """
    return sqlite3.connect(f"file:{_DB_PATH_STR}?mode=ro", uri=True)


def _threshold_s(conn: sqlite3.Connection) -> float:
    return float(_settings.get(conn, "threshold_min")) * 60.0  # type: ignore[arg-type]


if _READY:

    # ============================================================
    # projects_* — project enumeration
    # ============================================================

    @mcp.tool()
    def projects_list() -> str:
        """List all projects in the transcripts DB with the current-project marker.

        Returns {current, projects: [...]}. `current` is the encoded name of
        the current project (CLAUDE_PROJECT_DIR with separators replaced by
        dashes); `projects` is the full set in the DB. Call before
        `sessions_query` or `exchanges_query` if you need to widen scope.
        """
        conn = _connect()
        try:
            _ingest.sync(conn, "")
            return _ok(_scope.projects(conn))
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    # ============================================================
    # sessions_* — session metadata retrieval
    # ============================================================

    @mcp.tool()
    def sessions_query(
        project: str = "",
        all_projects: bool = False,
        from_ts: str | None = None,
        to_ts: str | None = None,
        show: list[str] | None = None,
    ) -> str:
        """Sessions in scope, with optional date-range filter.

        Args:
            project: Filter by name substring (default: current project; ignored when all_projects=true).
            all_projects: When true, include every project in the DB.
            from_ts: ISO timestamp lower bound on session activity.
            to_ts: ISO timestamp upper bound on session activity.
            show: Detail buckets to include. Recognized: "timeframes" (adds
                first_ts/last_ts), "bytes" (adds bytes). Default is lean —
                {project, session, n_exchanges, n_purposed} per row.

        Returns {filter, n_sessions, sessions: [...]}.
        """
        conn = _connect()
        try:
            project_filter = "" if all_projects else (project or _db.current_project_name())
            _ingest.sync(conn, project_filter)
            return _ok(_scope.sessions(
                conn,
                project_filter=project_filter,
                from_ts=from_ts,
                to_ts=to_ts,
                show=show,
            ))
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    # ============================================================
    # exchanges_* — per-exchange retrieval
    # ============================================================

    @mcp.tool()
    def exchanges_query(
        project: str = "",
        all_projects: bool = False,
        session: str = "",
        range_from: int | None = None,
        range_to: int | None = None,
        from_ts: str | None = None,
        to_ts: str | None = None,
        show: list[str] | None = None,
    ) -> str:
        """Exchanges in scope, default-lean with `show` opt-ins.

        Scope precedence: session > all_projects > project > current project.

        Args:
            project: Filter by name substring (default: current project).
            all_projects: Include every project in the DB.
            session: Exact session id or unique prefix; takes precedence over project.
            range_from: Inclusive lower bound on exchange number (requires session).
            range_to: Inclusive upper bound on exchange number (requires session).
            from_ts: ISO timestamp lower bound on event activity.
            to_ts: ISO timestamp upper bound on event activity.
            show: Detail buckets. Recognized: "messages" (chat content),
                "active" (active_s only), "breakdown" (active_s + user_s/agent_s),
                "metrics" (full hierarchy: active_s + user_s/agent_s + total_s/idle_s),
                "timeframes" (exchange_start/exchange_end). Default lean —
                {project, session, exchange, purpose} per row.

        Returns array of exchange rows.
        """
        conn = _connect()
        try:
            if session:
                project_filter = ""
            elif all_projects:
                project_filter = ""
            else:
                project_filter = project or _db.current_project_name()
            _ingest.sync(conn, project_filter)
            return _ok(_scope.exchanges(
                conn, _threshold_s(conn),
                project_filter=project_filter,
                session_id=session,
                range_from=range_from,
                range_to=range_to,
                from_ts=from_ts,
                to_ts=to_ts,
                show=show,
            ))
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    # ============================================================
    # purposes_* — per-exchange purpose annotations
    # ============================================================

    @mcp.tool()
    def purposes_set(session: str, purposes: dict[int, str]) -> str:
        """Batch upsert per-exchange purpose summaries.

        A purpose is a Purpose Statement-style line — scope + role, no
        mechanics, no history. Persists across ingest; only `reset` wipes.

        Args:
            session: Session id or unique prefix.
            purposes: Map of exchange number → purpose text. Empty/whitespace
                values raise ValueError. Existing purposes are overwritten.

        Returns {session, written: {<exchange>: <trimmed_text>, ...}}.
        """
        conn = _connect()
        try:
            full_session = _scope.resolve_session(conn, session)
            written = _purposes.set_many(conn, full_session, purposes)
            return _ok({"session": full_session, "written": written})
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    @mcp.tool()
    def purposes_clear(session: str, exchanges: list[int]) -> str:
        """Batch clear per-exchange purpose summaries.

        Sets `purpose` and `purpose_updated_at` to NULL while preserving the
        annotations row so other annotation columns (when added) survive.

        Args:
            session: Session id or unique prefix.
            exchanges: Exchange numbers to clear. Exchanges with no stored
                purpose are silently skipped.

        Returns {session, cleared: [<exchange>, ...]}.
        """
        conn = _connect()
        try:
            full_session = _scope.resolve_session(conn, session)
            cleared = _purposes.clear_many(conn, full_session, exchanges)
            return _ok({"session": full_session, "cleared": cleared})
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    # ============================================================
    # settings_* — config + derived stats
    # ============================================================

    @mcp.tool()
    def settings_get(key: str = "") -> str:
        """Show config and derived stats. With key, return that single setting.

        Args:
            key: Optional setting key. When omitted, returns full
                {config, derived} envelope including avg_user_time_s.

        Returns dict.
        """
        conn = _connect()
        try:
            if key:
                return _ok({key: _settings.get(conn, key)})
            return _ok({
                "config": _settings.list_all(conn),
                "derived": {
                    "avg_user_time_s": {
                        "value": _stats.avg_user_time(conn, _threshold_s(conn)),
                        "description": _stats.AVG_USER_TIME_DESCRIPTION,
                    },
                },
            })
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    @mcp.tool()
    def settings_set(key: str, value: Any) -> str:
        """Update a setting. Returns the stored (typed) value.

        Args:
            key: Setting key (see settings_get for available keys).
            value: New value; coerced to the setting's declared SQL type.

        Returns {<key>: <stored_value>}.
        """
        conn = _connect()
        try:
            stored = _settings.set_value(conn, key, value)
            return _ok({key: stored})
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    # ============================================================
    # schema_* — introspection for sql_query authoring
    # ============================================================

    @mcp.tool()
    def schema_describe() -> str:
        """Live schema + semantics for writing `sql_query` statements.

        Returns:
            tables: {<name>: {columns, sql}}
            views:  {<name>: {columns, sql}}
            semantics: {exchange_model, time_accounting, gap_attribution, conservation}

        Read once at the start of an ad-hoc analysis. The semantics block
        explains gap_s attribution, exchange numbering, and the conservation
        property total_s = active_s + idle_s = user_s + agent_s + idle_s —
        knowledge required to write correct aggregating queries that the bare
        column listing cannot convey.
        """
        conn = _connect_readonly()
        try:
            tables: dict[str, Any] = {}
            views: dict[str, Any] = {}
            for name, type_, sql in conn.execute(
                "SELECT name, type, sql FROM sqlite_master "
                "WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' "
                "ORDER BY type, name"
            ).fetchall():
                cols = [
                    {"name": r[1], "type": r[2], "notnull": bool(r[3]), "pk": bool(r[5])}
                    for r in conn.execute(f"PRAGMA table_info({name})").fetchall()
                ]
                target = tables if type_ == "table" else views
                target[name] = {"columns": cols, "sql": sql}
            return _ok({
                "tables": tables,
                "views": views,
                "semantics": {
                    "exchange_model": (
                        "An exchange N is the set of events from user_msg N (start) "
                        "through the last event before user_msg N+1 (or session end). "
                        "Tied-timestamp user_msg events fold into one exchange "
                        "(slash-command pattern). queue-operation and sidechain_user_msg "
                        "events do not increment exchange — absorbed into the running one."
                    ),
                    "gap_attribution": (
                        "events_with_gaps.gap_s = seconds since prior event in same "
                        "parent_session, computed via LAG over (ts, file, line). "
                        "Each gap is owned by exactly one exchange. The user_msg event's "
                        "gap is the compose pause that produced this exchange; other "
                        "gaps are agent activity (or above-threshold idle)."
                    ),
                    "time_accounting": (
                        "Per exchange, threshold (default 15min, see settings_get) "
                        "partitions: user_s = user_msg gap when ≤ threshold else NULL; "
                        "agent_s = SUM(non-user_msg gap_s ≤ threshold); "
                        "idle_s = SUM(gap_s > threshold); "
                        "total_s = SUM(gap_s); active_s = (user_s or 0) + agent_s."
                    ),
                    "conservation": (
                        "For any exchange: total_s = user_s + agent_s + idle_s "
                        "(NULL user_s treated as 0). For any session: SUM(total_s) "
                        "across exchanges = MAX(ts) − MIN(ts). Pre-first-user_msg "
                        "events get exchange=0 and are excluded from accounting."
                    ),
                },
            })
        except Exception as e:
            return _err(e)
        finally:
            conn.close()

    @mcp.tool()
    def sql_query(sql: str, params: list[Any] | None = None, limit: int = 1000) -> str:
        """Execute a read-only SQL statement against the transcripts DB.

        Connection is opened in SQLite read-only mode (file:...?mode=ro) so
        writes are rejected at the engine level regardless of the SQL passed —
        no parsing, no authorizer, no bypass. Use for ad-hoc analyses not
        covered by the curated tools. Call `schema_describe` first.

        Args:
            sql: SELECT or WITH … SELECT statement. Multi-statement input is
                rejected by sqlite3.execute (one statement per call).
            params: Optional positional parameters for ? placeholders.
            limit: Cap on returned rows (default 1000). Apply LIMIT in your
                SQL if you need different row-set semantics.

        Returns {columns: [...], rows: [{...}], n_rows, truncated}.
        """
        conn = _connect_readonly()
        try:
            cursor = conn.execute(sql, tuple(params or ()))
            cols = [d[0] for d in cursor.description] if cursor.description else []
            rows: list[dict[str, Any]] = []
            for r in cursor:
                rows.append(dict(zip(cols, r, strict=False)))
                if len(rows) >= limit:
                    break
            truncated = cursor.fetchone() is not None
            return _ok({
                "columns": cols,
                "rows": rows,
                "n_rows": len(rows),
                "truncated": truncated,
            })
        except Exception as e:
            return _err(e)
        finally:
            conn.close()


if __name__ == "__main__":
    mcp.run()
