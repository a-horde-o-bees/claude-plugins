"""Edge CRUD — dependencies, addressing, and path pointers.

Two independent graphs over components. `depends_on` is the structural
DAG ("what must exist for this to work"). `addresses` is the capability
claim ("how is this concern handled") — each edge carries a rationale
describing the component's specific mechanism. Wiring rules enforced at
insertion prevent addressing a root need, addressing both a need and any
ancestor of it, and addressing both a need and any descendant of it —
every edge must land where the unmet test can fire meaningfully.
"""

import sqlite3

from . import _db


def depend(conn: sqlite3.Connection, comp_id: str, dep_id: str) -> None:
    """Record a component → component dependency. Rejects self-loops and cycles."""
    _db.check_component(conn, comp_id)
    _db.check_component(conn, dep_id)
    if comp_id == dep_id:
        raise ValueError("a component cannot depend on itself")
    if _would_cycle(conn, "depends_on", "component_id", "dependency_id", comp_id, dep_id):
        raise ValueError(
            f"{comp_id} → {dep_id} would create a dependency cycle"
        )
    try:
        conn.execute(
            "INSERT INTO depends_on (component_id, dependency_id) VALUES (?, ?)",
            (comp_id, dep_id),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("dependency already exists") from None


def undepend(conn: sqlite3.Connection, comp_id: str, dep_id: str) -> None:
    cur = conn.execute(
        "DELETE FROM depends_on WHERE component_id = ? AND dependency_id = ?",
        (comp_id, dep_id),
    )
    if cur.rowcount == 0:
        raise LookupError("dependency not found")
    conn.commit()


def address(
    conn: sqlite3.Connection, comp_id: str, need_id: str, rationale: str,
) -> None:
    """Record that a component addresses a need, with mechanism rationale.

    Wiring rules, enforced here:
    - Cannot address a root need (must land at depth >= 1)
    - Cannot address both a need and any ancestor of that need
    - Cannot address both a need and any descendant of that need
    """
    if not rationale or not rationale.strip():
        raise ValueError(
            "address requires a rationale explaining why this component "
            "addresses the need"
        )
    _db.check_component(conn, comp_id)
    _db.check_need(conn, need_id)

    parent = conn.execute(
        "SELECT parent_id FROM needs WHERE id = ?", (need_id,)
    ).fetchone()
    if parent[0] is None:
        raise ValueError(
            f"cannot address root need {need_id} — refine it into more "
            f"specific child needs first (use `refine {need_id} "
            f"<description>` to add a child, then address the child)"
        )

    ancestor_addressed = conn.execute(
        """
        WITH RECURSIVE ancestors(id) AS (
            SELECT parent_id FROM needs WHERE id = ? AND parent_id IS NOT NULL
            UNION
            SELECT n.parent_id FROM needs n JOIN ancestors a ON n.id = a.id
            WHERE n.parent_id IS NOT NULL
        )
        SELECT a.id FROM ancestors a
        WHERE EXISTS (
            SELECT 1 FROM addresses WHERE component_id = ? AND need_id = a.id
        )
        LIMIT 1
        """,
        (need_id, comp_id),
    ).fetchone()
    if ancestor_addressed:
        raise ValueError(
            f"{comp_id} already addresses {ancestor_addressed[0]}, an "
            f"ancestor of {need_id}. A component cannot address both a "
            f"need and its ancestor — pick the most specific applicable. "
            f"Unaddress {ancestor_addressed[0]} first if {need_id} is "
            f"the right level."
        )

    descendant_addressed = conn.execute(
        """
        WITH RECURSIVE descendants(id) AS (
            SELECT id FROM needs WHERE parent_id = ?
            UNION
            SELECT n.id FROM needs n JOIN descendants d ON n.parent_id = d.id
        )
        SELECT d.id FROM descendants d
        WHERE EXISTS (
            SELECT 1 FROM addresses WHERE component_id = ? AND need_id = d.id
        )
        LIMIT 1
        """,
        (need_id, comp_id),
    ).fetchone()
    if descendant_addressed:
        raise ValueError(
            f"{comp_id} already addresses {descendant_addressed[0]}, a "
            f"descendant of {need_id}. A component cannot address both a "
            f"need and its descendant — pick the most specific applicable. "
            f"Unaddress {descendant_addressed[0]} first if {need_id} is "
            f"the right level."
        )

    try:
        conn.execute(
            "INSERT INTO addresses (component_id, need_id, rationale) "
            "VALUES (?, ?, ?)",
            (comp_id, need_id, rationale.strip()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("addressing edge already exists") from None


def unaddress(conn: sqlite3.Connection, comp_id: str, need_id: str) -> None:
    cur = conn.execute(
        "DELETE FROM addresses WHERE component_id = ? AND need_id = ?",
        (comp_id, need_id),
    )
    if cur.rowcount == 0:
        raise LookupError("addressing edge not found")
    conn.commit()


def set_rationale(
    conn: sqlite3.Connection, comp_id: str, need_id: str, rationale: str,
) -> None:
    """Update the rationale on an existing addressing edge."""
    if not rationale or not rationale.strip():
        raise ValueError("rationale cannot be empty")
    cur = conn.execute(
        "UPDATE addresses SET rationale = ? WHERE component_id = ? AND need_id = ?",
        (rationale.strip(), comp_id, need_id),
    )
    if cur.rowcount == 0:
        raise LookupError(f"addressing edge {comp_id} → {need_id} not found")
    conn.commit()


def add_path(conn: sqlite3.Connection, comp_id: str, path: str) -> None:
    _db.check_component(conn, comp_id)
    try:
        conn.execute(
            "INSERT INTO component_paths (component_id, path) VALUES (?, ?)",
            (comp_id, path),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise ValueError("path already recorded for this component") from None


def remove_path(conn: sqlite3.Connection, comp_id: str, path: str) -> None:
    cur = conn.execute(
        "DELETE FROM component_paths WHERE component_id = ? AND path = ?",
        (comp_id, path),
    )
    if cur.rowcount == 0:
        raise LookupError("path not recorded for this component")
    conn.commit()


def _would_cycle(
    conn: sqlite3.Connection,
    table: str,
    from_col: str,
    to_col: str,
    new_from: str,
    new_to: str,
) -> bool:
    """Check if inserting (new_from, new_to) into a DAG edge table closes a cycle.

    Starts from new_to and walks forward through edges; reaching new_from
    means a cycle would form.
    """
    rows = conn.execute(
        f"""
        WITH RECURSIVE walk(id) AS (
            SELECT ? AS id
            UNION
            SELECT t.{to_col} FROM {table} t JOIN walk w ON t.{from_col} = w.id
        )
        SELECT 1 FROM walk WHERE id = ?
        """,
        (new_to, new_from),
    ).fetchone()
    return bool(rows)
