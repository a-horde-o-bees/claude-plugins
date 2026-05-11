"""Read-only analysis queries.

Data-retrieval half of the analysis surface — returns structured data
(dicts, lists of tuples) describing dependency trees, need trees,
addressing graphs, coverage status, and gaps. The CLI in __main__.py
renders these structures for the user; the facade returns them intact
so downstream consumers (future MCP tools, tests) can operate on the
data without parsing terminal output.
"""

import subprocess
import sqlite3
from fnmatch import fnmatch
from pathlib import Path


def coverage(conn: sqlite3.Connection, need_id: str) -> tuple[str, list[str]]:
    """Return (status, direct_addressers) for a need.

    Statuses:
    - 'covered'   — has direct addressers OR a descendant is addressed
    - 'gap'       — non-root leaf with no addressers
    - 'unrefined' — root with no children
    - 'abstract'  — interior or root with children but no addressed descendants yet
    """
    direct = [
        r[0]
        for r in conn.execute(
            "SELECT component_id FROM addresses WHERE need_id = ? "
            "ORDER BY CAST(SUBSTR(component_id, 2) AS INTEGER)",
            (need_id,),
        ).fetchall()
    ]

    if direct:
        return "covered", direct

    has_children = conn.execute(
        "SELECT 1 FROM needs WHERE parent_id = ?", (need_id,)
    ).fetchone() is not None

    if has_children:
        descendant_addressed = conn.execute(
            """
            WITH RECURSIVE descendants(id) AS (
                SELECT id FROM needs WHERE parent_id = ?
                UNION
                SELECT n.id FROM needs n JOIN descendants d ON n.parent_id = d.id
            )
            SELECT 1 FROM descendants d
            WHERE EXISTS (SELECT 1 FROM addresses WHERE need_id = d.id)
            LIMIT 1
            """,
            (need_id,),
        ).fetchone()
        if descendant_addressed:
            return "covered", []
        return "abstract", []

    is_root = conn.execute(
        "SELECT parent_id FROM needs WHERE id = ?", (need_id,)
    ).fetchone()[0] is None
    if is_root:
        return "unrefined", []
    return "gap", []


def component_row(conn: sqlite3.Connection, comp_id: str) -> tuple[str, int]:
    """Return (description, validated) for a component or raise LookupError."""
    row = conn.execute(
        "SELECT description, validated FROM components WHERE id = ?",
        (comp_id,),
    ).fetchone()
    if not row:
        raise LookupError(f"component '{comp_id}' not found")
    return row


def need_row(conn: sqlite3.Connection, need_id: str) -> tuple[str, int, str | None]:
    """Return (description, validated, parent_id) for a need or raise LookupError."""
    row = conn.execute(
        "SELECT description, validated, parent_id FROM needs WHERE id = ?",
        (need_id,),
    ).fetchone()
    if not row:
        raise LookupError(f"need '{need_id}' not found")
    return row


def dependency_roots(conn: sqlite3.Connection) -> list[tuple[str, str, int]]:
    """Components that don't depend on anything — roots of the dependency DAG."""
    return conn.execute(
        """
        SELECT c.id, c.description, c.validated FROM components c
        WHERE NOT EXISTS (
            SELECT 1 FROM depends_on d WHERE d.component_id = c.id
        )
        ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """
    ).fetchall()


def dependents_of(conn: sqlite3.Connection, comp_id: str) -> list[tuple[str, str, int]]:
    """Components that depend on comp_id."""
    return conn.execute(
        """
        SELECT c.id, c.description, c.validated FROM depends_on d
        JOIN components c ON c.id = d.component_id
        WHERE d.dependency_id = ?
        ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """,
        (comp_id,),
    ).fetchall()


def need_roots(conn: sqlite3.Connection) -> list[tuple[str, str, int]]:
    """Root needs — parent_id NULL."""
    return conn.execute(
        """
        SELECT id, description, validated FROM needs
        WHERE parent_id IS NULL
        ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)
        """
    ).fetchall()


def need_children(conn: sqlite3.Connection, parent_id: str) -> list[tuple[str, str, int]]:
    return conn.execute(
        """
        SELECT id, description, validated FROM needs
        WHERE parent_id = ?
        ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)
        """,
        (parent_id,),
    ).fetchall()


def direct_addressers(conn: sqlite3.Connection, need_id: str) -> list[tuple[str, str, int, str]]:
    """Components that directly address a need, with their rationales."""
    return conn.execute(
        """
        SELECT c.id, c.description, c.validated, a.rationale FROM addresses a
        JOIN components c ON c.id = a.component_id
        WHERE a.need_id = ?
        ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """,
        (need_id,),
    ).fetchall()


def addressed_needs(conn: sqlite3.Connection, comp_id: str) -> list[tuple]:
    """Needs a component addresses, with rationale and parent info."""
    return conn.execute(
        """
        SELECT n.id, n.description, n.validated, a.rationale, n.parent_id
        FROM addresses a JOIN needs n ON n.id = a.need_id
        WHERE a.component_id = ?
        ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
        """,
        (comp_id,),
    ).fetchall()


