"""MCP server for blueprint research database.

Domain tools for entity research lifecycle. Each tool encodes one operation
on one property. Business logic (validation, normalization, dedup) lives in
tool implementations. No generic CRUD, no query building, no raw SQL exposure.

Purpose: deterministic operations for agent-facing instructions where
supporting data is relational.

Runs via stdio transport. Database path from DB_PATH env var.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Add the plugin root to sys.path so we can import the research package
_plugin_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_plugin_root))

from skills.research import _db as core  # noqa: E402
from skills.research._entities import (  # noqa: E402
    register_entity as _register_entity,
    register_batch as _register_batch,
    update_entity as _update_entity,
    get_entity as _get_entity,
    list_entities as _list_entities,
    get_stats as _get_stats,
)
from skills.research._notes import (  # noqa: E402
    upsert_notes as _add_notes,
    update_note as _update_note,
    remove_notes as _remove_notes,
    clear_notes as _clear_notes,
)
from skills.research._measures import (  # noqa: E402
    upsert_measures as _set_measures,
    get_measures as _get_measures,
    clear_entity_measures as _clear_entity_measures,
    clear_measures as _clear_all_measures,
)
from skills.research._merge import (  # noqa: E402
    find_duplicates as _find_duplicates,
    merge_entities as _merge_entities,
)

# --- Configuration ---

DB_PATH = os.environ.get("DB_PATH", "blueprint/data/research.db")

mcp = FastMCP("blueprint-research")

# --- Helpers ---

_NO_DB_MSG = json.dumps({
    "error": "Database not initialized.",
    "action": "Run /blueprint-init or /blueprint-research to create the database first.",
})


def _check_db() -> str | None:
    """Return error JSON if database doesn't exist, None if OK."""
    if not Path(DB_PATH).exists():
        return _NO_DB_MSG
    return None


def _ok(result) -> str:
    """Wrap result as JSON response."""
    if isinstance(result, str):
        return json.dumps({"result": result})
    return json.dumps(result, default=str)


def _handle_check_error(e: sqlite3.IntegrityError) -> str | None:
    """Extract CHECK constraint expression from IntegrityError.

    Returns user-friendly error message if CHECK constraint violation,
    None otherwise. Fully dynamic — works for any CHECK constraint on
    any table without per-field hardcoding.
    """
    msg = str(e)
    if "CHECK constraint failed:" in msg:
        expression = msg.split("CHECK constraint failed:", 1)[1].strip()
        return json.dumps({
            "error": f"Value rejected by database constraint: {expression}",
            "hint": "Check the allowed values and try again.",
        })
    return None


def _err(e: Exception) -> str:
    """Wrap exception as JSON error."""
    return json.dumps({"error": str(e)})


# ============================================================
# Registration
# ============================================================


@mcp.tool()
def register_entity(data: dict) -> str:
    """Register a new entity with URL dedup, mode assignment, and provenance.

    Args:
        data: Entity object with fields: name (required), url, modes (list),
              description, relevance, purpose, source_url
    """
    if err := _check_db(): return err
    try:
        modes = data.get("modes")
        if isinstance(modes, str):
            modes = [modes]
        result = _register_entity(
            DB_PATH,
            name=data.get("name", ""),
            url=data.get("url"),
            source_url=data.get("source_url"),
            relevance=data.get("relevance"),
            description=data.get("description"),
            purpose=data.get("purpose"),
            modes=modes,
        )
        return _ok(result)
    except (ValueError, sqlite3.IntegrityError) as e:
        if isinstance(e, sqlite3.IntegrityError):
            if check_err := _handle_check_error(e):
                return check_err
        return _err(e)


@mcp.tool()
def register_entities(entities: list[dict], source_url: str | None = None) -> str:
    """Register multiple entities in batch. Handles dedup per entity.

    Args:
        entities: Array of entity objects (same fields as register_entity)
        source_url: Default provenance URL applied to all entities (individual entries can override)
    """
    if err := _check_db(): return err
    try:
        result = _register_batch(DB_PATH, entities, source_url)
        return _ok(result)
    except (ValueError, sqlite3.IntegrityError) as e:
        if isinstance(e, sqlite3.IntegrityError):
            if check_err := _handle_check_error(e):
                return check_err
        return _err(e)


# ============================================================
# Entity scalar properties
# ============================================================


