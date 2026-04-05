"""Plugin CLI.

Agent-facing entry point for init, status, and permissions operations.
Business logic lives in __init__.py.
"""

import argparse

from . import (
    run_init,
    run_permissions_analyze,
    run_permissions_clean,
    run_permissions_deploy,
    run_permissions_report,
    run_status,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="plugin",
        description="Plugin infrastructure: init, status, and permissions operations.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    init_p = commands.add_parser(
        "init",
        help="Deploy rules and initialize skill infrastructure",
    )
    init_p.add_argument(
        "--force", action="store_true",
        help="Overwrite existing rules and conventions with plugin defaults",
    )

    commands.add_parser(
        "status",
        help="Report plugin version, rules state, and skill infrastructure status",
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

    if args.command == "init":
        run_init(force=args.force)
    elif args.command == "status":
        run_status()
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
