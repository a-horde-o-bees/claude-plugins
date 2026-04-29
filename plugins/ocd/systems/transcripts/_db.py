"""transcripts database infrastructure.

Schema, connection factory, and the encoded-project-name helper. The DB
location is owned by `_init._db_path()` per the plugin's init/status
contract; this module exposes only schema mechanics so `tools.db.rectify`
can drive schema management.
"""

import sqlite3
from pathlib import Path

from tools import environment


SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    file TEXT NOT NULL,
    line INTEGER NOT NULL,
    project_name TEXT NOT NULL,
    parent_session TEXT NOT NULL,
    ts TEXT NOT NULL,
    label TEXT NOT NULL,
    text TEXT,
    tool_use_label TEXT,
    ref TEXT,
    parent_message TEXT,
    uuid TEXT,
    PRIMARY KEY (file, line)
);

CREATE INDEX IF NOT EXISTS idx_events_project           ON events(project_name);
CREATE INDEX IF NOT EXISTS idx_events_session           ON events(parent_session);
CREATE INDEX IF NOT EXISTS idx_events_uuid              ON events(uuid);
CREATE INDEX IF NOT EXISTS idx_events_parent_msg        ON events(parent_message);
CREATE INDEX IF NOT EXISTS idx_events_label             ON events(label);
CREATE INDEX IF NOT EXISTS idx_events_ts                ON events(ts);
CREATE INDEX IF NOT EXISTS idx_events_session_label_ts  ON events(parent_session, label, ts);

CREATE TABLE IF NOT EXISTS exchanges (
    parent_session TEXT NOT NULL,
    exchange INTEGER NOT NULL,
    purpose TEXT,
    purpose_updated_at TEXT,
    PRIMARY KEY (parent_session, exchange)
);

CREATE INDEX IF NOT EXISTS idx_exchanges_session ON exchanges(parent_session);

DROP VIEW IF EXISTS events_with_gaps;
CREATE VIEW events_with_gaps AS
SELECT
    e.*,
    (SELECT COUNT(DISTINCT u.ts) FROM events u
     WHERE u.parent_session = e.parent_session
       AND u.label = 'user_msg'
       AND u.parent_message IS NULL
       AND u.ts <= e.ts) AS exchange,
    (julianday(e.ts) - julianday(LAG(e.ts) OVER (
        PARTITION BY e.parent_session ORDER BY e.ts, e.file, e.line
    ))) * 86400 AS gap_s
FROM events e;

DROP VIEW IF EXISTS chat_messages;
CREATE VIEW chat_messages AS
SELECT
    project_name,
    parent_session,
    file,
    line,
    ts,
    CASE
        WHEN label = 'user_msg'           THEN 'user'
        WHEN label = 'sidechain_user_msg' THEN 'subagent_user'
        WHEN label LIKE 'assistant%'      THEN 'assistant'
    END AS role,
    text
FROM events
WHERE text IS NOT NULL
  AND label NOT LIKE 'tool_result%';
"""

EXPECTED_TABLES = {"events", "exchanges"}


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode and foreign keys enabled."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str) -> None:
    """Create database with schema. Idempotent. Used as schema_builder for tools.db.rectify."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def current_project_name() -> str:
    """Encode the current project root as Claude Code's project-name string.

    Claude Code stores transcripts under ~/.claude/projects/<encoded>/, where
    <encoded> is the absolute project path with separators replaced by dashes.
    Used as the default sync filter so we only ingest transcripts belonging
    to this project unless the caller widens scope.
    """
    return str(environment.get_project_dir()).replace("/", "-").replace("\\", "-")
