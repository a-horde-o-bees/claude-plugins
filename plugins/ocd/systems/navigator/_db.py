"""Navigator database infrastructure.

Schema, connection factory, and initialization. Pattern data loads at
scan time from deployed paths.csv files (via _scanner); init_db only
creates tables and seeds baseline config.
"""

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS paths (
    path TEXT PRIMARY KEY,
    parent_path TEXT,
    entry_type TEXT CHECK (entry_type IN ('file', 'directory')),
    exclude INTEGER NOT NULL DEFAULT 0,
    traverse INTEGER NOT NULL DEFAULT 1,
    purpose TEXT,
    git_hash TEXT,
    stale INTEGER NOT NULL DEFAULT 0,
    line_count INTEGER,
    char_count INTEGER
);

CREATE INDEX IF NOT EXISTS idx_paths_parent ON paths(parent_path);

CREATE TABLE IF NOT EXISTS path_patterns (
    pattern TEXT PRIMARY KEY,
    entry_type TEXT CHECK (entry_type IN ('file', 'directory')),
    exclude INTEGER NOT NULL DEFAULT 0,
    traverse INTEGER NOT NULL DEFAULT 1,
    purpose TEXT
);

CREATE TABLE IF NOT EXISTS path_pattern_sources (
    source_path TEXT PRIMARY KEY,
    content_hash TEXT NOT NULL,
    loaded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode for concurrent access."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> str:
    """Create database with schema and baseline config.

    Idempotent — safe to rerun. Schema creation uses IF NOT EXISTS; config
    seeding uses INSERT OR IGNORE. Path pattern data is not loaded here —
    _scanner consolidates from deployed paths.csv files at scan time.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    try:
        conn.executescript(SCHEMA)

        for key, value in [
            ("lines_warn_threshold", "500"),
            ("lines_fail_threshold", "2000"),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
                (key, value),
            )

        conn.commit()
        return f"Initialized: {path}"
    finally:
        conn.close()
