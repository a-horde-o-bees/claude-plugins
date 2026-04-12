"""Compound entity operations — multi-step mutations combining several primitives."""

from __future__ import annotations

import sqlite3

from . import _helpers
from ._helpers import _check_db, _ok, _err

from skills.research._entities import update_entity as _update_entity
from skills.research._notes import upsert_notes as _add_notes
from skills.research._merge import merge_entities as _merge_entities


def reject_entity(entity_id: str, reason: str) -> str:
    """Reject entity — sets stage to rejected, relevance to -1, adds reason as note.

    Args:
        entity_id: Entity ID (e.g., e1)
        reason: Rejection reason (added as note)
    """
    if err := _check_db(): return err
    try:
        _update_entity(_helpers.DB_PATH, ids=[entity_id], stage="rejected", relevance=-1)
        _add_notes(_helpers.DB_PATH, entity_id, [f"Rejected: {reason}"])
        return _ok(f"Rejected {entity_id}: {reason}")
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def merge_entities(entity_ids: list[str]) -> str:
    """Merge entities into lowest-ID survivor. Mechanical — preserves all data.

    Combines descriptions, moves notes/URLs/provenance/source data to survivor.
    Sets survivor stage to merged, clears relevance and measures.

    Args:
        entity_ids: Entity IDs to merge (e.g., ["e1", "e2"])
    """
    if err := _check_db(): return err
    try:
        return _ok(_merge_entities(_helpers.DB_PATH, entity_ids))
    except ValueError as e:
        return _err(e)
