"""Plugin CLI.

Agent-facing entry point for init and status operations.
Business logic lives in __init__.py.
"""

import argparse

from . import run_init, run_status


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="plugin",
        description="Plugin infrastructure: init and status operations.",
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

    args = parser.parse_args()

    if args.command == "init":
        run_init(force=args.force)
    elif args.command == "status":
        run_status()


if __name__ == "__main__":
    main()
