"""Entity query tools — read-only domain queries and aggregations.

Covers entity detail, filtered listing, research queue, unclassified
entities, duplicate detection, dashboard stats, and measure summary.
"""

from __future__ import annotations

from . import _helpers
from ._helpers import _check_db, _ok, _err

from skills.research import _db as core
from skills.research._entities import (
    get_entity as _get_entity,
    list_entities as _list_entities,
    get_stats as _get_stats,
)
from skills.research._measures import get_measures as _get_measures
from skills.research._merge import find_duplicates as _find_duplicates


def get_entity(entity_id: str) -> str:
    """Full entity detail: modes, notes, URLs, provenance, measures, source data.

    Args:
        entity_id: Entity ID (e.g., e1)
    """
    if err := _check_db(): return err
    try:
        return _ok(_get_entity(_helpers.DB_PATH, entity_id))
    except ValueError as e:
        return _err(e)


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

    conn = core.get_connection(_helpers.DB_PATH)
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

    result = _list_entities(_helpers.DB_PATH, filters=filters if filters else None)

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


def get_research_queue() -> str:
    """Entities ready for Phase 2 deep research: example mode, stage new, ordered by relevance descending."""
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
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


def get_unclassified() -> str:
    """Entities with unclassified mode marker, ordered by relevance descending."""
    if err := _check_db(): return err
    conn = core.get_connection(_helpers.DB_PATH)
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


def find_duplicates() -> str:
    """Detect duplicate entities by URL overlap. Detection only — does not merge."""
    if err := _check_db(): return err
    return _ok(_find_duplicates(_helpers.DB_PATH))


def get_dashboard() -> str:
    """Aggregated stats for re-entry and status: entity counts by stage and mode, note/measure/URL totals, relevance distribution, provenance sources."""
    if err := _check_db(): return err
    return _ok(_get_stats(_helpers.DB_PATH))


def get_measure_summary() -> str:
    """Measure distribution across entities for Phase 3 analysis."""
    if err := _check_db(): return err
    return _ok(_get_measures(_helpers.DB_PATH))
