"""System and skill discovery.

Discovers systems with init infrastructure and workflow skills (slash
commands) within a plugin directory tree. All systems live under
systems/; a subsystem may own state (has _init.py), expose a workflow
(has SKILL.md), or both.
"""

from pathlib import Path


def _discover_systems(plugin_root: Path) -> list[str]:
    """Discover systems with init infrastructure.

    Returns sorted list of subsystem names whose package contains an
    _init.py module (conforming to the Init/Status Contract). These
    systems own state — database files, deployed conventions,
    configuration — and their init routines bootstrap or refresh it.
    """
    subsystems_dir = plugin_root / "systems"
    if not subsystems_dir.is_dir():
        return []

    return sorted(
        init_path.parent.name
        for init_path in subsystems_dir.glob("*/_init.py")
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
