"""Criteria definitions, note linking, and assessment operations."""

from __future__ import annotations

import logging

from . import _db as _core

logger = logging.getLogger(__name__)

__all__ = [
    "register_criteria",
    "add_criterion",
    "remove_criterion",
    "get_criteria",
    "link_criterion_note",
    "unlink_criterion_note",
    "clear_criterion_links",
    "get_assessment",
    "compute_relevance",
]


@_core.retry_write
def register_criteria(db_path: str, criteria: list[dict]) -> str:
    """Replace ALL criteria definitions. Cascades: removes old criteria and their links.

    Each dict: {type: "hardline"|"relevancy", name: str, gate: str}
    """
    conn = _core.get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM criteria")
            for entry in criteria:
                cid = _core._next_id(conn, "criteria", "c")
                conn.execute(
                    "INSERT INTO criteria (id, type, name, gate) VALUES (?, ?, ?, ?)",
                    (cid, entry["type"], entry["name"], entry["gate"]),
                )
                _core._touch(conn, "criteria", cid)
        return f"Registered {len(criteria)} criteria (replaced all previous)"
    finally:
        conn.close()


@_core.retry_write
def add_criterion(db_path: str, type: str, name: str, gate: str) -> str:
    """Add a single criterion definition."""
    conn = _core.get_connection(db_path)
    try:
        with conn:
            cid = _core._next_id(conn, "criteria", "c")
            conn.execute(
                "INSERT INTO criteria (id, type, name, gate) VALUES (?, ?, ?, ?)",
                (cid, type, name, gate),
            )
            _core._touch(conn, "criteria", cid)
        return f"Added criterion {cid}: {name}"
    finally:
        conn.close()


@_core.retry_write
def remove_criterion(db_path: str, criterion_id: str) -> str:
    """Remove criterion and cascade-delete all its note links."""
    conn = _core.get_connection(db_path)
    try:
        row = conn.execute("SELECT id, name FROM criteria WHERE id = ?", (criterion_id,)).fetchone()
        if not row:
            raise ValueError(f"Criterion not found: {criterion_id}")
        with conn:
            conn.execute("DELETE FROM criteria WHERE id = ?", (criterion_id,))
        return f"Removed criterion {criterion_id}: {row['name']}"
    finally:
        conn.close()


def get_criteria(db_path: str) -> str:
    """List all criteria definitions with type, name, and gate."""
    conn = _core.get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT id, type, name, gate FROM criteria ORDER BY type, CAST(SUBSTR(id, 2) AS INTEGER)",
        ).fetchall()
        if not rows:
            return "No criteria defined."

        lines = [f"Criteria ({len(rows)}):"]
        for r in rows:
            lines.append(f"  [{r['type'][0].upper()}] {r['id']}. {r['name']} — {r['gate']}")
        return "\n".join(lines)
    finally:
        conn.close()


@_core.retry_write
def link_criterion_note(db_path: str, criterion_id: str, note_id: str, quality: str) -> str:
    """Link a criterion to a note with quality (pass/fail). Replaces existing link."""
    conn = _core.get_connection(db_path)
    try:
        if not conn.execute("SELECT id FROM criteria WHERE id = ?", (criterion_id,)).fetchone():
            raise ValueError(f"Criterion not found: {criterion_id}")
        if not conn.execute("SELECT id FROM entity_notes WHERE id = ?", (note_id,)).fetchone():
            raise ValueError(f"Note not found: {note_id}")
        with conn:
            conn.execute(
                "INSERT OR REPLACE INTO criteria_notes (criterion_id, note_id, quality) VALUES (?, ?, ?)",
                (criterion_id, note_id, quality),
            )
        return f"Linked {criterion_id} to {note_id} with quality '{quality}'"
    finally:
        conn.close()


@_core.retry_write
def unlink_criterion_note(db_path: str, criterion_id: str, note_id: str) -> str:
    """Remove a specific criterion-note link."""
    conn = _core.get_connection(db_path)
    try:
        with conn:
            cursor = conn.execute(
                "DELETE FROM criteria_notes WHERE criterion_id = ? AND note_id = ?",
                (criterion_id, note_id),
            )
        if cursor.rowcount == 0:
            return f"No link found between {criterion_id} and {note_id}"
        return f"Unlinked {criterion_id} from {note_id}"
    finally:
        conn.close()


