"""Governance database infrastructure.

Schema, migrations, connection factory, and initialization for the
governance database. Stores conventions, rules, their pattern
junctions, and the governance dependency graph. Independent from the
navigator database — separate file, separate concerns.
"""

import logging
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS conventions (
    entry_path TEXT PRIMARY KEY,
    includes TEXT NOT NULL,
    excludes TEXT,
    git_hash TEXT
);

CREATE TABLE IF NOT EXISTS convention_includes (
    entry_path TEXT NOT NULL REFERENCES conventions(entry_path) ON DELETE CASCADE,
    pattern TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS convention_excludes (
    entry_path TEXT NOT NULL REFERENCES conventions(entry_path) ON DELETE CASCADE,
    pattern TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_convention_includes_entry ON convention_includes(entry_path);
CREATE INDEX IF NOT EXISTS idx_convention_excludes_entry ON convention_excludes(entry_path);

CREATE TABLE IF NOT EXISTS rules (
    entry_path TEXT PRIMARY KEY,
    git_hash TEXT
);

CREATE TABLE IF NOT EXISTS governance_depends_on (
    entry_path TEXT NOT NULL,
    depends_on_path TEXT NOT NULL,
    PRIMARY KEY (entry_path, depends_on_path)
);

CREATE INDEX IF NOT EXISTS idx_governance_depends_target
    ON governance_depends_on(depends_on_path);

CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _path_match(path: str, pattern: str) -> bool:
    """Custom SQL function for governance pattern matching.

    Registered as path_match(path, pattern) on every connection.
    Delegates to matches_pattern which handles basename, ** prefix,
    and full-path matching modes.
    """
    from ._frontmatter import matches_pattern

    return matches_pattern(path, pattern)


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open a connection, creating the database and schema if missing.

    Lazy-init: the schema is applied on every connection open via
    `executescript`. CREATE TABLE IF NOT EXISTS makes this idempotent
    and makes the first caller the implicit initializer — no separate
    init_db hook is needed.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    conn.create_function("path_match", 2, _path_match, deterministic=True)
    conn.executescript(SCHEMA)
    return conn


def init_db(db_path: str) -> str:
    """Explicit initializer — opens a connection (which creates schema) and closes.

    Kept as a callable for tests and for code paths that want an eager
    init. Functionally equivalent to any caller of get_connection, which
    already applies the schema on connection open.
    """
    conn = get_connection(db_path)
    conn.close()
    return f"Initialized: {db_path}"
