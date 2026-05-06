"""Conventions CLI.

Presentation layer — argument parsing and dispatch wrappers only.
Business logic lives in __init__.py facade. Functions read directly
from disk on every call.
"""

import argparse
import sys

from . import (
    governance_list,
    governance_match,
)


def _dispatch_list(args: argparse.Namespace) -> None:
    del args  # no arguments used
    entries = governance_list()
    if not entries:
        print("No governance entries.")
        return
    for entry in entries:
        excludes = f"  excludes: {entry['excludes']}" if entry.get("excludes") else ""
        print(f"{entry['path']}  {entry['includes']}  [{entry['mode']}]{excludes}")


def _dispatch_for(args: argparse.Namespace) -> None:
    result = governance_match(args.files, include_rules=args.include_rules)
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


def build_parser() -> argparse.ArgumentParser:
    """Build argument parser for the governance CLI."""
    parser = argparse.ArgumentParser(
        prog="conventions",
        description=(
            "Convention operations — matching rules and conventions from\n"
            "frontmatter. Reads directly from disk.\n"
            "\n"
            "Commands:\n"
            "  list    — list all governance entries\n"
            "  for     — find conventions that govern given files\n"
            "\n"
            "Typical usage:\n"
            "  conventions list                     # browse registered entries\n"
            "  conventions for src/app.py           # check what governs a file"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    commands = parser.add_subparsers(dest="command", required=True)

    list_p = commands.add_parser(
        "list",
        help="List all governance entries with patterns and loading mode",
        description=(
            "List rules and conventions with include pattern and loading\n"
            "mode (rule = auto-loaded every session, convention = on-demand).\n"
            "\n"
            "Output format:\n"
            "  <path>  <pattern>  [rule|convention]"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
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
    )
    for_p.add_argument("files", nargs="+", help="File paths to check governance for")
    for_p.add_argument(
        "--include-rules",
        action="store_true",
        default=False,
        help="Include rules in matches (default: conventions only)",
    )
    for_p.set_defaults(_dispatch=_dispatch_for)

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
