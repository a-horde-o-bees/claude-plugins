"""Entity CRUD — components, needs, validation.

Component and need entities are identified by short auto-ids (c1, n1)
and carry their full meaning in the description. Descriptions must be
clear and complete — see the Writing Guidelines in needs-map's
ARCHITECTURE.md. Validation is informational: validated entities can
still gain new addressing edges. The `?` prefix in displays asks "is
this identity settled?", not "is this finalized?".
"""

import sqlite3

from . import _db


def add_component(conn: sqlite3.Connection, description: str) -> str:
    new_id = _db.next_id(conn, "c", "components")
    conn.execute(
        "INSERT INTO components (id, description) VALUES (?, ?)",
        (new_id, description),
    )
    conn.commit()
    return new_id


def set_component(conn: sqlite3.Connection, comp_id: str, description: str) -> None:
    cur = conn.execute(
        "UPDATE components SET description = ? WHERE id = ?",
        (description, comp_id),
    )
    if cur.rowcount == 0:
        raise LookupError(f"component '{comp_id}' not found")
    conn.commit()


def remove_component(conn: sqlite3.Connection, comp_id: str) -> None:
    cur = conn.execute("DELETE FROM components WHERE id = ?", (comp_id,))
    if cur.rowcount == 0:
        raise LookupError(f"component '{comp_id}' not found")
    conn.commit()


def add_need(conn: sqlite3.Connection, description: str) -> str:
    """Add a root need (parent_id NULL). Use `refine` to add a child need."""
    new_id = _db.next_id(conn, "n", "needs")
    conn.execute(
        "INSERT INTO needs (id, parent_id, description) VALUES (?, NULL, ?)",
        (new_id, description),
    )
    conn.commit()
    return new_id


def refine(conn: sqlite3.Connection, parent_id: str, description: str) -> str:
    """Add a child need under an existing parent need."""
    _db.check_need(conn, parent_id)
    new_id = _db.next_id(conn, "n", "needs")
    conn.execute(
        "INSERT INTO needs (id, parent_id, description) VALUES (?, ?, ?)",
        (new_id, parent_id, description),
    )
    conn.commit()
    return new_id


def set_need(conn: sqlite3.Connection, need_id: str, description: str) -> None:
    cur = conn.execute(
        "UPDATE needs SET description = ? WHERE id = ?",
        (description, need_id),
    )
    if cur.rowcount == 0:
        raise LookupError(f"need '{need_id}' not found")
    conn.commit()


def set_parent(conn: sqlite3.Connection, need_id: str, parent_id: str | None) -> None:
    """Re-parent a need. Pass `None` to make it a root."""
    _db.check_need(conn, need_id)
    if parent_id is not None:
        _db.check_need(conn, parent_id)
        if need_id == parent_id:
            raise ValueError("a need cannot be its own parent")
        if _would_cycle(conn, need_id, parent_id):
            raise ValueError(
                f"setting {need_id}'s parent to {parent_id} would create a cycle"
            )
    conn.execute("UPDATE needs SET parent_id = ? WHERE id = ?", (parent_id, need_id))
    conn.commit()


def remove_need(conn: sqlite3.Connection, need_id: str) -> None:
    """Remove a need. Refused if it has children — re-parent or remove them first."""
    children = conn.execute(
        "SELECT COUNT(*) FROM needs WHERE parent_id = ?", (need_id,)
    ).fetchone()[0]
    if children > 0:
        raise ValueError(
            f"need {need_id} has {children} child need(s); "
            f"remove or re-parent them first"
        )
    cur = conn.execute("DELETE FROM needs WHERE id = ?", (need_id,))
    if cur.rowcount == 0:
        raise LookupError(f"need '{need_id}' not found")
    conn.commit()


def _would_cycle(
    conn: sqlite3.Connection, need_id: str, new_parent_id: str,
) -> bool:
    """Check if making need_id a child of new_parent_id would create a cycle.

    Walks ancestors of new_parent_id; if need_id appears, the new edge
    would close a cycle.
    """
    rows = conn.execute(
        """
        WITH RECURSIVE ancestors(id) AS (
            SELECT ?
            UNION
            SELECT n.parent_id FROM needs n JOIN ancestors a ON n.id = a.id
            WHERE n.parent_id IS NOT NULL
        )
        SELECT 1 FROM ancestors WHERE id = ?
        """,
        (new_parent_id, need_id),
    ).fetchone()
    return bool(rows)


def validate(conn: sqlite3.Connection, item_id: str) -> str:
    """Mark a component or need as validated. Returns the entity kind."""
    for table in ("components", "needs"):
        cur = conn.execute(
            f"UPDATE {table} SET validated = 1 WHERE id = ?", (item_id,)
        )
        if cur.rowcount:
            conn.commit()
            return table
    raise LookupError(f"'{item_id}' not found")


def invalidate(conn: sqlite3.Connection, item_id: str) -> str:
    """Revert validation on a component or need. Returns the entity kind."""
    for table in ("components", "needs"):
        cur = conn.execute(
            f"UPDATE {table} SET validated = 0 WHERE id = ?", (item_id,)
        )
        if cur.rowcount:
            conn.commit()
            return table
    raise LookupError(f"'{item_id}' not found")
