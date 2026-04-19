"""Criteria tools — assessment definitions, note links, and relevance computation.

Criteria define pass/fail gates for entity assessment. Hardline criteria
reject on fail; relevancy criteria count toward the relevance score.
"""

from __future__ import annotations

import sqlite3

from . import _helpers
from ._helpers import _check_db, _ok, _err, _handle_check_error

from skills.research._criteria import (
    register_criteria as _register_criteria,
    add_criterion as _add_criterion,
    remove_criterion as _remove_criterion,
    get_criteria as _get_criteria,
    link_criterion_note as _link_criterion_note,
    unlink_criterion_note as _unlink_criterion_note,
    clear_criterion_links as _clear_criterion_links,
    get_assessment as _get_assessment,
    compute_relevance as _compute_relevance,
)


def set_criteria(criteria: list[dict]) -> str:
    """Replace ALL criteria definitions. Cascades: removes old criteria and their note links.

    Args:
        criteria: List of criterion objects, each with type ("hardline"|"relevancy"), name, and gate (pass/fail description)
    """
    if err := _check_db(): return err
    try:
        return _ok(_register_criteria(_helpers.DB_PATH, criteria))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def add_criterion(type: str, name: str, gate: str) -> str:
    """Add a single criterion definition.

    Args:
        type: "hardline" (reject on fail) or "relevancy" (count toward relevance score)
        name: Short criterion name
        gate: Explicit pass/fail description with concrete thresholds
    """
    if err := _check_db(): return err
    try:
        return _ok(_add_criterion(_helpers.DB_PATH, type, name, gate))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def remove_criterion(criterion_id: str) -> str:
    """Remove criterion and cascade-delete all its note links.

    Args:
        criterion_id: Criterion ID (e.g., c1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_remove_criterion(_helpers.DB_PATH, criterion_id))
    except ValueError as e:
        return _err(e)


def get_criteria() -> str:
    """List all criteria definitions with type, name, and gate description."""
    if err := _check_db(): return err
    return _ok(_get_criteria(_helpers.DB_PATH))


def link_criterion_note(criterion_id: str, note_id: str, quality: str) -> str:
    """Link a criterion to an entity note with quality assessment. Replaces existing link if present.

    Args:
        criterion_id: Criterion ID (e.g., c1)
        note_id: Entity note ID (e.g., n14)
        quality: "pass" or "fail" — whether this note provides evidence the criterion is met
    """
    if err := _check_db(): return err
    try:
        return _ok(_link_criterion_note(_helpers.DB_PATH, criterion_id, note_id, quality))
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


def unlink_criterion_note(criterion_id: str, note_id: str) -> str:
    """Remove a specific criterion-note link.

    Args:
        criterion_id: Criterion ID (e.g., c1)
        note_id: Entity note ID (e.g., n14)
    """
    if err := _check_db(): return err
    return _ok(_unlink_criterion_note(_helpers.DB_PATH, criterion_id, note_id))


def clear_criterion_links(criterion_id: str) -> str:
    """Remove all note links for a criterion. Use when criterion definition changes.

    Args:
        criterion_id: Criterion ID (e.g., c1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_clear_criterion_links(_helpers.DB_PATH, criterion_id))
    except ValueError as e:
        return _err(e)


def get_assessment(entity_id: str) -> str:
    """Computed assessment for an entity: per-criterion quality, hardline result, relevancy count.

    Resolution: any 'pass' link for a criterion-entity pair means passed (supersedes fail).
    Only 'fail' links means failed. No links means not assessed.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_get_assessment(_helpers.DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)


def compute_relevance(entity_id: str) -> str:
    """Recompute cached relevance score from criterion-note links. Updates entities.relevance.

    Relevance = count of distinct relevancy criteria with at least one 'pass' link for this entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_compute_relevance(_helpers.DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)
