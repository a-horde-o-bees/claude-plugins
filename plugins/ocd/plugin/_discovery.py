"""System and skill discovery.

Discovers server subsystems with init infrastructure and workflow
skills (slash commands) within a plugin directory tree.
"""

from pathlib import Path


def _discover_systems(plugin_root: Path) -> list[str]:
    """Discover library subsystems with init infrastructure.

    Returns sorted list of lib package names whose package contains
    an _init.py module (conforming to the init/status contract).
    Library subsystems own state — database files, deployed conventions,
    configuration — and their init routines bootstrap or refresh that state.
    """
    lib_dir = plugin_root / "lib"
    if not lib_dir.is_dir():
        return []

    return sorted(
        init_path.parent.name
        for init_path in lib_dir.glob("*/_init.py")
    )


def _discover_workflow_skills(plugin_root: Path) -> list[str]:
    """Discover workflow skills. Returns sorted list of skill names.

    Workflow skills are pure slash command workflows without persistent state —
    each has a SKILL.md in plugins/<plugin>/skills/<name>/ and is invoked as
    `/<name>`. They are listed in init/status output so the user sees what
    commands the plugin ships, but the plugin does not deploy or track them.
    """
    skills_dir = plugin_root / "skills"
    if not skills_dir.is_dir():
        return []

    return sorted(
        skill_md.parent.name
        for skill_md in skills_dir.glob("*/SKILL.md")
    )
