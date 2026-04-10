"""Governance operations.

Governance loading, matching, and analysis. Operates on conventions
(conventions, convention_includes, convention_excludes) and rules tables
in the navigator database — independent from navigator's entries table.

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


def _scan_disk_paths(project_dir: str) -> tuple[set[str], set[str]]:
    """Scan governance directories and return (rule_paths, convention_paths)."""
    rules_dir = Path(project_dir) / ".claude" / "rules"
    conv_dir = Path(project_dir) / ".claude" / "conventions"

    rule_paths: set[str] = set()
    conv_paths: set[str] = set()
    for scan_dir, target_set in ((rules_dir, rule_paths), (conv_dir, conv_paths)):
        if scan_dir.is_dir():
            for md_file in scan_dir.glob("*.md"):
                if md_file.is_file():
                    target_set.add(str(md_file.relative_to(project_dir)))

    return rule_paths, conv_paths


def _table_is_stale(
    conn, table: str, disk_paths: set[str], project_dir: str,
) -> bool:
    """Check if a governance table's entries match disk state."""
    db_rows = conn.execute(
        f"SELECT entry_path, git_hash FROM {table}"  # noqa: S608
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


def _governance_is_stale(db_path: str, project_dir: str) -> bool:
    """Check if rules or conventions tables need updating from disk.

    Compares the set of governance file paths on disk against the database,
    then compares git hashes against current file content. Returns True
    when either table needs reloading.
    """
    rule_paths, conv_paths = _scan_disk_paths(project_dir)

    conn = get_connection(db_path)
    try:
        return (
            _table_is_stale(conn, "rules", rule_paths, project_dir)
            or _table_is_stale(conn, "conventions", conv_paths, project_dir)
        )
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

    Parses frontmatter, stores rules in the rules table and conventions
    in conventions/convention_includes/convention_excludes tables. Records
    git_hash for staleness detection. Skips when current.
    Idempotent — safe to rerun.
    """
    if not _governance_is_stale(db_path, project_dir):
        conn = get_connection(db_path)
        try:
            rule_count = conn.execute("SELECT COUNT(*) as c FROM rules").fetchone()["c"]
            conv_count = conn.execute("SELECT COUNT(*) as c FROM conventions").fetchone()["c"]
            return {"governance_entries": rule_count + conv_count}
        finally:
            conn.close()

    entries = scan_governance_dirs(Path(project_dir))

    conn = get_connection(db_path)
    try:
        conn.execute("DELETE FROM convention_includes")
        conn.execute("DELETE FROM convention_excludes")
        conn.execute("DELETE FROM conventions")
        conn.execute("DELETE FROM rules")

        for entry_path, entry in entries.items():
            file_hash = _git_hash(str(Path(project_dir) / entry_path))
            is_rule = "/rules/" in entry_path

            if is_rule:
                conn.execute(
                    "INSERT INTO rules (entry_path, git_hash) VALUES (?, ?)",
                    (entry_path, file_hash),
                )
            else:
                conn.execute(
                    "INSERT INTO conventions (entry_path, matches, excludes, git_hash) "
                    "VALUES (?, ?, ?, ?)",
                    (entry_path, entry["matches"], entry.get("excludes"), file_hash),
                )

                for pattern in normalize_patterns(entry["matches"]):
                    conn.execute(
                        "INSERT INTO convention_includes (entry_path, pattern) VALUES (?, ?)",
                        (entry_path, pattern),
                    )

                if entry.get("excludes"):
                    for pattern in normalize_patterns(entry["excludes"]):
                        conn.execute(
                            "INSERT INTO convention_excludes (entry_path, pattern) VALUES (?, ?)",
                            (entry_path, pattern),
                        )

        conn.commit()

        rule_count = conn.execute("SELECT COUNT(*) as c FROM rules").fetchone()["c"]
        conv_count = conn.execute("SELECT COUNT(*) as c FROM conventions").fetchone()["c"]
        return {"governance_entries": rule_count + conv_count}
    finally:
        conn.close()


def governance_list(db_path: str) -> list[dict]:
    """List all governance entries with patterns and loading mode."""
    _ensure_current(db_path)
    conn = get_connection(db_path)
    try:
        rows = conn.execute(
            "SELECT entry_path, matches, excludes, 'convention' as mode "
            "FROM conventions "
            "UNION ALL "
            "SELECT entry_path, '*' as matches, NULL as excludes, 'rule' as mode "
            "FROM rules "
            "ORDER BY entry_path"
        ).fetchall()

        result = []
        for row in rows:
            entry = {
                "path": row["entry_path"],
                "matches": row["matches"],
                "mode": row["mode"],
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

        query = f"""
            WITH files(path) AS (VALUES {placeholders})
            SELECT DISTINCT f.path AS file_path, ci.entry_path
            FROM files f
            JOIN convention_includes ci ON path_match(f.path, ci.pattern)
            LEFT JOIN convention_excludes ce
                ON ci.entry_path = ce.entry_path AND path_match(f.path, ce.pattern)
            WHERE ce.entry_path IS NULL
            ORDER BY f.path, ci.entry_path
        """

        rows = conn.execute(query, params).fetchall()

        result_matches: dict[str, list[str]] = {}
        for row in rows:
            result_matches.setdefault(row["file_path"], []).append(row["entry_path"])

        if include_rules:
            rule_rows = conn.execute("SELECT entry_path FROM rules").fetchall()
            rule_paths = [r["entry_path"] for r in rule_rows]
            for fp in file_paths:
                for rp in rule_paths:
                    result_matches.setdefault(fp, []).append(rp)

        conventions = sorted({c for cs in result_matches.values() for c in cs})

        return {
            "matches": result_matches,
            "conventions": conventions,
        }
    finally:
        conn.close()


def governance_unclassified(db_path: str) -> dict:
    """Find file entries with no convention coverage, grouped by extension.

    Scans the filesystem first to ensure entries are current, then uses
    path_match() custom SQL function for single-query evaluation.
    Only checks convention coverage — rules apply universally and don't
    classify individual files.
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
            AND e.path NOT IN (SELECT entry_path FROM conventions)
            AND e.path NOT IN (SELECT entry_path FROM rules)
            AND NOT EXISTS (
                SELECT 1 FROM convention_includes ci
                WHERE path_match(e.path, ci.pattern)
                AND ci.entry_path NOT IN (
                    SELECT ce.entry_path FROM convention_excludes ce
                    WHERE path_match(e.path, ce.pattern)
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
