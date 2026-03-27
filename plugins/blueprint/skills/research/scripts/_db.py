"""Research database operations.

SQLite-backed storage for entity research data. Unified entity model
with URL-to-URL provenance tracking how entities were found. Relevance
scoring filters candidates for deep research.

WAL mode enables concurrent reads while writes are in progress.
Write contention handled by retry_write decorator with random jitter.
"""

from __future__ import annotations

import functools
import random
import sqlite3
import time
from collections.abc import Callable
from pathlib import Path
from typing import TypeVar
from urllib.parse import urlparse

F = TypeVar("F", bound=Callable)

SCHEMA = """
CREATE TABLE IF NOT EXISTS entities (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'example',
    stage TEXT NOT NULL DEFAULT 'new',
    relevance INTEGER DEFAULT 0,
    description TEXT NOT NULL DEFAULT '',
    last_modified TEXT
);

CREATE TABLE IF NOT EXISTS entity_urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    url TEXT NOT NULL,
    UNIQUE(entity_id, url)
);

CREATE TABLE IF NOT EXISTS entity_measures (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    measure TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (entity_id, measure)
);

CREATE TABLE IF NOT EXISTS entity_notes (
    id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    note TEXT NOT NULL,
    last_modified TEXT,
    UNIQUE(entity_id, note)
);

CREATE TABLE IF NOT EXISTS entity_source_data (
    entity_id TEXT NOT NULL REFERENCES entities(id),
    source_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (entity_id, source_type, key)
);

CREATE TABLE IF NOT EXISTS url_provenance (
    source_url TEXT NOT NULL,
    entity_id TEXT NOT NULL REFERENCES entities(id),
    PRIMARY KEY (source_url, entity_id)
);
"""


# --- Connection and utilities ---


def get_connection(db_path: str) -> sqlite3.Connection:
    """Open database connection with WAL mode and foreign keys."""
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=0")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def retry_write(func: F) -> F:
    """Retry write operations on database lock with random jitter.

    Catches sqlite3.OperationalError for 'database is locked' and retries
    with random 50-200ms jitter between attempts.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                return func(*args, **kwargs)
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    time.sleep(random.uniform(0.05, 0.2))
                else:
                    raise
    return wrapper  # type: ignore[return-value]


def normalize_url(url: str | None) -> str | None:
    """Normalize URL for storage and deduplication.

    Strips scheme, strips www., lowercases, strips trailing slash.
    Keeps path for profile-level identity.
    """
    if not url:
        return None
    parsed = urlparse(url if "://" in url else f"https://{url}")
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    hostname = hostname.lower()
    path = parsed.path.rstrip("/")
    result = f"{hostname}{path}" if path else hostname
    return result or None


def _next_id(conn: sqlite3.Connection, table: str, prefix: str) -> str:
    """Generate next prefixed ID for a table (e.g., e1, e2, n1, n2)."""
    row = conn.execute(
        f"SELECT id FROM {table} ORDER BY CAST(SUBSTR(id, {len(prefix) + 1}) AS INTEGER) DESC LIMIT 1",
    ).fetchone()
    if row:
        num = int(row["id"][len(prefix):]) + 1
    else:
        num = 1
    return f"{prefix}{num}"


def _find_entity_by_url(conn: sqlite3.Connection, url: str) -> dict | None:
    """Find existing entity by normalized URL match."""
    normalized = normalize_url(url)
    if not normalized:
        return None
    row = conn.execute(
        "SELECT e.id, e.name FROM entities e "
        "JOIN entity_urls eu ON e.id = eu.entity_id "
        "WHERE eu.url = ?",
        (normalized,),
    ).fetchone()
    return dict(row) if row else None


def _add_entity_url(conn: sqlite3.Connection, entity_id: str, url: str) -> None:
    """Add a normalized URL to an entity (ignores duplicates)."""
    normalized = normalize_url(url)
    if normalized:
        conn.execute(
            "INSERT OR IGNORE INTO entity_urls (entity_id, url) VALUES (?, ?)",
            (entity_id, normalized),
        )


def _add_provenance(conn: sqlite3.Connection, entity_id: str, source_url: str) -> None:
    """Record provenance — source URL that led to entity."""
    normalized = normalize_url(source_url)
    if normalized:
        conn.execute(
            "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
            (normalized, entity_id),
        )


def _touch(conn: sqlite3.Connection, table: str, row_id: str) -> None:
    """Set last_modified to current UTC timestamp."""
    conn.execute(
        f"UPDATE {table} SET last_modified = datetime('now') WHERE id = ?",
        (row_id,),
    )


# --- Database lifecycle ---


def init_db(db_path: str) -> str:
    """Create database with schema. Idempotent — safe to run on existing DB."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = get_connection(str(path))
    conn.executescript(SCHEMA)
    conn.close()
    return f"Database initialized: {path}"


# --- Entity registration ---


