"""Friction queue operations.

Facade module — public interface for friction queue functionality.
Business logic for adding, listing, searching, updating, and removing
process friction entries. Entries live in a SQLite database, one row
per friction observation, filed against the system the friction is about.

All functions take db_path as first argument and return structured data
(dicts/lists). Presentation and JSON serialization live in the MCP
server layer.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ._db import _validate_system, get_connection


def _now_iso() -> str:
    """Current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _entry_metadata(row) -> dict:
    """Extract metadata dict from a database row (no detail_md)."""
    return {
        "id": row["id"],
        "system": row["system"],
        "summary": row["summary"],
        "has_detail": bool(row["detail_md"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# --- Public interface ---


def friction_add(
    db_path: str,
    system: str,
    summary: str,
    detail_md: str | None = None,
) -> dict:
    """Add a friction entry for a system.

    Returns {id, system, summary, has_detail, created_at, updated_at}.
    Raises ValueError on invalid system name.
    """
    _validate_system(system)
    now = _now_iso()
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO friction_entries (system, summary, detail_md, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (system, summary, detail_md, now, now),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "system": system,
            "summary": summary,
            "has_detail": detail_md is not None and detail_md != "",
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def friction_list(
    db_path: str,
    system: str | None = None,
    ids: list[int] | None = None,
    limit: int | None = None,
) -> dict:
    """List friction entries as metadata (no detail_md).

    If ids provided, returns metadata for those specific entries (ignoring
    other filters). Otherwise returns all entries, optionally filtered by
    system.

    Returns {total, entries: [{id, system, summary, has_detail, created_at, updated_at}]}.
    """
    conn = get_connection(db_path)
    try:
        if ids is not None:
            placeholders = ",".join("?" for _ in ids)
            rows = conn.execute(
                f"SELECT * FROM friction_entries WHERE id IN ({placeholders}) "
                "ORDER BY created_at DESC",
                ids,
            ).fetchall()
        else:
            if system is not None:
                _validate_system(system)
                query = "SELECT * FROM friction_entries WHERE system = ? ORDER BY created_at DESC"
                params: list = [system]
            else:
                query = "SELECT * FROM friction_entries ORDER BY created_at DESC"
                params = []
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            rows = conn.execute(query, params).fetchall()

        entries = [_entry_metadata(row) for row in rows]
        return {"total": len(entries), "entries": entries}
    finally:
        conn.close()


def friction_search(
    db_path: str,
    pattern: str,
    system: str | None = None,
) -> dict:
    """Regex search across summary and detail_md.

    Returns same shape as friction_list (metadata only, no detail_md).
    """
    conn = get_connection(db_path)
    try:
        if system is not None:
            _validate_system(system)
            rows = conn.execute(
                "SELECT * FROM friction_entries "
                "WHERE (summary REGEXP ? OR detail_md REGEXP ?) AND system = ? "
                "ORDER BY created_at DESC",
                (pattern, pattern, system),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM friction_entries "
                "WHERE (summary REGEXP ? OR detail_md REGEXP ?) "
                "ORDER BY created_at DESC",
                (pattern, pattern),
            ).fetchall()

        entries = [_entry_metadata(row) for row in rows]
        return {"total": len(entries), "entries": entries}
    finally:
        conn.close()


def friction_get(
    db_path: str,
    ids: int | list[int],
) -> dict:
    """Get full entries including detail_md.

    Takes a single id or list of ids.
    Returns {entries: [{id, system, summary, detail_md, created_at, updated_at}]}.
    """
    if isinstance(ids, int):
        ids = [ids]
    conn = get_connection(db_path)
    try:
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT * FROM friction_entries WHERE id IN ({placeholders}) "
            "ORDER BY created_at DESC",
            ids,
        ).fetchall()

        entries = [
            {
                "id": row["id"],
                "system": row["system"],
                "summary": row["summary"],
                "detail_md": row["detail_md"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ]
        return {"entries": entries}
    finally:
        conn.close()


def friction_update(
    db_path: str,
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
    system: str | None = None,
) -> dict:
    """Update fields on an existing friction entry.

    None = don't touch the field. Empty string "" clears detail_md.
    Updates updated_at to now.

    Returns updated entry metadata.
    Raises ValueError if id not found or system name invalid.
    """
    if system is not None:
        _validate_system(system)

    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT * FROM friction_entries WHERE id = ?", (id,)
        ).fetchone()
        if existing is None:
            raise ValueError(f"Friction entry not found: id={id}")

        updates = []
        params: list = []
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)
        if detail_md is not None:
            updates.append("detail_md = ?")
            # Empty string means clear
            params.append(detail_md if detail_md != "" else None)
        if system is not None:
            updates.append("system = ?")
            params.append(system)

        now = _now_iso()
        updates.append("updated_at = ?")
        params.append(now)
        params.append(id)

        conn.execute(
            f"UPDATE friction_entries SET {', '.join(updates)} WHERE id = ?",
            params,
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM friction_entries WHERE id = ?", (id,)
        ).fetchone()
        return _entry_metadata(row)
    finally:
        conn.close()


def friction_remove(db_path: str, id: int) -> dict:
    """Delete a friction entry by id.

    Returns {removed: {entry metadata}, remaining: N}.
    Raises ValueError if id not found.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM friction_entries WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Friction entry not found: id={id}")

        removed = _entry_metadata(row)
        conn.execute("DELETE FROM friction_entries WHERE id = ?", (id,))
        conn.commit()

        remaining = conn.execute(
            "SELECT COUNT(*) FROM friction_entries"
        ).fetchone()[0]
        return {"removed": removed, "remaining": remaining}
    finally:
        conn.close()


def friction_systems_list(db_path: str) -> dict:
    """List all systems with friction entries, with counts.

    Returns {total_systems, total_entries, systems: [{name, count}]}.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT system, COUNT(*) as count FROM friction_entries "
            "GROUP BY system ORDER BY count DESC"
        ).fetchall()

        systems = [{"name": row["system"], "count": row["count"]} for row in rows]
        total_entries = sum(s["count"] for s in systems)
        return {
            "total_systems": len(systems),
            "total_entries": total_entries,
            "systems": systems,
        }
    finally:
        conn.close()
