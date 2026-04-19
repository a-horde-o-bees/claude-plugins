"""Entity mode tools — interaction mode CRUD on satellite table.

Modes: example, directory, context, unclassified. An entity may have
multiple modes simultaneously.
"""

from __future__ import annotations

import sqlite3

from . import _helpers
from ._helpers import _check_db, _ok, _handle_check_error, _err

from skills.research import _db as core


def set_modes(entity_id: str, modes: list[str]) -> str:
    """Replace all modes on entity.

    Valid modes: example, directory, context, unclassified.
    An entity may have multiple modes simultaneously.

    Args:
        entity_id: Entity ID (e.g., e1)
        modes: Complete list of modes (replaces all existing)
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    try:
        with conn:
            conn.execute("DELETE FROM entity_modes WHERE entity_id = ?", (entity_id,))
            for mode in modes:
                conn.execute(
                    "INSERT INTO entity_modes (entity_id, mode) VALUES (?, ?)",
                    (entity_id, mode),
                )
            core._touch(conn, "entities", entity_id)
        return _ok(f"Set modes on {entity_id}: {', '.join(modes)}")
    except sqlite3.IntegrityError as e:
        if check_err := _handle_check_error(e):
            return check_err
        return _err(e)
    finally:
        conn.close()


def add_modes(entity_id: str, modes: list[str]) -> str:
    """Add modes to entity (preserves existing).

    Args:
        entity_id: Entity ID (e.g., e1)
        modes: Modes to add
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    try:
        with conn:
            for mode in modes:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_modes (entity_id, mode) VALUES (?, ?)",
                    (entity_id, mode),
                )
            core._touch(conn, "entities", entity_id)
        return _ok(f"Added modes to {entity_id}: {', '.join(modes)}")
    except sqlite3.IntegrityError as e:
        if check_err := _handle_check_error(e):
            return check_err
        return _err(e)
    finally:
        conn.close()


def remove_modes(entity_id: str, modes: list[str]) -> str:
    """Remove specific modes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
        modes: Mode values to remove
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    try:
        with conn:
            for mode in modes:
                conn.execute(
                    "DELETE FROM entity_modes WHERE entity_id = ? AND mode = ?",
                    (entity_id, mode),
                )
            core._touch(conn, "entities", entity_id)
        return _ok(f"Removed modes from {entity_id}: {', '.join(modes)}")
    finally:
        conn.close()


def clear_modes(entity_id: str) -> str:
    """Remove all modes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
    try:
        with conn:
            conn.execute("DELETE FROM entity_modes WHERE entity_id = ?", (entity_id,))
            core._touch(conn, "entities", entity_id)
        return _ok(f"Cleared all modes from {entity_id}")
    finally:
        conn.close()
