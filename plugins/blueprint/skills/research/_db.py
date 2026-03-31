"""Core database utilities and schema.

SQLite-backed storage for entity research data. This module provides
connection management, schema, shared utilities, and re-exports all
domain operations for backward compatibility.

WAL mode enables concurrent reads while writes are in progress.
Write contention handled by retry_write decorator with random jitter.
"""

from __future__ import annotations

import functools
import logging
import random
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)

VALID_MODES = ("example", "directory", "context", "unclassified")
VALID_STAGES = ("new", "rejected", "researched", "merged")

SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    stage TEXT NOT NULL DEFAULT 'new' CHECK(stage IN ('new', 'rejected', 'researched', 'merged')),
    relevance INTEGER DEFAULT 0,
    description TEXT NOT NULL DEFAULT '',
    purpose TEXT NOT NULL DEFAULT '',
    last_modified TEXT
);

CREATE TABLE IF NOT EXISTS entity_modes (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    mode TEXT NOT NULL CHECK(mode IN ('example', 'directory', 'context', 'unclassified')),
    PRIMARY KEY (entity_id, mode)
);

CREATE TABLE IF NOT EXISTS entity_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    url TEXT NOT NULL,
    UNIQUE(entity_id, url)
);

CREATE TABLE IF NOT EXISTS entity_measures (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    measure TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (entity_id, measure)
);

CREATE TABLE IF NOT EXISTS entity_notes (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    note TEXT NOT NULL,
    last_modified TEXT,
    UNIQUE(entity_id, note)
);

CREATE TABLE IF NOT EXISTS entity_source_data (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    source_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (entity_id, source_type, key)
);

CREATE TABLE IF NOT EXISTS url_provenance (
    source_url TEXT NOT NULL,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    PRIMARY KEY (source_url, entity_id)
);
"""


# --- Connection and utilities ---


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode and foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=0")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def retry_write(func: F) -> F:
    """Retry write operations on database lock with random jitter.

    Catches sqlite3.OperationalError for 'database is locked' and retries
    with random 50-200ms jitter between attempts.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(random.uniform(0.05, 0.2))
                else:
                    raise
    return wrapper  # type: ignore[return-value]


def normalize_url(url: str | None) -> str | None:
    """Normalize URL for storage and deduplication.

    Strips scheme, strips www., lowercases, strips trailing slash.
    Keeps path for profile-level identity.
    """
    if not url:
        return None
    parsed = urlparse(url if "://" in url else f"https://{url}")
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    hostname = hostname.lower()
    path = parsed.path.rstrip("/")
    result = f"{hostname}{path}" if path else hostname
    return result or None


def _next_id(conn: sqlite3.Connection, table: str, prefix: str) -> str:
    """Generate next prefixed ID for a table (e.g., e1, e2, n1, n2)."""
    row = conn.execute(
        f"SELECT id FROM {table} ORDER BY CAST(SUBSTR(id, {len(prefix) + 1}) AS INTEGER) DESC LIMIT 1",
    ).fetchone()
    if row:
        num = int(row["id"][len(prefix):]) + 1
    else:
        num = 1
    return f"{prefix}{num}"


def _find_entity_by_url(conn: sqlite3.Connection, url: str) -> dict | None:
    """Find existing entity by normalized URL match."""
    normalized = normalize_url(url)
    if not normalized:
        return None
    row = conn.execute(
        "SELECT e.id, e.name FROM entities e "
        "JOIN entity_urls eu ON e.id = eu.entity_id "
        "WHERE eu.url = ?",
        (normalized,),
    ).fetchone()
    return dict(row) if row else None


def _add_entity_url(conn: sqlite3.Connection, entity_id: str, url: str) -> None:
    """Add a normalized URL to an entity (ignores duplicates)."""
    normalized = normalize_url(url)
    if normalized:
        conn.execute(
            "INSERT OR IGNORE INTO entity_urls (entity_id, url) VALUES (?, ?)",
            (entity_id, normalized),
        )


def _add_provenance(conn: sqlite3.Connection, entity_id: str, source_url: str) -> None:
    """Record provenance — source URL that led to entity."""
    normalized = normalize_url(source_url)
    if normalized:
        conn.execute(
            "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
            (normalized, entity_id),
        )


def _touch(conn: sqlite3.Connection, table: str, row_id: str) -> None:
    """Set last_modified to current UTC timestamp."""
    conn.execute(
        f"UPDATE {table} SET last_modified = datetime('now') WHERE id = ?",
        (row_id,),
    )


