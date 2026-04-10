"""Friction database infrastructure.

Schema, connection factory, and system name validation.
"""

import re
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS friction_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  system TEXT NOT NULL,
  summary TEXT NOT NULL,
  detail_md TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_friction_system ON friction_entries(system);
"""

_SAFE_SYSTEM_RE = re.compile(r"^[a-zA-Z0-9_][a-zA-Z0-9_\-]*$")


def _validate_system(system: str) -> None:
    """Raise ValueError if system name contains invalid characters."""
    if not _SAFE_SYSTEM_RE.match(system):
        raise ValueError(
            f"Invalid system name: {system!r}. "
            "Use alphanumerics, underscore, or dash; no path separators."
        )


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode for concurrent access."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    conn.create_function(
        "regexp", 2, lambda pattern, text: bool(re.search(pattern, text or "", re.IGNORECASE))
    )
    conn.executescript(SCHEMA)
    return conn
