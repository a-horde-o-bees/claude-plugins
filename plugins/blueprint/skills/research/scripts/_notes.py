"""Notes CRUD operations for entity research data."""

from __future__ import annotations

import logging
import sqlite3

from . import _db as _core

logger = logging.getLogger(__name__)

__all__ = [
    "upsert_notes",
    "update_note",
    "remove_notes",
]


@_core.retry_write
def upsert_notes(db_path: str, entity_id: str, notes: list[str]) -> str:
    """Add notes (atomic facts) to entity. Skips duplicates."""
    conn = _core.get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")

        added = 0
        skipped = 0
        with conn:
            for note in notes:
                note_id = _core._next_id(conn, "entity_notes", "n")
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO entity_notes (id, entity_id, note) VALUES (?, ?, ?)",
                    (note_id, entity_id, note),
                )
                if cursor.rowcount > 0:
                    _core._touch(conn, "entity_notes", note_id)
                    added += 1
                else:
                    skipped += 1

        parts = [f"Added {added} notes to {row['name']} (id: {entity_id})"]
        if skipped:
            parts.append(f"Skipped {skipped} duplicates")
        return ". ".join(parts)
    finally:
        conn.close()


@_core.retry_write
def update_note(db_path: str, note_id: str, note: str) -> str:
    """Update a single note by ID with corrected text."""
    conn = _core.get_connection(db_path)
    try:
        row = conn.execute("SELECT id, entity_id FROM entity_notes WHERE id = ?", (note_id,)).fetchone()
        if not row:
            raise ValueError(f"Note not found: {note_id}")
        with conn:
            conn.execute("UPDATE entity_notes SET note = ? WHERE id = ?", (note, note_id))
            _core._touch(conn, "entity_notes", note_id)
        return f"Updated note {note_id}"
    finally:
        conn.close()


@_core.retry_write
def remove_notes(db_path: str, entity_id: str, note_ids: list[str]) -> str:
    """Remove specific notes by ID from entity."""
    conn = _core.get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        with conn:
            placeholders = ",".join("?" * len(note_ids))
            existing = conn.execute(
                f"SELECT id FROM entity_notes WHERE entity_id = ? AND id IN ({placeholders})",
                [entity_id] + note_ids,
            ).fetchall()
            existing_ids = {r["id"] for r in existing}
            if existing_ids:
                placeholders = ",".join("?" * len(existing_ids))
                conn.execute(
                    f"DELETE FROM entity_notes WHERE entity_id = ? AND id IN ({placeholders})",
                    [entity_id] + list(existing_ids),
                )
        return f"Removed {len(existing_ids)} notes from {row['name']} (id: {entity_id})"
    finally:
        conn.close()
