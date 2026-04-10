"""Decisions database infrastructure.

Schema, connection factory, and regex support for search.
"""

import re
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS decisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  summary TEXT NOT NULL,
  detail_md TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode for concurrent access."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    conn.create_function(
        "regexp", 2, lambda pattern, text: bool(re.search(pattern, text or ""))
    )
    conn.executescript(SCHEMA)
    return conn
