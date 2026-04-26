"""Log CLI dispatch.

Presentation layer for `ocd-run log <subcommand>`. Runtime analytical
logic lives in the `research` subpackage. The legacy add/list/remove
verbs remain skill-level workflow fragments (`_add.md`, `_list.md`,
`_remove.md`) — they're context-only operations and don't need Python
runtime code.

Adding a subcommand: register a new argparse subparser in
`build_parser` and set `_dispatch` on it. `_dispatch` handlers return
an int exit code (0 pass, 1 fail) — no manual `sys.exit` calls inside
dispatchers, so composition remains straightforward.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .research._sample_tools import (
    DuplicateHeadingError,
    check_no_duplicate_headings,
    consolidate_section,
    count_sections,
)


def _resolve_samples_dir(args: argparse.Namespace) -> Path:
    """Resolve `--subject NAME` or `--dir PATH` to an absolute samples directory.

    Exactly one of the two is required (enforced by the mutually
    exclusive group), so one branch always fires. `--subject` maps to
    the project-local convention `logs/research/<name>/samples/`.
    """
    if getattr(args, "subject", None):
        return (Path.cwd() / "logs" / "research" / args.subject / "samples").resolve()
    return Path(args.dir).resolve()


def _dispatch_research_check(args: argparse.Namespace) -> int:
    """Run duplicate-heading check on a single markdown file."""
    path = Path(args.path).resolve()
    if not path.is_file():
        print(f"File not found: {path}", file=sys.stderr)
        return 1
    try:
        check_no_duplicate_headings(path)
    except DuplicateHeadingError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"OK — no sibling-duplicate headings in {path}")
    return 0


def _dispatch_research_count_sections(args: argparse.Namespace) -> int:
    """Print per-chain-key coverage across a samples directory."""
    samples_dir = _resolve_samples_dir(args)
    if not samples_dir.is_dir():
        print(f"Samples directory not found: {samples_dir}", file=sys.stderr)
        return 1
    counts = count_sections(samples_dir)
    if not counts:
        print(f"No sections found in {samples_dir}")
        return 0
    total_samples = len(
        [p for p in samples_dir.glob("*.md") if not p.name.startswith("_")]
    )
    # Sort by coverage descending, then chain key ascending — highest-
    # coverage sections first, with stable alphabetical tie-break.
    sorted_items = sorted(counts.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    max_key_len = max(len(k) for k, _ in sorted_items)
    print(f"{'chain_key'.ljust(max_key_len)}  count  coverage")
    for chain_key, files in sorted_items:
        pct = len(files) / total_samples * 100 if total_samples else 0
        print(f"{chain_key.ljust(max_key_len)}  {len(files):5d}  {pct:5.1f}%")
    return 0


def _dispatch_research_consolidate(args: argparse.Namespace) -> int:
    """Print serialized section content from every sample containing the chain."""
    samples_dir = _resolve_samples_dir(args)
    if not samples_dir.is_dir():
        print(f"Samples directory not found: {samples_dir}", file=sys.stderr)
        return 1
    results = consolidate_section(args.chain, samples_dir)
    if not results:
        print(f"No samples contain chain key {args.chain!r}")
        return 0
    for path, content in results:
        print(f"=== {path} ===")
        print(content)
        print()
    return 0


def _add_samples_location_args(p: argparse.ArgumentParser) -> None:
    """Attach `--subject NAME` / `--dir PATH` as a mutually exclusive group.

    Factored because both `count-sections` and `consolidate` need the
    same locator; keeping the argument surface identical avoids users
    learning two dialects for the same concept.
    """
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--subject",
        help="Research subject name — resolves to CWD/logs/research/<name>/samples/",
    )
    group.add_argument(
        "--dir",
        help="Explicit path to a samples directory",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="log",
        description=(
            "Log system CLI — research corpus analysis.\n"
            "\n"
            "Subcommand groups:\n"
            "  research   Analyze markdown samples under logs/research/<subject>/samples/\n"
            "\n"
            "Legacy verbs (add/list/remove) remain as skill-level workflow fragments\n"
            "dispatched by the /log skill; they are not reachable via this CLI."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    research = sub.add_parser(
        "research",
        help="Analyze research corpora under logs/research/<subject>/samples/",
        description=(
            "Research corpus analysis.\n"
            "\n"
            "Verbs:\n"
            "  check           Verify a markdown file has no sibling-duplicate headings\n"
            "  count-sections  Print chain-key coverage across a samples directory\n"
            "  consolidate     Print per-sample content under a given chain key\n"
            "\n"
            "Samples-directory locators (count-sections, consolidate):\n"
            "  --subject <name>    CWD/logs/research/<name>/samples/\n"
            "  --dir <path>        Explicit directory path\n"
            "\n"
            "Usage:\n"
            "  log research check <path>\n"
            "  log research count-sections --subject <name>\n"
            "  log research count-sections --dir <path>\n"
            "  log research consolidate --chain <key> --subject <name>\n"
            "  log research consolidate --chain <key> --dir <path>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    rsub = research.add_subparsers(dest="verb", required=True)

    r_check = rsub.add_parser(
        "check",
        help="Verify no sibling-duplicate headings in a markdown file",
    )
    r_check.add_argument("path", help="Path to markdown file")
    r_check.set_defaults(_dispatch=_dispatch_research_check)

    r_count = rsub.add_parser(
        "count-sections",
        help="Print chain-key coverage across a samples directory",
    )
    _add_samples_location_args(r_count)
    r_count.set_defaults(_dispatch=_dispatch_research_count_sections)

    r_consolidate = rsub.add_parser(
        "consolidate",
        help="Print per-sample content under a chain key",
    )
    _add_samples_location_args(r_consolidate)
    r_consolidate.add_argument(
        "--chain",
        required=True,
        help="Chain key like 'Transport > Configuration' (` > ` separator)",
    )
    r_consolidate.set_defaults(_dispatch=_dispatch_research_consolidate)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "_dispatch"):
        sys.exit(args._dispatch(args))
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
