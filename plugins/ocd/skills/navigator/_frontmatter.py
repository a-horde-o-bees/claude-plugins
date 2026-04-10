"""Governance frontmatter parser.

Reads matches, excludes, and governed_by fields from YAML frontmatter
in governance files (rules and conventions). No PyYAML dependency —
parses the specific structure used by governance frontmatter.

Fields:
  matches:      (required) file patterns this governance entry applies to
  excludes:     (optional) file patterns to exclude from matches
  governed_by:  (optional) governance files this entry builds on (evaluation ordering)
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path


def parse_governance(file_path: Path) -> dict | None:
    """Extract governance frontmatter from a markdown file.

    Returns {matches, excludes, governed_by} dict if governance frontmatter
    exists, None if file has no frontmatter or no matches field.
    """
    try:
        content = file_path.read_text()
    except (FileNotFoundError, PermissionError, OSError):
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    matches = None
    matches_items: list[str] = []
    excludes = None
    excludes_items: list[str] = []
    governed_by: list[str] = []
    in_matches = False
    in_excludes = False
    in_governed_by = False

    def _end_block() -> None:
        nonlocal matches, matches_items, excludes, excludes_items
        nonlocal in_matches, in_excludes, in_governed_by
        if in_matches and matches_items:
            matches = json.dumps(matches_items)
        if in_excludes and excludes_items:
            excludes = json.dumps(excludes_items)
        in_matches = False
        in_excludes = False
        in_governed_by = False

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break

        if stripped.startswith("matches:"):
            _end_block()
            value = stripped[len("matches:"):].strip()
            if value.startswith("["):
                matches = value
            elif value:
                matches = value.strip('"').strip("'")
            else:
                in_matches = True
                matches_items = []

        elif in_matches and stripped.startswith("- "):
            matches_items.append(stripped[2:].strip().strip('"').strip("'"))

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
    if in_matches and matches_items:
        matches = json.dumps(matches_items)
    if in_excludes and excludes_items:
        excludes = json.dumps(excludes_items)

    if matches is None:
        return None

    return {"matches": matches, "excludes": excludes, "governed_by": governed_by}


def scan_governance_dirs(
    project_dir: Path,
    rules_dir: str = ".claude/rules",
    conventions_dir: str = ".claude/conventions",
) -> dict[str, dict]:
    """Scan governance directories for files with governance frontmatter.

    Returns {relative_path: {matches, excludes, governed_by}} map for all
    governance files found. Paths are relative to project_dir.
    """
    result: dict[str, dict] = {}

    for dir_rel in (rules_dir, conventions_dir):
        scan_dir = project_dir / dir_rel
        if not scan_dir.is_dir():
            continue
        for md_file in sorted(scan_dir.glob("*.md")):
            if not md_file.is_file():
                continue
            parsed = parse_governance(md_file)
            if parsed is not None:
                rel_path = str(md_file.relative_to(project_dir))
                result[rel_path] = parsed

    return result


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

    Used by governance_match, governance_unclassified, and scan-time
    governance matching.
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
