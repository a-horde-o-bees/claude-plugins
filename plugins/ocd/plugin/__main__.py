"""Plugin CLI.

Agent-facing entry point for install, list, and permissions operations.
Business logic lives in __init__.py.
"""

import argparse
import importlib

from . import run_install, run_list


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="plugin",
        description="Plugin infrastructure: install, list, and permissions operations.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    install_p = commands.add_parser(
        "install",
        help="Deploy every lib subsystem — rules, conventions, patterns, logs, navigator",
    )
    install_p.add_argument(
        "--force", action="store_true",
        help="Overwrite existing state with plugin defaults; destructive",
    )
    install_p.add_argument(
        "--system", default=None,
        help="Scope install to one lib subsystem (rules, conventions, navigator, ...)",
    )

    list_p = commands.add_parser(
        "list",
        help="Report plugin version and state of every lib subsystem",
    )
    list_p.add_argument(
        "--system", default=None,
        help="Scope list to one lib subsystem (rules, conventions, navigator, ...)",
    )

    perm_p = commands.add_parser(
        "permissions",
        help="Manage recommended auto-approve permission patterns",
    )
    perm_commands = perm_p.add_subparsers(dest="perm_command", required=True)

    perm_commands.add_parser(
        "list",
        help="Structured report of both scopes' permission state",
    )

    install_perm_p = perm_commands.add_parser(
        "install",
        help="Deploy recommended patterns to one scope",
    )
    install_perm_p.add_argument(
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

    if args.command == "install":
        run_install(force=args.force, system=args.system)
    elif args.command == "list":
        run_list(system=args.system)
    elif args.command == "permissions":
        # Runtime import — permissions lives in lib/, discovered via sys.path
        # established by run.py. importlib keeps this consistent with how
        # orchestration dispatches to lib/<subsystem>/_init.py.
        perm = importlib.import_module("lib.permissions")
        if args.perm_command == "list":
            perm.run_permissions_list()
        elif args.perm_command == "install":
            perm.run_permissions_install(scope=args.scope)
        elif args.perm_command == "analyze":
            perm.run_permissions_analyze()
        elif args.perm_command == "clean":
            perm.run_permissions_clean(scope=args.scope)


if __name__ == "__main__":
    main()