@retry_write
def register_entity(
    db_path: str,
    name: str,
    url: str | None = None,
    source_url: str | None = None,
    relevance: int | None = None,
    description: str | None = None,
    role: str | None = None,
) -> str:
    """Register entity with URL dedup and optional provenance."""
    conn = get_connection(db_path)
    try:
        with conn:
            if url:
                existing = _find_entity_by_url(conn, url)
                if existing:
                    if source_url:
                        _add_provenance(conn, existing["id"], source_url)
                    return f"Already registered: {existing['name']} (id: {existing['id']})"

            entity_id = _next_id(conn, "entities", "e")
            conn.execute(
                "INSERT INTO entities (id, name, role, relevance, description) VALUES (?, ?, ?, ?, ?)",
                (entity_id, name, role or "example", relevance or 0, description or ""),
            )

            if url:
                _add_entity_url(conn, entity_id, url)
            if source_url:
                _add_provenance(conn, entity_id, source_url)

            _touch(conn, "entities", entity_id)
            return f"Registered: {name} (id: {entity_id})"
    finally:
        conn.close()


def compute_normalize_url(url: str) -> str:
    """Compute and return normalized form of a URL."""
    result = normalize_url(url)
    return result if result else url


# --- Stage enforcement ---


_STAGE_ORDER = ["new", "rejected", "researched"]


def _enforce_stage(conn: sqlite3.Connection, entity_id: str, target_stage: str) -> None:
    """Enforce stage transition by clearing data above target stage.

    Moving to a lower stage clears higher stage data. Transitioning from
    'merged' only allows 'new' (post-reconciliation).
    """
    current = conn.execute(
        "SELECT stage FROM entities WHERE id = ?", (entity_id,),
    ).fetchone()["stage"]

    if current == "merged":
        if target_stage != "new":
            raise ValueError(
                f"Entity {entity_id} is merged — can only transition to 'new', not '{target_stage}'",
            )
        conn.execute("UPDATE entities SET stage = 'new' WHERE id = ?", (entity_id,))
        return

    current_idx = _STAGE_ORDER.index(current)
    target_idx = _STAGE_ORDER.index(target_stage)

    if current_idx <= target_idx:
        conn.execute("UPDATE entities SET stage = ? WHERE id = ?", (target_stage, entity_id))
        return

    # Clear from researched downward if moving below it
    if current_idx >= _STAGE_ORDER.index("researched") and target_idx < _STAGE_ORDER.index("researched"):
        conn.execute("DELETE FROM entity_notes WHERE entity_id = ?", (entity_id,))
        conn.execute("DELETE FROM entity_measures WHERE entity_id = ?", (entity_id,))

    conn.execute("UPDATE entities SET stage = ? WHERE id = ?", (target_stage, entity_id))


# --- Entity updates ---


@retry_write
def update_entity(
    db_path: str,
    ids: list[str] | None = None,
    all_entities: bool = False,
    stage: str | None = None,
    relevance: int | None = None,
    description: str | None = None,
    name: str | None = None,
    role: str | None = None,
) -> str:
    """Update entity stage, relevance, description, name, and/or role."""
    if not stage and relevance is None and description is None and name is None and role is None:
        raise ValueError("At least one of stage, relevance, description, name, or role is required")

    conn = get_connection(db_path)
    try:
        if all_entities:
            entity_ids = [r["id"] for r in conn.execute(
                "SELECT id FROM entities ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
            ).fetchall()]
        else:
            entity_ids = ids or []

        updated = 0
        with conn:
            for entity_id in entity_ids:
                row = conn.execute("SELECT id FROM entities WHERE id = ?", (entity_id,)).fetchone()
                if not row:
                    continue
                if stage:
                    _enforce_stage(conn, entity_id, stage)
                if relevance is not None:
                    conn.execute("UPDATE entities SET relevance = ? WHERE id = ?", (relevance, entity_id))
                if description is not None:
                    conn.execute("UPDATE entities SET description = ? WHERE id = ?", (description, entity_id))
                if name is not None:
                    conn.execute("UPDATE entities SET name = ? WHERE id = ?", (name, entity_id))
                if role is not None:
                    conn.execute("UPDATE entities SET role = ? WHERE id = ?", (role, entity_id))
                _touch(conn, "entities", entity_id)
                updated += 1

        parts = []
        if stage:
            parts.append(f"stage: {stage}")
        if relevance is not None:
            parts.append(f"relevance: {relevance}")
        if description is not None:
            parts.append(f"description: {description}")
        if name is not None:
            parts.append(f"name: {name}")
        if role is not None:
            parts.append(f"role: {role}")
        return f"Updated {updated} entities ({', '.join(parts)})"
    finally:
        conn.close()


# --- Notes ---


