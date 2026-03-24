"""Conventions CLI.

Presentation layer: argument parsing and dispatch wrappers only.
Business logic lives in conventions.py.
"""

import argparse
import os
import sys
from pathlib import Path

# Support both package import and direct execution
try:
    from . import conventions
except ImportError:
    import conventions  # type: ignore[import-not-found]


_PROJECT_DIR = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))

DEFAULT_MANIFEST = _PROJECT_DIR / ".claude" / "ocd" / "conventions" / "manifest.yaml"


def _dispatch_list_patterns(args: argparse.Namespace) -> None:
    manifest = Path(args.manifest) if args.manifest else DEFAULT_MANIFEST

    try:
        patterns = conventions.list_patterns(manifest)
    except FileNotFoundError:
        print("Error: manifest.yaml not found. Run /ocd-init to deploy.", file=sys.stderr)
        sys.exit(1)

    if not patterns:
        print("No conventions found.")
        return

    for path, pattern in patterns:
        print(f"{path}  {pattern}")


def _dispatch_list_matching(args: argparse.Namespace) -> None:
    manifest = Path(args.manifest) if args.manifest else DEFAULT_MANIFEST

    try:
        matches = conventions.list_matching(manifest, args.files)
    except FileNotFoundError:
        print("Error: manifest.yaml not found. Run /ocd-init to deploy.", file=sys.stderr)
        sys.exit(1)

    if not matches:
        print(f"No criteria match: {', '.join(args.files)}")
        return

    for file_path, conv_paths in sorted(matches.items()):
        print(f"{file_path} follows:")
        for conv_path in conv_paths:
            print(f"  {conv_path}")


def _dispatch_list_self(args: argparse.Namespace) -> None:
    manifest = Path(args.manifest) if args.manifest else DEFAULT_MANIFEST

    try:
        levels = conventions.topological_order(manifest)
    except FileNotFoundError:
        print("Error: manifest.yaml not found. Run /ocd-init to deploy.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    for i, level in enumerate(levels):
        print(f"Level {i}:")
        for path in level:
            print(f"  {path}")


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to manifest.yaml (default: .claude/ocd/conventions/manifest.yaml)",
    )


def _add_subcommands(commands: argparse._SubParsersAction) -> None:
    lp_p = commands.add_parser(
        "list-patterns",
        help=(
            "Show all conventions with their match patterns. "
            "Output is one line per convention: relative path followed by pattern."
        ),
    )
    lp_p.set_defaults(_dispatch=_dispatch_list_patterns)

    lm_p = commands.add_parser(
        "list-matching",
        help=(
            "Return conventions matching given file paths, grouped by target file. "
            "Output groups: target file followed by indented convention paths. "
            "Empty result means no criteria apply."
        ),
    )
    lm_p.add_argument(
        "files",
        nargs="+",
        help="File paths to match against convention patterns",
    )
    lm_p.set_defaults(_dispatch=_dispatch_list_matching)

    ls_p = commands.add_parser(
        "list-self",
        help=(
            "Topologically sort conventions by dependency order for self-evaluation. "
            "Level 0 has no dependencies (roots), Level 1 depends only on Level 0, etc. "
            "Files within same level are independent. Detects and reports cycles."
        ),
    )
    ls_p.set_defaults(_dispatch=_dispatch_list_self)


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
        description="Manage convention patterns, matching, and dependency ordering.",
    )
    _add_common_args(parser)

    commands = parser.add_subparsers(dest="command")
    commands.required = True
    _add_subcommands(commands)

    args = parser.parse_args()
    args._dispatch(args)


if __name__ == "__main__":
    main()
