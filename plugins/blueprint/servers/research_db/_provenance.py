"""URL and provenance tools — entity URL management and discovery tracking."""

from __future__ import annotations

from . import _helpers
from ._helpers import _check_db, _ok

from skills.research import _db as core


def add_url(entity_id: str, url: str) -> str:
    """Add normalized URL to entity. Deduplicates automatically.

    Args:
        entity_id: Entity ID (e.g., e1)
        url: URL to add (will be normalized)
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    try:
        with conn:
            core._add_entity_url(conn, entity_id, url)
            core._touch(conn, "entities", entity_id)
        return _ok(f"Added URL to {entity_id}")
    finally:
        conn.close()


def add_provenance(entity_id: str, source_url: str) -> str:
    """Record that entity was discovered via source URL.

    Args:
        entity_id: Entity ID (e.g., e1)
        source_url: URL where entity was found
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    try:
        with conn:
            core._add_provenance(conn, entity_id, source_url)
        return _ok(f"Added provenance to {entity_id}")
    finally:
        conn.close()
