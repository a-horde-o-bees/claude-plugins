"""Setup CLI — meta verbs and per-system dispatch.

Dispatch shape:

    ocd-run setup                      → usage (meta verbs + migrated systems)
    ocd-run setup list                 → lettered system list with purposes
    ocd-run setup status               → aggregated status across migrated systems
    ocd-run setup <system>             → that system's usage
    ocd-run setup <system> <verb> ...  → that system's verb handler

Meta-verb match takes priority. If the first positional is not a meta
verb, it is treated as a system name and dispatched to that system's
setup module. Per-system verbs route through the system's standard
handlers (status, list_items, install, uninstall) when those functions
exist; systems with their own verb set expose `dispatch(verb, args)`
which receives every verb directly. Unknown systems error with the full
list.
"""

from __future__ import annotations

import argparse
import importlib
import sys

from tools.environment import get_plugin_root
from . import (
    run_purposes,
    run_statuses,
    run_system_usage,
)
from ._formatting import format_columns
from ._orchestration import _require_git_project_dir
from ._system_discovery import _discover_systems


META_VERBS = ("list", "status")


def _format_section(heading: str, result: dict) -> None:
    from ._formatting import format_section, format_status
    if "rows" in result and "columns" in result:
        for line in format_status(heading, result["rows"], result["columns"], result.get("extra")):
            print(line)
    else:
        for line in format_section(heading, result.get("files", []), result.get("extra")):
            print(line)


def _format_catalog(heading: str, items: list[dict]) -> list[str]:
    from ._formatting import format_catalog
    return format_catalog(heading, items)


def _dispatch_system_verb(system_name: str, verb: str, rest: list[str]) -> None:
    """Dispatch a verb to the named system's setup module.

    A system that exposes `dispatch(verb, args)` owns its full verb
    surface — every verb routes through it. Systems without dispatch fall
    through to the standard handlers (status, list, install, uninstall),
    which call the matching function on the module.
    """
    mod = importlib.import_module(f"systems.{system_name}")

    if hasattr(mod, "dispatch"):
        mod.dispatch(verb, rest)
        return

    if verb == "status":
        if not hasattr(mod, "status"):
            print(f"System '{system_name}' does not support status.", file=sys.stderr)
            sys.exit(1)
        parser = argparse.ArgumentParser(prog=f"setup {system_name} status")
        parser.add_argument("--scope", choices=["user", "project"], default=None)
        args = parser.parse_args(rest)
        result = mod.status(scope=args.scope)
        _format_section(f"{system_name.capitalize()} status", result)
        return

    if verb == "list":
        if not hasattr(mod, "list_items"):
            print(f"System '{system_name}' does not expose a catalog.", file=sys.stderr)
            sys.exit(1)
        parser = argparse.ArgumentParser(prog=f"setup {system_name} list")
        parser.parse_args(rest)
        result = mod.list_items()
        for line in _format_catalog(f"{system_name.capitalize()} catalog", result.get("items", [])):
            print(line)
        return

    if verb == "install":
        if not hasattr(mod, "install"):
            print(f"System '{system_name}' does not support install.", file=sys.stderr)
            sys.exit(1)
        parser = argparse.ArgumentParser(prog=f"setup {system_name} install")
        parser.add_argument("targets", nargs="*", default=[])
        parser.add_argument("--scope", required=True, choices=["user", "project"])
        parser.add_argument("--all", action="store_true", dest="all_targets")
        parser.add_argument("--force", action="store_true")
        args = parser.parse_args(rest)
        if not args.targets and not args.all_targets:
            print(f"setup {system_name} install: specify one or more targets, or --all", file=sys.stderr)
            print(f"Run `ocd-run setup {system_name} list` to see available targets.", file=sys.stderr)
            sys.exit(1)
        if args.scope == "project":
            _require_git_project_dir()
        targets = None if args.all_targets else args.targets
        result = mod.install(scope=args.scope, targets=targets, force=args.force)
        _format_section(f"{system_name.capitalize()} install", result)
        return

    if verb == "uninstall":
        if not hasattr(mod, "uninstall"):
            print(f"System '{system_name}' does not support uninstall.", file=sys.stderr)
            sys.exit(1)
        parser = argparse.ArgumentParser(prog=f"setup {system_name} uninstall")
        parser.add_argument("targets", nargs="*", default=[])
        parser.add_argument("--scope", required=True, choices=["user", "project"])
        parser.add_argument("--all", action="store_true", dest="all_targets")
        args = parser.parse_args(rest)
        if not args.targets and not args.all_targets:
            print(f"setup {system_name} uninstall: specify one or more targets, or --all", file=sys.stderr)
            print(f"Run `ocd-run setup {system_name} status` to see deployed targets.", file=sys.stderr)
            sys.exit(1)
        if args.scope == "project":
            _require_git_project_dir()
        targets = None if args.all_targets else args.targets
        result = mod.uninstall(scope=args.scope, targets=targets)
        _format_section(f"{system_name.capitalize()} uninstall", result)
        return

    print(f"Unknown verb '{verb}' for system '{system_name}'", file=sys.stderr)
    print(f"Run `ocd-run setup {system_name}` to see this system's verbs.", file=sys.stderr)
    sys.exit(1)


def _print_skill_usage() -> None:
    plugin_root = get_plugin_root()
    systems = _discover_systems(plugin_root)
    print("setup — manage plugin infrastructure")
    print()
    print("Meta verbs:")
    rows = [
        ("list", "lettered list of systems with purpose statements"),
        ("status", "aggregated status across systems"),
    ]
    for line in format_columns(rows):
        print(f"  {line}")
    print()
    print("Per-system:")
    print("  <system>  see its purpose and verbs")
    print()
    if systems:
        print(f"Migrated systems: {', '.join(systems)}")
    else:
        print("No migrated systems yet.")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        _print_skill_usage()
        return

    first = args[0]
    rest = args[1:]

    if first in META_VERBS:
        if first == "list":
            run_purposes()
        elif first == "status":
            run_statuses()
        return

    plugin_root = get_plugin_root()
    available = _discover_systems(plugin_root)
    if first not in available:
        print(f"Unknown verb or system: {first}", file=sys.stderr)
        print(f"Meta verbs: {', '.join(META_VERBS)}", file=sys.stderr)
        if available:
            print(f"Migrated systems: {', '.join(available)}", file=sys.stderr)
        else:
            print("No migrated systems yet.", file=sys.stderr)
        sys.exit(1)

    system_name = first
    if not rest:
        run_system_usage(system_name)
        return

    verb = rest[0]
    verb_args = rest[1:]
    _dispatch_system_verb(system_name, verb, verb_args)


if __name__ == "__main__":
    main()
