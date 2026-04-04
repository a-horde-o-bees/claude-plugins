"""Governance frontmatter parser.

Reads pattern and depends fields from YAML frontmatter in governance
files (rules and conventions). No PyYAML dependency — parses the
specific structure used by governance frontmatter.
"""

from __future__ import annotations

from pathlib import Path


def parse_governance(file_path: Path) -> dict | None:
    """Extract governance frontmatter from a markdown file.

    Returns {pattern, depends} dict if governance frontmatter exists,
    None if file has no frontmatter or no pattern field.
    """
    try:
        content = file_path.read_text()
    except (FileNotFoundError, PermissionError, OSError):
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    pattern = None
    depends: list[str] = []
    in_depends = False

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break

        if stripped.startswith("pattern:"):
            in_depends = False
            value = stripped[len("pattern:"):].strip()
            pattern = value.strip('"').strip("'")

        elif stripped == "depends:":
            in_depends = True

        elif in_depends and stripped.startswith("- "):
            depends.append(stripped[2:].strip().strip('"').strip("'"))

        else:
            in_depends = False

    if pattern is None:
        return None

    return {"pattern": pattern, "depends": depends}


def scan_governance_dirs(
    project_dir: Path,
    rules_dir: str = ".claude/rules",
    conventions_dir: str = ".claude/conventions",
) -> dict[str, dict]:
    """Scan governance directories for files with governance frontmatter.

    Returns {relative_path: {pattern, depends}} map for all governance
    files found. Paths are relative to project_dir.
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