def leaf_gaps(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    """Refined leaf needs with no direct addressers."""
    return conn.execute(
        """
        SELECT n.id, n.description FROM needs n
        WHERE n.parent_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM needs c WHERE c.parent_id = n.id)
          AND NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
        ORDER BY CAST(SUBSTR(n.id, 2) AS INTEGER)
        """
    ).fetchall()


def orphans(conn: sqlite3.Connection) -> list[tuple[str, str, int]]:
    """Components that don't address anything."""
    return conn.execute(
        """
        SELECT c.id, c.description, c.validated FROM components c
        WHERE NOT EXISTS (SELECT 1 FROM addresses a WHERE a.component_id = c.id)
        ORDER BY CAST(SUBSTR(c.id, 2) AS INTEGER)
        """
    ).fetchall()


def all_needs(conn: sqlite3.Connection) -> list[tuple[str]]:
    return conn.execute(
        "SELECT id FROM needs ORDER BY CAST(SUBSTR(id, 2) AS INTEGER)"
    ).fetchall()


def component_paths(conn: sqlite3.Connection, comp_id: str) -> list[str]:
    return [
        p for (p,) in conn.execute(
            "SELECT path FROM component_paths WHERE component_id = ? ORDER BY path",
            (comp_id,),
        ).fetchall()
    ]


def summary_counts(conn: sqlite3.Connection) -> dict:
    """Counts and gap status for summary view."""
    q = conn.execute
    comp_count = q("SELECT COUNT(*) FROM components").fetchone()[0]
    need_count = q("SELECT COUNT(*) FROM needs").fetchone()[0]
    root_count = q(
        "SELECT COUNT(*) FROM needs WHERE parent_id IS NULL"
    ).fetchone()[0]
    leaf_count = q(
        """
        SELECT COUNT(*) FROM needs n
        WHERE NOT EXISTS (SELECT 1 FROM needs c WHERE c.parent_id = n.id)
        """
    ).fetchone()[0]
    dep_count = q("SELECT COUNT(*) FROM depends_on").fetchone()[0]
    addr_count = q("SELECT COUNT(*) FROM addresses").fetchone()[0]
    unrefined = q(
        """
        SELECT COUNT(*) FROM needs n
        WHERE n.parent_id IS NULL
          AND NOT EXISTS (SELECT 1 FROM needs c WHERE c.parent_id = n.id)
        """
    ).fetchone()[0]
    gaps = q(
        """
        SELECT COUNT(*) FROM needs n
        WHERE n.parent_id IS NOT NULL
          AND NOT EXISTS (SELECT 1 FROM needs c WHERE c.parent_id = n.id)
          AND NOT EXISTS (SELECT 1 FROM addresses a WHERE a.need_id = n.id)
        """
    ).fetchone()[0]
    validated_comps = q(
        "SELECT COUNT(*) FROM components WHERE validated = 1"
    ).fetchone()[0]
    validated_needs = q(
        "SELECT COUNT(*) FROM needs WHERE validated = 1"
    ).fetchone()[0]
    return {
        "components": comp_count,
        "validated_components": validated_comps,
        "needs": need_count,
        "roots": root_count,
        "leaves": leaf_count,
        "validated_needs": validated_needs,
        "dependencies": dep_count,
        "addresses": addr_count,
        "unrefined": unrefined,
        "gaps": gaps,
    }


def dependency_ancestors(
    conn: sqlite3.Connection, comp_id: str,
) -> list[tuple[str, str, int]]:
    """All components reachable via depends_on from comp_id. Depth-limited to 50."""
    return conn.execute(
        """
        WITH RECURSIVE ancestors(id, depth) AS (
            SELECT dependency_id, 1
            FROM depends_on WHERE component_id = ?
            UNION
            SELECT d.dependency_id, a.depth + 1
            FROM ancestors a
            JOIN depends_on d ON d.component_id = a.id
            WHERE a.depth < 50
        )
        SELECT DISTINCT c.id, c.description, c.validated
        FROM ancestors a
        JOIN components c ON c.id = a.id
        """,
        (comp_id,),
    ).fetchall()


def all_component_ids(conn: sqlite3.Connection) -> list[str]:
    return [
        cid for (cid,) in conn.execute(
            "SELECT id FROM components ORDER BY id"
        ).fetchall()
    ]


def all_component_paths(conn: sqlite3.Connection) -> list[str]:
    return [
        p for (p,) in conn.execute("SELECT path FROM component_paths").fetchall()
    ]


def _is_test_file(path: str) -> bool:
    """Test implementations are derivative, not independent components."""
    parts = path.split("/")
    if any(p == "tests" for p in parts):
        return True
    name = parts[-1] if parts else ""
    return name.startswith("test_") or name == "conftest.py"


def uncovered_files(conn: sqlite3.Connection) -> list[str]:
    """Git-tracked source files not attached to any component.

    Excludes tests, conftest.py, and files whose path matches a recorded
    component path (exact path or glob pattern, with optional #anchor).
    """
    root_result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False,
    )
    if root_result.returncode != 0:
        raise RuntimeError(f"git rev-parse failed: {root_result.stderr.strip()}")
    project_root = Path(root_result.stdout.strip()).resolve()

    ls = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, cwd=str(project_root), check=False,
    )
    if ls.returncode != 0:
        raise RuntimeError(f"git ls-files failed: {ls.stderr.strip()}")

    source_files = {
        line for line in ls.stdout.splitlines()
        if line and not _is_test_file(line)
    }

    exact_paths: set[str] = set()
    glob_patterns: list[str] = []
    for p in all_component_paths(conn):
        base = p.split("#")[0].rstrip("/")
        if "*" in base or "?" in base:
            glob_patterns.append(base)
        else:
            exact_paths.add(base)

    def _covered(f: str) -> bool:
        if f in exact_paths:
            return True
        return any(fnmatch(f, pat) for pat in glob_patterns)

    return sorted(f for f in source_files if not _covered(f))