@mcp.tool()
def set_name(entity_id: str, name: str) -> str:
    """Set entity display name.

    Args:
        entity_id: Entity ID (e.g., e1)
        name: New name
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], name=name))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def clear_name(entity_id: str) -> str:
    """Reset entity name to empty.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], name=""))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def set_description(entity_id: str, description: str) -> str:
    """Set entity description — one-sentence identity statement.

    Args:
        entity_id: Entity ID (e.g., e1)
        description: One sentence: what entity is and primary approach
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], description=description))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def clear_description(entity_id: str) -> str:
    """Reset entity description to empty.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], description=""))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def set_purpose(entity_id: str, purpose: str) -> str:
    """Set entity purpose — why this entity matters to the research.

    Args:
        entity_id: Entity ID (e.g., e1)
        purpose: Why this entity is relevant to the research project
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], purpose=purpose))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def clear_purpose(entity_id: str) -> str:
    """Reset entity purpose to empty.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], purpose=""))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def set_relevance(entity_id: str, relevance: int) -> str:
    """Set entity relevance score.

    Args:
        entity_id: Entity ID (e.g., e1)
        relevance: Integer score (higher = more relevant, scale from assessment criteria)
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], relevance=relevance))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def clear_relevance(entity_id: str) -> str:
    """Reset entity relevance to 0 (unassessed).

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], relevance=0))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def set_stage(entity_id: str, stage: str) -> str:
    """Set entity stage with validated transitions.

    Valid stages: new, rejected, researched, merged.
    Moving to a lower stage clears higher-stage data.
    Merged entities can only transition to new.

    Args:
        entity_id: Entity ID (e.g., e1)
        stage: Target stage
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_entity(DB_PATH, ids=[entity_id], stage=stage))
    except (ValueError, sqlite3.IntegrityError) as e:
        if isinstance(e, sqlite3.IntegrityError):
            if check_err := _handle_check_error(e):
                return check_err
        return _err(e)


# ============================================================
# Modes (interaction modes — satellite table)
# ============================================================


@mcp.tool()
def set_modes(entity_id: str, modes: list[str]) -> str:
    """Replace all modes on entity.

    Valid modes: example, directory, context, unclassified.
    An entity may have multiple modes simultaneously.

    Args:
        entity_id: Entity ID (e.g., e1)
        modes: Complete list of modes (replaces all existing)
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
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


@mcp.tool()
def add_modes(entity_id: str, modes: list[str]) -> str:
    """Add modes to entity (preserves existing).

    Args:
        entity_id: Entity ID (e.g., e1)
        modes: Modes to add
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
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


@mcp.tool()
def remove_modes(entity_id: str, modes: list[str]) -> str:
    """Remove specific modes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
        modes: Mode values to remove
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
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


@mcp.tool()
def clear_modes(entity_id: str) -> str:
    """Remove all modes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    try:
        with conn:
            conn.execute("DELETE FROM entity_modes WHERE entity_id = ?", (entity_id,))
            core._touch(conn, "entities", entity_id)
        return _ok(f"Cleared all modes from {entity_id}")
    finally:
        conn.close()


# ============================================================
# Notes (knowledge accumulation)
# ============================================================


@mcp.tool()
def add_notes(entity_id: str, notes: list[str]) -> str:
    """Add notes to entity. Skips exact duplicates.

    Notes are atomic, self-explanatory facts. Each note should stand alone.

    Args:
        entity_id: Entity ID (e.g., e1)
        notes: List of note texts to add
    """
    if err := _check_db(): return err
    try:
        return _ok(_add_notes(DB_PATH, entity_id, notes))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def set_note(note_id: str, text: str) -> str:
    """Replace text of an existing note.

    Args:
        note_id: Note ID (e.g., n14)
        text: New note text
    """
    if err := _check_db(): return err
    try:
        return _ok(_update_note(DB_PATH, note_id, text))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def remove_notes(entity_id: str, note_ids: list[str]) -> str:
    """Remove specific notes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
        note_ids: Note IDs to remove (e.g., ["n3", "n7"])
    """
    if err := _check_db(): return err
    try:
        return _ok(_remove_notes(DB_PATH, entity_id, note_ids))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def clear_notes(entity_id: str) -> str:
    """Remove all notes from entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_clear_notes(DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)


# ============================================================
# Measures (analysis output)
# ============================================================


