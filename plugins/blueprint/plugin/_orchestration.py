"""Install and list orchestration.

Top-level run_init and run_status entry points that discover every
systems/ entry and dispatch uniformly to each subsystem's _init.py.
Content domains (rules, conventions, patterns, logs) and operational
systems (navigator, permissions) follow the same contract.
"""

import importlib
import subprocess
from pathlib import Path

from ._discovery import _discover_systems, _discover_workflow_skills
from ._environment import get_claude_home, get_plugin_root, get_project_dir
from ._formatting import format_bare_skill, format_section
from ._metadata import find_marketplace_source, format_header, get_installed_version, get_plugin_name


_META_SKILLS = {"setup"}


def _set_hookspath(project_dir: Path) -> bool:
    """Configure git to use .githooks/ when that directory exists.

    Returns True if hookspath was newly set, False if already set or absent.
    """
    githooks_dir = project_dir / ".githooks"
    if not githooks_dir.is_dir():
        return False
    current = subprocess.run(
        ["git", "-C", str(project_dir), "config", "--get", "core.hookspath"],
        capture_output=True, text=True,
    )
    if current.returncode == 0 and current.stdout.strip() == ".githooks":
        return False
    subprocess.run(
        ["git", "-C", str(project_dir), "config", "core.hookspath", ".githooks"],
        capture_output=True,
    )
    return True


def run_init(force: bool = False, system: str | None = None) -> None:
    """Install: discover and init every subsystem.

    system: when provided, scopes init to one subsystem. Unknown names
    print an error listing available systems.

    force: passed through to each subsystem's init(). Destructive semantics
    are defined per-subsystem (typically rebuilds state from scratch).
    """
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    plugin_name = get_plugin_name(plugin_root)

    systems = _discover_systems(plugin_root)
    if system is not None and system not in systems:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(systems)}" if systems else "No systems discovered.")
        return

    print(f"{plugin_name} install" + (f" --system {system}" if system else ""))
    print()

    target_systems = [system] if system is not None else systems
    rules_changed = False

    for system_name in target_systems:
        mod = importlib.import_module(f"systems.{system_name}._init")
        result = mod.init(force=force)
        for line in format_section(system_name.capitalize(), result["files"], result.get("extra")):
            print(line)
        print()

        if system_name == "rules":
            rules_changed = any(f["before"] != f["after"] for f in result["files"])

    # Git hookspath (project-wide; skipped when scoped to a single subsystem)
    if system is None and _set_hookspath(project_dir):
        print("Git hookspath set to .githooks")
        print()

    # Workflow skills (only when not scoped)
    if system is None:
        skills = _discover_workflow_skills(plugin_root)
        shown = [s for s in skills if s not in _META_SKILLS]
        if shown:
            print("Skills")
            for skill_name in shown:
                print(f"  {format_bare_skill(plugin_name, skill_name)}")
            print()

    if rules_changed:
        print("Done. Restart Claude session to load new rules.")
    else:
        print("Done.")


def run_status(system: str | None = None) -> None:
    """List: discover and report state for every subsystem.

    system: when provided, scopes output to one subsystem. Unknown names
    print an error listing available systems.
    """
    plugin_root = get_plugin_root()
    claude_home = get_claude_home()
    plugin_name = get_plugin_name(plugin_root)

    systems = _discover_systems(plugin_root)
    if system is not None and system not in systems:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(systems)}" if systems else "No systems discovered.")
        return

    # Header (plugin-wide; skipped when scoped to a single subsystem)
    if system is None:
        installed_version = get_installed_version(plugin_root)
        source_version, marketplace_name = find_marketplace_source(
            plugin_name, plugin_root, claude_home,
        )
        print(format_header(plugin_name, installed_version, source_version, marketplace_name))
        print()

    target_systems = [system] if system is not None else systems

    for system_name in target_systems:
        mod = importlib.import_module(f"systems.{system_name}._init")
        result = mod.status()
        for line in format_section(system_name.capitalize(), result["files"], result.get("extra")):
            print(line)
        print()

    # Workflow skills (only when not scoped)
    if system is None:
        skills = _discover_workflow_skills(plugin_root)
        shown = [s for s in skills if s not in _META_SKILLS]
        if shown:
            print("Skills")
            for skill_name in shown:
                print(f"  {format_bare_skill(plugin_name, skill_name)}")
            print()
