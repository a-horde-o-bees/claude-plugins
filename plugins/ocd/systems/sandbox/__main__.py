"""CLI entry for ocd-run sandbox.

Subcommands mirror the verb structure documented in SKILL.md:

    ocd-run sandbox project setup <path>
    ocd-run sandbox project teardown <path>
    ocd-run sandbox worktree setup <topic>
    ocd-run sandbox worktree teardown <topic>
    ocd-run sandbox worktree-add <name> --branch <branch> [--base-ref <ref>]
                                         [--block-push]
    ocd-run sandbox worktree-remove <name> [--delete-branch] [--unblock-push]
    ocd-run sandbox worktree-status <name>
    ocd-run sandbox worktree-list
    ocd-run sandbox sibling-path <name>
    ocd-run sandbox cleanup inventory
    ocd-run sandbox cleanup remove [--sibling <path> ...] [--worktree <path> ...]

The `tests` verb moved to `bin/project-run sandbox-tests` — it depends
on project-level test infrastructure and is not a plugin concern.
"""

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from . import *  # noqa: F401,F403


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ocd-run sandbox",
        description="Sandbox substrate orchestration for /ocd:sandbox verbs.",
    )
    verbs = parser.add_subparsers(dest="verb", required=True)

    _add_project_parser(verbs)
    _add_worktree_parser(verbs)
    _add_durable_parsers(verbs)
    _add_cleanup_parser(verbs)

    args = parser.parse_args()

    if args.verb == "project":
        return _dispatch_project(args)
    if args.verb == "worktree":
        return _dispatch_worktree(args)
    if args.verb == "worktree-add":
        return _dispatch_worktree_add(args)
    if args.verb == "worktree-remove":
        return _dispatch_worktree_remove(args)
    if args.verb == "worktree-status":
        return _dispatch_worktree_status(args)
    if args.verb == "worktree-list":
        return _dispatch_worktree_list()
    if args.verb == "sibling-path":
        return _dispatch_sibling_path(args)
    if args.verb == "cleanup":
        return _dispatch_cleanup(args)
    return 1


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


def _add_durable_parsers(verbs: argparse._SubParsersAction) -> None:
    add = verbs.add_parser(
        "worktree-add",
        help="Create a sibling worktree on a branch (durable feature boxes).",
    )
    add.add_argument("name", help="Sibling name — used for <project>--<name>.")
    add.add_argument("--branch", required=True, help="Branch to create or attach to.")
    add.add_argument(
        "--base-ref",
        default=None,
        help="Base ref for new branch; omit to attach to existing branch.",
    )
    add.add_argument(
        "--block-push",
        action="store_true",
        help="Set an invalid pushurl on origin during the worktree's life.",
    )

    remove = verbs.add_parser(
        "worktree-remove",
        help="Remove a sibling worktree; optionally delete its branch.",
    )
    remove.add_argument("name", help="Sibling name to remove.")
    remove.add_argument(
        "--delete-branch",
        action="store_true",
        help="Delete the worktree's branch after removal.",
    )
    remove.add_argument(
        "--unblock-push",
        action="store_true",
        help="Clear the invalid pushurl previously set by --block-push.",
    )

    status = verbs.add_parser(
        "worktree-status",
        help="Emit JSON status for a named sibling worktree.",
    )
    status.add_argument("name", help="Sibling name to inspect.")

    verbs.add_parser(
        "worktree-list",
        help="Emit JSON array of every non-main worktree on the project.",
    )

    sp = verbs.add_parser(
        "sibling-path",
        help="Print the resolved sibling path for a name.",
    )
    sp.add_argument("name", help="Sibling name.")


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


def _dispatch_worktree_add(args: argparse.Namespace) -> int:
    path = worktree_add(
        args.name,
        args.branch,
        base_ref=args.base_ref,
        block_push=args.block_push,
    )
    sys.stdout.write(f"{path}\n")
    return 0


def _dispatch_worktree_remove(args: argparse.Namespace) -> int:
    worktree_remove(
        args.name,
        delete_branch=args.delete_branch,
        unblock_push=args.unblock_push,
    )
    return 0


def _dispatch_worktree_status(args: argparse.Namespace) -> int:
    status = worktree_status(args.name)
    payload = asdict(status)
    payload["path"] = str(payload["path"])
    sys.stdout.write(json.dumps(payload, indent=2))
    sys.stdout.write("\n")
    return 0


def _dispatch_worktree_list() -> int:
    entries = worktree_list()
    payload = [asdict(e) for e in entries]
    for entry in payload:
        entry["path"] = str(entry["path"])
    sys.stdout.write(json.dumps(payload, indent=2))
    sys.stdout.write("\n")
    return 0


def _dispatch_sibling_path(args: argparse.Namespace) -> int:
    sys.stdout.write(f"{sibling_path(args.name)}\n")
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
