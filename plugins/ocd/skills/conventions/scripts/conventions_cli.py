"""Conventions CLI.

Presentation layer: argument parsing and dispatch wrappers only.
Business logic lives in conventions.py.
"""

import argparse
import os
from pathlib import Path

# Support both package import and direct execution
try:
    from . import conventions
except ImportError:
    import conventions  # type: ignore[import-not-found]


DEFAULT_CONVENTIONS_DIR = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
    ".claude", "ocd", "conventions",
)

DEFAULT_RULES_DIR = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
    ".claude", "rules",
)

DEFAULT_CACHE_DB = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
    ".claude", "ocd", "cache.db",
)


def _dispatch_get(args: argparse.Namespace) -> None:
    conventions_dir = args.conventions_dir or DEFAULT_CONVENTIONS_DIR
    rules_dir = args.rules_dir or DEFAULT_RULES_DIR
    cache_db = args.cache_db or DEFAULT_CACHE_DB

    rules = conventions.collect_rules(rules_dir)
    matched = conventions.match_conventions(conventions_dir, cache_db, args.files)

    all_paths = rules + matched
    if not all_paths:
        print(f"No criteria match: {', '.join(args.files)}")
        return

    for path in all_paths:
        print(path)


def _dispatch_list(args: argparse.Namespace) -> None:
    conventions_dir = args.conventions_dir or DEFAULT_CONVENTIONS_DIR
    cache_db = args.cache_db or DEFAULT_CACHE_DB

    patterns = conventions.sync_patterns(cache_db, conventions_dir)

    if not patterns:
        print("No conventions found.")
        return

    for path, pattern in sorted(patterns.items(), key=lambda x: Path(x[0]).name):
        name = Path(path).name
        print(f"{name}  {pattern}")


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--conventions-dir",
        default=None,
        help="Path to conventions directory (default: .claude/ocd/conventions/)",
    )
    parser.add_argument(
        "--rules-dir",
        default=None,
        help="Path to rules directory (default: .claude/rules/)",
    )
    parser.add_argument(
        "--cache-db",
        default=None,
        help="Path to cache database (default: .claude/ocd/cache.db)",
    )


def _add_subcommands(commands: argparse._SubParsersAction) -> None:
    get_p = commands.add_parser(
        "get",
        help=(
            "Return file paths for all rules and conventions matching given file paths. "
            "Rules (.claude/rules/ocd-*.md) are always included. "
            "Conventions are pattern-matched against input file paths. "
            "Output is one file path per line. Empty result means no criteria apply."
        ),
    )
    get_p.add_argument(
        "files",
        nargs="+",
        help="File paths to match against convention patterns",
    )
    get_p.set_defaults(_dispatch=_dispatch_get)

    list_p = commands.add_parser(
        "list",
        help=(
            "Show all available conventions and their match patterns. "
            "Output is one line per convention: filename followed by pattern."
        ),
    )
    list_p.set_defaults(_dispatch=_dispatch_list)


def register_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "convention",
        help="Discover rules and conventions applicable to target file paths",
    )
    _add_common_args(parser)

    commands = parser.add_subparsers(dest="command")
    commands.required = True
    _add_subcommands(commands)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover rules and conventions applicable to target file paths.",
    )
    _add_common_args(parser)

    commands = parser.add_subparsers(dest="command")
    commands.required = True
    _add_subcommands(commands)

    args = parser.parse_args()
    args._dispatch(args)


if __name__ == "__main__":
    main()
