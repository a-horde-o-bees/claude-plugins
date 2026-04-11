"""Log subsystem infrastructure.

Implements the init() and status() contract consumed by the plugin init
orchestrator. Bootstraps the log database on first init and seeds the
default types. Reports operational health via type/record/tag counts.
"""

import sqlite3
from pathlib import Path

import plugin

from . import type_add, type_list
from ._db import get_connection
from .default_types import DEFAULT_TYPES

_EXPECTED_TABLES = {"types", "records", "tags", "record_tags"}


def _plugin_name() -> str:
    return plugin.get_plugin_name(plugin.get_plugin_root())


def _db_path() -> Path:
    return (
        plugin.get_project_dir()
        / ".claude"
        / _plugin_name()
        / "log"
        / "log.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/log/log.db"


def _bootstrap_defaults(db_path: str) -> None:
    """Insert default types if the types table is empty.

    Idempotent: when any type already exists, this is a no-op. Existing user
    edits to type instructions survive re-init because this is an insert, not
    an upsert — defaults only populate empty state.
    """
    existing = {t["name"] for t in type_list(db_path)["types"]}
    for entry in DEFAULT_TYPES:
        if entry["name"] in existing:
            continue
        type_add(db_path, name=entry["name"], instructions=entry["instructions"])


def _status_extra() -> list[dict]:
    """Check log DB health and return extra status lines."""
    db = _db_path()

    if not db.exists():
        return [
            {"label": "overall status", "value": "not initialized"},
            {"label": "action needed", "value": "/init"},
        ]

    try:
        conn = get_connection(str(db))

        actual_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
        }
        if not _EXPECTED_TABLES.issubset(actual_tables):
            conn.close()
            return [
                {"label": "overall status", "value": "error \u2014 divergent schema"},
                {"label": "action needed", "value": "/init --force --system log"},
            ]

        type_count = conn.execute("SELECT COUNT(*) FROM types").fetchone()[0]
        record_count = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        tag_count = conn.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
        conn.close()

        return [
            {
                "label": "overall status",
                "value": (
                    f"operational \u2014 {type_count} types, "
                    f"{record_count} records, {tag_count} tags"
                ),
            },
            {"label": "action needed", "value": "/log"},
        ]

    except sqlite3.Error as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "/init --force --system log"},
        ]


def init(force: bool = False) -> dict:
    """Initialize the log database and seed default types.

    Returns {"files": [...], "extra": [...]}.
    """
    db = _db_path()
    rel_path = _db_rel_path()

    before = "current" if db.exists() else "absent"

    if force and db.exists():
        db.unlink()
        before = "absent"

    conn = get_connection(str(db))
    conn.close()
    _bootstrap_defaults(str(db))

    files = [{"path": rel_path, "before": before, "after": "current"}]
    extra = [{"label": "overall status", "value": "initialized"}]

    status_extra = _status_extra()
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status() -> dict:
    """Report log infrastructure state.

    Returns {"files": [...], "extra": [...]}.
    """
    db = _db_path()
    rel_path = _db_rel_path()

    state = "current" if db.exists() else "absent"
    files = [{"path": rel_path, "before": state, "after": state}]
    extra = _status_extra()
    return {"files": files, "extra": extra}
