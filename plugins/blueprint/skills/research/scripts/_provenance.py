"""URL, provenance, and reach operations for entity research data."""

from __future__ import annotations

import logging
import sqlite3

import _db as _core  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

__all__ = [
    "upsert_provenance",
    "upsert_url",
    "list_provenance",
    "list_reach",
]


@_core.retry_write
def upsert_provenance(db_path: str, entity_id: str, source_url: str) -> str:
    """Record that entity was found via a source URL."""
    conn = _core.get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        normalized = _core.normalize_url(source_url)
        if not normalized:
            raise ValueError("Could not normalize source URL")
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
                (normalized, entity_id),
            )
        return f"Provenance added: {row['name']} (id: {entity_id}) found via {normalized}"
    finally:
        conn.close()


@_core.retry_write
def upsert_url(db_path: str, entity_id: str, url: str) -> str:
    """Add URL to existing entity (ignores duplicates)."""
    conn = _core.get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        normalized = _core.normalize_url(url)
        if not normalized:
            raise ValueError("Could not normalize URL")
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO entity_urls (entity_id, url) VALUES (?, ?)",
                (row["id"], normalized),
            )
        return f"Added URL {normalized} to {row['name']} (id: {row['id']})"
    finally:
        conn.close()


def list_provenance(db_path: str, entity_id: str | None = None) -> str:
    """List provenance relationships, optionally filtered by entity ID."""
    conn = _core.get_connection(db_path)
    try:
        if entity_id:
            rows = conn.execute(
                "SELECT source_url FROM url_provenance WHERE entity_id = ? ORDER BY source_url",
                (entity_id,),
            ).fetchall()
            if not rows:
                return f"No provenance for entity {entity_id}"
            lines = [f"Provenance for {entity_id} ({len(rows)} sources):"]
            for r in rows:
                lines.append(f"  {r['source_url']}")
        else:
            rows = conn.execute(
                "SELECT source_url, COUNT(*) as cnt FROM url_provenance GROUP BY source_url ORDER BY cnt DESC",
            ).fetchall()
            if not rows:
                return "No provenance recorded."
            lines = [f"Provenance sources ({len(rows)}):"]
            for r in rows:
                lines.append(f"  {r['source_url']} ({r['cnt']} entities)")
        return "\n".join(lines)
    finally:
        conn.close()


def list_reach(db_path: str, min_count: int = 0) -> str:
    """Entities ranked by number of independent provenance sources."""
    conn = _core.get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT entity_id, COUNT(*) as cnt FROM url_provenance "
            "GROUP BY entity_id HAVING cnt >= ? ORDER BY cnt DESC",
            (min_count,),
        ).fetchall()
        if not rows:
            return "No entities with provenance."
        lines = [f"Entities by reach ({len(rows)}):"]
        for r in rows:
            entity = conn.execute("SELECT name FROM entities WHERE id = ?", (r["entity_id"],)).fetchone()
            name = entity["name"] if entity else "?"
            lines.append(f"  {r['entity_id']}. {name} ({r['cnt']} sources)")
        return "\n".join(lines)
    finally:
        conn.close()
