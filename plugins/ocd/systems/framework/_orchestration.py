"""Install and list orchestration.

Top-level run_init and run_status entry points that discover every
systems/ entry and dispatch uniformly to each subsystem's _init.py.
Content domains (rules, conventions, log) and operational systems
(navigator, permissions) follow the same contract.

Enable/disable orchestration respects the per-project opt-in config
(`.claude/<plugin>/enabled-systems.json`). `run_init` deploys only
enabled systems and prunes deployed artifacts for disabled systems
via each system's optional `clean()` contract. `run_enable` and
`run_disable` mutate the config and reconcile disk state.
"""

import importlib

from ._enabled import effective_enabled, read_enabled, write_enabled
from ._system_discovery import _discover_systems, _discover_workflow_skills
from ._environment import get_claude_home, get_plugin_root
from ._formatting import format_bare_skill, format_section
from ._metadata import find_marketplace_source, format_header, get_installed_version, get_plugin_name


_META_SKILLS = {"setup"}


def run_init(
    force: bool = False,
    system: str | None = None,
    all_systems: bool = False,
    selected: list[str] | None = None,
) -> None:
    """Install: init enabled systems and prune disabled ones.

    system: narrow scope to one subsystem for this run. Does not mutate
    the enabled-systems config — use it for targeted re-init.

    all_systems: enable every discovered system and persist.

    selected: enable exactly this list (validated against discovery) and
    persist. Mutually exclusive with all_systems.

    No flags: use the existing enabled-systems config. If no config
    exists yet (first install), default to enabling every discovered
    system so the plugin works out of the box.

    force: passed through to each subsystem's init().
    """
    plugin_root = get_plugin_root()
    plugin_name = get_plugin_name(plugin_root)

    available = _discover_systems(plugin_root)
    if system is not None and system not in available:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(available)}" if available else "No systems discovered.")
        return

    narrow_run = system is not None

    if narrow_run:
        target_systems = [system]
        disabled = []
    else:
        if all_systems:
            target_systems = list(available)
            write_enabled(plugin_root, target_systems)
        elif selected is not None:
            unknown = [s for s in selected if s not in available]
            if unknown:
                print(f"Unknown system(s): {', '.join(unknown)}")
                print(f"Available: {', '.join(available)}")
                return
            target_systems = sorted(set(selected))
            write_enabled(plugin_root, target_systems)
        else:
            target_systems = effective_enabled(plugin_root, available)
            if read_enabled(plugin_root) is None:
                write_enabled(plugin_root, target_systems)
        disabled = [s for s in available if s not in target_systems]

    print(f"{plugin_name} install" + (f" --system {system}" if narrow_run else ""))
    print()

    rules_changed = False

    for system_name in target_systems:
        mod = importlib.import_module(f"systems.{system_name}._init")
        result = mod.init(force=force)
        for line in format_section(system_name.capitalize(), result["files"], result.get("extra")):
            print(line)
        print()

        if system_name == "rules":
            rules_changed = any(f["before"] != f["after"] for f in result["files"])

    for system_name in disabled:
        mod = importlib.import_module(f"systems.{system_name}._init")
        if not hasattr(mod, "clean"):
            continue
        result = mod.clean()
        for line in format_section(
            f"{system_name.capitalize()} (disabled)", result["files"], result.get("extra"),
        ):
            print(line)
        print()

    if not narrow_run:
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


def run_enable(system: str) -> None:
    """Add system to the enabled list and init it in-place."""
    plugin_root = get_plugin_root()
    available = _discover_systems(plugin_root)
    if system not in available:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(available)}")
        return

    enabled = effective_enabled(plugin_root, available)
    if system in enabled:
        print(f"{system} is already enabled")
        return

    enabled.append(system)
    write_enabled(plugin_root, enabled)

    mod = importlib.import_module(f"systems.{system}._init")
    result = mod.init(force=False)
    for line in format_section(system.capitalize(), result["files"], result.get("extra")):
        print(line)
    print()

    if system == "rules" and any(f["before"] != f["after"] for f in result["files"]):
        print(f"{system} enabled. Restart Claude session to load new rules.")
    else:
        print(f"{system} enabled.")


def run_disable(system: str) -> None:
    """Remove system from enabled list and clean its deployed artifacts."""
    plugin_root = get_plugin_root()
    available = _discover_systems(plugin_root)
    if system not in available:
        print(f"Unknown system: {system}")
        print(f"Available: {', '.join(available)}")
        return

    enabled = effective_enabled(plugin_root, available)
    if system not in enabled:
        print(f"{system} is already disabled")
        return

    enabled.remove(system)
    write_enabled(plugin_root, enabled)

    mod = importlib.import_module(f"systems.{system}._init")
    if hasattr(mod, "clean"):
        result = mod.clean()
        for line in format_section(
            f"{system.capitalize()} (disabled)", result["files"], result.get("extra"),
        ):
            print(line)
        print()
        print(f"{system} disabled.")
    else:
        print()
        print(
            f"{system} removed from enabled list. No clean() contract — "
            f"deployed artifacts (if any) were not removed automatically.",
        )


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
    enabled = set(effective_enabled(plugin_root, systems))

    for system_name in target_systems:
        mod = importlib.import_module(f"systems.{system_name}._init")
        result = mod.status()
        opt_in = "enabled" if system_name in enabled else "disabled"
        heading = f"{system_name.capitalize()} [{opt_in}]"
        for line in format_section(heading, result["files"], result.get("extra")):
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
