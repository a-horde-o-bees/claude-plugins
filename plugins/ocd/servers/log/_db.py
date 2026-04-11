"""Log database infrastructure.

Schema, connection factory, and foreign-key enforcement. Four tables form
an aggregate star schema: types (root), records (aggregate root keyed by
log_type), tags (satellite keyed by type), record_tags (junction). Every
foreign key is declared ON DELETE CASCADE except records.log_type, which
uses RESTRICT so type_remove refuses by default when records exist.
"""

import re
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS types (
    name TEXT PRIMARY KEY,
    instructions TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_type TEXT NOT NULL
        REFERENCES types(name) ON UPDATE CASCADE ON DELETE RESTRICT,
    summary TEXT NOT NULL,
    detail_md TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_records_type ON records(log_type);

CREATE TABLE IF NOT EXISTS tags (
    log_type TEXT NOT NULL
        REFERENCES types(name) ON UPDATE CASCADE ON DELETE CASCADE,
    name TEXT NOT NULL,
    PRIMARY KEY (log_type, name)
);

CREATE TABLE IF NOT EXISTS record_tags (
    record_id INTEGER NOT NULL REFERENCES records(id) ON DELETE CASCADE,
    log_type TEXT NOT NULL,
    tag_name TEXT NOT NULL,
    PRIMARY KEY (record_id, tag_name),
    FOREIGN KEY (log_type, tag_name)
        REFERENCES tags(log_type, name) ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_record_tags_type_tag ON record_tags(log_type, tag_name);
"""


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode and FK enforcement.

    PRAGMA foreign_keys is per-connection, not per-database — the CASCADE
    and RESTRICT clauses in the schema are silently ignored without it.
    """
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    conn.create_function(
        "regexp",
        2,
        lambda pattern, text: bool(re.search(pattern, text or "", re.IGNORECASE)),
    )
    conn.executescript(SCHEMA)
    return conn
