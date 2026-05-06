"""Setup CLI — meta verbs and per-system dispatch.

Dispatch shape:

    ocd-run setup                      → usage (this skill's verbs + system list)
    ocd-run setup purposes             → lettered system list with purpose statements
    ocd-run setup statuses             → aggregated status across migrated systems
    ocd-run setup permissions <verb>   → permissions subcommands (status/deploy/analyze/clean)
    ocd-run setup <system>             → that system's usage
    ocd-run setup <system> <verb> ...  → that system's verb handler

Meta-verb match takes priority. If the first positional is not a meta
verb or 'permissions', it is treated as a system name and dispatched to
that system's setup module. Unknown systems error with the full list.
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
from ._orchestration import _require_git_project_dir
from ._system_discovery import _discover_systems


META_VERBS = ("purposes", "statuses")


def _format_section(heading: str, result: dict) -> None:
    from ._formatting import format_section
    for line in format_section(heading, result.get("files", []), result.get("extra")):
        print(line)


def _dispatch_system_verb(system_name: str, verb: str, rest: list[str]) -> None:
    """Dispatch a verb to the named system's setup module."""
    mod = importlib.import_module(f"systems.{system_name}")

    if verb == "status":
        parser = argparse.ArgumentParser(prog=f"setup {system_name} status")
        parser.add_argument("--scope", choices=["user", "project"], default=None)
        args = parser.parse_args(rest)
        result = mod.status(scope=args.scope)
        _format_section(f"{system_name.capitalize()} status", result)
        return

    if verb == "install":
        parser = argparse.ArgumentParser(prog=f"setup {system_name} install")
        parser.add_argument("target", nargs="?", default=None)
        parser.add_argument("--scope", required=True, choices=["user", "project"])
        parser.add_argument("--force", action="store_true")
        args = parser.parse_args(rest)
        if args.scope == "project":
            _require_git_project_dir()
        result = mod.install(scope=args.scope, target=args.target, force=args.force)
        _format_section(f"{system_name.capitalize()} install", result)
        return

    if verb == "uninstall":
        parser = argparse.ArgumentParser(prog=f"setup {system_name} uninstall")
        parser.add_argument("target", nargs="?", default=None)
        parser.add_argument("--scope", required=True, choices=["user", "project"])
        args = parser.parse_args(rest)
        if args.scope == "project":
            _require_git_project_dir()
        result = mod.uninstall(scope=args.scope, target=args.target)
        _format_section(f"{system_name.capitalize()} uninstall", result)
        return

    print(f"Unknown verb '{verb}' for system '{system_name}'", file=sys.stderr)
    print("Available verbs: install, uninstall, status", file=sys.stderr)
    sys.exit(1)


def _dispatch_permissions(rest: list[str]) -> None:
    parser = argparse.ArgumentParser(prog="setup permissions")
    sub = parser.add_subparsers(dest="perm_command", required=True)

    sub.add_parser("status", help="Both scopes' permission state")

    deploy = sub.add_parser("deploy", help="Deploy recommended patterns to one scope")
    deploy.add_argument("--scope", required=True, choices=["user", "project"])

    sub.add_parser("analyze", help="Cross-scope health analysis")

    clean = sub.add_parser("clean", help="Remove recommendations redundant with the other scope")
    clean.add_argument("--scope", required=True, choices=["user", "project"])

    args = parser.parse_args(rest)

    perm = importlib.import_module("systems.permissions")
    if args.perm_command == "status":
        perm.run_permissions_status()
    elif args.perm_command == "deploy":
        perm.run_permissions_deploy(scope=args.scope)
    elif args.perm_command == "analyze":
        perm.run_permissions_analyze()
    elif args.perm_command == "clean":
        perm.run_permissions_clean(scope=args.scope)


def _print_skill_usage() -> None:
    plugin_root = get_plugin_root()
    systems = _discover_systems(plugin_root)
    print("setup — manage plugin infrastructure")
    print()
    print("Meta verbs:")
    print("  purposes      — lettered list of systems with purpose statements")
    print("  statuses      — aggregated status across systems")
    print("  permissions   — auto-approve permission patterns (status/deploy/analyze/clean)")
    print()
    print("Per-system:")
    print("  <system>            — that system's usage and available verbs")
    print("  <system> <verb> ... — install / uninstall / status with --scope")
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
        if first == "purposes":
            run_purposes()
        elif first == "statuses":
            run_statuses()
        return

    if first == "permissions":
        _dispatch_permissions(rest)
        return

    plugin_root = get_plugin_root()
    available = _discover_systems(plugin_root)
    if first not in available:
        print(f"Unknown verb or system: {first}", file=sys.stderr)
        print(f"Meta verbs: {', '.join(META_VERBS)}, permissions", file=sys.stderr)
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
