"""Plugin CLI.

Agent-facing entry point for init, status, and permissions operations.
Business logic lives in __init__.py.
"""

import argparse
import importlib

from . import run_enable, run_disable, run_init, run_status


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="plugin",
        description="Plugin infrastructure: init, status, and permissions operations.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    init_p = commands.add_parser(
        "init",
        help="Deploy enabled subsystems; mutate the enabled list with --all or --systems",
    )
    init_p.add_argument(
        "--force", action="store_true",
        help="Overwrite existing state with plugin defaults; destructive",
    )
    init_p.add_argument(
        "--system", default=None,
        help="Scope init to one subsystem; does not mutate the enabled list",
    )
    init_p.add_argument(
        "--all", action="store_true", dest="all_systems",
        help="Enable every discovered system and persist the selection",
    )
    init_p.add_argument(
        "--systems", default=None,
        help="Comma-separated list of systems to enable; persists the selection",
    )

    enable_p = commands.add_parser(
        "enable",
        help="Add one system to the enabled list and init it",
    )
    enable_p.add_argument("system", help="System name (e.g. rules, navigator)")

    disable_p = commands.add_parser(
        "disable",
        help="Remove one system from the enabled list and clean its deployed artifacts",
    )
    disable_p.add_argument("system", help="System name (e.g. rules, navigator)")

    status_p = commands.add_parser(
        "status",
        help="Report plugin version, opt-in state, and state of every subsystem",
    )
    status_p.add_argument(
        "--system", default=None,
        help="Scope status to one subsystem (rules, conventions, navigator, ...)",
    )

    perm_p = commands.add_parser(
        "permissions",
        help="Manage recommended auto-approve permission patterns",
    )
    perm_commands = perm_p.add_subparsers(dest="perm_command", required=True)

    perm_commands.add_parser(
        "status",
        help="Structured report of both scopes' permission state",
    )

    deploy_perm_p = perm_commands.add_parser(
        "deploy",
        help="Deploy recommended patterns to one scope",
    )
    deploy_perm_p.add_argument(
        "--scope", required=True, choices=["user", "project"],
        help="Target scope for deployment",
    )

    perm_commands.add_parser(
        "analyze",
        help="Cross-scope health analysis",
    )

    clean_p = perm_commands.add_parser(
        "clean",
        help="Remove recommended patterns redundant with the other scope",
    )
    clean_p.add_argument(
        "--scope", required=True, choices=["user", "project"],
        help="Scope to clean",
    )

    args = parser.parse_args()

    if args.command == "init":
        if args.all_systems and args.systems is not None:
            parser.error("--all and --systems are mutually exclusive")
        if args.system is not None and (args.all_systems or args.systems is not None):
            parser.error("--system cannot combine with --all or --systems")
        selected = (
            [name.strip() for name in args.systems.split(",") if name.strip()]
            if args.systems is not None
            else None
        )
        run_init(
            force=args.force,
            system=args.system,
            all_systems=args.all_systems,
            selected=selected,
        )
    elif args.command == "enable":
        run_enable(args.system)
    elif args.command == "disable":
        run_disable(args.system)
    elif args.command == "status":
        run_status(system=args.system)
    elif args.command == "permissions":
        # Runtime import — permissions lives in systems/, discovered via
        # sys.path established by run.py. importlib keeps this consistent with
        # how orchestration dispatches to systems/<subsystem>/_init.py.
        perm = importlib.import_module("systems.permissions")
        if args.perm_command == "status":
            perm.run_permissions_status()
        elif args.perm_command == "deploy":
            perm.run_permissions_deploy(scope=args.scope)
        elif args.perm_command == "analyze":
            perm.run_permissions_analyze()
        elif args.perm_command == "clean":
            perm.run_permissions_clean(scope=args.scope)


if __name__ == "__main__":
    main()
