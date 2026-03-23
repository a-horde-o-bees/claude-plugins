"""Conventions skill init and status.

Deploys convention templates and reports infrastructure state.
"""

import argparse
import re
import shutil
from pathlib import Path


def get_project_dir() -> str:
    import os
    return os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())


def get_plugin_root() -> Path:
    """Resolve plugin root from script location (skills/conventions/scripts/ -> plugin root)."""
    import os
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    return Path(__file__).parent.parent.parent.parent


def get_conventions_dir(project_dir: str) -> Path:
    return Path(project_dir) / ".claude" / "ocd" / "conventions"


def init(plugin_root: Path, project_dir: str, force: bool = False) -> list[str]:
    """Deploy convention templates. Returns status lines."""
    templates_src = plugin_root / "templates" / "conventions"
    conventions_dst = get_conventions_dir(project_dir)
    conventions_dst.mkdir(parents=True, exist_ok=True)

    lines = []

    if not templates_src.is_dir():
        lines.append("No convention templates found in plugin")
        return lines

    for src in sorted(templates_src.glob("*.md")):
        dst = conventions_dst / src.name
        if dst.exists() and not force:
            lines.append(f"Skipped (exists): {src.name}")
            continue
        action = "Overwritten" if dst.exists() else "Deployed"
        shutil.copy2(src, dst)
        lines.append(f"{action}: {src.name}")

    return lines


def _has_valid_pattern(file_path: Path) -> bool:
    """Check if file has valid pattern field in YAML frontmatter."""
    try:
        content = file_path.read_text()
    except OSError:
        return False

    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if not match:
        return False

    for line in match.group(1).splitlines():
        if line.strip().startswith("pattern:"):
            return True

    return False


def status(project_dir: str) -> dict:
    """Check conventions infrastructure state.

    Returns dict with:
    - state: "operational" | "adopted"
    - details: list of human-readable status lines
    - actions: list of actionable commands
    """
    conventions_dir = get_conventions_dir(project_dir)

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

    valid_count = sum(1 for f in md_files if _has_valid_pattern(f))

    return {
        "state": "operational",
        "details": [f"Convention files: {len(md_files)} ({valid_count} with valid patterns)"],
        "actions": [],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Conventions skill init and status.")
    parser.add_argument("--status", action="store_true", help="Report infrastructure state")
    parser.add_argument("--force", action="store_true", help="Overwrite existing convention files")
    args = parser.parse_args()

    project_dir = get_project_dir()

    if args.status:
        result = status(project_dir)
        print(f"conventions: {result['state']}")
        for detail in result.get("details", []):
            print(f"  {detail}")
        for action in result.get("actions", []):
            print(f"  Action: {action}")
    else:
        plugin_root = get_plugin_root()
        lines = init(plugin_root, project_dir, force=args.force)
        for line in lines:
            print(line)


if __name__ == "__main__":
    main()
