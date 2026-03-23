"""Conventions operations.

Matches file paths against convention pattern rules stored in frontmatter.
Collects rule files from project rules directory.
Caches pattern metadata in SQLite to avoid re-reading files on every call.
"""

import hashlib
import logging
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


def _compute_git_hash(file_path: Path) -> str | None:
    """Compute git-compatible blob hash for a file."""
    try:
        data = file_path.read_bytes()
    except (OSError, IsADirectoryError):
        return None
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create cache table if missing."""
    conn.executescript(CACHE_SCHEMA)


def get_cache_connection(db_path: Path) -> sqlite3.Connection:
    """Open cache database connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _extract_pattern(file_path: Path) -> str | None:
    """Extract pattern field from YAML frontmatter."""
    try:
        content = file_path.read_text()
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


def sync_patterns(db_path: Path, conventions_dir: Path) -> dict[str, str]:
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
        disk_files: dict[str, Path] = {}
        if conventions_dir.is_dir():
            for f in sorted(conventions_dir.glob("*.md")):
                disk_files[str(f)] = f

        # Remove stale cache entries
        for path in list(cached):
            if path not in disk_files:
                conn.execute("DELETE FROM convention_patterns WHERE path = ?", (path,))
                del cached[path]

        # Update changed or new entries
        result = {}
        for path_str, path_obj in disk_files.items():
            current_hash = _compute_git_hash(path_obj)
            if current_hash is None:
                continue

            cache_entry = cached.get(path_str)
            if cache_entry and cache_entry["git_hash"] == current_hash:
                result[path_str] = cache_entry["pattern"]
                continue

            pattern = _extract_pattern(path_obj)
            if pattern is None:
                continue

            conn.execute(
                "INSERT OR REPLACE INTO convention_patterns (path, git_hash, pattern) "
                "VALUES (?, ?, ?)",
                (path_str, current_hash, pattern),
            )
            result[path_str] = pattern

        conn.commit()
        return result
    finally:
        conn.close()


def match_conventions(conventions_dir: Path, db_path: Path, file_paths: list[str]) -> list[str]:
    """Match file paths against convention patterns. Returns list of matching convention file paths.

    Each convention declares a glob pattern in frontmatter. All conventions whose
    pattern matches any of the input file paths are returned, deduplicated.
    """
    patterns = sync_patterns(db_path, conventions_dir)

    matched = []
    for conv_path, pattern in patterns.items():
        for file_path in file_paths:
            basename = Path(file_path).name
            if fnmatch.fnmatch(basename, pattern) or fnmatch.fnmatch(file_path, pattern):
                matched.append(conv_path)
                break

    return sorted(matched)


def collect_rules(rules_dir: Path) -> list[str]:
    """Collect ocd rule file paths from rules directory. Returns sorted paths."""
    if not rules_dir.is_dir():
        return []
    return sorted(str(f) for f in rules_dir.glob("ocd-*.md"))