@retry_write
def upsert_notes(db_path: str, entity_id: str, notes: list[str]) -> str:
    """Add notes (atomic facts) to entity. Skips duplicates."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")

        added = 0
        skipped = 0
        with conn:
            for note in notes:
                note_id = _next_id(conn, "entity_notes", "n")
                cursor = conn.execute(
                    "INSERT OR IGNORE INTO entity_notes (id, entity_id, note) VALUES (?, ?, ?)",
                    (note_id, entity_id, note),
                )
                if cursor.rowcount > 0:
                    _touch(conn, "entity_notes", note_id)
                    added += 1
                else:
                    skipped += 1

        parts = [f"Added {added} notes to {row['name']} (id: {entity_id})"]
        if skipped:
            parts.append(f"Skipped {skipped} duplicates")
        return ". ".join(parts)
    finally:
        conn.close()


# --- Queries ---


def get_entity(db_path: str, entity_id: str) -> str:
    """Entity detail: URLs, provenance, relevance, description, measures, source data, notes."""
    conn = get_connection(db_path)
    try:
        entity = conn.execute("SELECT * FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")

        lines = [
            f"# {entity['name']} (id: {entity['id']})",
            f"Role: {entity['role']}",
            f"Stage: {entity['stage']}",
            f"Relevance: {entity['relevance'] if entity['relevance'] is not None else 'unset'}",
        ]
        if entity["last_modified"]:
            lines.append(f"Last modified: {entity['last_modified']}")
        if entity["description"]:
            lines.append(f"Description: {entity['description']}")

        urls = conn.execute(
            "SELECT url FROM entity_urls WHERE entity_id = ? ORDER BY id", (entity_id,),
        ).fetchall()
        if urls:
            lines.append(f"\nURLs ({len(urls)}):")
            for u in urls:
                lines.append(f"  {u['url']}")

        provenance = conn.execute(
            "SELECT source_url FROM url_provenance WHERE entity_id = ? ORDER BY source_url",
            (entity_id,),
        ).fetchall()
        if provenance:
            lines.append(f"\nFound via ({len(provenance)}):")
            for p in provenance:
                lines.append(f"  {p['source_url']}")

        measures = conn.execute(
            "SELECT measure, value FROM entity_measures WHERE entity_id = ? ORDER BY measure",
            (entity_id,),
        ).fetchall()
        if measures:
            lines.append(f"\nMeasures ({len(measures)}):")
            for m in measures:
                lines.append(f"  {m['measure']}: {m['value']}")

        source_data = conn.execute(
            "SELECT source_type, key, value FROM entity_source_data WHERE entity_id = ? ORDER BY source_type, key",
            (entity_id,),
        ).fetchall()
        if source_data:
            lines.append(f"\nSource data ({len(source_data)}):")
            current_type = None
            for sd in source_data:
                if sd["source_type"] != current_type:
                    current_type = sd["source_type"]
                    lines.append(f"  [{current_type}]")
                lines.append(f"    {sd['key']}: {sd['value']}")

        notes = conn.execute(
            "SELECT id, note FROM entity_notes WHERE entity_id = ? ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
            (entity_id,),
        ).fetchall()
        if notes:
            lines.append(f"\nNotes ({len(notes)}):")
            for n in notes:
                lines.append(f"  [{n['id']}] {n['note']}")

        return "\n".join(lines)
    finally:
        conn.close()


def list_entities(
    db_path: str,
    role: str | None = None,
    stage: str | None = None,
    modified_before: str | None = None,
) -> str:
    """List entities with stage and relevance, optionally filtered."""
    conn = get_connection(db_path)
    try:
        conditions: list[str] = []
        params: list[str] = []
        if role:
            conditions.append("e.role = ?")
            params.append(role)
        if stage:
            conditions.append("e.stage = ?")
            params.append(stage)
        if modified_before:
            conditions.append("(e.last_modified IS NULL OR datetime(e.last_modified) < datetime(?))")
            params.append(modified_before)
        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        entities = conn.execute(
            f"SELECT e.id, e.name, e.role, e.stage, e.relevance, e.description FROM entities e{where} ORDER BY e.relevance DESC, e.name",
            params,
        ).fetchall()

        if not entities:
            return "No entities registered."

        stage_icons = {"new": ".", "rejected": "x", "researched": "+", "merged": "~"}
        filters = []
        if role:
            filters.append(f"role: {role}")
        if stage:
            filters.append(f"stage: {stage}")
        label = f" ({', '.join(filters)})" if filters else ""
        lines = [f"Entities ({len(entities)}){label}:"]
        for e in entities:
            icon = stage_icons.get(e["stage"], "?")
            role_tag = f" [{e['role']}]" if not role else ""
            desc_part = f" -- {e['description']}" if e["description"] else ""
            rel_display = e["relevance"] if e["relevance"] is not None else "?"
            lines.append(f"  [{icon}] {e['id']}. {e['name']} (relevance: {rel_display}){desc_part}{role_tag}")
        return "\n".join(lines)
    finally:
        conn.close()


def get_stats(db_path: str) -> str:
    """Database summary: entity counts by role, stage distribution, provenance stats."""
    conn = get_connection(db_path)
    try:
        entity_total = conn.execute("SELECT COUNT(*) FROM entities").fetchone()[0]

        role_counts = {}
        for role_name in ("example", "directory", "context"):
            role_counts[role_name] = conn.execute(
                "SELECT COUNT(*) FROM entities WHERE role = ?", (role_name,),
            ).fetchone()[0]

        stage_counts = {}
        for stage_name in ("new", "rejected", "researched", "merged"):
            stage_counts[stage_name] = conn.execute(
                "SELECT COUNT(*) FROM entities WHERE stage = ?", (stage_name,),
            ).fetchone()[0]

        url_count = conn.execute("SELECT COUNT(*) FROM entity_urls").fetchone()[0]
        provenance_count = conn.execute("SELECT COUNT(*) FROM url_provenance").fetchone()[0]
        measure_count = conn.execute("SELECT COUNT(*) FROM entity_measures").fetchone()[0]
        note_count = conn.execute("SELECT COUNT(*) FROM entity_notes").fetchone()[0]
        source_data_count = conn.execute("SELECT COUNT(*) FROM entity_source_data").fetchone()[0]

        relevance_rows = conn.execute(
            "SELECT relevance, COUNT(*) as cnt FROM entities WHERE role = 'example' GROUP BY relevance ORDER BY relevance DESC",
        ).fetchall()

        lines = ["Database Statistics:"]
        role_parts = [f"{role_counts[r]} {r}" for r in ("example", "directory", "context") if role_counts[r] > 0]
        lines.append(f"  Entities: {entity_total} ({', '.join(role_parts)})")
        stage_parts = [f"{stage_counts['new']} new", f"{stage_counts['rejected']} rejected", f"{stage_counts['researched']} researched"]
        if stage_counts["merged"] > 0:
            stage_parts.append(f"{stage_counts['merged']} merged")
        lines.append(f"  Stage: {', '.join(stage_parts)}")
        lines.append(f"  URLs: {url_count}")
        lines.append(f"  Provenance links: {provenance_count}")
        lines.append(f"  Measures: {measure_count}")
        lines.append(f"  Notes: {note_count}")
        lines.append(f"  Source data fields: {source_data_count}")

        if relevance_rows:
            lines.append(f"\nRelevance distribution (examples):")
            for r in relevance_rows:
                lines.append(f"  {r['relevance']}: {r['cnt']} entities")

        return "\n".join(lines)
    finally:
        conn.close()


# --- Batch registration ---


@retry_write
def register_batch(db_path: str, entities: list[dict], source_url: str | None = None) -> str:
    """Register multiple entities with URL dedup, optional notes for new entities.

    Each entity dict may contain: name, url, source_url, description, relevance,
    role, notes. Notes only written for newly created entities.
    """
    conn = get_connection(db_path)
    try:
        new_count = 0
        already_registered = []
        errors = []
        normalized_source = normalize_url(source_url) if source_url else None
        with conn:
            for entry in entities:
                name = entry.get("name", "")
                url = entry.get("url")
                desc = entry.get("description", "")
                rel = entry.get("relevance", 0)
                role = entry.get("role", "example")
                notes = entry.get("notes", [])
                entry_source = entry.get("source_url")
                effective_source = normalize_url(entry_source) if entry_source else normalized_source

                if not name:
                    errors.append("Skipped entry with no name")
                    continue

                existing = _find_entity_by_url(conn, url) if url else None

                if existing:
                    entity_id = existing["id"]
                    if effective_source:
                        conn.execute(
                            "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
                            (effective_source, entity_id),
                        )
                    normalized = normalize_url(url)
                    already_registered.append(f"  {entity_id}. {normalized}")
                else:
                    entity_id = _next_id(conn, "entities", "e")
                    conn.execute(
                        "INSERT INTO entities (id, name, role, relevance, description) VALUES (?, ?, ?, ?, ?)",
                        (entity_id, name, role, rel, desc),
                    )
                    if url:
                        _add_entity_url(conn, entity_id, url)
                    if effective_source:
                        conn.execute(
                            "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
                            (effective_source, entity_id),
                        )
                    for note in notes:
                        note_id = _next_id(conn, "entity_notes", "n")
                        conn.execute(
                            "INSERT OR IGNORE INTO entity_notes (id, entity_id, note) VALUES (?, ?, ?)",
                            (note_id, entity_id, note),
                        )
                        _touch(conn, "entity_notes", note_id)
                    _touch(conn, "entities", entity_id)
                    new_count += 1

        parts = [f"Batch: {new_count} new, {len(already_registered)} already registered"]
        if already_registered:
            parts.append("Already registered (reconcile manually):")
            parts.extend(already_registered)
        if errors:
            parts.append(f"Errors: {len(errors)}")
            parts.extend(f"  {e}" for e in errors)
        return "\n".join(parts)
    finally:
        conn.close()


# --- Provenance and URLs ---


@retry_write
def upsert_provenance(db_path: str, entity_id: str, source_url: str) -> str:
    """Record that entity was found via a source URL."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        normalized = normalize_url(source_url)
        if not normalized:
            raise ValueError("Could not normalize source URL")
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
                (normalized, entity_id),
            )
        return f"Provenance added: {row['name']} (id: {entity_id}) found via {normalized}"
    finally:
        conn.close()


