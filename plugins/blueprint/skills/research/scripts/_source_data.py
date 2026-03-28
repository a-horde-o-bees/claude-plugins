"""Source data management."""

from __future__ import annotations

import logging

from _db import get_connection, retry_write  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

__all__ = [
    "upsert_source_data",
    "list_source_data",
]


@retry_write
def upsert_source_data(db_path: str, entity_id: str, source_type: str, data: list[str]) -> str:
    """Upsert structured key:value source data to entity. Data is list of 'key=value' strings."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        pairs = {}
        for item in data:
            if "=" not in item:
                raise ValueError(f"Invalid format '{item}' — expected key=value")
            key, value = item.split("=", 1)
            pairs[key.strip()] = value.strip()
        with conn:
            for key, value in pairs.items():
                conn.execute(
                    "INSERT OR REPLACE INTO entity_source_data (entity_id, source_type, key, value) VALUES (?, ?, ?, ?)",
                    (entity_id, source_type, key, value),
                )
        return f"Set {len(pairs)} {source_type} fields for {row['name']} (id: {entity_id}): {', '.join(pairs.keys())}"
    finally:
        conn.close()


def list_source_data(
    db_path: str,
    source_type: str | None = None,
    key: str | None = None,
    entity_id: str | None = None,
) -> str:
    """List source data, optionally filtered."""
    conn = get_connection(db_path)
    try:
        conditions = []
        params = []
        if source_type:
            conditions.append("sd.source_type = ?")
            params.append(source_type)
        if key:
            conditions.append("sd.key = ?")
            params.append(key)
        if entity_id:
            conditions.append("sd.entity_id = ?")
            params.append(entity_id)

        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = conn.execute(
            f"SELECT sd.entity_id, sd.source_type, sd.key, sd.value, e.name as entity_name "
            f"FROM entity_source_data sd JOIN entities e ON sd.entity_id = e.id "
            f"{where} ORDER BY e.name, sd.source_type, sd.key",
            params,
        ).fetchall()

        if not rows:
            return "No source data found."

        lines = []
        current_entity = None
        current_type = None
        for r in rows:
            if r["entity_id"] != current_entity:
                current_entity = r["entity_id"]
                current_type = None
                lines.append(f"\n{r['entity_name']} ({r['entity_id']}):")
            if r["source_type"] != current_type:
                current_type = r["source_type"]
                lines.append(f"  [{r['source_type']}]")
            lines.append(f"    {r['key']}: {r['value']}")
        lines.append(f"\nTotal: {len(rows)} fields")
        return "\n".join(lines)
    finally:
        conn.close()
