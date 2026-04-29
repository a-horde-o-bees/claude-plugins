"""transcripts CLI.

Thin agent-debug surface mirroring the MCP server's tools. Each verb maps
1:1 to an MCP tool of the same name (e.g. `sessions` → `sessions_query`).
JSON output throughout — agent-consumable. Each verb except `reset`
requires the DB to be ready (initialized via `/ocd:setup init`).

Verbs:
    projects                                                                  All projects, current marked
    sessions   [--project X | --all-projects] [--from D --to D] [--show ...]  Sessions in scope
    exchanges  [--project X | --session Y [--range R] | --all-projects]
               [--from D --to D] [--show ...]                                 Per-exchange rows; default lean
    purposes-set    <session> <json>                                          Batch upsert purposes
    purposes-clear  <session> <exchange1> [<exchange2> ...]                   Batch clear purposes
    settings   [<key> [<value>]]                                              Config + derived stats
    reset                                                                     Backup + wipe DB

Scope precedence on `exchanges`: --session > --all-projects > --project >
current project (default). Date filters apply on top of any scope filter.
The `--show` flag accepts space-separated bucket names; see
`SHOW_EXCHANGES` / `SHOW_SESSIONS` in `_scope.py` for the recognized values.
"""

import argparse
import json
import sqlite3
import sys

from tools.errors import InitError, NotReadyError

from . import _db, _ingest, _init, _purposes, _scope, _settings, _stats


def _connect() -> sqlite3.Connection:
    """Return a connection to the deployed transcripts database.

    Ensures readiness first — if the DB is absent or has a divergent
    schema, raises NotReadyError so the CLI catch-and-format path runs.
    """
    _init.ensure_ready()
    conn = _db.get_connection(str(_init._db_path()))
    _settings.init_settings(conn)
    return conn


