"""CLI entry for ocd-run refactor.

Subcommands:

    ocd-run refactor rename-symbol --from <old> --to <new> [--scope <path>]
"""

import argparse
import sys
from pathlib import Path

from . import *  # noqa: F401,F403


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="ocd-run refactor",
        description="Agent-callable source transformations — mass renames, moves, pattern rewrites.",
    )
    verbs = parser.add_subparsers(dest="verb", required=True)

    rename = verbs.add_parser(
        "rename-symbol",
        help="AST-aware Python identifier rename across a scope.",
    )
    rename.add_argument(
        "--from",
        dest="old",
        required=True,
        help="Current identifier (module name or module-like name to rewrite).",
    )
    rename.add_argument(
        "--to",
        dest="new",
        required=True,
        help="New identifier to replace `--from` with.",
    )
    rename.add_argument(
        "--scope",
        default=".",
        help="Directory to scan recursively (default: cwd).",
    )

    args = parser.parse_args()

    if args.verb == "rename-symbol":
        return _run_rename_symbol(old=args.old, new=args.new, scope=Path(args.scope))
    return 1


def _run_rename_symbol(old: str, new: str, scope: Path) -> int:
    scope = scope.resolve()
    if not scope.is_dir():
        sys.stderr.write(f"scope is not a directory: {scope}\n")
        return 1

    results = rename_symbol_in_scope(old=old, new=new, scope=scope)
    rewritten = [r for r in results if r.rewritten]
    errors = [r for r in results if r.error]

    for r in rewritten:
        rel = r.file.relative_to(scope)
        print(f"  {rel}: {r.edits} edit{'s' if r.edits != 1 else ''}")
    for r in errors:
        rel = r.file.relative_to(scope)
        sys.stderr.write(f"  {rel}: {r.error}\n")

    print(f"\n{len(rewritten)} file(s) rewritten, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
