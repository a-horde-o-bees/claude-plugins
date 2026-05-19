"""transcripts infrastructure.

Initialize the transcripts database and report DB health. Data is the
events table populated from Claude Code JSONL transcripts under
`~/.claude/projects/<project>/`. Re-runs of ingest only add newly-appended
lines (PK is `(file, line)`, JSONL is append-only). Settings and derived
stats are queryable independently; see `_settings` and `_stats`.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

import sqlite3
import shutil
from pathlib import Path

from . import _db, _settings
from . import _environment as environment
from . import _schema as dbtools
from ._errors import NotReadyError


def _db_path() -> Path:
    return (
        environment.get_project_dir()
        / ".claude"
        / "transcripts"
        / "transcripts.db"
    )


def _legacy_db_path() -> Path:
    """One-time migration source — the path used when transcripts lived under
    the ocd plugin's namespace. If the new path is absent and this is present,
    init moves it before rectifying.
    """
    return (
        environment.get_project_dir()
        / ".claude"
        / "ocd"
        / "transcripts"
        / "transcripts.db"
    )


def _db_rel_path() -> str:
    return ".claude/transcripts/transcripts.db"


def _build_schema(target_path: str) -> None:
    """Build the canonical schema at target_path. Used by _schema.rectify."""
    _db.init_db(target_path)
    conn = _db.get_connection(target_path)
    try:
        _settings.init_settings(conn)
    finally:
        conn.close()


def _maybe_migrate_legacy_db() -> dict | None:
    """Move a pre-migration DB from the old ocd-plugin path into the new path.

    Triggered when the new path is absent and the old path exists. Idempotent —
    after the move, the legacy path no longer exists. Returns a `files` entry
    describing the move, or None if no migration was needed.
    """
    new = _db_path()
    old = _legacy_db_path()
    if new.exists() or not old.exists():
        return None
    new.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(old), str(new))
    return {
        "path": _db_rel_path(),
        "before": "absent",
        "after": "migrated from .claude/ocd/transcripts/transcripts.db",
    }


def ready(db_path: Path | None = None) -> bool:
    """Return True when the DB structurally matches the canonical schema."""
    target = db_path if db_path is not None else _db_path()
    return target.exists() and dbtools.matches_expected(target, _build_schema)


def ensure_ready(db_path: Path | None = None) -> None:
    """Raise NotReadyError when transcripts is not operational."""
    if not ready(db_path):
        raise NotReadyError(
            "transcripts is dormant — run `python -m scripts reset` from the "
            "skill directory to initialize (or `init --force` if a divergent "
            "schema is blocking)."
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
    files: list[dict] = []
    migrated = _maybe_migrate_legacy_db()
    if migrated:
        files.append(migrated)
    files.extend(dbtools.rectify(
        _db_path(), _build_schema, _db_rel_path(), force=force,
    ))
    return {"files": files, "extra": _status_extra(_db_path())}


def reset() -> dict:
    """Backup, wipe, and rebuild — the explicit destructive verb."""
    files: list[dict] = []
    migrated = _maybe_migrate_legacy_db()
    if migrated:
        files.append(migrated)
    files.extend(dbtools.reset_db(_db_path(), _build_schema, _db_rel_path()))
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
