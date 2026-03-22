"""Plugin status report.

Displays a single status line showing:
- Installed plugin version
- Init status (whether rule files exist in project)
- Version mismatch (for local-directory marketplaces only)

No network calls, no automated updates — informational only.
"""

import json
import os
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


def check_init_status(plugin_root: Path, project_dir: Path) -> str:
    """Check if init has been run by verifying manifest files exist."""
    manifest = read_json(plugin_root / "references" / "init_manifest.json")
    files = manifest.get("files", [])

    if not files:
        return "unknown"

    found = sum(1 for f in files if (project_dir / f).exists())

    if found == 0:
        return "not initialized"
    if found < len(files):
        return f"partial init ({found}/{len(files)} files)"
    return "initialized"


def find_marketplace_source(
    plugin_name: str, plugin_root: Path, claude_home: Path,
) -> tuple[str | None, str | None]:
    """Find source version for local-directory marketplaces.

    Reads installed_plugins.json to find the marketplace name,
    then known_marketplaces.json to find the source path,
    then reads the source plugin.json for its version.

    Returns (source_version, marketplace_name) tuple.
    Both None if not a local marketplace or if any lookup fails.
    """
    installed = read_json(claude_home / "plugins" / "installed_plugins.json")
    plugins = installed.get("plugins", {})

    # Find marketplace name from installed_plugins key (format: "name@marketplace")
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

    # Look up marketplace source
    known = read_json(claude_home / "plugins" / "known_marketplaces.json")
    marketplace = known.get(marketplace_name, {})
    source = marketplace.get("source", {})

    if source.get("source") != "directory":
        return None, marketplace_name

    marketplace_path = Path(source.get("path", ""))
    if not marketplace_path.is_dir():
        return None, marketplace_name

    # Read marketplace manifest to find plugin source path
    manifest = read_json(marketplace_path / ".claude-plugin" / "marketplace.json")
    for plugin_entry in manifest.get("plugins", []):
        if plugin_entry.get("name") == plugin_name:
            plugin_source = plugin_entry.get("source", "")
            source_dir = (marketplace_path / plugin_source).resolve()
            source_plugin = read_json(source_dir / ".claude-plugin" / "plugin.json")
            return source_plugin.get("version"), marketplace_name

    return None, marketplace_name


def main():
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    claude_home = get_claude_home()

    plugin_name = get_plugin_name(plugin_root)
    installed_version = get_installed_version(plugin_root)

    # Init status
    init_status = check_init_status(plugin_root, project_dir)

    # Version comparison (local-directory marketplaces only)
    source_version, marketplace_name = find_marketplace_source(
        plugin_name, plugin_root, claude_home,
    )

    # Build status line
    parts = [f"{plugin_name} v{installed_version}"]

    if init_status == "not initialized":
        parts.append("not initialized (run /ocd-init)")
    elif init_status.startswith("partial"):
        parts.append(f"{init_status} (run /ocd-init)")
    else:
        parts.append(init_status)

    if source_version and source_version != installed_version:
        parts.append(
            f"update available: v{source_version}"
            f" (run /plugin marketplace update {marketplace_name}"
            f" then /plugin install {plugin_name})"
        )
    elif source_version:
        parts.append("up to date")

    print(" | ".join(parts))


if __name__ == "__main__":
    main()