def cmd_projects(_args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        _ingest.sync(conn, "")
        print(json.dumps(_scope.projects(conn), indent=2))
    finally:
        conn.close()
    return 0


def cmd_sessions(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        project_filter = "" if args.all_projects else (args.project or _db.current_project_name())
        _ingest.sync(conn, project_filter)
        data = _scope.sessions(
            conn,
            project_filter=project_filter,
            from_ts=args.from_ts or None,
            to_ts=args.to_ts or None,
            show=args.show or None,
        )
        print(json.dumps(data, indent=2))
    finally:
        conn.close()
    return 0


def cmd_exchanges(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        threshold_min = _settings.get(conn, "threshold_min")
        threshold_s = float(threshold_min) * 60.0  # type: ignore[arg-type]

        if args.session:
            project_filter = ""
            session_id = args.session
        elif args.all_projects:
            project_filter = ""
            session_id = ""
        else:
            project_filter = args.project or _db.current_project_name()
            session_id = ""

        _ingest.sync(conn, project_filter)

        range_from: int | None = None
        range_to: int | None = None
        if args.range:
            if "-" in args.range:
                rf, rt = args.range.split("-", 1)
                range_from = int(rf)
                range_to = int(rt)
            else:
                range_from = range_to = int(args.range)

        data = _scope.exchanges(
            conn, threshold_s,
            project_filter=project_filter,
            session_id=session_id,
            range_from=range_from,
            range_to=range_to,
            from_ts=args.from_ts or None,
            to_ts=args.to_ts or None,
            show=args.show or None,
        )
        print(json.dumps(data, indent=2))
    finally:
        conn.close()
    return 0


def cmd_settings(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        if args.key and args.value is not None:
            stored = _settings.set_value(conn, args.key, args.value)
            print(json.dumps({args.key: stored}, indent=2))
            return 0
        if args.key:
            print(json.dumps({args.key: _settings.get(conn, args.key)}, indent=2))
            return 0
        threshold_min = _settings.get(conn, "threshold_min")
        threshold_s = float(threshold_min) * 60.0  # type: ignore[arg-type]
        out = {
            "config": _settings.list_all(conn),
            "derived": {
                "avg_user_time_s": {
                    "value": _stats.avg_user_time(conn, threshold_s),
                    "description": _stats.AVG_USER_TIME_DESCRIPTION,
                },
            },
        }
        print(json.dumps(out, indent=2))
    finally:
        conn.close()
    return 0


def cmd_purposes_set(args: argparse.Namespace) -> int:
    """Batch upsert purposes from a JSON object: {"<exchange>": "<text>", ...}."""
    try:
        raw = json.loads(args.purposes)
    except json.JSONDecodeError as exc:
        raise ValueError(f"--purposes must be valid JSON: {exc}") from exc
    if not isinstance(raw, dict):
        raise ValueError("--purposes must be a JSON object mapping exchange numbers to text")
    purposes_map: dict[int, str] = {}
    for k, v in raw.items():
        try:
            purposes_map[int(k)] = v
        except (TypeError, ValueError) as exc:
            raise ValueError(f"exchange key '{k}' is not an integer") from exc

    conn = _connect()
    try:
        session = _scope.resolve_session(conn, args.session_id)
        written = _purposes.set_many(conn, session, purposes_map)
        print(json.dumps({"session": session, "written": written}, indent=2))
    finally:
        conn.close()
    return 0


def cmd_purposes_clear(args: argparse.Namespace) -> int:
    conn = _connect()
    try:
        session = _scope.resolve_session(conn, args.session_id)
        cleared = _purposes.clear_many(conn, session, args.exchanges)
        print(json.dumps({"session": session, "cleared": cleared}, indent=2))
    finally:
        conn.close()
    return 0


def cmd_reset(_args: argparse.Namespace) -> int:
    """Reset the transcripts DB. Skips ensure_ready since we're rebuilding."""
    result = _init.reset()
    print(json.dumps(result, indent=2))
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(
        prog="transcripts",
        description=(__doc__ or "").split("\n\n")[0],
    )
    sub = ap.add_subparsers(dest="verb", required=True)

    p_projects = sub.add_parser("projects", help="All projects with current marker")
    p_projects.set_defaults(func=cmd_projects)

    p_sessions = sub.add_parser("sessions", help="Sessions in scope")
    p_sessions.add_argument("--project", default="", help="Filter by name substring (default: current project)")
    p_sessions.add_argument("--all-projects", action="store_true", help="Include every project")
    p_sessions.add_argument("--from", dest="from_ts", default="", help="ISO timestamp lower bound")
    p_sessions.add_argument("--to", dest="to_ts", default="", help="ISO timestamp upper bound")
    p_sessions.add_argument("--show", nargs="*", default=[],
                            help="Add detail buckets: timeframes, bytes")
    p_sessions.set_defaults(func=cmd_sessions)

    p_exchanges = sub.add_parser("exchanges", help="Exchanges with optional metrics + messages")
    p_exchanges.add_argument("--project", default="", help="Filter by name substring (default: current project)")
    p_exchanges.add_argument("--all-projects", action="store_true", help="Include every project")
    p_exchanges.add_argument("--session", default="", help="Exact session id or unique prefix")
    p_exchanges.add_argument("--range", default="", help="Exchange number ('5') or range ('5-10'); requires --session")
    p_exchanges.add_argument("--from", dest="from_ts", default="", help="ISO timestamp lower bound")
    p_exchanges.add_argument("--to", dest="to_ts", default="", help="ISO timestamp upper bound")
    p_exchanges.add_argument("--show", nargs="*", default=[],
                            help="Add detail buckets: messages, active, breakdown, metrics, timeframes")
    p_exchanges.set_defaults(func=cmd_exchanges)

    p_settings = sub.add_parser("settings", help="Show/set config; lists derived stats")
    p_settings.add_argument("key", nargs="?", default="")
    p_settings.add_argument("value", nargs="?", default=None)
    p_settings.set_defaults(func=cmd_settings)

    p_purposes_set = sub.add_parser("purposes-set", help="Batch upsert per-exchange purposes")
    p_purposes_set.add_argument("session_id", help="Session ID or unique prefix")
    p_purposes_set.add_argument(
        "purposes",
        help='JSON object mapping exchange numbers to purpose text (e.g. \'{"5": "...", "12": "..."}\')',
    )
    p_purposes_set.set_defaults(func=cmd_purposes_set)

    p_purposes_clear = sub.add_parser("purposes-clear", help="Batch clear per-exchange purposes")
    p_purposes_clear.add_argument("session_id", help="Session ID or unique prefix")
    p_purposes_clear.add_argument(
        "exchanges", nargs="+", type=int,
        help="Exchange numbers to clear (one or more)",
    )
    p_purposes_clear.set_defaults(func=cmd_purposes_clear)

    p_reset = sub.add_parser("reset", help="Backup and wipe the DB")
    p_reset.set_defaults(func=cmd_reset)

    args = ap.parse_args()

    try:
        rc = args.func(args)
        sys.exit(rc)
    except (LookupError, ValueError, KeyError, NotReadyError, InitError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
