"""Conventions state check.

Verifies convention infrastructure by inspecting deployed convention files.
"""

import re
from pathlib import Path


def _has_valid_pattern(file_path: str) -> bool:
    """Check if file has valid pattern field in YAML frontmatter."""
    try:
        content = Path(file_path).read_text()
    except OSError:
        return False

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return False

    for line in match.group(1).splitlines():
        if line.strip().startswith("pattern:"):
            return True

    return False


def check_state(project_dir: str) -> dict:
    """Check conventions infrastructure state.

    Returns dict with:
    - state: "operational" | "adopted"
    - details: list of human-readable status lines
    - actions: list of actionable commands
    """
    conventions_dir = Path(project_dir) / ".claude" / "ocd" / "conventions"

    if not conventions_dir.is_dir():
        return {
            "state": "adopted",
            "details": ["Convention files: not found"],
            "actions": ["Run /ocd-init to deploy convention files"],
        }

    md_files = sorted(conventions_dir.glob("*.md"))

    if not md_files:
        return {
            "state": "adopted",
            "details": ["Convention files: none"],
            "actions": ["Run /ocd-init to deploy convention files"],
        }

    valid_count = sum(1 for f in md_files if _has_valid_pattern(str(f)))

    return {
        "state": "operational",
        "details": [f"Convention files: {len(md_files)} ({valid_count} with valid patterns)"],
        "actions": [],
    }
