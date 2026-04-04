"""Navigator database infrastructure.

Schema, migrations, connection factory, and initialization with seed rules.
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

CREATE TABLE IF NOT EXISTS governance (
    entry_path TEXT PRIMARY KEY REFERENCES entries(path) ON DELETE CASCADE,
    pattern TEXT NOT NULL,
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

MIGRATIONS = [
    "ALTER TABLE entries ADD COLUMN stale INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE entries ADD COLUMN line_count INTEGER",
    "ALTER TABLE entries ADD COLUMN char_count INTEGER",
]

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
    """Create database with schema, upsert seed rules from CSV.

    Idempotent — safe to rerun. Creates schema if missing, then upserts
    seed rules (adds new patterns, updates changed ones). Non-seed
    entries are untouched.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    try:
        conn.executescript(SCHEMA)

        for migration in MIGRATIONS:
            try:
                conn.execute(migration)
            except sqlite3.OperationalError:
                pass

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
                    "FROM entries WHERE path = ?",
                    (row["path"],),
                ).fetchone()

                if existing is None:
                    conn.execute(
                        "INSERT INTO entries "
                        "(path, parent_path, entry_type, exclude, traverse, description) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (row["path"], None, entry_type, exclude, traverse, description),
                    )
                    added += 1
                elif (
                    existing[0] != exclude
                    or existing[1] != traverse
                    or existing[2] != description
                    or existing[3] != entry_type
                ):
                    conn.execute(
                        "UPDATE entries SET exclude = ?, traverse = ?, "
                        "description = ?, entry_type = ? WHERE path = ?",
                        (exclude, traverse, description, entry_type, row["path"]),
                    )
                    updated += 1

        conn.commit()
        parts = []
        if added:
            parts.append(f"{added} added")
        if updated:
            parts.append(f"{updated} updated")
        if not parts:
            parts.append("all current")
        return f"Initialized: {path} (seed rules: {', '.join(parts)})"
    finally:
        conn.close()
