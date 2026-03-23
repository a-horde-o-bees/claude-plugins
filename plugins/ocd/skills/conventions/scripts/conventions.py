"""Conventions operations.

Matches file paths against convention pattern rules stored in frontmatter.
Collects rule files from project rules directory.
Caches pattern metadata in SQLite to avoid re-reading files on every call.
"""

import hashlib
import logging
import os
import re
import fnmatch
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

CACHE_SCHEMA = """
CREATE TABLE IF NOT EXISTS convention_patterns (
    path TEXT PRIMARY KEY,
    git_hash TEXT NOT NULL,
    pattern TEXT NOT NULL
);
"""


def _compute_git_hash(file_path: str) -> str | None:
    """Compute git-compatible blob hash for a file."""
    try:
        data = Path(file_path).read_bytes()
    except (OSError, IsADirectoryError):
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create cache table if missing."""
    conn.executescript(CACHE_SCHEMA)


def get_cache_connection(db_path: str) -> sqlite3.Connection:
    """Open cache database connection."""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _extract_pattern(file_path: str) -> str | None:
    """Extract pattern field from YAML frontmatter."""
    try:
        with open(file_path) as f:
            content = f.read()
    except OSError:
        return None

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return None

    for line in match.group(1).splitlines():
        line = line.strip()
        if line.startswith("pattern:"):
            value = line[len("pattern:"):].strip()
            return value.strip('"').strip("'")

    return None


def sync_patterns(db_path: str, conventions_dir: str) -> dict[str, str]:
    """Sync convention file patterns to cache. Returns {path: pattern} map.

    Reads frontmatter only for files whose git hash has changed.
    Removes cache entries for files no longer on disk.
    """
    conn = get_cache_connection(db_path)
    try:
        # Load cached entries
        cached = {}
        for row in conn.execute("SELECT path, git_hash, pattern FROM convention_patterns"):
            cached[row["path"]] = {"git_hash": row["git_hash"], "pattern": row["pattern"]}

        # Scan convention files on disk
        disk_files = {}
        conv_path = Path(conventions_dir)
        if conv_path.is_dir():
            for f in sorted(conv_path.glob("*.md")):
                disk_files[str(f)] = True

        # Remove stale cache entries
        for path in list(cached):
            if path not in disk_files:
                conn.execute("DELETE FROM convention_patterns WHERE path = ?", (path,))
                del cached[path]

        # Update changed or new entries
        result = {}
        for path in disk_files:
            current_hash = _compute_git_hash(path)
            if current_hash is None:
                continue

            cache_entry = cached.get(path)
            if cache_entry and cache_entry["git_hash"] == current_hash:
                result[path] = cache_entry["pattern"]
                continue

            pattern = _extract_pattern(path)
            if pattern is None:
                continue

            conn.execute(
                "INSERT OR REPLACE INTO convention_patterns (path, git_hash, pattern) "
                "VALUES (?, ?, ?)",
                (path, current_hash, pattern),
            )
            result[path] = pattern

        conn.commit()
        return result
    finally:
        conn.close()


def match_conventions(conventions_dir: str, db_path: str, file_paths: list[str]) -> list[str]:
    """Match file paths against convention patterns. Returns list of matching convention file paths.

    Each convention declares a glob pattern in frontmatter. All conventions whose
    pattern matches any of the input file paths are returned, deduplicated.
    """
    patterns = sync_patterns(db_path, conventions_dir)

    matched = []
    for conv_path, pattern in patterns.items():
        for file_path in file_paths:
            basename = os.path.basename(file_path)
            if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(file_path, pattern):
                matched.append(conv_path)
                break

    return sorted(matched)


def collect_rules(rules_dir: str) -> list[str]:
    """Collect ocd rule file paths from rules directory. Returns sorted paths."""
    rules_path = Path(rules_dir)
    if not rules_path.is_dir():
        return []
    return sorted(str(f) for f in rules_path.glob("ocd-*.md"))
