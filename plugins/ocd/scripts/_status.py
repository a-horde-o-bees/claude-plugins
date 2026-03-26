"""Status reporting.

Plugin version, rules state, skill infrastructure status.
"""

import json
import os
import subprocess
from pathlib import Path

from _deploy import compare_deployed, discover_skill_clis, format_columns, get_plugin_root, get_project_dir


def get_claude_home() -> Path:
    return Path.home() / ".claude"


def read_json(path: Path) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def get_installed_version(plugin_root: Path) -> str:
    data = read_json(plugin_root / ".claude-plugin" / "plugin.json")
    return data.get("version", "unknown")


def get_plugin_name(plugin_root: Path) -> str:
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
    parts = [f"{plugin_name} v{installed_version}"]
    if source_version and source_version != installed_version:
        parts.append(f"update available: v{source_version}")
    elif source_version:
        parts.append("up to date")
    return " | ".join(parts)


def format_rules_section(plugin_root: Path, project_dir: Path) -> list[str]:
    """Format rules section using compare_deployed."""
    src_dir = plugin_root / "rules"
    dst_dir = project_dir / ".claude" / "rules"

    if not src_dir.is_dir():
        return ["  No rules found in plugin"]

    rows = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        dst = dst_dir / src.name
        state = compare_deployed(src, dst)
        name = src.stem.removeprefix("ocd-")
        rows.append((state, name))

    if not rows:
        return ["  No rules found in plugin"]

    return [f"  {line}" for line in format_columns(rows)]


def discover_skills(plugin_root: Path) -> list[str]:
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return []
    return [skill_md.parent.name for skill_md in sorted(skills_dir.glob("*/SKILL.md"))]


def format_skills_section(plugin_root: Path) -> list[str]:
    """Format skills section by calling each skill CLI status subcommand."""
    skills = discover_skills(plugin_root)
    if not skills:
        return ["  No skills found in plugin"]

    skill_clis = discover_skill_clis(plugin_root)
    lines = []
    for skill in skills:
        cli_path = skill_clis.get(skill)
        if cli_path is None:
            lines.append(f"  {skill}")
            continue
        result = subprocess.run(
            ["python3", str(cli_path), "status"],
            capture_output=True, text=True, env=os.environ,
        )
        output = result.stdout.strip()
        if output:
            for line in output.splitlines():
                lines.append(f"  {line}")
        else:
            lines.append(f"  {skill}")
    return lines


def run_status() -> None:
    """Full status report. Prints output directly."""
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    claude_home = get_claude_home()

    plugin_name = get_plugin_name(plugin_root)
    installed_version = get_installed_version(plugin_root)
    source_version, marketplace_name = find_marketplace_source(
        plugin_name, plugin_root, claude_home,
    )

    print(format_header(plugin_name, installed_version, source_version, marketplace_name))
    print()
    print("Rules")
    for line in format_rules_section(plugin_root, project_dir):
        print(line)
    print()
    print("Skills")
    for line in format_skills_section(plugin_root):
        print(line)
