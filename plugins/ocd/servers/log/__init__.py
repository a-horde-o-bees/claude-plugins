"""Log operations.

Facade module — public interface for recording project context across a
small set of log types (decision, friction, problem, idea, and any types
the user registers). Business logic for adding, listing, searching,
updating, and removing records; managing types and their routing
instructions; and managing tags scoped per type.

All functions take db_path as first argument and return structured data
(dicts/lists). Presentation and JSON serialization live in the MCP server
layer and the CLI.
"""

from __future__ import annotations

from datetime import datetime, timezone

from ._db import get_connection


def _now_iso() -> str:
    """Current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def _record_metadata(row, tags: list[str]) -> dict:
    """Row + tag list → metadata dict (no detail_md)."""
    return {
        "id": row["id"],
        "log_type": row["log_type"],
        "summary": row["summary"],
        "has_detail": bool(row["detail_md"]),
        "tags": tags,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _record_full(row, tags: list[str]) -> dict:
    """Row + tag list → full dict (includes detail_md)."""
    return {
        "id": row["id"],
        "log_type": row["log_type"],
        "summary": row["summary"],
        "detail_md": row["detail_md"],
        "tags": tags,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _fetch_tags(conn, record_id: int) -> list[str]:
    """Return sorted tag names for a record."""
    rows = conn.execute(
        "SELECT tag_name FROM record_tags WHERE record_id = ? ORDER BY tag_name",
        (record_id,),
    ).fetchall()
    return [r["tag_name"] for r in rows]


def _type_exists(conn, name: str) -> bool:
    """True iff a row in types has this name."""
    row = conn.execute("SELECT 1 FROM types WHERE name = ?", (name,)).fetchone()
    return row is not None


def _require_type(conn, name: str) -> None:
    """Raise ValueError with corrective guidance if type is unknown."""
    if not _type_exists(conn, name):
        raise ValueError(
            f"Unknown log_type {name!r}. "
            "Call type_list to see available types or type_add to register a new one."
        )


def _apply_tags(conn, record_id: int, log_type: str, tags: list[str]) -> None:
    """Replace the record's tag set: upsert each tag, then rewrite junction rows."""
    conn.execute("DELETE FROM record_tags WHERE record_id = ?", (record_id,))
    for tag in tags:
        conn.execute(
            "INSERT OR IGNORE INTO tags (log_type, name) VALUES (?, ?)",
            (log_type, tag),
        )
        conn.execute(
            "INSERT OR IGNORE INTO record_tags (record_id, log_type, tag_name) "
            "VALUES (?, ?, ?)",
            (record_id, log_type, tag),
        )


# --- Records ---


