"""Entity registration, stage transitions, updates, queries, batch, and touch."""

from __future__ import annotations

import logging
import sqlite3

try:
    from . import _db as _core
except ImportError:
    import _db as _core  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)

__all__ = [
    "register_entity",
    "compute_normalize_url",
    "update_entity",
    "get_entity",
    "list_entities",
    "get_stats",
    "register_batch",
    "touch_entities",
]


@_core.retry_write
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
    conn = _core.get_connection(db_path)
    try:
        with conn:
            if url:
                existing = _core._find_entity_by_url(conn, url)
                if existing:
                    if source_url:
                        _core._add_provenance(conn, existing["id"], source_url)
                    return f"Already registered: {existing['name']} (id: {existing['id']})"

            entity_id = _core._next_id(conn, "entities", "e")
            conn.execute(
                "INSERT INTO entities (id, name, role, relevance, description) VALUES (?, ?, ?, ?, ?)",
                (entity_id, name, role or "example", relevance or 0, description or ""),
            )

            if url:
                _core._add_entity_url(conn, entity_id, url)
            if source_url:
                _core._add_provenance(conn, entity_id, source_url)

            _core._touch(conn, "entities", entity_id)
            return f"Registered: {name} (id: {entity_id})"
    finally:
        conn.close()


def compute_normalize_url(url: str) -> str:
    """Compute and return normalized form of a URL."""
    result = _core.normalize_url(url)
    return result if result else url


@_core.retry_write
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

    conn = _core.get_connection(db_path)
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
                    _core._enforce_stage(conn, entity_id, stage)
                if relevance is not None:
                    conn.execute("UPDATE entities SET relevance = ? WHERE id = ?", (relevance, entity_id))
                if description is not None:
                    conn.execute("UPDATE entities SET description = ? WHERE id = ?", (description, entity_id))
                if name is not None:
                    conn.execute("UPDATE entities SET name = ? WHERE id = ?", (name, entity_id))
                if role is not None:
                    conn.execute("UPDATE entities SET role = ? WHERE id = ?", (role, entity_id))
                _core._touch(conn, "entities", entity_id)
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


def get_entity(db_path: str, entity_id: str) -> str:
    """Entity detail: URLs, provenance, relevance, description, measures, source data, notes."""
    conn = _core.get_connection(db_path)
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
    conn = _core.get_connection(db_path)
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
    conn = _core.get_connection(db_path)
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


@_core.retry_write
def register_batch(db_path: str, entities: list[dict], source_url: str | None = None) -> str:
    """Register multiple entities with URL dedup, optional notes for new entities.

    Each entity dict may contain: name, url, source_url, description, relevance,
    role, notes. Notes only written for newly created entities.
    """
    conn = _core.get_connection(db_path)
    try:
        new_count = 0
        already_registered = []
        errors = []
        normalized_source = _core.normalize_url(source_url) if source_url else None
        with conn:
            for entry in entities:
                name = entry.get("name", "")
                url = entry.get("url")
                desc = entry.get("description", "")
                rel = entry.get("relevance", 0)
                role = entry.get("role", "example")
                notes = entry.get("notes", [])
                entry_source = entry.get("source_url")
                effective_source = _core.normalize_url(entry_source) if entry_source else normalized_source

                if not name:
                    errors.append("Skipped entry with no name")
                    continue

                existing = _core._find_entity_by_url(conn, url) if url else None

                if existing:
                    entity_id = existing["id"]
                    if effective_source:
                        conn.execute(
                            "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
                            (effective_source, entity_id),
                        )
                    normalized = _core.normalize_url(url)
                    already_registered.append(f"  {entity_id}. {normalized}")
                else:
                    entity_id = _core._next_id(conn, "entities", "e")
                    conn.execute(
                        "INSERT INTO entities (id, name, role, relevance, description) VALUES (?, ?, ?, ?, ?)",
                        (entity_id, name, role, rel, desc),
                    )
                    if url:
                        _core._add_entity_url(conn, entity_id, url)
                    if effective_source:
                        conn.execute(
                            "INSERT OR IGNORE INTO url_provenance (source_url, entity_id) VALUES (?, ?)",
                            (effective_source, entity_id),
                        )
                    for note in notes:
                        note_id = _core._next_id(conn, "entity_notes", "n")
                        conn.execute(
                            "INSERT OR IGNORE INTO entity_notes (id, entity_id, note) VALUES (?, ?, ?)",
                            (note_id, entity_id, note),
                        )
                        _core._touch(conn, "entity_notes", note_id)
                    _core._touch(conn, "entities", entity_id)
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


@_core.retry_write
def touch_entities(db_path: str, ids: list[str] | None = None, all_entities: bool = False) -> str:
    """Mark entities as reviewed — sets last_modified to now without changes."""
    conn = _core.get_connection(db_path)
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
                _core._touch(conn, "entities", entity_id)
                touched += 1
        return f"Touched {touched} entities"
    finally:
        conn.close()
