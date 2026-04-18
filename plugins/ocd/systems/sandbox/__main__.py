"""CLI entry for ocd-run sandbox.

Subcommands mirror the verb structure documented in SKILL.md:

    ocd-run sandbox tests [--ref <ref>] [--plugin <name> | --project]
    ocd-run sandbox project setup <path>
    ocd-run sandbox project teardown <path>
    ocd-run sandbox worktree setup <topic>
    ocd-run sandbox worktree teardown <topic>
    ocd-run sandbox cleanup inventory
    ocd-run sandbox cleanup remove [--sibling <path> ...] [--worktree <path> ...]
"""

import argparse
import sys
from pathlib import Path

from . import *  # noqa: F401,F403


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ocd-run sandbox",
        description="Sandbox substrate orchestration for /ocd:sandbox verbs.",
    )
    verbs = parser.add_subparsers(dest="verb", required=True)

    _add_tests_parser(verbs)
    _add_project_parser(verbs)
    _add_worktree_parser(verbs)
    _add_cleanup_parser(verbs)

    args = parser.parse_args()

    if args.verb == "tests":
        return tests_run(
            ref=args.ref,
            plugin_filter=args.plugin,
            project_only=args.project,
        )
    if args.verb == "project":
        return _dispatch_project(args)
    if args.verb == "worktree":
        return _dispatch_worktree(args)
    if args.verb == "cleanup":
        return _dispatch_cleanup(args)
    return 1


def _add_tests_parser(verbs: argparse._SubParsersAction) -> None:
    tests = verbs.add_parser("tests", help="Run the project test suite.")
    tests.add_argument("--ref", default="main", help="Git ref (default: main).")
    scope = tests.add_mutually_exclusive_group()
    scope.add_argument("--plugin", help="Run only the named plugin's tests.")
    scope.add_argument(
        "--project",
        action="store_true",
        help="Run only the project-level tests/ suite.",
    )


def _add_project_parser(verbs: argparse._SubParsersAction) -> None:
    project = verbs.add_parser("project", help="Project substrate lifecycle.")
    phases = project.add_subparsers(dest="phase", required=True)
    ps = phases.add_parser("setup", help="Create the sibling sandbox directory.")
    ps.add_argument("path", help="Absolute or project-relative sandbox path.")
    pt = phases.add_parser("teardown", help="Remove the sibling sandbox directory.")
    pt.add_argument("path", help="Sandbox path previously created by setup.")


def _add_worktree_parser(verbs: argparse._SubParsersAction) -> None:
    worktree = verbs.add_parser("worktree", help="Branched worktree lifecycle.")
    phases = worktree.add_subparsers(dest="phase", required=True)
    ws = phases.add_parser("setup", help="Create the branched worktree.")
    ws.add_argument("topic", help="Kebab-case topic slug.")
    wt = phases.add_parser("teardown", help="Remove worktree, branch, pushurl block.")
    wt.add_argument("topic", help="Topic slug previously used by setup.")


def _add_cleanup_parser(verbs: argparse._SubParsersAction) -> None:
    cleanup = verbs.add_parser("cleanup", help="Inventory or remove sandbox artifacts.")
    phases = cleanup.add_subparsers(dest="phase", required=True)
    phases.add_parser(
        "inventory",
        help="Emit JSON listing sibling projects and non-main worktrees.",
    )
    cr = phases.add_parser(
        "remove",
        help="Remove named siblings and worktrees (pre-filtered by the skill).",
    )
    cr.add_argument(
        "--sibling",
        action="append",
        default=[],
        help="Sibling sandbox path to remove (repeatable).",
    )
    cr.add_argument(
        "--worktree",
        action="append",
        default=[],
        help="Worktree path to remove (repeatable).",
    )


def _dispatch_project(args: argparse.Namespace) -> int:
    path = Path(args.path)
    if args.phase == "setup":
        resolved = project_setup(path)
        sys.stdout.write(f"{resolved}\n")
    elif args.phase == "teardown":
        project_teardown(path)
    return 0


def _dispatch_worktree(args: argparse.Namespace) -> int:
    if args.phase == "setup":
        resolved = worktree_setup(args.topic)
        sys.stdout.write(f"{resolved}\n")
    elif args.phase == "teardown":
        worktree_teardown(args.topic)
    return 0


def _dispatch_cleanup(args: argparse.Namespace) -> int:
    if args.phase == "inventory":
        cleanup_print_inventory_json()
    elif args.phase == "remove":
        cleanup_remove(
            [Path(p) for p in args.sibling],
            [Path(p) for p in args.worktree],
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
