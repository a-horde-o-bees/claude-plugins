"""Coverage computation and domain/goal management.

Domains and goals form a relationship model above criteria:
goals → goal_domains → domains → domain_criteria → criteria → criteria_notes → entity_notes → entities

Coverage queries traverse this chain to compute per-domain and per-goal
entity counts. Many-to-many relationships require DISTINCT counts.
"""

from __future__ import annotations

from . import _db as _core

get_connection = _core.get_connection
retry_write = _core.retry_write


# --- Domain CRUD ---


@retry_write
def register_domains(db_path: str, domains: list[dict]) -> str:
    """Replace ALL domain definitions. Cascade deletes old junction links."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM domain_criteria")
            conn.execute("DELETE FROM goal_domains")
            conn.execute("DELETE FROM domains")
            for d in domains:
                domain_id = _core._next_id(conn, "domains", "d")
                conn.execute(
                    "INSERT INTO domains (id, name, description) VALUES (?, ?, ?)",
                    (domain_id, d["name"], d.get("description", "")),
                )
                _core._touch(conn, "domains", domain_id)
        return f"Registered {len(domains)} domains (replaced all previous)"
    finally:
        conn.close()


@retry_write
def add_domain(db_path: str, name: str, description: str = "") -> str:
    """Add single domain definition."""
    conn = get_connection(db_path)
    try:
        with conn:
            domain_id = _core._next_id(conn, "domains", "d")
            conn.execute(
                "INSERT INTO domains (id, name, description) VALUES (?, ?, ?)",
                (domain_id, name, description),
            )
            _core._touch(conn, "domains", domain_id)
        return f"Added domain: {name} (id: {domain_id})"
    finally:
        conn.close()


@retry_write
def remove_domain(db_path: str, domain_id: str) -> str:
    """Remove domain and cascade-delete junction links."""
    conn = get_connection(db_path)
    try:
        with conn:
            row = conn.execute("SELECT name FROM domains WHERE id = ?", (domain_id,)).fetchone()
            if not row:
                raise ValueError(f"Domain not found: {domain_id}")
            conn.execute("DELETE FROM domains WHERE id = ?", (domain_id,))
        return f"Removed domain: {row['name']} ({domain_id})"
    finally:
        conn.close()


def get_domains(db_path: str) -> str:
    """List all domains with linked criteria counts."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT d.id, d.name, d.description, "
            "COUNT(dc.criterion_id) as criteria_count "
            "FROM domains d "
            "LEFT JOIN domain_criteria dc ON dc.domain_id = d.id "
            "GROUP BY d.id ORDER BY d.id",
        ).fetchall()
        if not rows:
            return "No domains defined."
        lines = [f"Domains ({len(rows)}):"]
        for r in rows:
            lines.append(f"  {r['id']}. {r['name']} ({r['criteria_count']} criteria) — {r['description']}")
        return "\n".join(lines)
    finally:
        conn.close()


# --- Goal CRUD ---


@retry_write
def register_goals(db_path: str, goals: list[dict]) -> str:
    """Replace ALL goal definitions. Cascade deletes old junction links."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM goal_domains")
            conn.execute("DELETE FROM goals")
            for g in goals:
                goal_id = _core._next_id(conn, "goals", "g")
                conn.execute(
                    "INSERT INTO goals (id, name, description) VALUES (?, ?, ?)",
                    (goal_id, g["name"], g.get("description", "")),
                )
                _core._touch(conn, "goals", goal_id)
        return f"Registered {len(goals)} goals (replaced all previous)"
    finally:
        conn.close()


@retry_write
def add_goal(db_path: str, name: str, description: str = "") -> str:
    """Add single goal definition."""
    conn = get_connection(db_path)
    try:
        with conn:
            goal_id = _core._next_id(conn, "goals", "g")
            conn.execute(
                "INSERT INTO goals (id, name, description) VALUES (?, ?, ?)",
                (goal_id, name, description),
            )
            _core._touch(conn, "goals", goal_id)
        return f"Added goal: {name} (id: {goal_id})"
    finally:
        conn.close()


@retry_write
def remove_goal(db_path: str, goal_id: str) -> str:
    """Remove goal and cascade-delete junction links."""
    conn = get_connection(db_path)
    try:
        with conn:
            row = conn.execute("SELECT name FROM goals WHERE id = ?", (goal_id,)).fetchone()
            if not row:
                raise ValueError(f"Goal not found: {goal_id}")
            conn.execute("DELETE FROM goals WHERE id = ?", (goal_id,))
        return f"Removed goal: {row['name']} ({goal_id})"
    finally:
        conn.close()


def get_goals(db_path: str) -> str:
    """List all goals with linked domain counts."""
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT g.id, g.name, g.description, "
            "COUNT(gd.domain_id) as domain_count "
            "FROM goals g "
            "LEFT JOIN goal_domains gd ON gd.goal_id = g.id "
            "GROUP BY g.id ORDER BY g.id",
        ).fetchall()
        if not rows:
            return "No goals defined."
        lines = [f"Goals ({len(rows)}):"]
        for r in rows:
            lines.append(f"  {r['id']}. {r['name']} ({r['domain_count']} domains) — {r['description']}")
        return "\n".join(lines)
    finally:
        conn.close()


# --- Junction management ---


@retry_write
def link_goal_domain(db_path: str, goal_id: str, domain_id: str) -> str:
    """Link goal to domain."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO goal_domains (goal_id, domain_id) VALUES (?, ?)",
                (goal_id, domain_id),
            )
        return f"Linked goal {goal_id} to domain {domain_id}"
    finally:
        conn.close()


