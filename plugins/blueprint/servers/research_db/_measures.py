"""Entity measure tools — analysis output CRUD.

Measures are key-value pairs attached to entities for assessment tracking.
"""

from __future__ import annotations

from . import _helpers
from ._helpers import _check_db, _ok, _err

from skills.research._measures import (
    upsert_measures as _set_measures,
    clear_entity_measures as _clear_entity_measures,
    clear_measures as _clear_all_measures,
)


def set_measures(entity_id: str, measures: list[dict]) -> str:
    """Set measures on entity. Each measure is a key-value pair.

    Args:
        entity_id: Entity ID (e.g., e1)
        measures: List of {measure: "name", value: "value"} objects
    """
    if err := _check_db(): return err
    try:
        formatted = [f"{m['measure']}={m['value']}" for m in measures]
        return _ok(_set_measures(_helpers.DB_PATH, entity_id, formatted))
    except (ValueError, KeyError) as e:
        return _err(e)


def clear_measures(entity_id: str) -> str:
    """Clear all measures from one entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_clear_entity_measures(_helpers.DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)


def clear_all_measures() -> str:
    """Clear all measures across all entities. Used when assessment or effectiveness criteria change."""
    if err := _check_db(): return err
    return _ok(_clear_all_measures(_helpers.DB_PATH))
