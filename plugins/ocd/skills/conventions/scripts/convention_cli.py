"""Convention CLI.

Presentation layer: argument parsing and dispatch wrappers only.
Business logic lives in convention.py.
"""

import argparse
import os
from pathlib import Path

# Support both package import and direct execution
try:
    from . import convention
except ImportError:
    import convention  # type: ignore[import-not-found]


DEFAULT_CONVENTIONS_DIR = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
    ".claude", "ocd", "conventions",
)

DEFAULT_CACHE_DB = os.path.join(
    os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()),
    ".claude", "ocd", "cache.db",
)


def _dispatch_get(args: argparse.Namespace) -> None:
    conventions_dir = args.conventions_dir or DEFAULT_CONVENTIONS_DIR
    cache_db = args.cache_db or DEFAULT_CACHE_DB

    matched = convention.match_conventions(conventions_dir, cache_db, args.files)

    if not matched:
        print(f"No conventions match: {', '.join(args.files)}")
        return

    print(convention.get_convention_content(matched))


def _dispatch_list(args: argparse.Namespace) -> None:
    conventions_dir = args.conventions_dir or DEFAULT_CONVENTIONS_DIR
    cache_db = args.cache_db or DEFAULT_CACHE_DB

    patterns = convention.sync_patterns(cache_db, conventions_dir)

    if not patterns:
        print("No conventions found.")
        return

    for path, pattern in sorted(patterns.items(), key=lambda x: Path(x[0]).name):
        name = Path(path).name
        print(f"{name}  {pattern}")


def register_commands(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "convention",
        help="Match file paths against convention patterns and return applicable conventions",
    )
    parser.add_argument(
        "--conventions-dir",
        default=None,
        help=f"Path to conventions directory (default: .claude/ocd/conventions/)",
    )
    parser.add_argument(
        "--cache-db",
        default=None,
        help=f"Path to cache database (default: .claude/ocd/cache.db)",
    )

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    get_p = commands.add_parser(
        "get",
        help=(
            "Return content of all conventions matching the given file paths. "
            "Call before creating or modifying files to load applicable conventions. "
            "Output is delimited sections: === filename.md === followed by content. "
            "Empty result means no conventions apply."
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


def main():
    parser = argparse.ArgumentParser(
        description="Match file paths against convention patterns and return applicable conventions.",
    )
    parser.add_argument(
        "--conventions-dir",
        default=None,
        help=f"Path to conventions directory (default: .claude/ocd/conventions/)",
    )
    parser.add_argument(
        "--cache-db",
        default=None,
        help=f"Path to cache database (default: .claude/ocd/cache.db)",
    )

    commands = parser.add_subparsers(dest="command")
    commands.required = True

    get_p = commands.add_parser(
        "get",
        help="Return content of all conventions matching the given file paths.",
    )
    get_p.add_argument(
        "files",
        nargs="+",
        help="File paths to match against convention patterns",
    )
    get_p.set_defaults(_dispatch=_dispatch_get)

    list_p = commands.add_parser(
        "list",
        help="Show all available conventions and their match patterns.",
    )
    list_p.set_defaults(_dispatch=_dispatch_list)

    args = parser.parse_args()
    args._dispatch(args)


if __name__ == "__main__":
    main()
