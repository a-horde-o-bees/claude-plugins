"""Navigator database infrastructure.

Schema, migrations, connection factory, and initialization with seed patterns.
"""

import csv
import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS entries (
    path TEXT PRIMARY KEY,
    parent_path TEXT,
    entry_type TEXT CHECK (entry_type IN ('file', 'directory')),
    exclude INTEGER NOT NULL DEFAULT 0,
    traverse INTEGER NOT NULL DEFAULT 1,
    description TEXT,
    git_hash TEXT,
    stale INTEGER NOT NULL DEFAULT 0,
    line_count INTEGER,
    char_count INTEGER
);

CREATE INDEX IF NOT EXISTS idx_entries_parent ON entries(parent_path);

CREATE TABLE IF NOT EXISTS patterns (
    pattern TEXT PRIMARY KEY,
    entry_type TEXT CHECK (entry_type IN ('file', 'directory')),
    exclude INTEGER NOT NULL DEFAULT 0,
    traverse INTEGER NOT NULL DEFAULT 1,
    description TEXT
);

CREATE TABLE IF NOT EXISTS governance (
    entry_path TEXT PRIMARY KEY REFERENCES entries(path) ON DELETE CASCADE,
    matches TEXT NOT NULL,
    excludes TEXT,
    auto_loaded INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS governs (
    governor_path TEXT REFERENCES entries(path) ON DELETE CASCADE,
    governed_path TEXT REFERENCES entries(path) ON DELETE CASCADE,
    PRIMARY KEY (governor_path, governed_path)
);

CREATE INDEX IF NOT EXISTS idx_governs_governed ON governs(governed_path);

CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""

SEED_PATH = Path(__file__).parent / "navigator_seed.csv"


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode for concurrent access."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> str:
    """Create database with schema, upsert seed patterns from CSV.

    Idempotent — safe to rerun. Creates schema if missing, migrates
    legacy pattern rows from entries to patterns table, then upserts
    seed patterns. Non-seed entries are untouched.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    try:
        conn.executescript(SCHEMA)

        if not SEED_PATH.exists():
            return f"Initialized: {path} (no seed file)"

        added = 0
        updated = 0
        with open(SEED_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                desc_raw = row.get("description", "")
                description = desc_raw if desc_raw else None
                exclude = int(row.get("exclude", 0))
                traverse = int(row.get("traverse", 1))
                entry_type = row.get("entry_type") or None

                existing = conn.execute(
                    "SELECT exclude, traverse, description, entry_type "
                    "FROM patterns WHERE pattern = ?",
                    (row["path"],),
                ).fetchone()

                if existing is None:
                    conn.execute(
                        "INSERT INTO patterns "
                        "(pattern, entry_type, exclude, traverse, description) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (row["path"], entry_type, exclude, traverse, description),
                    )
                    added += 1
                elif (
                    existing[0] != exclude
                    or existing[1] != traverse
                    or existing[2] != description
                    or existing[3] != entry_type
                ):
                    conn.execute(
                        "UPDATE patterns SET exclude = ?, traverse = ?, "
                        "description = ?, entry_type = ? WHERE pattern = ?",
                        (exclude, traverse, description, entry_type, row["path"]),
                    )
                    updated += 1

        # Seed default config values (won't overwrite existing)
        for key, value in [
            ("lines_warn_threshold", "500"),
            ("lines_fail_threshold", "2000"),
        ]:
            conn.execute(
                "INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)",
                (key, value),
            )

        conn.commit()
        parts = []
        if added:
            parts.append(f"{added} added")
        if updated:
            parts.append(f"{updated} updated")
        if not parts:
            parts.append("all current")
        return f"Initialized: {path} (seed patterns: {', '.join(parts)})"
    finally:
        conn.close()
