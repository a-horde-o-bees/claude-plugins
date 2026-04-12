"""Entity note tools — knowledge accumulation CRUD.

Notes are atomic, self-explanatory facts. Each note stands alone.
"""

from __future__ import annotations

from . import _helpers
from ._helpers import _check_db, _ok, _err

from skills.research._notes import (
    upsert_notes as _add_notes,
    update_note as _update_note,
    remove_notes as _remove_notes,
    clear_notes as _clear_notes,
)


def add_notes(entity_id: str, notes: list[str]) -> str:
    """Add notes to entity. Skips exact duplicates.

    Notes are atomic, self-explanatory facts. Each note should stand alone.

    Args:
        entity_id: Entity ID (e.g., e1)
        notes: List of note texts to add
    """
    if err := _check_db(): return err
    try:
        return _ok(_add_notes(_helpers.DB_PATH, entity_id, notes))
    except ValueError as e:
        return _err(e)


def set_note(note_id: str, text: str) -> str:
    """Replace text of an existing note.

    Args:
        note_id: Note ID (e.g., n14)
        text: New note text
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_note(_helpers.DB_PATH, note_id, text))
    except ValueError as e:
        return _err(e)


def remove_notes(entity_id: str, note_ids: list[str]) -> str:
    """Remove specific notes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
        note_ids: Note IDs to remove (e.g., ["n3", "n7"])
    """
    if err := _check_db(): return err
    try:
        return _ok(_remove_notes(_helpers.DB_PATH, entity_id, note_ids))
    except ValueError as e:
        return _err(e)


def clear_notes(entity_id: str) -> str:
    """Remove all notes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_clear_notes(_helpers.DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)