@retry_write
def unlink_goal_domain(db_path: str, goal_id: str, domain_id: str) -> str:
    """Unlink goal from domain."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "DELETE FROM goal_domains WHERE goal_id = ? AND domain_id = ?",
                (goal_id, domain_id),
            )
        return f"Unlinked goal {goal_id} from domain {domain_id}"
    finally:
        conn.close()


@retry_write
def link_domain_criterion(db_path: str, domain_id: str, criterion_id: str) -> str:
    """Link domain to criterion."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "INSERT OR IGNORE INTO domain_criteria (domain_id, criterion_id) VALUES (?, ?)",
                (domain_id, criterion_id),
            )
        return f"Linked domain {domain_id} to criterion {criterion_id}"
    finally:
        conn.close()


@retry_write
def unlink_domain_criterion(db_path: str, domain_id: str, criterion_id: str) -> str:
    """Unlink domain from criterion."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute(
                "DELETE FROM domain_criteria WHERE domain_id = ? AND criterion_id = ?",
                (domain_id, criterion_id),
            )
        return f"Unlinked domain {domain_id} from criterion {criterion_id}"
    finally:
        conn.close()


# --- Coverage computation ---


def get_coverage(db_path: str) -> str:
    """Compute coverage metrics per domain. Deterministic — all from database state.

    Returns per-domain: distinct researched entity count, criteria count,
    average notes per entity. Plus entity pool trajectory and diminishing
    returns signal.
    """
    conn = get_connection(db_path)
    try:
        # Per-domain coverage via the full chain
        domain_rows = conn.execute(
            "SELECT d.id, d.name, "
            "COUNT(DISTINCT e.id) as entity_count, "
            "COUNT(DISTINCT dc.criterion_id) as criteria_count "
            "FROM domains d "
            "LEFT JOIN domain_criteria dc ON dc.domain_id = d.id "
            "LEFT JOIN criteria_notes cn ON cn.criterion_id = dc.criterion_id AND cn.quality = 'pass' "
            "LEFT JOIN entity_notes en ON en.id = cn.note_id "
            "LEFT JOIN entities e ON e.id = en.entity_id AND e.stage = 'researched' "
            "GROUP BY d.id ORDER BY d.id",
        ).fetchall()

        # Per-domain average notes for researched entities
        domain_notes = {}
        for dr in domain_rows:
            if dr["entity_count"] > 0:
                avg_row = conn.execute(
                    "SELECT AVG(note_count) as avg_notes FROM ("
                    "  SELECT COUNT(DISTINCT en2.id) as note_count "
                    "  FROM domains d2 "
                    "  JOIN domain_criteria dc2 ON dc2.domain_id = d2.id "
                    "  JOIN criteria_notes cn2 ON cn2.criterion_id = dc2.criterion_id AND cn2.quality = 'pass' "
                    "  JOIN entity_notes en2 ON en2.id = cn2.note_id "
                    "  JOIN entities e2 ON e2.id = en2.entity_id AND e2.stage = 'researched' "
                    "  WHERE d2.id = ? "
                    "  GROUP BY e2.id"
                    ")",
                    (dr["id"],),
                ).fetchone()
                domain_notes[dr["id"]] = round(avg_row["avg_notes"], 1) if avg_row and avg_row["avg_notes"] else 0
            else:
                domain_notes[dr["id"]] = 0

        # Entity pool trajectory
        pool = conn.execute(
            "SELECT "
            "  SUM(CASE WHEN stage = 'new' THEN 1 ELSE 0 END) as unresearched, "
            "  SUM(CASE WHEN stage = 'researched' THEN 1 ELSE 0 END) as researched, "
            "  SUM(CASE WHEN stage = 'rejected' THEN 1 ELSE 0 END) as rejected "
            "FROM entities",
        ).fetchone()

        # Average relevance of unresearched entities
        avg_rel = conn.execute(
            "SELECT AVG(relevance) as avg_rel FROM entities WHERE stage = 'new' AND relevance >= 0",
        ).fetchone()

        # Build output
        lines = ["Coverage by domain:"]
        for dr in domain_rows:
            avg_n = domain_notes.get(dr["id"], 0)
            lines.append(
                f"  {dr['id']}. {dr['name']}: "
                f"{dr['entity_count']} researched entities, "
                f"{dr['criteria_count']} criteria, "
                f"{avg_n} avg notes/entity"
            )

        lines.append("")
        lines.append("Entity pool:")
        lines.append(f"  Researched: {pool['researched'] or 0}")
        lines.append(f"  Unresearched: {pool['unresearched'] or 0}")
        lines.append(f"  Rejected: {pool['rejected'] or 0}")
        avg_relevance = round(avg_rel["avg_rel"], 1) if avg_rel and avg_rel["avg_rel"] is not None else 0
        lines.append(f"  Unresearched avg relevance: {avg_relevance}")

        return "\n".join(lines)
    finally:
        conn.close()
