"""Shared deployment primitives.

Environment resolution, template stamping, deployed file comparison,
file deployment, skill CLI discovery, and output formatting.
"""

import os
import shutil
from pathlib import Path


def get_plugin_root() -> Path:
    """Resolve plugin root from CLAUDE_PLUGIN_ROOT or script location."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    return Path(__file__).parent.parent


def get_project_dir() -> Path:
    """Resolve project directory from environment or cwd."""
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def stamp_deployed(path: Path) -> None:
    """Replace type: template with type: deployed in frontmatter only."""
    content = path.read_text()
    if not content.startswith("---\n"):
        return
    end = content.index("\n---\n", 4)
    frontmatter = content[: end + 5]
    stamped = frontmatter.replace("type: template", "type: deployed")
    path.write_text(stamped + content[end + 5 :])


def compare_deployed(src: Path, dst: Path) -> str:
    """Compare single source template against deployed file.

    Returns:
    - "absent": dst does not exist
    - "current": dst matches src (with template→deployed stamp applied)
    - "divergent": dst exists but content differs from src
    """
    if not dst.exists():
        return "absent"
    src_deployed = src.read_bytes().replace(b"type: template", b"type: deployed", 1)
    if src_deployed == dst.read_bytes():
        return "current"
    return "divergent"


def deploy_files(
    src_dir: Path, dst_dir: Path, pattern: str = "*.md", force: bool = False,
) -> list[dict]:
    """Deploy template files from src_dir to dst_dir.

    Returns list of {name, before, after} dicts.
    - before: comparison state before action
    - after: state after action (transitions when files are created or replaced)
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    results = []

    if not src_dir.is_dir():
        return results

    for src in sorted(src_dir.glob(pattern)):
        if not src.is_file():
            continue
        dst = dst_dir / src.name
        before = compare_deployed(src, dst)

        if before == "absent":
            shutil.copy2(src, dst)
            stamp_deployed(dst)
            after = "current"
        elif before == "divergent" and force:
            shutil.copy2(src, dst)
            stamp_deployed(dst)
            after = "current"
        else:
            after = before

        results.append({"name": src.name, "before": before, "after": after})

    return results


def discover_skill_clis(plugin_root: Path) -> dict[str, Path]:
    """Find all skills/*/scripts/*_cli.py files. Returns {skill_name: path}."""
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return {}
    result = {}
    for cli_path in sorted(skills_dir.glob("*/scripts/*_cli.py")):
        result[cli_path.parent.parent.name] = cli_path
    return result


def format_columns(rows: list[tuple[str, ...]], separator: str = "  ") -> list[str]:
    """Format rows into aligned columns.

    Each row is a tuple of strings. Columns are left-aligned with widths
    calculated from data.
    """
    if not rows:
        return []
    widths = [max(len(cell) for cell in col) for col in zip(*rows)]
    return [separator.join(cell.ljust(w) for cell, w in zip(row, widths)).rstrip() for row in rows]
