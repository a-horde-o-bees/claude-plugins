"""Governance operations.

Governance loading, matching, and analysis. Operates on the governance,
governance_includes, and governance_excludes tables in the navigator database.

Governance data self-refreshes: query functions check staleness via
git_hash comparison and reload from disk when stale. The governance
module manages its own freshness independently from the scanner.

All functions return structured data (dicts/lists). Formatting for
CLI display belongs in __main__.py.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from ._db import get_connection
from ._frontmatter import normalize_patterns, scan_governance_dirs


def _git_hash(file_path: str) -> str | None:
    """Compute git-compatible blob hash for a file."""
    try:
        data = Path(file_path).read_bytes()
    except (OSError, IsADirectoryError):
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _infer_project_dir(db_path: str) -> str | None:
    """Infer project directory from database path convention.

    Navigator db is at .claude/ocd/navigator/navigator.db relative to project root.
    Returns None if db_path doesn't match the convention (e.g. test databases).
    """
    db = Path(db_path).resolve()
    if len(db.parts) >= 5 and db.parts[-4:] == (".claude", "ocd", "navigator", "navigator.db"):
        return str(db.parents[3])
    return None


def _governance_is_stale(db_path: str, project_dir: str) -> bool:
    """Check if governance table needs updating from disk.

    Compares the set of governance file paths on disk against the database,
    then compares git hashes stored in the governance table against current
    file content. Returns True when governance data needs reloading.
    """
    rules_dir = Path(project_dir) / ".claude" / "rules"
    conv_dir = Path(project_dir) / ".claude" / "conventions"

    disk_paths: set[str] = set()
    for scan_dir in (rules_dir, conv_dir):
        if scan_dir.is_dir():
            for md_file in scan_dir.glob("*.md"):
                if md_file.is_file():
                    disk_paths.add(str(md_file.relative_to(project_dir)))

    conn = get_connection(db_path)
    try:
        db_rows = conn.execute(
            "SELECT entry_path, git_hash FROM governance"
        ).fetchall()
        db_paths = {row["entry_path"] for row in db_rows}

        if disk_paths != db_paths:
            return True

        for row in db_rows:
            stored_hash = row["git_hash"]
            if stored_hash is None:
                return True
            current_hash = _git_hash(
                str(Path(project_dir) / row["entry_path"])
            )
            if current_hash != stored_hash:
                return True

        return False
    finally:
        conn.close()


def _ensure_current(db_path: str) -> None:
    """Refresh governance from disk if stale. Called before every query.

    Skips when db_path doesn't match the conventional navigator path
    (e.g. test databases at arbitrary locations).
    """
    project_dir = _infer_project_dir(db_path)
    if project_dir is None:
        return
    governance_load(db_path, project_dir)


def governance_load(db_path: str, project_dir: str) -> dict:
    """Load governance entries from frontmatter in rules and conventions.

    Parses frontmatter, stores raw patterns in governance table, normalizes
    patterns into governance_includes and governance_excludes tables, and
    records git_hash for staleness detection. Skips when current.
    Idempotent — safe to rerun.
    """
    if not _governance_is_stale(db_path, project_dir):
        conn = get_connection(db_path)
        try:
            gov_count = conn.execute("SELECT COUNT(*) as c FROM governance").fetchone()["c"]
            return {"governance_entries": gov_count}
        finally:
            conn.close()

    entries = scan_governance_dirs(Path(project_dir))

    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM governance_includes")
        conn.execute("DELETE FROM governance_excludes")

        for entry_path, entry in entries.items():
            file_hash = _git_hash(str(Path(project_dir) / entry_path))
            conn.execute(
                "INSERT INTO entries (path, entry_type, git_hash) VALUES (?, 'file', ?) "
                "ON CONFLICT(path) DO UPDATE SET git_hash = excluded.git_hash",
                (entry_path, file_hash),
            )
            auto_loaded = 1 if "/rules/" in entry_path else 0
            conn.execute(
                "INSERT OR REPLACE INTO governance (entry_path, matches, excludes, auto_loaded, git_hash) "
                "VALUES (?, ?, ?, ?, ?)",
                (entry_path, entry["matches"], entry.get("excludes"), auto_loaded, file_hash),
            )

            for pattern in normalize_patterns(entry["matches"]):
                conn.execute(
                    "INSERT INTO governance_includes (entry_path, pattern) VALUES (?, ?)",
                    (entry_path, pattern),
                )

            if entry.get("excludes"):
                for pattern in normalize_patterns(entry["excludes"]):
                    conn.execute(
                        "INSERT INTO governance_excludes (entry_path, pattern) VALUES (?, ?)",
                        (entry_path, pattern),
                    )

        conn.commit()

        gov_count = conn.execute("SELECT COUNT(*) as c FROM governance").fetchone()["c"]
        return {"governance_entries": gov_count}
    finally:
        conn.close()


def governance_list(db_path: str) -> list[dict]:
    """List all governance entries with patterns and loading mode."""
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT g.entry_path, g.matches, g.excludes, g.auto_loaded "
            "FROM governance g ORDER BY g.entry_path"
        ).fetchall()

        result = []
        for row in rows:
            entry = {
                "path": row["entry_path"],
                "matches": row["matches"],
                "mode": "rule" if row["auto_loaded"] else "convention",
            }
            if row["excludes"]:
                entry["excludes"] = row["excludes"]
            result.append(entry)
        return result
    finally:
        conn.close()


def governance_match(db_path: str, file_paths: list[str], include_rules: bool = False) -> dict:
    """Match files against governance patterns.

    By default returns only conventions (on-demand) since rules are always
    loaded into agent context. Set include_rules=True for governance
    evaluation where rules themselves are the evaluation target.

    Uses path_match() custom SQL function for matching — same semantics
    as matches_pattern (basename, ** prefix, full-path modes).
    """
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        placeholders = ", ".join("(?)" for _ in file_paths)
        params: list[str] = list(file_paths)

        auto_filter = "" if include_rules else "AND g.auto_loaded = 0"

        query = f"""
            WITH files(path) AS (VALUES {placeholders})
            SELECT DISTINCT f.path AS file_path, gi.entry_path
            FROM files f
            JOIN governance_includes gi ON path_match(f.path, gi.pattern)
            JOIN governance g ON gi.entry_path = g.entry_path {auto_filter}
            LEFT JOIN governance_excludes ge
                ON gi.entry_path = ge.entry_path AND path_match(f.path, ge.pattern)
            WHERE ge.entry_path IS NULL
            ORDER BY f.path, gi.entry_path
        """

        rows = conn.execute(query, params).fetchall()

        result_matches: dict[str, list[str]] = {}
        for row in rows:
            result_matches.setdefault(row["file_path"], []).append(row["entry_path"])

        conventions = sorted({c for cs in result_matches.values() for c in cs})

        return {
            "matches": result_matches,
            "conventions": conventions,
        }
    finally:
        conn.close()


def governance_unclassified(db_path: str) -> dict:
    """Find file entries with no governance coverage, grouped by extension.

    Scans the filesystem first to ensure entries are current, then uses
    path_match() custom SQL function for single-query evaluation.
    """
    project_dir = _infer_project_dir(db_path)
    if project_dir is not None:
        from ._scanner import scan_path

        scan_path(db_path, project_dir)
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute("""
            SELECT e.path FROM entries e
            WHERE e.entry_type = 'file' AND e.exclude = 0
            AND e.path NOT IN (SELECT entry_path FROM governance)
            AND NOT EXISTS (
                SELECT 1 FROM governance_includes gi
                JOIN governance g ON gi.entry_path = g.entry_path AND g.auto_loaded = 0
                WHERE path_match(e.path, gi.pattern)
                AND gi.entry_path NOT IN (
                    SELECT ge.entry_path FROM governance_excludes ge
                    WHERE path_match(e.path, ge.pattern)
                )
            )
            ORDER BY e.path
        """).fetchall()

        unclassified = [row["path"] for row in rows]

        by_ext: dict[str, list[str]] = {}
        for path in unclassified:
            ext = Path(path).suffix or "(no extension)"
            by_ext.setdefault(ext, []).append(path)

        return {
            "total": len(unclassified),
            "by_extension": by_ext,
        }
    finally:
        conn.close()
