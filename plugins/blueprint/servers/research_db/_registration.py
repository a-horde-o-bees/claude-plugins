"""Entity registration tools — single and batch.

Handles URL dedup, mode assignment, and provenance on registration.
"""

from __future__ import annotations

import sqlite3

from . import _helpers
from ._helpers import _check_db, _ok, _handle_check_error, _err


def register_entity(data: dict) -> str:
    """Register a new entity with URL dedup, mode assignment, and provenance.

    Args:
        data: Entity object with fields: name (required), url, modes (list),
              description, relevance, purpose, source_url
    """
    from skills.research._entities import register_entity as _register_entity

    if err := _check_db(): return err
    try:
        modes = data.get("modes")
        if isinstance(modes, str):
            modes = [modes]
        result = _register_entity(
            _helpers.DB_PATH,
            name=data.get("name", ""),
            url=data.get("url"),
            source_url=data.get("source_url"),
            relevance=data.get("relevance"),
            description=data.get("description"),
            purpose=data.get("purpose"),
            modes=modes,
        )
        return _ok(result)
    except (ValueError, sqlite3.IntegrityError) as e:
        if isinstance(e, sqlite3.IntegrityError):
            if check_err := _handle_check_error(e):
                return check_err
        return _err(e)


def register_entities(entities: list[dict], source_url: str | None = None) -> str:
    """Register multiple entities in batch. Handles dedup per entity.

    Args:
        entities: Array of entity objects (same fields as register_entity)
        source_url: Default provenance URL applied to all entities (individual entries can override)
    """
    from skills.research._entities import register_batch as _register_batch

    if err := _check_db(): return err
    try:
        result = _register_batch(_helpers.DB_PATH, entities, source_url)
        return _ok(result)
    except (ValueError, sqlite3.IntegrityError) as e:
        if isinstance(e, sqlite3.IntegrityError):
            if check_err := _handle_check_error(e):
                return check_err
        return _err(e)