@retry_write
def upsert_url(db_path: str, entity_id: str, url: str) -> str:
    """Add URL to existing entity (ignores duplicates)."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        normalized = normalize_url(url)
        if not normalized:
            raise ValueError("Could not normalize URL")
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO entity_urls (entity_id, url) VALUES (?, ?)",
                (row["id"], normalized),
            )
        return f"Added URL {normalized} to {row['name']} (id: {row['id']})"
    finally:
        conn.close()


# --- Note operations ---


@retry_write
def update_note(db_path: str, note_id: str, note: str) -> str:
    """Update a single note by ID with corrected text."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, entity_id FROM entity_notes WHERE id = ?", (note_id,)).fetchone()
        if not row:
            raise ValueError(f"Note not found: {note_id}")
        with conn:
            conn.execute("UPDATE entity_notes SET note = ? WHERE id = ?", (note, note_id))
            _touch(conn, "entity_notes", note_id)
        return f"Updated note {note_id}"
    finally:
        conn.close()


@retry_write
def remove_notes(db_path: str, entity_id: str, note_ids: list[str]) -> str:
    """Remove specific notes by ID from entity."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        with conn:
            placeholders = ",".join("?" * len(note_ids))
            existing = conn.execute(
                f"SELECT id FROM entity_notes WHERE entity_id = ? AND id IN ({placeholders})",
                [entity_id] + note_ids,
            ).fetchall()
            existing_ids = {r["id"] for r in existing}
            if existing_ids:
                placeholders = ",".join("?" * len(existing_ids))
                conn.execute(
                    f"DELETE FROM entity_notes WHERE entity_id = ? AND id IN ({placeholders})",
                    [entity_id] + list(existing_ids),
                )
        return f"Removed {len(existing_ids)} notes from {row['name']} (id: {entity_id})"
    finally:
        conn.close()


# --- Touch ---


@retry_write
def touch_entities(db_path: str, ids: list[str] | None = None, all_entities: bool = False) -> str:
    """Mark entities as reviewed — sets last_modified to now without changes."""
    conn = get_connection(db_path)
    try:
        if all_entities:
            entity_ids = [r["id"] for r in conn.execute(
                "SELECT id FROM entities ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
            ).fetchall()]
        else:
            entity_ids = ids or []
        touched = 0
        with conn:
            for entity_id in entity_ids:
                row = conn.execute("SELECT id FROM entities WHERE id = ?", (entity_id,)).fetchone()
                if not row:
                    continue
                _touch(conn, "entities", entity_id)
                touched += 1
        return f"Touched {touched} entities"
    finally:
        conn.close()


# --- Provenance queries ---


def list_provenance(db_path: str, entity_id: str | None = None) -> str:
    """List provenance relationships, optionally filtered by entity ID."""
    conn = get_connection(db_path)
    try:
        if entity_id:
            rows = conn.execute(
                "SELECT source_url FROM url_provenance WHERE entity_id = ? ORDER BY source_url",
                (entity_id,),
            ).fetchall()
            if not rows:
                return f"No provenance for entity {entity_id}"
            lines = [f"Provenance for {entity_id} ({len(rows)} sources):"]
            for r in rows:
                lines.append(f"  {r['source_url']}")
        else:
            rows = conn.execute(
                "SELECT source_url, COUNT(*) as cnt FROM url_provenance GROUP BY source_url ORDER BY cnt DESC",
            ).fetchall()
            if not rows:
                return "No provenance recorded."
            lines = [f"Provenance sources ({len(rows)}):"]
            for r in rows:
                lines.append(f"  {r['source_url']} ({r['cnt']} entities)")
        return "\n".join(lines)
    finally:
        conn.close()


def list_reach(db_path: str, min_count: int = 0) -> str:
    """Entities ranked by number of independent provenance sources."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT entity_id, COUNT(*) as cnt FROM url_provenance "
            "GROUP BY entity_id HAVING cnt >= ? ORDER BY cnt DESC",
            (min_count,),
        ).fetchall()
        if not rows:
            return "No entities with provenance."
        lines = [f"Entities by reach ({len(rows)}):"]
        for r in rows:
            entity = conn.execute("SELECT name FROM entities WHERE id = ?", (r["entity_id"],)).fetchone()
            name = entity["name"] if entity else "?"
            lines.append(f"  {r['entity_id']}. {name} ({r['cnt']} sources)")
        return "\n".join(lines)
    finally:
        conn.close()


