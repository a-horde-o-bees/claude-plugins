"""System and skill discovery.

Discovers systems with setup infrastructure and workflow skills (slash
commands) within a plugin directory tree. All systems live under
systems/; a subsystem participates in the setup surface when its
package's top-level `__init__.py` declares the four facade functions
per `plugin-system.md`.
"""

from pathlib import Path

# Reserved system names that live under systems/ but are not user-facing
# subsystems — they implement plugin-wide infrastructure rather than a
# discrete setup-managed system.
_INFRASTRUCTURE_SYSTEMS = frozenset({"setup"})

# Sentinel function every migrated system's __init__.py must export.
# Beyond purpose, systems may expose any combination of standard verbs
# (status, list_items, install, uninstall) or their own dispatch(verb,
# args) for system-specific verbs — see plugin-system.md.
_REQUIRED_FACADE_FUNCTIONS = ("purpose",)


def _discover_systems(plugin_root: Path) -> list[str]:
    """Discover systems migrated to the setup surface.

    Returns sorted list of subsystem names whose package's `__init__.py`
    exposes `purpose()` per the plugin-system convention. Beyond purpose,
    systems declare their own verb shape — standard handlers, custom
    dispatch, or both. Systems without `purpose()` are invisible to the
    setup orchestrator until they migrate.
    """
    subsystems_dir = plugin_root / "systems"
    if not subsystems_dir.is_dir():
        return []

    discovered: list[str] = []
    for init_file in subsystems_dir.glob("*/__init__.py"):
        system_name = init_file.parent.name
        if system_name in _INFRASTRUCTURE_SYSTEMS:
            continue
        text = init_file.read_text(errors="ignore")
        if all(f"def {fn}(" in text for fn in _REQUIRED_FACADE_FUNCTIONS):
            discovered.append(system_name)
    return sorted(discovered)


def _discover_workflow_skills(plugin_root: Path) -> list[str]:
    """Discover workflow skills. Returns sorted list of skill names.

    Workflow skills are systems that expose a SKILL.md — each is
    invoked as `/<plugin>:<name>`. A subsystem may carry both an _init.py
    and a SKILL.md; it shows up in both discoveries. They are listed in
    setup status output so the user sees what commands the plugin ships,
    but the plugin does not deploy or track the skill files themselves.
    """
    subsystems_dir = plugin_root / "systems"
    if not subsystems_dir.is_dir():
        return []

    return sorted(
        skill_md.parent.name
        for skill_md in subsystems_dir.glob("*/SKILL.md")
    )
