"""Research skill infrastructure.

Initialize research database and check DB health.
Interface contract: init() and status() return {"files": [...], "extra": [...]}.
"""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from . import _db as db

logger = logging.getLogger(__name__)


DB_REL_PATH = "blueprint/data/research.db"


def _db_path(project_dir: Path) -> Path:
    return project_dir / DB_REL_PATH


def _status_extra(project_dir: Path) -> list[dict]:
    """Check DB health and return extra lines."""
    path = _db_path(project_dir)

    if not path.exists():
        return [
            {"label": "overall status", "value": "not initialized"},
            {"label": "action needed", "value": "/blueprint-init"},
        ]

    try:
        conn = db.get_connection(str(path))

        expected_tables = {"entities", "entity_urls", "url_provenance", "entity_notes", "entity_measures", "entity_source_data"}
        actual_tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'",
        ).fetchall()}
        if not expected_tables.issubset(actual_tables):
            conn.close()
            return [
                {"label": "overall status", "value": "error \u2014 divergent schema"},
                {"label": "action needed", "value": "/blueprint-init --force"},
            ]

        total = conn.execute("SELECT COUNT(*) as c FROM entities").fetchone()["c"]
        researched = conn.execute(
            "SELECT COUNT(*) as c FROM entities WHERE stage = 'researched'",
        ).fetchone()["c"]
        new = conn.execute(
            "SELECT COUNT(*) as c FROM entities WHERE stage = 'new'",
        ).fetchone()["c"]
        notes = conn.execute("SELECT COUNT(*) as c FROM entity_notes").fetchone()["c"]

        conn.close()

        extra = [{"label": "overall status", "value": f"operational \u2014 {total} entities, {researched} researched, {new} new, {notes} notes"}]

        extra.append({"label": "action needed", "value": "/blueprint-research"})

        return extra

    except sqlite3.Error as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "/blueprint-init --force"},
        ]


def init(plugin_root: Path, project_dir: Path, force: bool = False) -> dict:
    """Initialize research database. Returns {files, extra}."""
    path = _db_path(project_dir)

    before = "current" if path.exists() else "absent"

    if force and path.exists():
        path.unlink()
        before = "absent"

    path.parent.mkdir(parents=True, exist_ok=True)
    db.init_db(str(path))

    after = "current"
    files = [{"path": DB_REL_PATH, "before": before, "after": after}]

    extra = [{"label": "overall status", "value": "initialized"}]

    status_extra = _status_extra(project_dir)
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status(plugin_root: Path, project_dir: Path) -> dict:
    """Check research DB state. Returns {files, extra}."""
    path = _db_path(project_dir)

    state = "current" if path.exists() else "absent"
    files = [{"path": DB_REL_PATH, "before": state, "after": state}]

    extra = _status_extra(project_dir)
    return {"files": files, "extra": extra}
