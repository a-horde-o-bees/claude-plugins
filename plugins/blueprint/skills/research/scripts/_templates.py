"""Source templates database operations.

Manages source type definitions and expected keys for structured data collection.
Source types define what external data can be fetched (e.g., GitHub repo metadata)
and how to detect duplicates by matching key values across entities.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path

try:
    from . import _db as db
except ImportError:
    import _db as db  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

TEMPLATES_SCHEMA = """
CREATE TABLE IF NOT EXISTS source_types (
    type TEXT PRIMARY KEY,
    url_pattern TEXT NOT NULL DEFAULT '',
    dedup_key TEXT NOT NULL DEFAULT '[]',
    notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS source_type_keys (
    source_type TEXT NOT NULL REFERENCES source_types(type),
    key TEXT NOT NULL,
    format TEXT NOT NULL DEFAULT 'text',
    description TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (source_type, key)
);
"""

TEMPLATES_DB_DEFAULT = str(Path(__file__).resolve().parent.parent.parent.parent / "references" / "source-templates.db")


def get_templates_connection(db_path: str) -> sqlite3.Connection:
    """Open templates database connection with WAL mode and foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def init_templates(templates_db: str) -> str:
    """Create source templates database with schema. Idempotent."""
    path = Path(templates_db)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_templates_connection(str(path))
    conn.executescript(TEMPLATES_SCHEMA)
    conn.close()
    return f"Templates database initialized: {path}"


def upsert_template_key(
    templates_db: str,
    source_type: str,
    key: str,
    format: str = "text",
    description: str = "",
) -> str:
    """Upsert key definition for source type. Creates source type if missing."""
    conn = get_templates_connection(templates_db)
    try:
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO source_types (type, url_pattern, dedup_key, notes) VALUES (?, '', '[]', '')",
                (source_type,),
            )
            conn.execute(
                "INSERT OR REPLACE INTO source_type_keys (source_type, key, format, description) VALUES (?, ?, ?, ?)",
                (source_type, key, format, description),
            )
        return f"Set key {source_type}.{key} ({format}): {description}"
    finally:
        conn.close()


def update_source_type(
    templates_db: str,
    type_name: str,
    url_pattern: str | None = None,
    dedup_key: str | None = None,
    notes: str | None = None,
) -> str:
    """Update source type metadata (url_pattern, dedup_key, notes)."""
    if url_pattern is None and dedup_key is None and notes is None:
        raise ValueError("At least one of url_pattern, dedup_key, or notes is required")

    conn = get_templates_connection(templates_db)
    try:
        row = conn.execute("SELECT type FROM source_types WHERE type = ?", (type_name,)).fetchone()
        if not row:
            raise ValueError(f"Source type not found: {type_name}")

        if dedup_key is not None:
            try:
                key_list = json.loads(dedup_key)
            except json.JSONDecodeError:
                raise ValueError("dedup_key must be valid JSON array")
            if not isinstance(key_list, list):
                raise ValueError("dedup_key must be a JSON array")
            for k in key_list:
                exists = conn.execute(
                    "SELECT 1 FROM source_type_keys WHERE source_type = ? AND key = ?",
                    (type_name, k),
                ).fetchone()
                if not exists:
                    raise ValueError(f"Key '{k}' not found for source type '{type_name}'")

        updates = []
        params = []
        if url_pattern is not None:
            updates.append("url_pattern = ?")
            params.append(url_pattern)
        if dedup_key is not None:
            updates.append("dedup_key = ?")
            params.append(dedup_key)
        if notes is not None:
            updates.append("notes = ?")
            params.append(notes)

        params.append(type_name)
        with conn:
            conn.execute(f"UPDATE source_types SET {', '.join(updates)} WHERE type = ?", params)
        return f"Updated source type: {type_name}"
    finally:
        conn.close()


def get_source_template(templates_db: str, source_type: str) -> str:
    """Full template for one source type."""
    conn = get_templates_connection(templates_db)
    try:
        row = conn.execute("SELECT * FROM source_types WHERE type = ?", (source_type,)).fetchone()
        if not row:
            raise ValueError(f"Source type not found: {source_type}")
        keys = conn.execute(
            "SELECT key, format, description FROM source_type_keys WHERE source_type = ? ORDER BY key",
            (source_type,),
        ).fetchall()
        lines = [
            f"Source type: {row['type']}",
            f"URL pattern: {row['url_pattern']}",
            f"Dedup key: {row['dedup_key']}",
            f"Notes: {row['notes']}",
            "",
            f"Keys ({len(keys)}):",
        ]
        for k in keys:
            lines.append(f"  {k['key']} ({k['format']}): {k['description']}")
        return "\n".join(lines)
    finally:
        conn.close()


def list_source_templates(templates_db: str) -> str:
    """List all source types with key count."""
    conn = get_templates_connection(templates_db)
    try:
        rows = conn.execute(
            "SELECT st.type, st.url_pattern, st.dedup_key, COUNT(sk.key) as key_count "
            "FROM source_types st "
            "LEFT JOIN source_type_keys sk ON sk.source_type = st.type "
            "GROUP BY st.type ORDER BY st.type",
        ).fetchall()
        lines = [f"Source templates ({len(rows)}):"]
        for r in rows:
            lines.append(f"  {r['type']} ({r['url_pattern']}) -- {r['key_count']} keys, dedup: {r['dedup_key']}")
        return "\n".join(lines)
    finally:
        conn.close()


def match_source_type(templates_db: str, url: str) -> str:
    """Check URL against url_patterns and return matching source type."""
    normalized = db.normalize_url(url) or url
    conn = get_templates_connection(templates_db)
    try:
        rows = conn.execute("SELECT type, url_pattern FROM source_types WHERE url_pattern != ''").fetchall()
        for r in rows:
            pattern_normalized = r["url_pattern"].rstrip("*").rstrip("/")
            if normalized.startswith(pattern_normalized):
                return r["type"]
        raise ValueError(f"No matching source type for: {url}")
    finally:
        conn.close()
