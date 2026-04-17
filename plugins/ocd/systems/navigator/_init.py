"""Navigator skill infrastructure.

Initialize the navigator database (entries and pattern tables) and
report DB health. Governance (rules, conventions, dependency graph)
is owned by the separate governance skill and initialized there.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

import plugin

from . import _db


def _plugin_name() -> str:
    return plugin.get_plugin_name(plugin.get_plugin_root())


def _db_path() -> Path:
    return (
        plugin.get_project_dir()
        / ".claude"
        / _plugin_name()
        / "navigator"
        / "navigator.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/navigator/navigator.db"


def _status_extra() -> list[dict]:
    """Check DB health and return the overall status line."""
    db_path = _db_path()

    if not db_path.exists():
        return [{"label": "overall status", "value": "not initialized"}]

    try:
        conn = _db.get_connection(str(db_path))

        expected_tables = {"entries", "patterns", "config"}
        actual_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
        }
        if not expected_tables.issubset(actual_tables):
            conn.close()
            return [{"label": "overall status", "value": "error \u2014 divergent schema"}]

        total = conn.execute(
            "SELECT COUNT(*) as c FROM entries",
        ).fetchone()["c"]

        undescribed = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE description IS NULL",
        ).fetchone()["c"]

        stale = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE stale = 1",
        ).fetchone()["c"]

        conn.close()

        return [
            {
                "label": "overall status",
                "value": (
                    f"operational \u2014 {total} entries, "
                    f"{undescribed} undescribed, {stale} stale"
                ),
            },
        ]

    except sqlite3.Error as e:
        return [{"label": "overall status", "value": f"error \u2014 {e}"}]


def init(force: bool = False) -> dict:
    """Initialize the navigator database.

    Captures the DB's state before any mutation so the reported transition
    reflects what the user saw, not the intermediate wipe state. A
    force-rebuild of an existing DB emits `current → reinstalled`; a
    fresh install emits `absent → current`.
    """
    db = _db_path()
    rel_path = _db_rel_path()

    existed_before = db.exists()
    before = "current" if existed_before else "absent"

    if force and existed_before:
        db.unlink()

    _db.init_db(str(db))

    after = "reinstalled" if existed_before and force else "current"

    files = [{"path": rel_path, "before": before, "after": after}]
    extra = _status_extra()

    return {"files": files, "extra": extra}


def status() -> dict:
    """Check navigator DB state."""
    db = _db_path()
    rel_path = _db_rel_path()

    state = "current" if db.exists() else "absent"
    files = [{"path": rel_path, "before": state, "after": state}]

    extra = _status_extra()
    return {"files": files, "extra": extra}
