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
    """Check DB health and return extra lines."""
    db_path = _db_path()

    if not db_path.exists():
        return [
            {"label": "overall status", "value": "not initialized"},
            {"label": "action needed", "value": "/init"},
        ]

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
            return [
                {"label": "overall status", "value": "error \u2014 divergent schema"},
                {"label": "action needed", "value": "/init --force"},
            ]

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
            {"label": "action needed", "value": "/navigator"},
        ]

    except sqlite3.Error as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "/init --force"},
        ]


def init(force: bool = False) -> dict:
    """Initialize the navigator database."""
    db = _db_path()
    rel_path = _db_rel_path()

    before = "current" if db.exists() else "absent"

    if force and db.exists():
        db.unlink()
        before = "absent"

    result_msg = _db.init_db(str(db))

    summary = ""
    if "(seed rules:" in result_msg:
        seed_part = result_msg.split("(seed rules: ")[1].rstrip(")")
        summary = f"initialized \u2014 seed rules: {seed_part}"
    elif "(no seed file)" in result_msg:
        summary = "initialized \u2014 no seed file"
    else:
        summary = "initialized"

    files = [{"path": rel_path, "before": before, "after": "current"}]
    extra = [{"label": "overall status", "value": summary}]

    status_extra = _status_extra()
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status() -> dict:
    """Check navigator DB state."""
    db = _db_path()
    rel_path = _db_rel_path()

    state = "current" if db.exists() else "absent"
    files = [{"path": rel_path, "before": state, "after": state}]

    extra = _status_extra()
    return {"files": files, "extra": extra}
