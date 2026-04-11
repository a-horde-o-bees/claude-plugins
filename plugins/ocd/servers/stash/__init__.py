"""Stash operations.

Facade module — public interface for capturing ideas, future work, and
unaddressed observations. Storage is SQLite-backed via _db. Each entry
has a summary (one-liner for scanning) and optional detail_md (rich
markdown with context, approaches explored, or blockers).

All functions take db_path as first argument and return structured data
(dicts). Scope resolution (project vs user) lives in the MCP server
layer — skill functions are pure and operate on whatever db_path is
passed.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ._db import get_connection


def _now_iso() -> str:
    """Current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _row_to_metadata(row) -> dict:
    """Convert a database row to metadata dict (no detail_md)."""
    return {
        "id": row["id"],
        "summary": row["summary"],
        "has_detail": bool(row["detail_md"] is not None and row["detail_md"] != ""),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _row_to_full(row) -> dict:
    """Convert a database row to full dict (includes detail_md)."""
    return {
        "id": row["id"],
        "summary": row["summary"],
        "detail_md": row["detail_md"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# --- Public operations ---


def stash_add(db_path: str, summary: str, detail_md: str | None = None) -> dict:
    """Insert a new stash entry. Returns metadata for the created entry."""
    now = _now_iso()
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO stash_entries (summary, detail_md, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (summary, detail_md, now, now),
        )
        conn.commit()
        return {
            "id": cursor.lastrowid,
            "summary": summary,
            "has_detail": bool(detail_md is not None and detail_md != ""),
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def stash_list(
    db_path: str, ids: list[int] | None = None, limit: int | None = None
) -> dict:
    """List stash entry metadata. Optionally filter by ids or cap with limit."""
    conn = get_connection(db_path)
    try:
        if ids:
            placeholders = ",".join("?" for _ in ids)
            rows = conn.execute(
                f"SELECT * FROM stash_entries WHERE id IN ({placeholders}) ORDER BY id ASC",
                ids,
            ).fetchall()
        else:
            query = "SELECT * FROM stash_entries ORDER BY id ASC"
            if limit is not None:
                query += " LIMIT ?"
                rows = conn.execute(query, (limit,)).fetchall()
            else:
                rows = conn.execute(query).fetchall()

        total = conn.execute("SELECT COUNT(*) FROM stash_entries").fetchone()[0]
        return {
            "total": total,
            "entries": [_row_to_metadata(r) for r in rows],
        }
    finally:
        conn.close()


def stash_search(db_path: str, pattern: str) -> dict:
    """Regex search across summary and detail_md. Returns metadata only."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT * FROM stash_entries WHERE summary REGEXP ? OR detail_md REGEXP ? "
            "ORDER BY id ASC",
            (pattern, pattern),
        ).fetchall()
        return {
            "total": len(rows),
            "entries": [_row_to_metadata(r) for r in rows],
        }
    finally:
        conn.close()


def stash_get(db_path: str, ids: int | list[int]) -> dict:
    """Get full stash entry content (including detail_md) by id(s)."""
    if isinstance(ids, int):
        ids = [ids]
    conn = get_connection(db_path)
    try:
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT * FROM stash_entries WHERE id IN ({placeholders}) ORDER BY id ASC",
            ids,
        ).fetchall()
        return {
            "entries": [_row_to_full(r) for r in rows],
        }
    finally:
        conn.close()


def stash_update(
    db_path: str,
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
) -> dict:
    """Update an existing stash entry. None = don't touch; "" clears detail_md to null."""
    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT * FROM stash_entries WHERE id = ?", (id,)
        ).fetchone()
        if existing is None:
            raise ValueError(
                f"No stash entry with id {id}; call stash_list to see available entries"
            )

        new_summary = summary if summary is not None else existing["summary"]
        # Empty string clears detail_md to null
        if detail_md is not None:
            new_detail_md = None if detail_md == "" else detail_md
        else:
            new_detail_md = existing["detail_md"]

        now = _now_iso()
        conn.execute(
            "UPDATE stash_entries SET summary = ?, detail_md = ?, updated_at = ? "
            "WHERE id = ?",
            (new_summary, new_detail_md, now, id),
        )
        conn.commit()
        return {
            "id": id,
            "summary": new_summary,
            "has_detail": bool(new_detail_md is not None and new_detail_md != ""),
            "created_at": existing["created_at"],
            "updated_at": now,
        }
    finally:
        conn.close()


def stash_remove(db_path: str, id: int) -> dict:
    """Delete a stash entry by id. Returns metadata of removed entry and remaining count."""
    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT * FROM stash_entries WHERE id = ?", (id,)
        ).fetchone()
        if existing is None:
            raise ValueError(
                f"No stash entry with id {id}; call stash_list to see available entries"
            )

        metadata = _row_to_metadata(existing)
        conn.execute("DELETE FROM stash_entries WHERE id = ?", (id,))
        conn.commit()
        remaining = conn.execute("SELECT COUNT(*) FROM stash_entries").fetchone()[0]
        return {
            "removed": metadata,
            "remaining": remaining,
        }
    finally:
        conn.close()
