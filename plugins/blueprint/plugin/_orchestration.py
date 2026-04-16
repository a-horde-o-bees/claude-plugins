"""Init and status orchestration.

Top-level run_init and run_status entry points that compose
environment, metadata, content deployment, discovery, formatting,
and permissions into coherent CLI operations.
"""

import importlib
import subprocess

from ._content import (
    deploy_conventions,
    deploy_logs,
    deploy_patterns,
    deploy_rules,
    get_conventions_states,
    get_logs_states,
    get_patterns_states,
    get_rules_states,
)
from ._discovery import _discover_systems, _discover_workflow_skills
from ._environment import get_claude_home, get_plugin_root, get_project_dir
from ._formatting import format_bare_skill, format_section
from ._metadata import find_marketplace_source, format_header, get_installed_version, get_plugin_name
from ._permissions import _show_permissions_status


_META_SKILLS = {"plugin"}


def run_init(force: bool = False, system: str | None = None) -> None:
    """Generic init: deploy rules, call server subsystem init hooks, list skills.

    system: when provided, scopes init to one server subsystem — rules and
    workflow skill listing are skipped, and only the named subsystem's init
    runs. Unknown system names print an error listing available subsystems.

    force: passed through to each subsystem's init(), which defines its own
    destructive semantics (typically rebuilds the database from empty state).
    """
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    plugin_name = get_plugin_name(plugin_root)

    systems = _discover_systems(plugin_root)
    if system is not None and system not in systems:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(systems)}" if systems else "No systems discovered.")
        return

    print(f"{plugin_name} init" + (f" --system {system}" if system else ""))
    print()

    rules: list[dict] = []

    # Rules and patterns (plugin-wide; skipped when scoped to a single subsystem)
    if system is None:
        rules = deploy_rules(plugin_root, project_dir, force=force)
        for line in format_section("Rules", rules):
            print(line)
        print()

        conventions = deploy_conventions(plugin_root, project_dir, force=force)
        if conventions:
            for line in format_section("Conventions", conventions):
                print(line)
            print()

        patterns = deploy_patterns(plugin_root, project_dir, force=force)
        if patterns:
            for line in format_section("Patterns", patterns):
                print(line)
            print()

        logs = deploy_logs(plugin_root, project_dir, force=force)
        if logs:
            for line in format_section("Logs", logs):
                print(line)
            print()

    # Git hookspath (project-wide; skipped when scoped to a single subsystem)
    if system is None:
        githooks_dir = project_dir / ".githooks"
        if githooks_dir.is_dir():
            current = subprocess.run(
                ["git", "-C", str(project_dir), "config", "--get", "core.hookspath"],
                capture_output=True, text=True,
            )
            if current.returncode != 0 or current.stdout.strip() != ".githooks":
                subprocess.run(
                    ["git", "-C", str(project_dir), "config", "core.hookspath", ".githooks"],
                    capture_output=True,
                )
                print("Git hookspath set to .githooks")
                print()

    # MCP servers
    target_systems = [system] if system is not None else systems
    if target_systems:
        print("MCP Servers")
        for system_name in target_systems:
            mod = importlib.import_module(f"lib.{system_name}._init")
            result = mod.init(force=force)
            for line in format_section(system_name.capitalize(), result["files"], result.get("extra")):
                print(f"  {line}")
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

    # Footer
    rules_changed = any(r["before"] != r["after"] for r in rules)
    if rules_changed:
        print("Done. Restart Claude session to load new rules.")
    else:
        print("Done.")


def run_status(system: str | None = None) -> None:
    """Generic status: report rules, server subsystems, and workflow skills.

    system: when provided, scopes output to one server subsystem —
    header, rules, and skill listing are skipped. Unknown system names
    print an error listing available subsystems.
    """
    plugin_root = get_plugin_root()
    project_dir = get_project_dir()
    claude_home = get_claude_home()
    plugin_name = get_plugin_name(plugin_root)

    systems = _discover_systems(plugin_root)
    if system is not None and system not in systems:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(systems)}" if systems else "No systems discovered.")
        return

    # Header, rules, patterns (plugin-wide; skipped when scoped to a single subsystem)
    if system is None:
        installed_version = get_installed_version(plugin_root)
        source_version, marketplace_name = find_marketplace_source(
            plugin_name, plugin_root, claude_home,
        )
        print(format_header(plugin_name, installed_version, source_version, marketplace_name))
        print()

        rules = get_rules_states(plugin_root, project_dir)
        for line in format_section("Rules", rules):
            print(line)
        print()

        conventions = get_conventions_states(plugin_root, project_dir)
        if conventions:
            for line in format_section("Conventions", conventions):
                print(line)
            print()

        patterns = get_patterns_states(plugin_root, project_dir)
        if patterns:
            for line in format_section("Patterns", patterns):
                print(line)
            print()

        logs = get_logs_states(plugin_root, project_dir)
        if logs:
            for line in format_section("Logs", logs):
                print(line)
            print()

    # MCP servers
    target_systems = [system] if system is not None else systems
    if target_systems:
        print("MCP Servers")
        for system_name in target_systems:
            mod = importlib.import_module(f"lib.{system_name}._init")
            result = mod.status()
            for line in format_section(system_name.capitalize(), result["files"], result.get("extra")):
                print(f"  {line}")
        print()

    # Workflow skills and permissions (only when not scoped)
    if system is None:
        skills = _discover_workflow_skills(plugin_root)
        shown = [s for s in skills if s not in _META_SKILLS]
        if shown:
            print("Skills")
            for skill_name in shown:
                print(f"  {format_bare_skill(plugin_name, skill_name)}")
            print()

        _show_permissions_status(plugin_root)
