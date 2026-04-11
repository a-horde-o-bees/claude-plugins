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

import plugin

from ._db import get_connection
from ._frontmatter import normalize_patterns, parse_governance


def _git_hash(file_path: Path) -> str | None:
    """Compute git-compatible blob hash for a file."""
    try:
        data = file_path.read_bytes()
    except (OSError, IsADirectoryError):
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _scan_disk_paths() -> tuple[set[str], set[str]]:
    """Scan governance directories and return (rule_paths, convention_paths).

    Paths are project-relative strings, anchored on plugin.get_project_dir().
    """
    project_dir = plugin.get_project_dir()
    rules_dir = project_dir / ".claude" / "rules"
    conv_dir = project_dir / ".claude" / "conventions"

    rule_paths: set[str] = set()
    conv_paths: set[str] = set()
    for scan_dir, target_set in ((rules_dir, rule_paths), (conv_dir, conv_paths)):
        if scan_dir.is_dir():
            for md_file in scan_dir.glob("*.md"):
                if md_file.is_file():
                    target_set.add(str(md_file.relative_to(project_dir)))

    return rule_paths, conv_paths


def _ensure_current(db_path: str) -> None:
    """Refresh governance from disk before queries."""
    governance_load(db_path)


def _reconcile_rules(conn, rule_paths: set[str]) -> None:
    """Incrementally reconcile the rules table against disk state.

    Rule files must carry governance frontmatter to count as rules —
    subsystem documentation (README.md, architecture.md) living under
    .claude/rules/ is filtered out.
    """
    project_dir = plugin.get_project_dir()
    db_rules = {
        row["entry_path"]: row["git_hash"]
        for row in conn.execute("SELECT entry_path, git_hash FROM rules").fetchall()
    }

    for removed in db_rules.keys() - rule_paths:
        conn.execute("DELETE FROM rules WHERE entry_path = ?", (removed,))

    for path in rule_paths:
        current_hash = _git_hash(project_dir / path)
        if db_rules.get(path) == current_hash:
            continue

        entry = parse_governance(project_dir / path)
        if entry is None:
            conn.execute("DELETE FROM rules WHERE entry_path = ?", (path,))
            continue

        conn.execute(
            "INSERT OR REPLACE INTO rules (entry_path, git_hash) VALUES (?, ?)",
            (path, current_hash),
        )


def _reconcile_conventions(conn, conv_paths: set[str]) -> None:
    """Incrementally reconcile the conventions tables against disk state.

    CASCADE on convention_includes/convention_excludes handles pattern
    table cleanup whenever a conventions row is deleted.
    """
    project_dir = plugin.get_project_dir()
    db_convs = {
        row["entry_path"]: row["git_hash"]
        for row in conn.execute("SELECT entry_path, git_hash FROM conventions").fetchall()
    }

    for removed in db_convs.keys() - conv_paths:
        conn.execute("DELETE FROM conventions WHERE entry_path = ?", (removed,))

    for path in conv_paths:
        current_hash = _git_hash(project_dir / path)
        if db_convs.get(path) == current_hash:
            continue

        entry = parse_governance(project_dir / path)
        if entry is None:
            # File has no frontmatter — drop any stale row
            conn.execute("DELETE FROM conventions WHERE entry_path = ?", (path,))
            continue

        # Replace any existing row (CASCADE clears include/exclude patterns)
        conn.execute("DELETE FROM conventions WHERE entry_path = ?", (path,))
        conn.execute(
            "INSERT INTO conventions (entry_path, matches, excludes, git_hash) "
            "VALUES (?, ?, ?, ?)",
            (path, entry["matches"], entry.get("excludes"), current_hash),
        )

        for pattern in normalize_patterns(entry["matches"]):
            conn.execute(
                "INSERT INTO convention_includes (entry_path, pattern) VALUES (?, ?)",
                (path, pattern),
            )

        if entry.get("excludes"):
            for pattern in normalize_patterns(entry["excludes"]):
                conn.execute(
                    "INSERT INTO convention_excludes (entry_path, pattern) VALUES (?, ?)",
                    (path, pattern),
                )


def governance_load(db_path: str) -> dict:
    """Incrementally reconcile governance tables against disk state.

    Single pass across rules and conventions: removes deleted entries,
    adds new entries, updates changed entries. Frontmatter is parsed only
    for new or changed convention files — unchanged files are skipped by
    git_hash comparison. Project root resolves from plugin.get_project_dir.
    Safe to call before every query.
    """
    rule_paths, conv_paths = _scan_disk_paths()

    conn = get_connection(db_path)
    try:
        _reconcile_rules(conn, rule_paths)
        _reconcile_conventions(conn, conv_paths)
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

    Uses path_match() custom SQL function for single-query evaluation.
    Only checks convention coverage — rules apply universally and don't
    classify individual files. Callers must ensure navigator entries are
    populated first (the facade layer owns that contract).
    """
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