# --- Search and export ---


def search_notes(db_path: str, pattern: str, stage: str | None = None, min_relevance: int | None = None) -> str:
    """Search notes by keyword pattern across entities."""
    conn = get_connection(db_path)
    try:
        conditions = ["n.note LIKE ?"]
        params: list[str | int] = [f"%{pattern}%"]
        if stage:
            conditions.append("e.stage = ?")
            params.append(stage)
        if min_relevance is not None:
            conditions.append("e.relevance >= ?")
            params.append(min_relevance)

        where = " AND ".join(conditions)
        rows = conn.execute(
            f"SELECT n.id, n.note, e.id as entity_id, e.name "
            f"FROM entity_notes n JOIN entities e ON n.entity_id = e.id "
            f"WHERE {where} ORDER BY e.relevance DESC, e.name",
            params,
        ).fetchall()

        if not rows:
            return f'No notes matching "{pattern}"'
        lines = [f'Notes matching "{pattern}" ({len(rows)}):']
        for r in rows:
            lines.append(f"  [{r['id']}] {r['entity_id']}. {r['name']}: {r['note']}")
        return "\n".join(lines)
    finally:
        conn.close()


def export_db(db_path: str, format: str = "json") -> str:
    """Export full database."""
    import csv
    import io
    import json

    conn = get_connection(db_path)
    try:
        entities = conn.execute(
            "SELECT * FROM entities ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
        ).fetchall()

        if format == "json":
            result = []
            for e in entities:
                entity_data = dict(e)
                entity_data["urls"] = [r["url"] for r in conn.execute(
                    "SELECT url FROM entity_urls WHERE entity_id = ? ORDER BY id", (e["id"],),
                ).fetchall()]
                entity_data["provenance"] = [r["source_url"] for r in conn.execute(
                    "SELECT source_url FROM url_provenance WHERE entity_id = ? ORDER BY source_url",
                    (e["id"],),
                ).fetchall()]
                entity_data["notes"] = [{"id": r["id"], "note": r["note"]} for r in conn.execute(
                    "SELECT id, note FROM entity_notes WHERE entity_id = ? ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)",
                    (e["id"],),
                ).fetchall()]
                entity_data["measures"] = {r["measure"]: r["value"] for r in conn.execute(
                    "SELECT measure, value FROM entity_measures WHERE entity_id = ?", (e["id"],),
                ).fetchall()}
                result.append(entity_data)
            return json.dumps(result, indent=2)

        elif format == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["id", "name", "role", "stage", "relevance", "description", "urls", "note_count"])
            for e in entities:
                urls = [r["url"] for r in conn.execute(
                    "SELECT url FROM entity_urls WHERE entity_id = ?", (e["id"],),
                ).fetchall()]
                note_count = conn.execute(
                    "SELECT COUNT(*) FROM entity_notes WHERE entity_id = ?", (e["id"],),
                ).fetchone()[0]
                writer.writerow([
                    e["id"], e["name"], e["role"], e["stage"],
                    e["relevance"], e["description"], "; ".join(urls), note_count,
                ])
            return output.getvalue()

        return f"Unknown format: {format}"
    finally:
        conn.close()


