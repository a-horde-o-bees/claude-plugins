"""Measure storage and queries."""

from __future__ import annotations

import logging

from ._db import get_connection, retry_write

logger = logging.getLogger(__name__)

__all__ = [
    "upsert_measures",
    "get_measures",
    "clear_measures",
]


@retry_write
def upsert_measures(db_path: str, entity_id: str, measures: list[str]) -> str:
    """Add or update measures for entity. Measures are key=value pairs."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        updated = 0
        with conn:
            for m in measures:
                key, _, value = m.partition("=")
                if not value:
                    raise ValueError(f"Invalid measure format (expected key=value): {m}")
                conn.execute(
                    "INSERT OR REPLACE INTO entity_measures (entity_id, measure, value) VALUES (?, ?, ?)",
                    (entity_id, key.strip(), value.strip()),
                )
                updated += 1
        return f"Upserted {updated} measures for {row['name']} (id: {entity_id})"
    finally:
        conn.close()


def get_measures(db_path: str) -> str:
    """Measure distributions across entities."""
    conn = get_connection(db_path)
    try:
        measures = conn.execute(
            "SELECT measure, COUNT(DISTINCT entity_id) as cnt FROM entity_measures GROUP BY measure ORDER BY cnt DESC",
        ).fetchall()
        if not measures:
            return "No measures recorded."
        lines = [f"Measure distributions ({len(measures)} unique measures):"]
        for m in measures:
            lines.append(f"  {m['measure']}: {m['cnt']} entities")
        return "\n".join(lines)
    finally:
        conn.close()


@retry_write
def clear_measures(db_path: str) -> str:
    """Clear all entity measures (for re-analysis)."""
    conn = get_connection(db_path)
    try:
        with conn:
            count = conn.execute("SELECT COUNT(*) FROM entity_measures").fetchone()[0]
            conn.execute("DELETE FROM entity_measures")
        return f"Cleared {count} measures"
    finally:
        conn.close()
