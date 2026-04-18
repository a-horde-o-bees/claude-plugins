"""CLI entry for ocd-run tests."""

import argparse
import sys

from . import *  # noqa: F401,F403


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ocd-run tests",
        description="Run project and plugin test suites in the current working directory.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--plugin",
        help="Run only the named plugin's tests",
    )
    group.add_argument(
        "--project",
        action="store_true",
        help="Run only the project-level tests/ suite",
    )

    args = parser.parse_args()
    return run(plugin_filter=args.plugin, project_only=args.project)


if __name__ == "__main__":
    sys.exit(main())
