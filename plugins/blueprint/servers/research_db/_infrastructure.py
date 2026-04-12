"""Infrastructure tools — database initialization and schema discovery."""

from __future__ import annotations

import json

from . import _helpers
from ._helpers import _check_db, _ok, _err

from skills.research import _db as core


def init_database() -> str:
    """Initialize research database. Creates schema if database doesn't exist. Idempotent — safe to call on existing database."""
    result = core.init_db(_helpers.DB_PATH)
    return _ok(result)


def describe_schema(table: str | None = None) -> str:
    """Discover database schema — tables, columns, types, and FK relationships.

    Args:
        table: Specific table to describe (optional; omit for all tables)
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    all_tables = {
        r["name"] for r in
        conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'").fetchall()
    }
    try:
        if table:
            if table not in all_tables:
                return _err(ValueError(f"Unknown table: {table}. Valid: {', '.join(sorted(all_tables))}"))
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            fks = conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
            return json.dumps({
                "table": table,
                "columns": [{"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"]), "default": c["dflt_value"]} for c in columns],
                "foreign_keys": [{"column": fk["from"], "references": f"{fk['table']}.{fk['to']}"} for fk in fks],
            })

        result = {}
        for t in sorted(all_tables):
            columns = conn.execute(f"PRAGMA table_info({t})").fetchall()
            result[t] = {
                "columns": [{"name": c["name"], "type": c["type"]} for c in columns],
            }
        return json.dumps(result)
    finally:
        conn.close()
