"""Plugin CLI.

Agent-facing entry point for install, list, and permissions operations.
Business logic lives in __init__.py.
"""

import argparse

from . import (
    run_install,
    run_list,
    run_permissions_analyze,
    run_permissions_clean,
    run_permissions_deploy,
    run_permissions_report,
)


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
        "report",
        help="Structured report of both scopes' permission state",
    )

    deploy_p = perm_commands.add_parser(
        "deploy",
        help="Deploy recommended patterns to one scope",
    )
    deploy_p.add_argument(
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
        if args.perm_command == "report":
            run_permissions_report()
        elif args.perm_command == "deploy":
            run_permissions_deploy(scope=args.scope)
        elif args.perm_command == "analyze":
            run_permissions_analyze()
        elif args.perm_command == "clean":
            run_permissions_clean(scope=args.scope)


if __name__ == "__main__":
    main()