def log_add(
    db_path: str,
    log_type: str,
    summary: str,
    detail_md: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Insert a new record under log_type.

    Tags are upserted under the record's log_type. Raises ValueError if
    log_type is not registered.
    Returns {id, log_type, summary, has_detail, tags, created_at, updated_at}.
    """
    now = _now_iso()
    conn = get_connection(db_path)
    try:
        _require_type(conn, log_type)
        cursor = conn.execute(
            "INSERT INTO records (log_type, summary, detail_md, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (log_type, summary, detail_md, now, now),
        )
        record_id = cursor.lastrowid
        assert record_id is not None
        if tags:
            _apply_tags(conn, record_id, log_type, tags)
        conn.commit()
        return {
            "id": record_id,
            "log_type": log_type,
            "summary": summary,
            "has_detail": bool(detail_md),
            "tags": sorted(tags or []),
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def log_get(db_path: str, ids: int | list[int]) -> dict:
    """Return full records for one or more ids.

    Returns {entries: [{id, log_type, summary, detail_md, tags, ...}]}.
    """
    if isinstance(ids, int):
        ids = [ids]
    conn = get_connection(db_path)
    try:
        if not ids:
            return {"entries": []}
        placeholders = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT * FROM records WHERE id IN ({placeholders}) ORDER BY id ASC",
            ids,
        ).fetchall()
        entries = [_record_full(row, _fetch_tags(conn, row["id"])) for row in rows]
        return {"entries": entries}
    finally:
        conn.close()


def log_list(
    db_path: str,
    log_type: str | None = None,
    tags: list[str] | None = None,
    ids: list[int] | None = None,
    limit: int | None = None,
) -> dict:
    """List records as metadata (no detail_md).

    Filters apply conjunctively: ids (if given, overrides others),
    otherwise log_type and tags narrow the result set. Tags filter
    requires every tag in the list to be attached to the record.

    Returns {total, entries: [{id, log_type, summary, has_detail, tags, ...}]}.
    """
    conn = get_connection(db_path)
    try:
        if ids is not None:
            placeholders = ",".join("?" for _ in ids)
            rows = (
                conn.execute(
                    f"SELECT * FROM records WHERE id IN ({placeholders}) ORDER BY id ASC",
                    ids,
                ).fetchall()
                if ids
                else []
            )
        else:
            clauses: list[str] = []
            params: list = []
            if log_type is not None:
                clauses.append("log_type = ?")
                params.append(log_type)
            if tags:
                placeholders = ",".join("?" for _ in tags)
                clauses.append(
                    f"id IN ("
                    f"  SELECT record_id FROM record_tags WHERE tag_name IN ({placeholders})"
                    f"  GROUP BY record_id HAVING COUNT(DISTINCT tag_name) = ?"
                    f")"
                )
                params.extend(tags)
                params.append(len(set(tags)))

            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            query = f"SELECT * FROM records{where} ORDER BY id ASC"
            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)
            rows = conn.execute(query, params).fetchall()

        entries = [_record_metadata(row, _fetch_tags(conn, row["id"])) for row in rows]
        return {"total": len(entries), "entries": entries}
    finally:
        conn.close()


def log_search(
    db_path: str,
    pattern: str,
    log_type: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Regex search across summary and detail_md, optionally scoped by type or tags.

    Returns metadata only (no detail_md): {total, entries: [...]}.
    """
    conn = get_connection(db_path)
    try:
        clauses: list[str] = ["(summary REGEXP ? OR detail_md REGEXP ?)"]
        params: list = [pattern, pattern]
        if log_type is not None:
            clauses.append("log_type = ?")
            params.append(log_type)
        if tags:
            placeholders = ",".join("?" for _ in tags)
            clauses.append(
                f"id IN ("
                f"  SELECT record_id FROM record_tags WHERE tag_name IN ({placeholders})"
                f"  GROUP BY record_id HAVING COUNT(DISTINCT tag_name) = ?"
                f")"
            )
            params.extend(tags)
            params.append(len(set(tags)))

        query = f"SELECT * FROM records WHERE {' AND '.join(clauses)} ORDER BY id ASC"
        rows = conn.execute(query, params).fetchall()
        entries = [_record_metadata(row, _fetch_tags(conn, row["id"])) for row in rows]
        return {"total": len(entries), "entries": entries}
    finally:
        conn.close()


def log_update(
    db_path: str,
    id: int,
    summary: str | None = None,
    detail_md: str | None = None,
    tags: list[str] | None = None,
) -> dict:
    """Update fields on an existing record.

    None on summary/detail_md/tags leaves the field unchanged. Empty string
    on detail_md clears it to NULL. A list on tags (even empty) replaces
    the full tag set on the record.

    Returns updated metadata.
    Raises ValueError if id not found.
    """
    conn = get_connection(db_path)
    try:
        existing = conn.execute(
            "SELECT * FROM records WHERE id = ?", (id,)
        ).fetchone()
        if existing is None:
            raise ValueError(f"No record with id {id}")

        updates: list[str] = []
        params: list = []
        if summary is not None:
            updates.append("summary = ?")
            params.append(summary)
        if detail_md is not None:
            updates.append("detail_md = ?")
            params.append(detail_md if detail_md != "" else None)

        now = _now_iso()
        updates.append("updated_at = ?")
        params.append(now)
        params.append(id)

        conn.execute(
            f"UPDATE records SET {', '.join(updates)} WHERE id = ?",
            params,
        )

        if tags is not None:
            _apply_tags(conn, id, existing["log_type"], tags)

        conn.commit()

        row = conn.execute("SELECT * FROM records WHERE id = ?", (id,)).fetchone()
        return _record_metadata(row, _fetch_tags(conn, id))
    finally:
        conn.close()


def log_remove(db_path: str, id: int) -> dict:
    """Delete a record by id. Cascades to record_tags.

    Returns {removed: {metadata}, remaining: N}.
    Raises ValueError if id not found.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM records WHERE id = ?", (id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"No record with id {id}")

        removed = _record_metadata(row, _fetch_tags(conn, id))
        conn.execute("DELETE FROM records WHERE id = ?", (id,))
        conn.commit()

        remaining = conn.execute("SELECT COUNT(*) FROM records").fetchone()[0]
        return {"removed": removed, "remaining": remaining}
    finally:
        conn.close()


# --- Types ---


def type_add(db_path: str, name: str, instructions: str) -> dict:
    """Register a new log type with routing instructions.

    Returns {name, instructions, created_at, updated_at}.
    Raises ValueError if name already exists.
    """
    now = _now_iso()
    conn = get_connection(db_path)
    try:
        if _type_exists(conn, name):
            raise ValueError(
                f"Type {name!r} already exists. Call type_update to modify it."
            )
        conn.execute(
            "INSERT INTO types (name, instructions, created_at, updated_at) "
            "VALUES (?, ?, ?, ?)",
            (name, instructions, now, now),
        )
        conn.commit()
        return {
            "name": name,
            "instructions": instructions,
            "created_at": now,
            "updated_at": now,
        }
    finally:
        conn.close()


def type_list(db_path: str) -> dict:
    """List all registered types with record and tag counts.

    Returns {types: [{name, instructions, record_count, tag_count, created_at, updated_at}]}.
    """
    conn = get_connection(db_path)
    try:
        rows = conn.execute("SELECT * FROM types ORDER BY name ASC").fetchall()
        types = []
        for row in rows:
            rc = conn.execute(
                "SELECT COUNT(*) FROM records WHERE log_type = ?", (row["name"],)
            ).fetchone()[0]
            tc = conn.execute(
                "SELECT COUNT(*) FROM tags WHERE log_type = ?", (row["name"],)
            ).fetchone()[0]
            types.append(
                {
                    "name": row["name"],
                    "instructions": row["instructions"],
                    "record_count": rc,
                    "tag_count": tc,
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            )
        return {"types": types}
    finally:
        conn.close()


def type_update(
    db_path: str,
    name: str,
    instructions: str | None = None,
    rename: str | None = None,
) -> dict:
    """Update instructions and/or rename a type.

    Rename cascades automatically via ON UPDATE CASCADE on the foreign keys
    in records.log_type, tags.log_type, and record_tags.log_type. None on
    either field leaves it unchanged.

    Returns updated type dict.
    Raises ValueError if name not found or rename target already exists.
    """
    conn = get_connection(db_path)
    try:
        if not _type_exists(conn, name):
            raise ValueError(
                f"Unknown type {name!r}. Call type_list to see available types."
            )
        if rename is not None and rename != name and _type_exists(conn, rename):
            raise ValueError(
                f"Cannot rename {name!r} to {rename!r}: target already exists."
            )

        now = _now_iso()
        target = rename if rename is not None else name

        if rename is not None and rename != name:
            conn.execute(
                "UPDATE types SET name = ?, updated_at = ? WHERE name = ?",
                (rename, now, name),
            )

        if instructions is not None:
            conn.execute(
                "UPDATE types SET instructions = ?, updated_at = ? WHERE name = ?",
                (instructions, now, target),
            )

        conn.commit()
        row = conn.execute(
            "SELECT * FROM types WHERE name = ?", (target,)
        ).fetchone()
        return {
            "name": row["name"],
            "instructions": row["instructions"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
    finally:
        conn.close()


def type_remove(db_path: str, name: str, force: bool = False) -> dict:
    """Remove a type. Refuses if records exist and force is False.

    With force=True, deletes matching records (which cascades to record_tags),
    then deletes the type's tags, then the type itself.

    Returns {removed: {name, instructions}, records_deleted, tags_deleted, remaining_types}.
    Raises ValueError if the type is not found, or if records exist without force.
    """
    conn = get_connection(db_path)
    try:
        row = conn.execute(
            "SELECT * FROM types WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            raise ValueError(
                f"Unknown type {name!r}. Call type_list to see available types."
            )

        rc = conn.execute(
            "SELECT COUNT(*) FROM records WHERE log_type = ?", (name,)
        ).fetchone()[0]
        if rc > 0 and not force:
            raise ValueError(
                f"Type {name!r} has {rc} record(s). "
                "Pass force=True to cascade-delete the records, tags, and the type."
            )

        records_deleted = conn.execute(
            "DELETE FROM records WHERE log_type = ?", (name,)
        ).rowcount
        tags_deleted = conn.execute(
            "DELETE FROM tags WHERE log_type = ?", (name,)
        ).rowcount
        conn.execute("DELETE FROM types WHERE name = ?", (name,))
        conn.commit()

        remaining = conn.execute("SELECT COUNT(*) FROM types").fetchone()[0]
        return {
            "removed": {"name": row["name"], "instructions": row["instructions"]},
            "records_deleted": records_deleted,
            "tags_deleted": tags_deleted,
            "remaining_types": remaining,
        }
    finally:
        conn.close()


# --- Tags ---


def tag_add(db_path: str, log_type: str, name: str) -> dict:
    """Pre-declare a tag under a log_type.

    Idempotent: upserting an existing tag returns success with record_count.
    Raises ValueError if log_type is not registered.

    Returns {log_type, name, record_count}.
    """
    conn = get_connection(db_path)
    try:
        _require_type(conn, log_type)
        conn.execute(
            "INSERT OR IGNORE INTO tags (log_type, name) VALUES (?, ?)",
            (log_type, name),
        )
        conn.commit()
        count = conn.execute(
            "SELECT COUNT(*) FROM record_tags WHERE log_type = ? AND tag_name = ?",
            (log_type, name),
        ).fetchone()[0]
        return {"log_type": log_type, "name": name, "record_count": count}
    finally:
        conn.close()


def tag_list(db_path: str, log_type: str | None = None) -> dict:
    """List tags with record counts.

    With log_type: returns {log_type, tags: [{name, record_count}]} sorted by
    count DESC then name ASC — misspellings stand out as singletons next to
    canonical entries.

    Without log_type: returns {by_type: {type_name: [{name, record_count}], ...}}
    covering every registered type, including types with no tags (empty list).
    """
    conn = get_connection(db_path)
    try:
        if log_type is not None:
            _require_type(conn, log_type)
            rows = conn.execute(
                "SELECT t.name AS name, COUNT(rt.record_id) AS c "
                "FROM tags t "
                "LEFT JOIN record_tags rt ON rt.log_type = t.log_type AND rt.tag_name = t.name "
                "WHERE t.log_type = ? "
                "GROUP BY t.name "
                "ORDER BY c DESC, t.name ASC",
                (log_type,),
            ).fetchall()
            tags = [{"name": r["name"], "record_count": r["c"]} for r in rows]
            return {"log_type": log_type, "tags": tags}

        type_rows = conn.execute("SELECT name FROM types ORDER BY name ASC").fetchall()
        by_type: dict[str, list[dict]] = {}
        for t_row in type_rows:
            tn = t_row["name"]
            rows = conn.execute(
                "SELECT t.name AS name, COUNT(rt.record_id) AS c "
                "FROM tags t "
                "LEFT JOIN record_tags rt ON rt.log_type = t.log_type AND rt.tag_name = t.name "
                "WHERE t.log_type = ? "
                "GROUP BY t.name "
                "ORDER BY c DESC, t.name ASC",
                (tn,),
            ).fetchall()
            by_type[tn] = [{"name": r["name"], "record_count": r["c"]} for r in rows]
        return {"by_type": by_type}
    finally:
        conn.close()


def tag_update(db_path: str, log_type: str, old: str, new: str) -> dict:
    """Rename a tag, merging into an existing tag if the target name exists.

    If new is the same as old: no-op. If new does not exist: pure rename — the
    tags row and all record_tags rows are renamed. If new exists: merge — all
    records carrying old get new instead (deduplicated so records that already
    had both end up with one), then old is deleted.

    Returns {log_type, old, new, records_affected}.
    Raises ValueError if log_type or old is not found.
    """
    conn = get_connection(db_path)
    try:
        _require_type(conn, log_type)
        exists_old = conn.execute(
            "SELECT 1 FROM tags WHERE log_type = ? AND name = ?",
            (log_type, old),
        ).fetchone()
        if exists_old is None:
            raise ValueError(
                f"Unknown tag {old!r} under type {log_type!r}. "
                "Call tag_list to see available tags."
            )

        if old == new:
            count = conn.execute(
                "SELECT COUNT(*) FROM record_tags WHERE log_type = ? AND tag_name = ?",
                (log_type, old),
            ).fetchone()[0]
            return {"log_type": log_type, "old": old, "new": new, "records_affected": count}

        exists_new = conn.execute(
            "SELECT 1 FROM tags WHERE log_type = ? AND name = ?",
            (log_type, new),
        ).fetchone()

        if exists_new is None:
            # Pure rename — create the new tag row, update junction, drop old
            conn.execute(
                "INSERT INTO tags (log_type, name) VALUES (?, ?)",
                (log_type, new),
            )
            affected = conn.execute(
                "UPDATE record_tags SET tag_name = ? "
                "WHERE log_type = ? AND tag_name = ?",
                (new, log_type, old),
            ).rowcount
            conn.execute(
                "DELETE FROM tags WHERE log_type = ? AND name = ?",
                (log_type, old),
            )
        else:
            # Merge — records with only old get new; records with both lose old
            record_rows = conn.execute(
                "SELECT record_id FROM record_tags "
                "WHERE log_type = ? AND tag_name = ?",
                (log_type, old),
            ).fetchall()
            affected = len(record_rows)
            for r in record_rows:
                conn.execute(
                    "INSERT OR IGNORE INTO record_tags (record_id, log_type, tag_name) "
                    "VALUES (?, ?, ?)",
                    (r["record_id"], log_type, new),
                )
            conn.execute(
                "DELETE FROM record_tags WHERE log_type = ? AND tag_name = ?",
                (log_type, old),
            )
            conn.execute(
                "DELETE FROM tags WHERE log_type = ? AND name = ?",
                (log_type, old),
            )

        conn.commit()
        return {"log_type": log_type, "old": old, "new": new, "records_affected": affected}
    finally:
        conn.close()


def tag_remove(db_path: str, log_type: str, name: str) -> dict:
    """Strip a tag from all records under log_type; records survive.

    Returns {log_type, name, records_affected}.
    Raises ValueError if log_type or the tag is not found.
    """
    conn = get_connection(db_path)
    try:
        _require_type(conn, log_type)
        row = conn.execute(
            "SELECT 1 FROM tags WHERE log_type = ? AND name = ?",
            (log_type, name),
        ).fetchone()
        if row is None:
            raise ValueError(
                f"Unknown tag {name!r} under type {log_type!r}. "
                "Call tag_list to see available tags."
            )
        affected = conn.execute(
            "DELETE FROM record_tags WHERE log_type = ? AND tag_name = ?",
            (log_type, name),
        ).rowcount
        conn.execute(
            "DELETE FROM tags WHERE log_type = ? AND name = ?",
            (log_type, name),
        )
        conn.commit()
        return {"log_type": log_type, "name": name, "records_affected": affected}
    finally:
        conn.close()
