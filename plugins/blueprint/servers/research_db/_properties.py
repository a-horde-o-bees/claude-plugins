"""Entity scalar property tools — set and clear individual fields.

Covers name, description, purpose, relevance, and stage transitions.
"""

from __future__ import annotations

import sqlite3

from . import _helpers
from ._helpers import _check_db, _ok, _handle_check_error, _err


def _update(entity_id: str, **kwargs) -> str:
    from skills.research._entities import update_entity as _update_entity
    return _ok(_update_entity(_helpers.DB_PATH, ids=[entity_id], **kwargs))


def set_name(entity_id: str, name: str) -> str:
    """Set entity display name.

    Args:
        entity_id: Entity ID (e.g., e1)
        name: New name
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, name=name)
    except ValueError as e:
        return _err(e)


def clear_name(entity_id: str) -> str:
    """Reset entity name to empty.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, name="")
    except ValueError as e:
        return _err(e)


def set_description(entity_id: str, description: str) -> str:
    """Set entity description — one-sentence identity statement.

    Args:
        entity_id: Entity ID (e.g., e1)
        description: One sentence: what entity is and primary approach
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, description=description)
    except ValueError as e:
        return _err(e)


def clear_description(entity_id: str) -> str:
    """Reset entity description to empty.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, description="")
    except ValueError as e:
        return _err(e)


def set_purpose(entity_id: str, purpose: str) -> str:
    """Set entity purpose — why this entity matters to the research.

    Args:
        entity_id: Entity ID (e.g., e1)
        purpose: Why this entity is relevant to the research project
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, purpose=purpose)
    except ValueError as e:
        return _err(e)


def clear_purpose(entity_id: str) -> str:
    """Reset entity purpose to empty.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, purpose="")
    except ValueError as e:
        return _err(e)


def set_relevance(entity_id: str, relevance: int) -> str:
    """Set entity relevance score.

    Args:
        entity_id: Entity ID (e.g., e1)
        relevance: Integer score (higher = more relevant, scale from assessment criteria)
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, relevance=relevance)
    except ValueError as e:
        return _err(e)


def clear_relevance(entity_id: str) -> str:
    """Reset entity relevance to 0 (unassessed).

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, relevance=0)
    except ValueError as e:
        return _err(e)


def set_stage(entity_id: str, stage: str) -> str:
    """Set entity stage with validated transitions.

    Valid stages: new, rejected, researched, merged.
    Moving to a lower stage clears higher-stage data.
    Merged entities can only transition to new.

    Args:
        entity_id: Entity ID (e.g., e1)
        stage: Target stage
    """
    if err := _check_db(): return err
    try:
        return _update(entity_id, stage=stage)
    except (ValueError, sqlite3.IntegrityError) as e:
        if isinstance(e, sqlite3.IntegrityError):
            if check_err := _handle_check_error(e):
                return check_err
        return _err(e)
