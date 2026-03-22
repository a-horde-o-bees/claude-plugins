"""Plugin status report.

Derives all state deterministically from filesystem:
- Plugin version and marketplace version comparison
- Rule states via diff of source vs deployed files
- Skill states via per-skill infrastructure checks

No state file, no network calls, no automated updates.
"""

import importlib
import json
import os
import sys
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


def get_claude_home() -> Path:
    """Resolve Claude home directory."""
    return Path.home() / ".claude"


def read_json(path: Path) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_installed_version(plugin_root: Path) -> str:
    """Read version from installed plugin.json."""
    data = read_json(plugin_root / ".claude-plugin" / "plugin.json")
    return data.get("version", "unknown")


def get_plugin_name(plugin_root: Path) -> str:
    """Read name from installed plugin.json."""
    data = read_json(plugin_root / ".claude-plugin" / "plugin.json")
    return data.get("name", "ocd")


def find_marketplace_source(
    plugin_name: str, plugin_root: Path, claude_home: Path,
) -> tuple[str | None, str | None]:
    """Find source version for local-directory marketplaces.

    Returns (source_version, marketplace_name) tuple.
    Both None if not a local marketplace or if any lookup fails.
    """
    installed = read_json(claude_home / "plugins" / "installed_plugins.json")
    plugins = installed.get("plugins", {})

    marketplace_name = None
    plugin_root_str = str(plugin_root)
    for key, entries in plugins.items():
        for entry in entries:
            if entry.get("installPath") == plugin_root_str:
                parts = key.split("@", 1)
                if len(parts) == 2:
                    marketplace_name = parts[1]
                break
        if marketplace_name:
            break

    if not marketplace_name:
        return None, None

    known = read_json(claude_home / "plugins" / "known_marketplaces.json")
    marketplace = known.get(marketplace_name, {})
    source = marketplace.get("source", {})

    if source.get("source") != "directory":
        return None, marketplace_name

    marketplace_path = Path(source.get("path", ""))
    if not marketplace_path.is_dir():
        return None, marketplace_name

    manifest = read_json(marketplace_path / ".claude-plugin" / "marketplace.json")
    for plugin_entry in manifest.get("plugins", []):
        if plugin_entry.get("name") == plugin_name:
            plugin_source = plugin_entry.get("source", "")
            source_dir = (marketplace_path / plugin_source).resolve()
            source_plugin = read_json(source_dir / ".claude-plugin" / "plugin.json")
            return source_plugin.get("version"), marketplace_name

    return None, marketplace_name


def format_header(
    plugin_name: str,
    installed_version: str,
    source_version: str | None,
    marketplace_name: str | None,
) -> str:
    """Format header line with version and update status."""
    parts = [f"{plugin_name} v{installed_version}"]

    if source_version and source_version != installed_version:
        parts.append(f"update available: v{source_version}")
    elif source_version:
        parts.append("up to date")

    return " | ".join(parts)


def format_rules_section(plugin_root: Path, project_dir: Path) -> list[str]:
    """Format rules section using diff-based state check."""
    scripts_dir = plugin_root / "scripts"
    sys.path.insert(0, str(scripts_dir))
    try:
        import rules_state
        importlib.reload(rules_state)
        results = rules_state.check_rules(str(plugin_root), str(project_dir))
    except Exception as e:
        return [f"  Error checking rules: {e}"]
    finally:
        sys.path.pop(0)
        sys.modules.pop("rules_state", None)

    if not results:
        return ["  No rules found in plugin"]

    lines = []
    for r in results:
        lines.append(f"  {r['state']:<12}{r['rule']}")
    return lines


def discover_skills(plugin_root: Path) -> list[str]:
    """Discover available skills from SKILL.md files."""
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return []

    skills = []
    for skill_md in sorted(skills_dir.glob("*/SKILL.md")):
        skills.append(skill_md.parent.name)
    return skills


def run_skill_state_check(plugin_root: Path, skill: str, project_dir: Path) -> dict | None:
    """Run a skill's state.py check if it exists. Returns result dict or None."""
    state_script = plugin_root / "skills" / skill / "scripts" / "state.py"
    if not state_script.exists():
        return None

    scripts_dir = state_script.parent
    sys.path.insert(0, str(scripts_dir))
    try:
        import state
        importlib.reload(state)
        return state.check_state(str(project_dir))
    except Exception as e:
        return {
            "state": "error",
            "details": [f"State check failed: {e}"],
            "actions": [],
        }
    finally:
        sys.path.pop(0)
        sys.modules.pop("state", None)


def format_skills_section(plugin_root: Path, project_dir: Path) -> list[str]:
    """Format skills section with per-skill state checks."""
    skills = discover_skills(plugin_root)

    if not skills:
        return ["  No skills found in plugin"]

    lines = []
    for skill in skills:
        result = run_skill_state_check(plugin_root, skill, project_dir)

        if result is None:
            lines.append(f"  {skill}")
            continue

        lines.append(f"  {skill}: {result['state']}")
        for detail in result.get("details", []):
            lines.append(f"    {detail}")
        for action in result.get("actions", []):
            lines.append(f"    Action: {action}")

    return lines


def main() -> None:
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    claude_home = get_claude_home()

    plugin_name = get_plugin_name(plugin_root)
    installed_version = get_installed_version(plugin_root)

    source_version, marketplace_name = find_marketplace_source(
        plugin_name, plugin_root, claude_home,
    )

    header = format_header(
        plugin_name, installed_version, source_version, marketplace_name,
    )
    print(header)

    print()
    print("Rules")
    for line in format_rules_section(plugin_root, project_dir):
        print(line)

    print()
    print("Skills")
    for line in format_skills_section(plugin_root, project_dir):
        print(line)


if __name__ == "__main__":
    main()