@mcp.tool()
def set_measures(entity_id: str, measures: list[dict]) -> str:
    """Set measures on entity. Each measure is a key-value pair.

    Args:
        entity_id: Entity ID (e.g., e1)
        measures: List of {measure: "name", value: "value"} objects
    """
    if err := _check_db(): return err
    try:
        formatted = [f"{m['measure']}={m['value']}" for m in measures]
        return _ok(_set_measures(DB_PATH, entity_id, formatted))
    except (ValueError, KeyError) as e:
        return _err(e)


@mcp.tool()
def clear_measures(entity_id: str) -> str:
    """Clear all measures from one entity.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_clear_entity_measures(DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def clear_all_measures() -> str:
    """Clear all measures across all entities. Used when assessment or effectiveness criteria change."""
    if err := _check_db(): return err
    return _ok(_clear_all_measures(DB_PATH))


# ============================================================
# URLs and Provenance
# ============================================================


@mcp.tool()
def add_url(entity_id: str, url: str) -> str:
    """Add normalized URL to entity. Deduplicates automatically.

    Args:
        entity_id: Entity ID (e.g., e1)
        url: URL to add (will be normalized)
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    try:
        with conn:
            core._add_entity_url(conn, entity_id, url)
            core._touch(conn, "entities", entity_id)
        return _ok(f"Added URL to {entity_id}")
    finally:
        conn.close()


@mcp.tool()
def add_provenance(entity_id: str, source_url: str) -> str:
    """Record that entity was discovered via source URL.

    Args:
        entity_id: Entity ID (e.g., e1)
        source_url: URL where entity was found
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    try:
        with conn:
            core._add_provenance(conn, entity_id, source_url)
        return _ok(f"Added provenance to {entity_id}")
    finally:
        conn.close()


# ============================================================
# Compound operations
# ============================================================


@mcp.tool()
def reject_entity(entity_id: str, reason: str) -> str:
    """Reject entity — sets stage to rejected, relevance to 0, adds reason as note.

    Args:
        entity_id: Entity ID (e.g., e1)
        reason: Rejection reason (added as note)
    """
    if err := _check_db(): return err
    try:
        _update_entity(DB_PATH, ids=[entity_id], stage="rejected", relevance=0)
        _add_notes(DB_PATH, entity_id, [f"Rejected: {reason}"])
        return _ok(f"Rejected {entity_id}: {reason}")
    except (ValueError, sqlite3.IntegrityError) as e:
        return _err(e)


@mcp.tool()
def merge_entities(entity_ids: list[str]) -> str:
    """Merge entities into lowest-ID survivor. Mechanical — preserves all data.

    Combines descriptions, moves notes/URLs/provenance/source data to survivor.
    Sets survivor stage to merged, clears relevance and measures.

    Args:
        entity_ids: Entity IDs to merge (e.g., ["e1", "e2"])
    """
    if err := _check_db(): return err
    try:
        return _ok(_merge_entities(DB_PATH, entity_ids))
    except ValueError as e:
        return _err(e)


# ============================================================
# Queries — domain reads
# ============================================================


@mcp.tool()
def get_entity(entity_id: str) -> str:
    """Full entity detail: modes, notes, URLs, provenance, measures, source data.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_get_entity(DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)


@mcp.tool()
def list_entities(mode: str | None = None, stage: str | None = None, min_relevance: int | None = None) -> str:
    """List entities filtered by mode, stage, and/or minimum relevance. Ordered by relevance descending.

    Args:
        mode: Filter to entities with this mode (e.g., "example", "directory", "context")
        stage: Filter to entities at this stage (e.g., "new", "researched")
        min_relevance: Filter to entities with relevance >= this value
    """
    if err := _check_db(): return err
    filters = []
    if stage:
        filters.append(f"stage={stage}")
    if min_relevance is not None:
        filters.append(f"relevance>={min_relevance}")

    conn = core.get_connection(DB_PATH)
    try:
        if mode:
            # Get entity IDs with this mode, then filter through list_entities
            mode_ids = {
                r["entity_id"] for r in
                conn.execute("SELECT entity_id FROM entity_modes WHERE mode = ?", (mode,)).fetchall()
            }
            if not mode_ids:
                return _ok("No entities found.")
        else:
            mode_ids = None
    finally:
        conn.close()

    result = _list_entities(DB_PATH, filters=filters if filters else None)

    if mode_ids is not None:
        # Filter result lines to only entities in mode set
        lines = result.split("\n")
        header = lines[0] if lines else ""
        filtered = [l for l in lines[1:] if any(f" {eid}." in l for eid in mode_ids)]
        if not filtered:
            return _ok("No entities found.")
        count = len(filtered)
        return _ok(f"Entities ({count}) [mode: {mode}]:\n" + "\n".join(filtered))

    return _ok(result)


