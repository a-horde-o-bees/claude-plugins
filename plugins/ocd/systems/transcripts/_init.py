"""transcripts infrastructure.

Initialize the transcripts database and report DB health. Data is the events
table populated from Claude Code JSONL transcripts under
`~/.claude/projects/<project>/`. Re-runs of ingest only add newly-appended
lines (PK is `(file, line)`, JSONL is append-only). Settings and derived
stats are queryable independently; see `_settings` and `_stats`.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

from systems import setup
from tools import db as dbtools
from tools import environment
from tools.errors import NotReadyError

from . import _db, _settings


def _plugin_name() -> str:
    return setup.get_plugin_name(environment.get_plugin_root())


def _db_path() -> Path:
    return (
        environment.get_project_dir()
        / ".claude"
        / _plugin_name()
        / "transcripts"
        / "transcripts.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/transcripts/transcripts.db"


def _build_schema(target_path: str) -> None:
    """Build the canonical schema at target_path. Used by tools.db.rectify.

    Includes both the events table/views (from `_db.init_db`) and the
    settings table (from `_settings.init_settings`), so the schema
    fingerprint reflects the full deployed shape.
    """
    _db.init_db(target_path)
    conn = _db.get_connection(target_path)
    try:
        _settings.init_settings(conn)
    finally:
        conn.close()


def ready(db_path: Path | None = None) -> bool:
    """Return True when the DB structurally matches the canonical schema."""
    target = db_path if db_path is not None else _db_path()
    return target.exists() and dbtools.matches_expected(target, _build_schema)


def ensure_ready(db_path: Path | None = None) -> None:
    """Raise NotReadyError when transcripts is not operational."""
    if not ready(db_path):
        raise NotReadyError(
            "transcripts is dormant — run /ocd:setup init to initialize."
        )


def _status_extra(db_path: Path) -> list[dict]:
    """Overall status + coverage metrics when operational."""
    if not db_path.exists():
        return [{"label": "overall status", "value": "not initialized"}]
    if not ready(db_path):
        return [{"label": "overall status", "value": "error — divergent schema"}]
    try:
        conn = _db.get_connection(str(db_path))
        n_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        n_sessions = conn.execute(
            "SELECT COUNT(DISTINCT parent_session) FROM events"
        ).fetchone()[0]
        n_projects = conn.execute(
            "SELECT COUNT(DISTINCT project_name) FROM events"
        ).fetchone()[0]
        conn.close()
        return [
            {
                "label": "overall status",
                "value": (
                    f"operational — {n_events} events, "
                    f"{n_sessions} sessions, {n_projects} projects"
                ),
            },
        ]
    except sqlite3.Error as e:
        return [{"label": "overall status", "value": f"error — {e}"}]


def init(force: bool = False) -> dict:
    """Rectify the transcripts database to the canonical schema."""
    files = dbtools.rectify(
        _db_path(), _build_schema, _db_rel_path(), force=force,
    )
    return {"files": files, "extra": _status_extra(_db_path())}


def reset() -> dict:
    """Backup, wipe, and rebuild — the explicit destructive verb."""
    files = dbtools.reset_db(_db_path(), _build_schema, _db_rel_path())
    return {"files": files, "extra": _status_extra(_db_path())}


def status() -> dict:
    """Report DB schema state and ingestion coverage."""
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
