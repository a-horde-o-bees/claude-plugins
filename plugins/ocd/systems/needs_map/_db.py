"""needs-map database infrastructure.

Schema, connection factory, and initialization. Two entity tables
(components, needs) connected by three edge tables (depends_on, addresses,
component_paths). Needs form a tree via parent_id. Short auto-ids (c1, n1)
assigned at insertion; descriptions carry the load-bearing meaning.
"""

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS components (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    validated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS needs (
    id TEXT PRIMARY KEY,
    parent_id TEXT REFERENCES needs(id),
    description TEXT NOT NULL,
    validated INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS depends_on (
    component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    dependency_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    PRIMARY KEY (component_id, dependency_id)
);

CREATE TABLE IF NOT EXISTS addresses (
    component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    need_id TEXT NOT NULL REFERENCES needs(id) ON DELETE CASCADE,
    rationale TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (component_id, need_id)
);

CREATE TABLE IF NOT EXISTS component_paths (
    component_id TEXT NOT NULL REFERENCES components(id) ON DELETE CASCADE,
    path TEXT NOT NULL,
    PRIMARY KEY (component_id, path)
);
"""

EXPECTED_TABLES = {"components", "needs", "depends_on", "addresses", "component_paths"}


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode and foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str) -> str:
    """Create database with schema. Idempotent — safe to rerun."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()
    return f"Initialized {db_path}"


def next_id(conn: sqlite3.Connection, prefix: str, table: str) -> str:
    """Generate next sequential short id (e.g. c5, n3)."""
    rows = conn.execute(
        f"SELECT id FROM {table} WHERE id LIKE ?", (f"{prefix}%",)
    ).fetchall()
    nums = []
    for (rid,) in rows:
        suffix = rid[len(prefix):]
        if suffix.isdigit():
            nums.append(int(suffix))
    return f"{prefix}{(max(nums) + 1) if nums else 1}"


def check_component(conn: sqlite3.Connection, comp_id: str) -> None:
    """Raise LookupError if component id does not exist."""
    if not conn.execute(
        "SELECT id FROM components WHERE id = ?", (comp_id,)
    ).fetchone():
        raise LookupError(f"component '{comp_id}' not found")


def check_need(conn: sqlite3.Connection, need_id: str) -> None:
    """Raise LookupError if need id does not exist."""
    if not conn.execute(
        "SELECT id FROM needs WHERE id = ?", (need_id,)
    ).fetchone():
        raise LookupError(f"need '{need_id}' not found")