# --- Database lifecycle ---


def _migrate_roles_to_modes(conn: sqlite3.Connection) -> None:
    """Migrate role column on entities to entity_modes satellite table.

    Detects old schema by checking for 'role' column on entities table.
    Creates entity_modes table if needed, copies role values as mode entries,
    then recreates entities table without role column (adding purpose).
    No-op if role column is already absent.
    """
    columns = [c["name"] for c in conn.execute("PRAGMA table_info(entities)").fetchall()]
    if "role" not in columns:
        return  # Already migrated

    conn.execute("PRAGMA foreign_keys = OFF")

    # Ensure entity_modes table exists
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS entity_modes (
            entity_id TEXT NOT NULL REFERENCES entities(id),
            mode TEXT NOT NULL CHECK(mode IN ('example', 'directory', 'context', 'unclassified')),
            PRIMARY KEY (entity_id, mode)
        );
    """)

    # Copy existing roles as modes + add unclassified marker
    rows = conn.execute("SELECT id, role FROM entities").fetchall()
    for row in rows:
        role = row["role"] if row["role"] in VALID_MODES else "unclassified"
        conn.execute(
            "INSERT OR IGNORE INTO entity_modes (entity_id, mode) VALUES (?, ?)",
            (row["id"], role),
        )
        conn.execute(
            "INSERT OR IGNORE INTO entity_modes (entity_id, mode) VALUES (?, ?)",
            (row["id"], "unclassified"),
        )

    # Recreate entities without role, with purpose
    conn.executescript("""
        CREATE TABLE entities_new (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            stage TEXT NOT NULL DEFAULT 'new' CHECK(stage IN ('new', 'rejected', 'researched', 'merged')),
            relevance INTEGER DEFAULT 0,
            description TEXT NOT NULL DEFAULT '',
            purpose TEXT NOT NULL DEFAULT '',
            last_modified TEXT
        );
    """)

    # Determine which columns exist for the copy
    if "purpose" in columns:
        conn.execute("""
            INSERT INTO entities_new (id, name, stage, relevance, description, purpose, last_modified)
            SELECT id, name, stage, relevance, description, purpose, last_modified FROM entities
        """)
    else:
        conn.execute("""
            INSERT INTO entities_new (id, name, stage, relevance, description, last_modified)
            SELECT id, name, stage, relevance, description, last_modified FROM entities
        """)

    conn.executescript("""
        DROP TABLE entities;
        ALTER TABLE entities_new RENAME TO entities;
    """)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.commit()


def init_db(db_path: str) -> str:
    """Create database with schema. Idempotent — safe to run on existing DB."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    conn.executescript(SCHEMA)
    _migrate_roles_to_modes(conn)
    conn.close()
    return f"Database initialized: {path}"


# --- Stage enforcement ---


_STAGE_ORDER = ["new", "rejected", "researched"]


def _enforce_stage(conn: sqlite3.Connection, entity_id: str, target_stage: str) -> None:
    """Enforce stage transition by clearing data above target stage.

    Moving to a lower stage clears higher stage data. Transitioning from
    'merged' only allows 'new' (post-reconciliation).
    """
    current = conn.execute(
        "SELECT stage FROM entities WHERE id = ?", (entity_id,),
    ).fetchone()["stage"]

    if current == "merged":
        if target_stage != "new":
            raise ValueError(
                f"Entity {entity_id} is merged — can only transition to 'new', not '{target_stage}'",
            )
        conn.execute("UPDATE entities SET stage = 'new' WHERE id = ?", (entity_id,))
        return

    current_idx = _STAGE_ORDER.index(current)
    target_idx = _STAGE_ORDER.index(target_stage)

    if current_idx <= target_idx:
        conn.execute("UPDATE entities SET stage = ? WHERE id = ?", (target_stage, entity_id))
        return

    # Clear from researched downward if moving below it
    if current_idx >= _STAGE_ORDER.index("researched") and target_idx < _STAGE_ORDER.index("researched"):
        conn.execute("DELETE FROM entity_notes WHERE entity_id = ?", (entity_id,))
        conn.execute("DELETE FROM entity_measures WHERE entity_id = ?", (entity_id,))

    conn.execute("UPDATE entities SET stage = ? WHERE id = ?", (target_stage, entity_id))
