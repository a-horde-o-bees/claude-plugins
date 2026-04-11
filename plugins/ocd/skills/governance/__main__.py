"""Governance CLI.

Presentation layer — argument parsing and dispatch wrappers only.
Business logic lives in __init__.py facade. The facade guarantees
the governance database is populated before each read or write.
"""

import argparse
import sys

from . import (
    governance_list,
    governance_load,
    governance_match,
    governance_order,
)


DEFAULT_DB = ".claude/ocd/governance/governance.db"


def _dispatch_list(args: argparse.Namespace) -> None:
    entries = governance_list(args.db)
    if not entries:
        print("No governance entries.")
        return
    for entry in entries:
        excludes = f"  excludes: {entry['excludes']}" if entry.get("excludes") else ""
        print(f"{entry['path']}  {entry['includes']}  [{entry['mode']}]{excludes}")


def _dispatch_for(args: argparse.Namespace) -> None:
    result = governance_match(args.db, args.files, include_rules=args.include_rules)
    if not result["matches"]:
        print("No governance matches.")
        return
    print("Conventions:")
    for c in result["conventions"]:
        print(f"  {c}")
    print()
    for file_path in args.files:
        if file_path not in result["matches"]:
            continue
        print(f"{file_path} follows:")
        for c in result["matches"][file_path]:
            print(f"  {c}")


def _dispatch_load(args: argparse.Namespace) -> None:
    result = governance_load(args.db)
    print(f"Loaded {result['governance_entries']} governance entries")


def _dispatch_order(args: argparse.Namespace) -> None:
    result = governance_order(args.db)
    if result["dangling"]:
        print("Dangling governance references — fix frontmatter and re-run:")
        for d in result["dangling"]:
            print(f"  {d['entry_path']} \u2192 {d['missing']} (missing)")
        sys.exit(1)
    for level_idx, level in enumerate(result["levels"]):
        print(f"Level {level_idx}:")
        for entry in level:
            governors = entry["governors"]
            if governors:
                print(f"  {entry['path']}  (governed_by: {', '.join(governors)})")
            else:
                print(f"  {entry['path']}")


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for the governance CLI."""
    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to governance database (default: {DEFAULT_DB})",
    )

    parser = argparse.ArgumentParser(
        prog="governance",
        description=(
            "Governance operations — loading, matching, and ordering rules\n"
            "and conventions from frontmatter. The governance database is\n"
            "self-refreshing: each query reloads changed files from disk\n"
            "before answering.\n"
            "\n"
            "Commands:\n"
            "  load    — reload rules and conventions from disk\n"
            "  list    — list all governance entries\n"
            "  for     — find conventions that govern given files\n"
            "  order   — topologically grouped levels for root-first traversal\n"
            "\n"
            "Typical usage:\n"
            "  governance list                     # browse registered entries\n"
            "  governance for src/app.py           # check what governs a file\n"
            "  governance order                    # levels for chain evaluation"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    commands = parser.add_subparsers(dest="command", required=True)

    load_p = commands.add_parser(
        "load",
        help="Reload rules and conventions from disk frontmatter",
        description=(
            "Scan .claude/rules/ and .claude/conventions/ for files with\n"
            "governance frontmatter. Reloads changed files into the database.\n"
            "Idempotent — skips unchanged files via git_hash comparison."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    load_p.set_defaults(_dispatch=_dispatch_load)

    list_p = commands.add_parser(
        "list",
        help="List all governance entries with patterns and loading mode",
        description=(
            "List registered rules and conventions with include pattern and\n"
            "loading mode (rule = auto-loaded every session, convention =\n"
            "on-demand).\n"
            "\n"
            "Output format:\n"
            "  <path>  <pattern>  [rule|convention]"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    list_p.set_defaults(_dispatch=_dispatch_list)

    for_p = commands.add_parser(
        "for",
        help="Find which governance entries govern given files",
        description=(
            "Match file paths against governance patterns to find which\n"
            "rules and conventions apply.\n"
            "\n"
            "By default returns only conventions — rules are always loaded\n"
            "into agent context. Pass --include-rules to include rules in\n"
            "the matches, useful when rules themselves are the evaluation\n"
            "target.\n"
            "\n"
            "Output format:\n"
            "  Conventions:  (sorted unique list)\n"
            "  <file> follows:  (per-file governance list)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    for_p.add_argument("files", nargs="+", help="File paths to check governance for")
    for_p.add_argument(
        "--include-rules",
        action="store_true",
        default=False,
        help="Include rules in matches (default: conventions only)",
    )
    for_p.set_defaults(_dispatch=_dispatch_for)

    order_p = commands.add_parser(
        "order",
        help="Topologically order governance entries for root-first traversal",
        description=(
            "Group rules and conventions into levels via Tarjan's strongly-\n"
            "connected components algorithm on the governed_by dependency\n"
            "graph. Levels are emitted foundation-first. Files in the same\n"
            "level are mutually independent or mutually dependent (valid\n"
            "siblings).\n"
            "\n"
            "Dangling references — governed_by targets that are not\n"
            "themselves governance entries — are reported and cause a\n"
            "non-zero exit so the caller can fix frontmatter and retry.\n"
            "\n"
            "Output format:\n"
            "  Level N:\n"
            "    <path>  (governed_by: <governor>, ...)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    order_p.set_defaults(_dispatch=_dispatch_order)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "_dispatch"):
        args._dispatch(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