@_core.retry_write
def clear_criterion_links(db_path: str, criterion_id: str) -> str:
    """Remove all note links for a criterion."""
    conn = _core.get_connection(db_path)
    try:
        if not conn.execute("SELECT id FROM criteria WHERE id = ?", (criterion_id,)).fetchone():
            raise ValueError(f"Criterion not found: {criterion_id}")
        with conn:
            cursor = conn.execute(
                "DELETE FROM criteria_notes WHERE criterion_id = ?", (criterion_id,),
            )
        return f"Cleared {cursor.rowcount} links from criterion {criterion_id}"
    finally:
        conn.close()


def get_assessment(db_path: str, entity_id: str) -> str:
    """Computed assessment: per-criterion quality, hardline result, relevancy count.

    Resolution: any 'pass' link for criterion-entity → passed (supersedes fail).
    Only 'fail' links → failed. No links → not assessed.
    """
    conn = _core.get_connection(db_path)
    try:
        entity = conn.execute("SELECT id, name, relevance FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")

        criteria = conn.execute(
            "SELECT id, type, name, gate FROM criteria ORDER BY type, CAST(SUBSTR(id, 2) AS INTEGER)",
        ).fetchall()
        if not criteria:
            return f"No criteria defined. Entity {entity_id} ({entity['name']}) has no assessment."

        # Get all links for this entity's notes
        links = conn.execute(
            """SELECT cn.criterion_id, cn.note_id, cn.quality, en.note
            FROM criteria_notes cn
            JOIN entity_notes en ON cn.note_id = en.id
            WHERE en.entity_id = ?""",
            (entity_id,),
        ).fetchall()

        # Group by criterion
        criterion_links: dict[str, list[dict]] = {}
        for link in links:
            cid = link["criterion_id"]
            if cid not in criterion_links:
                criterion_links[cid] = []
            criterion_links[cid].append({"note_id": link["note_id"], "quality": link["quality"], "note": link["note"]})

        # Resolve each criterion
        hardline_failures = []
        relevancy_passed = 0
        relevancy_total = 0

        lines = [f"Assessment: {entity['name']} (id: {entity_id})", ""]

        for c in criteria:
            clinks = criterion_links.get(c["id"], [])
            if not clinks:
                status = "not assessed"
            elif any(l["quality"] == "pass" for l in clinks):
                status = "PASS"
                if c["type"] == "relevancy":
                    relevancy_passed += 1
            else:
                status = "FAIL"
                if c["type"] == "hardline":
                    hardline_failures.append(c["name"])

            if c["type"] == "relevancy":
                relevancy_total += 1

            icon = {"PASS": "+", "FAIL": "x", "not assessed": "?"}[status]
            lines.append(f"  [{icon}] {c['id']}. [{c['type'][0].upper()}] {c['name']}")
            lines.append(f"      Gate: {c['gate']}")
            if clinks:
                for l in clinks:
                    lines.append(f"      [{l['quality']}] {l['note_id']}: {l['note'][:80]}")
            else:
                lines.append("      No linked notes")

        lines.append("")
        lines.append(f"Hardline: {'FAIL — ' + ', '.join(hardline_failures) if hardline_failures else 'PASS'}")
        lines.append(f"Relevancy: {relevancy_passed}/{relevancy_total}")
        lines.append(f"Cached relevance: {entity['relevance']}")

        return "\n".join(lines)
    finally:
        conn.close()


@_core.retry_write
def compute_relevance(db_path: str, entity_id: str) -> str:
    """Recompute cached relevance from criterion-note links. Updates entities.relevance."""
    conn = _core.get_connection(db_path)
    try:
        entity = conn.execute("SELECT id, name, relevance FROM entities WHERE id = ?", (entity_id,)).fetchone()
        if not entity:
            raise ValueError(f"Entity not found: {entity_id}")

        # Count distinct relevancy criteria with at least one 'pass' link for this entity
        row = conn.execute(
            """SELECT COUNT(DISTINCT cn.criterion_id) as passed
            FROM criteria_notes cn
            JOIN entity_notes en ON cn.note_id = en.id
            JOIN criteria c ON cn.criterion_id = c.id
            WHERE en.entity_id = ? AND c.type = 'relevancy' AND cn.quality = 'pass'""",
            (entity_id,),
        ).fetchone()
        new_relevance = row["passed"]
        old_relevance = entity["relevance"]

        with conn:
            conn.execute("UPDATE entities SET relevance = ? WHERE id = ?", (new_relevance, entity_id))
            _core._touch(conn, "entities", entity_id)

        if new_relevance != old_relevance:
            return f"Relevance updated: {entity['name']} ({entity_id}) {old_relevance} → {new_relevance}"
        return f"Relevance unchanged: {entity['name']} ({entity_id}) = {new_relevance}"
    finally:
        conn.close()
