"""Top-level CLI dispatcher for project-level tooling.

Invoked by `bin/plugins-run <verb> [args...]`. Each verb dispatches into
a submodule under `tools/`; argparse subparsers define the per-verb
argument surface so `bin/plugins-run --help` enumerates the whole
project-level operation catalogue in one place.
"""

import argparse
import sys

from .testing import sandbox_tests_run, test_runner_argparse, tests_run
from .setup import setup_project


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="plugins-run",
        description="Project-level operations for the claude-plugins repo.",
    )
    verbs = parser.add_subparsers(dest="verb", required=True)

    tests = verbs.add_parser("tests", help="Run project and per-plugin test suites in the current tree.")
    test_runner_argparse(tests)

    sandbox = verbs.add_parser(
        "sandbox-tests",
        help="Run tests in a detached git worktree at a given ref.",
    )
    sandbox.add_argument("--ref", default="main", help="Git ref (default: main).")
    scope = sandbox.add_mutually_exclusive_group()
    scope.add_argument("--plugin", help="Run only the named plugin's tests.")
    scope.add_argument(
        "--project",
        action="store_true",
        help="Run only the project-level tests/ suite.",
    )

    verbs.add_parser(
        "setup",
        help="Configure project-local dev settings (git hookspath, etc.).",
    )

    args = parser.parse_args()

    if args.verb == "tests":
        return tests_run(plugin_filter=args.plugin, project_only=args.project)
    if args.verb == "sandbox-tests":
        return sandbox_tests_run(
            ref=args.ref,
            plugin_filter=args.plugin,
            project_only=args.project,
        )
    if args.verb == "setup":
        return setup_project()
    return 1


if __name__ == "__main__":
    sys.exit(main())
