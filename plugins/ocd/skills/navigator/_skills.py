"""Skill path resolution.

Resolves skill names to SKILL.md file paths by searching discovery
locations in Claude Code priority order. Searches highest priority
first — first match wins.
"""

import json
import os
from pathlib import Path


def _parse_frontmatter_name(skill_md: Path) -> str | None:
    """Extract name field from SKILL.md YAML frontmatter."""
    try:
        content = skill_md.read_text()
    except (FileNotFoundError, PermissionError, OSError):
        return None

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None

    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("name:"):
            value = stripped[len("name:"):].strip()
            return value.strip('"').strip("'")

    return None


def _search_skills_dir(directory: Path, name: str) -> Path | None:
    """Search skills directory for SKILL.md matching name.

    Matches by frontmatter name field. Directory must contain
    subdirectories with SKILL.md files.
    """
    if not directory.is_dir():
        return None

    for skill_dir in sorted(directory.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            continue
        frontmatter_name = _parse_frontmatter_name(skill_md)
        if frontmatter_name == name:
            return skill_md

    return None


def _get_claude_home() -> Path:
    """Return Claude global config directory."""
    return Path.home() / ".claude"


def _get_plugin_root() -> Path | None:
    """Return plugin root from environment or persisted file.

    Checks CLAUDE_PLUGIN_ROOT env var first (available in hook context),
    then reads .claude/ocd/.plugin_root (written by SessionStart hook
    for agent Bash commands where env var is not available).
    """
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    plugin_root_file = project_dir / ".claude" / "ocd" / ".plugin_root"
    try:
        value = plugin_root_file.read_text().strip()
        if value:
            return Path(value)
    except (FileNotFoundError, PermissionError):
        pass
    return None


def _get_marketplace_skill_dirs() -> list[Path]:
    """Read installed_plugins.json and return skill directories from installed plugins."""
    installed_path = _get_claude_home() / "plugins" / "installed_plugins.json"
    if not installed_path.is_file():
        return []

    try:
        data = json.loads(installed_path.read_text())
    except (json.JSONDecodeError, OSError):
        return []

    result = []
    plugins = data.get("plugins", {})
    for entries in plugins.values():
        for entry in entries:
            install_path = entry.get("installPath")
            if install_path:
                skills_dir = Path(install_path) / "skills"
                if skills_dir.is_dir():
                    result.append(skills_dir)

    return result


def skills_resolve(name: str) -> Path | None:
    """Resolve skill name to SKILL.md path.

    Searches in Claude Code priority order (highest wins):
    1. Personal: ~/.claude/skills/
    2. Project: $CLAUDE_PROJECT_DIR/.claude/skills/
    3. Plugin dir: $CLAUDE_PLUGIN_ROOT/skills/ (--plugin-dir, shadows marketplace)
    4. Marketplace: ~/.claude/plugins/installed_plugins.json install paths

    Returns absolute Path to SKILL.md or None if not found.
    """
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    plugin_root = _get_plugin_root()

    # 1. Personal skills
    personal_skills = _get_claude_home() / "skills"
    result = _search_skills_dir(personal_skills, name)
    if result:
        return result

    # 2. Project skills
    project_skills = project_dir / ".claude" / "skills"
    result = _search_skills_dir(project_skills, name)
    if result:
        return result

    # 3. Plugin dir (--plugin-dir)
    if plugin_root:
        plugin_skills = plugin_root / "skills"
        result = _search_skills_dir(plugin_skills, name)
        if result:
            return result

    # 4. Marketplace plugins
    for marketplace_skills_dir in _get_marketplace_skill_dirs():
        result = _search_skills_dir(marketplace_skills_dir, name)
        if result:
            return result

    return None


def skills_list() -> list[dict[str, str]]:
    """List all discoverable skills with source and path.

    Returns list of {name, source, path} dicts in priority order.
    """
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    plugin_root = _get_plugin_root()

    results: list[dict[str, str]] = []
    seen_names: set[str] = set()

    def _collect(directory: Path, source: str) -> None:
        if not directory.is_dir():
            return
        for skill_dir in sorted(directory.iterdir()):
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.is_file():
                continue
            name = _parse_frontmatter_name(skill_md)
            if name and name not in seen_names:
                seen_names.add(name)
                results.append({
                    "name": name,
                    "source": source,
                    "path": str(skill_md),
                })

    _collect(_get_claude_home() / "skills", "personal")
    _collect(project_dir / ".claude" / "skills", "project")
    if plugin_root:
        _collect(plugin_root / "skills", "plugin-dir")
    for marketplace_dir in _get_marketplace_skill_dirs():
        _collect(marketplace_dir, "marketplace")

    return results
