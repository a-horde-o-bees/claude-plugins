"""System and skill discovery.

Discovers systems with setup infrastructure and workflow skills (slash
commands) within a plugin directory tree. All systems live under
systems/; a subsystem may own state (has setup/__init__.py), expose a
workflow (has SKILL.md), or both.
"""

from pathlib import Path


def _discover_systems(plugin_root: Path) -> list[str]:
    """Discover systems with setup infrastructure.

    Returns sorted list of subsystem names whose package contains a
    `setup/__init__.py` exposing the per-system setup surface (purpose,
    status, install, uninstall). Systems without setup/ are invisible
    to the setup orchestrator until they migrate.
    """
    subsystems_dir = plugin_root / "systems"
    if not subsystems_dir.is_dir():
        return []

    return sorted(
        setup_init.parent.parent.name
        for setup_init in subsystems_dir.glob("*/setup/__init__.py")
    )


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
