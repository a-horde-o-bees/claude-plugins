"""Governance frontmatter parser.

Reads includes, excludes, and governed_by fields from YAML frontmatter
in governance files (rules and conventions). No PyYAML dependency —
parses the specific structure used by governance frontmatter.

Fields:
  includes:     (required) file patterns this governance entry applies to
  excludes:     (optional) file patterns to exclude from the include set
  governed_by:  (optional) governance files this entry builds on (evaluation ordering)
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path


def read_frontmatter(file_path: Path) -> list[str] | None:
    """Read YAML frontmatter lines from a file.

    Opens the file and reads lines until the closing `---` delimiter,
    returning the lines between (but not including) the delimiters.
    Returns None if the file has no frontmatter — either missing the
    opening delimiter, or EOF before the closing delimiter.

    Only reads what's needed — stops at the closing delimiter without
    loading the rest of the file.
    """
    try:
        with file_path.open() as f:
            first = f.readline()
            if not first or first.strip() != "---":
                return None
            lines: list[str] = []
            for line in f:
                if line.strip() == "---":
                    return lines
                lines.append(line.rstrip("\n"))
            return None
    except (FileNotFoundError, PermissionError, OSError):
        return None


def parse_governance(file_path: Path) -> dict | None:
    """Extract governance frontmatter from a markdown file.

    Returns {includes, excludes, governed_by} dict if governance frontmatter
    exists, None if file has no frontmatter or no includes field.
    """
    frontmatter_lines = read_frontmatter(file_path)
    if frontmatter_lines is None:
        return None

    includes = None
    includes_items: list[str] = []
    excludes = None
    excludes_items: list[str] = []
    governed_by: list[str] = []
    in_includes = False
    in_excludes = False
    in_governed_by = False

    def _end_block() -> None:
        nonlocal includes, includes_items, excludes, excludes_items
        nonlocal in_includes, in_excludes, in_governed_by
        if in_includes and includes_items:
            includes = json.dumps(includes_items)
        if in_excludes and excludes_items:
            excludes = json.dumps(excludes_items)
        in_includes = False
        in_excludes = False
        in_governed_by = False

    for line in frontmatter_lines:
        stripped = line.strip()

        if stripped.startswith("includes:"):
            _end_block()
            value = stripped[len("includes:"):].strip()
            if value.startswith("["):
                includes = value
            elif value:
                includes = value.strip('"').strip("'")
            else:
                in_includes = True
                includes_items = []

        elif in_includes and stripped.startswith("- "):
            includes_items.append(stripped[2:].strip().strip('"').strip("'"))

        elif stripped.startswith("excludes:"):
            _end_block()
            value = stripped[len("excludes:"):].strip()
            if value.startswith("["):
                excludes = value
            elif value:
                excludes = value.strip('"').strip("'")
            else:
                in_excludes = True
                excludes_items = []

        elif in_excludes and stripped.startswith("- "):
            excludes_items.append(stripped[2:].strip().strip('"').strip("'"))

        elif stripped.startswith("governed_by:"):
            _end_block()
            in_governed_by = True

        elif in_governed_by and stripped.startswith("- "):
            governed_by.append(stripped[2:].strip().strip('"').strip("'"))

        else:
            _end_block()

    # Handle block at end of frontmatter
    if in_includes and includes_items:
        includes = json.dumps(includes_items)
    if in_excludes and excludes_items:
        excludes = json.dumps(excludes_items)

    if includes is None:
        return None

    return {"includes": includes, "excludes": excludes, "governed_by": governed_by}


def normalize_patterns(pattern: str) -> list[str]:
    """Normalize a governance pattern to a list of fnmatch patterns.

    Handles both single pattern strings and flow-style YAML lists
    stored as JSON arrays (e.g. '["test_*.*", "*_test.*"]').
    """
    if pattern.startswith("["):
        return json.loads(pattern)
    return [pattern]


def matches_pattern(file_path: str, pattern: str) -> bool:
    """Match a file path against a governance pattern.

    Three matching modes, checked in order:

    1. Basename: "*.py" matches any .py file regardless of directory
    2. ** prefix: "**/servers/*.py" matches servers/*.py at any depth
    3. Full path: "servers/*.py" matches files at exactly that path

    Used by governance_match and scan-time governance matching.
    """
    basename = Path(file_path).name
    if fnmatch.fnmatch(basename, pattern):
        return True
    pattern_parts = Path(pattern).parts
    if pattern_parts and pattern_parts[0] == "**":
        target = str(Path(*pattern_parts[1:]))
        path_parts = Path(file_path).parts
        for i in range(len(path_parts)):
            candidate = str(Path(*path_parts[i:]))
            if fnmatch.fnmatch(candidate, target):
                return True
        return False
    return fnmatch.fnmatch(file_path, pattern)