@mcp.tool()
def get_research_queue() -> str:
    """Entities ready for Phase 2 deep research: example mode, stage new, ordered by relevance descending."""
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT e.id, e.name, e.relevance, e.description "
            "FROM entities e "
            "JOIN entity_modes m ON m.entity_id = e.id "
            "WHERE m.mode = 'example' AND e.stage = 'new' "
            "ORDER BY e.relevance DESC, e.name",
        ).fetchall()
        if not rows:
            return _ok("Research queue empty — no example entities at stage new.")
        lines = [f"Research queue ({len(rows)} entities):"]
        for r in rows:
            rel = r["relevance"] if r["relevance"] is not None else "?"
            desc = f" — {r['description']}" if r["description"] else ""
            lines.append(f"  {r['id']}. {r['name']} (relevance: {rel}){desc}")
        return _ok("\n".join(lines))
    finally:
        conn.close()


@mcp.tool()
def get_unclassified() -> str:
    """Entities with unclassified mode marker, ordered by relevance descending."""
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    try:
        rows = conn.execute(
            "SELECT e.id, e.name, e.relevance, e.description, e.stage "
            "FROM entities e "
            "JOIN entity_modes m ON m.entity_id = e.id "
            "WHERE m.mode = 'unclassified' "
            "ORDER BY e.relevance DESC, e.name",
        ).fetchall()
        if not rows:
            return _ok("No unclassified entities.")
        lines = [f"Unclassified entities ({len(rows)}):"]
        for r in rows:
            rel = r["relevance"] if r["relevance"] is not None else "?"
            lines.append(f"  {r['id']}. {r['name']} (relevance: {rel}, stage: {r['stage']})")
        return _ok("\n".join(lines))
    finally:
        conn.close()


@mcp.tool()
def find_duplicates() -> str:
    """Detect duplicate entities by URL overlap. Detection only — does not merge."""
    if err := _check_db(): return err
    return _ok(_find_duplicates(DB_PATH))


@mcp.tool()
def get_dashboard() -> str:
    """Aggregated stats for re-entry and status: entity counts by stage and mode, note/measure/URL totals, relevance distribution, provenance sources."""
    if err := _check_db(): return err
    return _ok(_get_stats(DB_PATH))


@mcp.tool()
def get_measure_summary() -> str:
    """Measure distribution across entities for Phase 3 analysis."""
    if err := _check_db(): return err
    return _ok(_get_measures(DB_PATH))


# ============================================================
# Infrastructure
# ============================================================


@mcp.tool()
def init_database() -> str:
    """Initialize research database. Creates schema if database doesn't exist. Idempotent — safe to call on existing database."""
    result = core.init_db(DB_PATH)
    return _ok(result)


@mcp.tool()
def describe_schema(table: str | None = None) -> str:
    """Discover database schema — tables, columns, types, and FK relationships.

    Args:
        table: Specific table to describe (optional; omit for all tables)
    """
    if err := _check_db(): return err
    conn = core.get_connection(DB_PATH)
    all_tables = {
        r["name"] for r in
        conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence'").fetchall()
    }
    try:
        if table:
            if table not in all_tables:
                return _err(ValueError(f"Unknown table: {table}. Valid: {', '.join(sorted(all_tables))}"))
            columns = conn.execute(f"PRAGMA table_info({table})").fetchall()
            fks = conn.execute(f"PRAGMA foreign_key_list({table})").fetchall()
            return json.dumps({
                "table": table,
                "columns": [{"name": c["name"], "type": c["type"], "notnull": bool(c["notnull"]), "pk": bool(c["pk"]), "default": c["dflt_value"]} for c in columns],
                "foreign_keys": [{"column": fk["from"], "references": f"{fk['table']}.{fk['to']}"} for fk in fks],
            })

        result = {}
        for t in sorted(all_tables):
            columns = conn.execute(f"PRAGMA table_info({t})").fetchall()
            result[t] = {
                "columns": [{"name": c["name"], "type": c["type"]} for c in columns],
            }
        return json.dumps(result)
    finally:
        conn.close()


# --- Entry point ---

if __name__ == "__main__":
    mcp.run()