# --- Measures ---


@retry_write
def upsert_measures(db_path: str, entity_id: str, measures: list[str]) -> str:
    """Add or update measures for entity. Measures are key=value pairs."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        updated = 0
        with conn:
            for m in measures:
                key, _, value = m.partition("=")
                if not value:
                    raise ValueError(f"Invalid measure format (expected key=value): {m}")
                conn.execute(
                    "INSERT OR REPLACE INTO entity_measures (entity_id, measure, value) VALUES (?, ?, ?)",
                    (entity_id, key.strip(), value.strip()),
                )
                updated += 1
        return f"Upserted {updated} measures for {row['name']} (id: {entity_id})"
    finally:
        conn.close()


def get_measures(db_path: str) -> str:
    """Measure distributions across entities."""
    conn = get_connection(db_path)
    try:
        measures = conn.execute(
            "SELECT measure, COUNT(DISTINCT entity_id) as cnt FROM entity_measures GROUP BY measure ORDER BY cnt DESC",
        ).fetchall()
        if not measures:
            return "No measures recorded."
        lines = [f"Measure distributions ({len(measures)} unique measures):"]
        for m in measures:
            lines.append(f"  {m['measure']}: {m['cnt']} entities")
        return "\n".join(lines)
    finally:
        conn.close()


@retry_write
def clear_measures(db_path: str) -> str:
    """Clear all entity measures (for re-analysis)."""
    conn = get_connection(db_path)
    try:
        with conn:
            count = conn.execute("SELECT COUNT(*) FROM entity_measures").fetchone()[0]
            conn.execute("DELETE FROM entity_measures")
        return f"Cleared {count} measures"
    finally:
        conn.close()


# --- Source data ---


@retry_write
def upsert_source_data(db_path: str, entity_id: str, source_type: str, data: list[str]) -> str:
    """Upsert structured key:value source data to entity. Data is list of 'key=value' strings."""
    conn = get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not row:
            raise ValueError(f"Entity not found: {entity_id}")
        pairs = {}
        for item in data:
            if "=" not in item:
                raise ValueError(f"Invalid format '{item}' — expected key=value")
            key, value = item.split("=", 1)
            pairs[key.strip()] = value.strip()
        with conn:
            for key, value in pairs.items():
                conn.execute(
                    "INSERT OR REPLACE INTO entity_source_data (entity_id, source_type, key, value) VALUES (?, ?, ?, ?)",
                    (entity_id, source_type, key, value),
                )
        return f"Set {len(pairs)} {source_type} fields for {row['name']} (id: {entity_id}): {', '.join(pairs.keys())}"
    finally:
        conn.close()


def list_source_data(
    db_path: str,
    source_type: str | None = None,
    key: str | None = None,
    entity_id: str | None = None,
) -> str:
    """List source data, optionally filtered."""
    conn = get_connection(db_path)
    try:
        conditions = []
        params = []
        if source_type:
            conditions.append("sd.source_type = ?")
            params.append(source_type)
        if key:
            conditions.append("sd.key = ?")
            params.append(key)
        if entity_id:
            conditions.append("sd.entity_id = ?")
            params.append(entity_id)

        where = f" WHERE {' AND '.join(conditions)}" if conditions else ""
        rows = conn.execute(
            f"SELECT sd.entity_id, sd.source_type, sd.key, sd.value, e.name as entity_name "
            f"FROM entity_source_data sd JOIN entities e ON sd.entity_id = e.id "
            f"{where} ORDER BY e.name, sd.source_type, sd.key",
            params,
        ).fetchall()

        if not rows:
            return "No source data found."

        lines = []
        current_entity = None
        current_type = None
        for r in rows:
            if r["entity_id"] != current_entity:
                current_entity = r["entity_id"]
                current_type = None
                lines.append(f"\n{r['entity_name']} ({r['entity_id']}):")
            if r["source_type"] != current_type:
                current_type = r["source_type"]
                lines.append(f"  [{r['source_type']}]")
            lines.append(f"    {r['key']}: {r['value']}")
        lines.append(f"\nTotal: {len(rows)} fields")
        return "\n".join(lines)
    finally:
        conn.close()


# --- Deduplication and merge ---


def _union_find_groups(pairs: list[tuple[str, str]]) -> dict[str, set[str]]:
    """Build transitive groups from pairs using union-find."""
    entity_groups: dict[str, set[str]] = {}
    entity_to_group: dict[str, str] = {}

    for a, b in pairs:
        existing_reps = set()
        for eid in (a, b):
            if eid in entity_to_group:
                existing_reps.add(entity_to_group[eid])

        all_members: set[str] = {a, b}
        for rep in existing_reps:
            all_members.update(entity_groups.pop(rep))

        new_rep = min(all_members, key=lambda e: int(e[1:]))
        entity_groups[new_rep] = all_members
        for eid in all_members:
            entity_to_group[eid] = new_rep

    return {rep: members for rep, members in entity_groups.items() if len(members) > 1}


def find_duplicates(db_path: str, templates_db: str | None = None) -> str:
    """Find duplicate entities by URL overlap and source-data key matches.

    Detection only — does not merge. Reports transitive groups with evidence.
    """
    import json
    from collections import defaultdict

    conn = get_connection(db_path)
    try:
        # URL overlap
        url_pairs: list[tuple[str, str]] = []
        url_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)

        overlaps = conn.execute(
            "SELECT url, GROUP_CONCAT(entity_id) as entity_ids, COUNT(DISTINCT entity_id) as cnt "
            "FROM entity_urls GROUP BY url HAVING cnt > 1 ORDER BY url",
        ).fetchall()

        for row in overlaps:
            ids = sorted([x.strip() for x in row["entity_ids"].split(",")], key=lambda e: int(e[1:]))
            for i in range(len(ids)):
                for j in range(i + 1, len(ids)):
                    pair = (ids[i], ids[j])
                    url_pairs.append(pair)
                    url_evidence[pair].append(f"URL match: {row['url']}")

        # Source-data dedup keys
        source_pairs: list[tuple[str, str]] = []
        source_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)

        if templates_db and Path(templates_db).exists():
            conn.execute("ATTACH DATABASE ? AS templates", (templates_db,))

            rows = conn.execute(
                "SELECT esd.entity_id, esd.source_type, GROUP_CONCAT(esd.value, '|') AS dedup_value "
                "FROM entity_source_data esd "
                "JOIN templates.source_types st ON st.type = esd.source_type "
                "JOIN json_each(st.dedup_key) dk ON esd.key = dk.value "
                "GROUP BY esd.entity_id, esd.source_type",
            ).fetchall()

            sd_groups: dict = defaultdict(list)
            for r in rows:
                sd_groups[(r["source_type"], r["dedup_value"])].append(r["entity_id"])

            dedup_key_names: dict[str, list[str]] = {}
            for source_type_key, _ in sd_groups:
                if source_type_key not in dedup_key_names:
                    dk_row = conn.execute(
                        "SELECT dedup_key FROM templates.source_types WHERE type = ?",
                        (source_type_key,),
                    ).fetchone()
                    try:
                        dedup_key_names[source_type_key] = json.loads(dk_row["dedup_key"]) if dk_row else []
                    except json.JSONDecodeError:
                        dedup_key_names[source_type_key] = []

            for (source_type_key, dedup_value), entity_ids in sd_groups.items():
                if len(entity_ids) < 2:
                    continue
                ids = sorted(entity_ids, key=lambda e: int(e[1:]))
                key_names = dedup_key_names.get(source_type_key, [])
                values = dedup_value.split("|")
                label_parts = [f"{k}={v}" for k, v in zip(key_names, values)]
                label = ", ".join(label_parts) if label_parts else dedup_value
                for i in range(len(ids)):
                    for j in range(i + 1, len(ids)):
                        pair = (ids[i], ids[j])
                        source_pairs.append(pair)
                        source_evidence[pair].append(f"Source match ({source_type_key}): {label}")

        # Combine into transitive groups
        all_pairs = url_pairs + source_pairs
        if not all_pairs:
            return "No duplicates found."

        groups = _union_find_groups(all_pairs)
        if not groups:
            return "No duplicates found."

        all_evidence: dict[tuple[str, str], list[str]] = defaultdict(list)
        for pair, evs in url_evidence.items():
            all_evidence[pair].extend(evs)
        for pair, evs in source_evidence.items():
            all_evidence[pair].extend(evs)

        entity_info: dict[str, dict] = {}
        all_ids = {eid for members in groups.values() for eid in members}
        for eid in all_ids:
            row = conn.execute("SELECT id, name, stage, relevance FROM entities WHERE id = ?", (eid,)).fetchone()
            if row:
                notes_count = conn.execute("SELECT COUNT(*) FROM entity_notes WHERE entity_id = ?", (eid,)).fetchone()[0]
                entity_info[eid] = {"name": row["name"], "stage": row["stage"], "relevance": row["relevance"], "notes": notes_count}

        stage_icons = {"new": ".", "rejected": "x", "researched": "+", "merged": "~"}
        lines = [f"Duplicate groups ({len(groups)}):\n"]
        for group_idx, (_, members) in enumerate(sorted(groups.items(), key=lambda item: int(item[0][1:])), 1):
            sorted_members = sorted(members, key=lambda e: int(e[1:]))
            lines.append(f"  Group {group_idx}:")
            for eid in sorted_members:
                info = entity_info.get(eid, {})
                icon = stage_icons.get(info.get("stage", ""), "?")
                lines.append(f"    [{icon}] {eid} {info.get('name', '?')} (relevance: {info.get('relevance', '?')}, notes: {info.get('notes', '?')})")
            lines.append("    Evidence:")
            shown = set()
            for i in range(len(sorted_members)):
                for j in range(i + 1, len(sorted_members)):
                    pair = (sorted_members[i], sorted_members[j])
                    if pair in all_evidence:
                        for ev in all_evidence[pair]:
                            ev_key = (pair, ev)
                            if ev_key not in shown:
                                lines.append(f"      {pair[0]}-{pair[1]}: {ev}")
                                shown.add(ev_key)
            lines.append("")

        lines.append(f"Found {len(groups)} duplicate groups containing {sum(len(m) for m in groups.values())} entities.")
        return "\n".join(lines)
    finally:
        conn.close()


@retry_write
def merge_entities(db_path: str, ids: list[str]) -> str:
    """Merge multiple entities into lowest-ID survivor. Fully mechanical."""
    if len(ids) < 2:
        raise ValueError("Merge requires at least 2 entity IDs")

    entity_ids_sorted = sorted(ids, key=lambda x: int(x[1:]))
    survivor_id = entity_ids_sorted[0]
    absorbed_ids = entity_ids_sorted[1:]

    conn = get_connection(db_path)
    try:
        entities = {}
        for eid in entity_ids_sorted:
            row = conn.execute("SELECT id, name, description FROM entities WHERE id = ?", (eid,)).fetchone()
            if not row:
                raise ValueError(f"Entity not found: {eid}")
            entities[eid] = row

        with conn:
            for source_id in absorbed_ids:
                conn.execute(
                    "INSERT OR IGNORE INTO entity_urls (entity_id, url) SELECT ?, url FROM entity_urls WHERE entity_id = ?",
                    (survivor_id, source_id),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) SELECT source_url, ? FROM url_provenance WHERE entity_id = ?",
                    (survivor_id, source_id),
                )
                conn.execute(
                    "INSERT OR IGNORE INTO entity_source_data (entity_id, source_type, key, value) SELECT ?, source_type, key, value FROM entity_source_data WHERE entity_id = ?",
                    (survivor_id, source_id),
                )
                conn.execute("UPDATE entity_notes SET entity_id = ? WHERE entity_id = ?", (survivor_id, source_id))

                conn.execute("DELETE FROM entity_urls WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM url_provenance WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM entity_source_data WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM entity_measures WHERE entity_id = ?", (source_id,))
                conn.execute("DELETE FROM entities WHERE id = ?", (source_id,))

            absorbed_descriptions = [entities[eid]["description"] for eid in absorbed_ids if entities[eid]["description"]]
            if absorbed_descriptions:
                survivor_desc = entities[survivor_id]["description"] or ""
                combined = "\n".join([survivor_desc] + absorbed_descriptions) if survivor_desc else "\n".join(absorbed_descriptions)
                conn.execute("UPDATE entities SET description = ? WHERE id = ?", (combined, survivor_id))

            conn.execute("UPDATE entities SET relevance = NULL, stage = 'merged' WHERE id = ?", (survivor_id,))
            conn.execute("DELETE FROM entity_measures WHERE entity_id = ?", (survivor_id,))
            _touch(conn, "entities", survivor_id)

        absorbed_names = [f"{entities[eid]['name']} ({eid})" for eid in absorbed_ids]
        return f"Merged {', '.join(absorbed_names)} into {entities[survivor_id]['name']} ({survivor_id})"
    finally:
        conn.close()
