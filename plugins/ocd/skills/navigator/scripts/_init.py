"""Navigator initialization and status.

Database creation, seed rule deployment, and infrastructure health checks.
"""

import logging
import os
import sqlite3
from pathlib import Path

try:
    from ._db import init_db, get_connection
except ImportError:
    from _db import init_db, get_connection  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


def get_project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_db_path(project_dir: Path) -> Path:
    return project_dir / ".claude" / "ocd" / "navigator" / "navigator.db"


def init(project_dir: Path) -> list[str]:
    """Initialize navigator database. Returns status lines."""
    db_path = get_db_path(project_dir)
    result = init_db(str(db_path))
    return [result]


def status(project_dir: Path) -> dict:
    """Check navigator infrastructure state.

    Returns dict with:
    - state: "operational" | "adopted" | "error"
    - details: list of human-readable status lines
    - actions: list of actionable commands
    """
    db_path = get_db_path(project_dir)

    if not db_path.exists():
        return {
            "state": "adopted",
            "details": ["Database: not found"],
            "actions": ["Run /ocd-init to create navigator database"],
        }

    try:
        conn = get_connection(str(db_path))

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='entries'",
        ).fetchone()
        if not tables:
            conn.close()
            return {
                "state": "error",
                "details": ["Database: missing entries table"],
                "actions": ["Run /ocd-init to reinitialize navigator database"],
            }

        total = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE path NOT LIKE '%*%'",
        ).fetchone()["c"]

        if total == 0:
            conn.close()
            return {
                "state": "adopted",
                "details": ["Database: ready", "Entries: none (scan needed)"],
                "actions": ["Run /ocd-navigator to scan and describe project"],
            }

        undescribed = conn.execute(
            "SELECT COUNT(*) as c FROM entries "
            "WHERE path NOT LIKE '%*%' AND description IS NULL",
        ).fetchone()["c"]

        stale = conn.execute(
            "SELECT COUNT(*) as c FROM entries "
            "WHERE path NOT LIKE '%*%' AND stale = 1",
        ).fetchone()["c"]

        conn.close()

        details = [f"Entries: {total} total, {undescribed} undescribed, {stale} stale"]
        actions = []

        if undescribed > 0 or stale > 0:
            parts = []
            if undescribed > 0:
                parts.append(f"describe {undescribed} entries")
            if stale > 0:
                parts.append(f"review {stale} stale entries")
            actions.append(f"Run /ocd-navigator to {' and '.join(parts)}")

        return {
            "state": "operational",
            "details": details,
            "actions": actions,
        }

    except sqlite3.Error as e:
        return {
            "state": "error",
            "details": [f"Database: {e}"],
            "actions": ["Run /ocd-init to reinitialize navigator database"],
        }
