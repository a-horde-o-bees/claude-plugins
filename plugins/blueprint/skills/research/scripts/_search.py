"""Search and export operations."""

from __future__ import annotations

import logging

from _db import get_connection

logger = logging.getLogger(__name__)

__all__ = [
    "search_notes",
    "export_db",
]


def search_notes(db_path: str, pattern: str, stage: str | None = None, min_relevance: int | None = None) -> str:
    """Search notes by keyword pattern across entities."""
    conn = get_connection(db_path)
    try:
        conditions = ["n.note LIKE ?"]
        params: list[str | int] = [f"%{pattern}%"]
        if stage:
            conditions.append("e.stage = ?")
            params.append(stage)
        if min_relevance is not None:
            conditions.append("e.relevance >= ?")
            params.append(min_relevance)

        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT n.id, n.note, e.id as entity_id, e.name "
            f"FROM entity_notes n JOIN entities e ON n.entity_id = e.id "
            f"WHERE {where} ORDER BY e.relevance DESC, e.name",
            params,
        ).fetchall()

        if not rows:
            return f'No notes matching "{pattern}"'
        lines = [f'Notes matching "{pattern}" ({len(rows)}):']
        for r in rows:
            lines.append(f"  [{r['id']}] {r['entity_id']}. {r['name']}: {r['note']}")
        return "\n".join(lines)
    finally:
        conn.close()


def export_db(db_path: str, format: str = "json") -> str:
    """Export full database."""
    import csv
    import io
    import json

    conn = get_connection(db_path)
    try:
        entities = conn.execute(
            "SELECT * FROM entities ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
        ).fetchall()

        if format == "json":
            result = []
            for e in entities:
                entity_data = dict(e)
                entity_data["urls"] = [r["url"] for r in conn.execute(
                    "SELECT url FROM entity_urls WHERE entity_id = ? ORDER BY id", (e["id"],),
                ).fetchall()]
                entity_data["provenance"] = [r["source_url"] for r in conn.execute(
                    "SELECT source_url FROM url_provenance WHERE entity_id = ? ORDER BY source_url",
                    (e["id"],),
                ).fetchall()]
                entity_data["notes"] = [{"id": r["id"], "note": r["note"]} for r in conn.execute(
                    "SELECT id, note FROM entity_notes WHERE entity_id = ? ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
                    (e["id"],),
                ).fetchall()]
                entity_data["measures"] = {r["measure"]: r["value"] for r in conn.execute(
                    "SELECT measure, value FROM entity_measures WHERE entity_id = ?", (e["id"],),
                ).fetchall()}
                result.append(entity_data)
            return json.dumps(result, indent=2)

        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "name", "role", "stage", "relevance", "description", "urls", "note_count"])
            for e in entities:
                urls = [r["url"] for r in conn.execute(
                    "SELECT url FROM entity_urls WHERE entity_id = ?", (e["id"],),
                ).fetchall()]
                note_count = conn.execute(
                    "SELECT COUNT(*) FROM entity_notes WHERE entity_id = ?", (e["id"],),
                ).fetchone()[0]
                writer.writerow([
                    e["id"], e["name"], e["role"], e["stage"],
                    e["relevance"], e["description"], "; ".join(urls), note_count,
                ])
            return output.getvalue()

        return f"Unknown format: {format}"
    finally:
        conn.close()
