"""needs-map infrastructure.

Initialize the needs-map database and report DB health. Data is
accumulated evaluation work — not regenerable by scan. The
schema-aware init contract is owned by `tools.db.rectify`; this module
declares where the DB lives and what schema it should have, then
composes the helper the same way file-backed systems compose
`setup.deploy_files`.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

from systems import setup
from tools import db as dbtools
from tools import environment
from tools.errors import NotReadyError

from . import _db


def _plugin_name() -> str:
    return setup.get_plugin_name(environment.get_plugin_root())


def _db_path() -> Path:
    return (
        environment.get_project_dir()
        / ".claude"
        / _plugin_name()
        / "needs-map"
        / "needs-map.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/needs-map/needs-map.db"


def _build_schema(target_path: str) -> None:
    """Build the canonical schema at target_path. Used by tools.db.rectify."""
    _db.init_db(target_path)


def ready(db_path: Path | None = None) -> bool:
    """Return True when the DB structurally matches the canonical schema."""
    target = db_path if db_path is not None else _db_path()
    return target.exists() and dbtools.matches_expected(target, _build_schema)


def ensure_ready(db_path: Path | None = None) -> None:
    """Raise NotReadyError when needs-map is not operational."""
    if not ready(db_path):
        raise NotReadyError(
            "needs-map is dormant — run /ocd:setup init to initialize."
        )


def _status_extra(db_path: Path) -> list[dict]:
    """Overall status + coverage metrics when operational."""
    if not db_path.exists():
        return [{"label": "overall status", "value": "not initialized"}]
    if not ready(db_path):
        return [{"label": "overall status", "value": "error — divergent schema"}]

    try:
        conn = _db.get_connection(str(db_path))
        comp_count = conn.execute("SELECT COUNT(*) FROM components").fetchone()[0]
        need_count = conn.execute("SELECT COUNT(*) FROM needs").fetchone()[0]
        addr_count = conn.execute("SELECT COUNT(*) FROM addresses").fetchone()[0]
        gap_count = conn.execute(
            """
            SELECT COUNT(*) FROM needs n
            WHERE n.parent_id IS NOT NULL
              AND NOT EXISTS (SELECT 1 FROM needs c WHERE c.parent_id = n.id)
              AND NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
            """
        ).fetchone()[0]
        conn.close()
        return [
            {
                "label": "overall status",
                "value": (
                    f"operational — {comp_count} components, "
                    f"{need_count} needs, {addr_count} addressing edges, "
                    f"{gap_count} gaps"
                ),
            },
        ]
    except sqlite3.Error as e:
        return [{"label": "overall status", "value": f"error — {e}"}]


def init(force: bool = False) -> dict:
    """Rectify the needs-map database to the canonical schema."""
    files = dbtools.rectify(
        _db_path(), _build_schema, _db_rel_path(), force=force,
    )
    return {"files": files, "extra": _status_extra(_db_path())}


def reset() -> dict:
    """Backup, wipe, and rebuild — the explicit destructive verb."""
    files = dbtools.reset_db(_db_path(), _build_schema, _db_rel_path())
    return {"files": files, "extra": _status_extra(_db_path())}


def status() -> dict:
    """Report DB schema state and evaluation coverage."""
    db = _db_path()
    rel_path = _db_rel_path()

    if not db.exists():
        state = "absent"
    elif ready(db):
        state = "current"
    else:
        state = "divergent"

    files = [{"path": rel_path, "before": state, "after": state}]
    extra = _status_extra(db)
    return {"files": files, "extra": extra}
