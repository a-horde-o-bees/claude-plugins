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

from tools import environment

from .research._diff import diff_summary
from .research._quantify import find_branch_points, render_table, write_tables
from .research._sample_tools import (
    DuplicateHeadingError,
    check_no_duplicate_headings,
    consolidate_section,
    consolidate_section_size,
    count_sections,
    section_sizes,
)


class _SubtopicResolutionError(Exception):
    """Raised when `--subject` cannot resolve to a single `<subtopic>-samples/`."""


def _resolve_samples_dir(args: argparse.Namespace) -> Path:
    """Resolve `--subject NAME [--subtopic NAME]` or `--dir PATH` to an absolute samples directory.

    `--subject` looks under `<project>/logs/research/<name>/` for one or
    more `<subtopic>-samples/` directories. Single-match auto-resolves;
    multi-match requires `--subtopic` to disambiguate; zero matches
    raises with a corrective message. `--dir` is the explicit-path
    escape hatch (no discovery).
    """
    if getattr(args, "dir", None):
        path = Path(args.dir).resolve()
        if not path.is_dir():
            raise _SubtopicResolutionError(f"Directory not found: {path}")
        return path

    project_dir = environment.get_project_dir()
    subject_dir = (project_dir / "logs" / "research" / args.subject).resolve()
    if not subject_dir.is_dir():
        raise _SubtopicResolutionError(
            f"Subject directory not found: {subject_dir}"
        )

    candidates = sorted(p for p in subject_dir.glob("*-samples") if p.is_dir())
    if not candidates:
        raise _SubtopicResolutionError(
            f"No <subtopic>-samples/ directory under {subject_dir} — "
            f"subject may not be migrated to the current research structure"
        )

    requested = getattr(args, "subtopic", None)
    if requested:
        target = subject_dir / f"{requested}-samples"
        if not target.is_dir():
            available = ", ".join(c.name.removesuffix("-samples") for c in candidates)
            raise _SubtopicResolutionError(
                f"Subtopic {requested!r} not found in {subject_dir}; "
                f"available: {available}"
            )
        return target

    if len(candidates) == 1:
        return candidates[0]

    available = ", ".join(c.name.removesuffix("-samples") for c in candidates)
    raise _SubtopicResolutionError(
        f"Multiple subtopics under {subject_dir}; "
        f"pass --subtopic <name> (one of: {available})"
    )


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


def _dispatch_research_sections(args: argparse.Namespace) -> int:
    """Print the chain-key tree across a samples directory.

    Bare invocation prints chain keys alphabetically. `--count` adds
    adoption count and coverage columns and switches sort to coverage-
    descending. `--size` adds a byte-count column. Flags compose; the
    columns appear left-to-right in fixed order (count, coverage, size).
    """
    samples_dir = _resolve_samples_dir(args)
    counts = count_sections(samples_dir)
    if not counts:
        print(f"No sections found in {samples_dir}")
        return 0

    sizes = section_sizes(samples_dir) if args.size else {}
    total_samples = len(
        [p for p in samples_dir.glob("*.md") if not p.name.startswith("_")]
    )

    # Sort by coverage-desc when --count drives the table; alphabetical
    # otherwise (the bare tree and --size-only views read top-to-bottom
    # without count weight).
    if args.count:
        sorted_keys = sorted(counts.keys(), key=lambda k: (-len(counts[k]), k))
    else:
        sorted_keys = sorted(counts.keys())

    max_key_len = max(len(k) for k in sorted_keys)

    header_parts = ["chain_key".ljust(max_key_len)]
    if args.count:
        header_parts.extend(["count", "coverage"])
    if args.size:
        header_parts.append("size")
    if args.count or args.size:
        print("  ".join(header_parts))

    for chain_key in sorted_keys:
        row = [chain_key.ljust(max_key_len)]
        if args.count:
            file_count = len(counts[chain_key])
            pct = file_count / total_samples * 100 if total_samples else 0
            row.append(f"{file_count:5d}")
            row.append(f"{pct:5.1f}%")
        if args.size:
            row.append(f"{sizes.get(chain_key, 0):8d}")
        print("  ".join(row))

    return 0


def _dispatch_research_references(args: argparse.Namespace) -> int:
    """List sample files containing a section at the given chain key.

    Default — print filenames, one per line. Flags compose:

    - `--count` — print just the integer count of matching files
    - `--size` — print the total UTF-8 byte count of section bodies under
      the chain across all samples (companion behavior so agents can
      budget cost before consuming)
    - `--show-content` — include each matching file's section body inline,
      separated by `=== <filename> ===` markers
    """
    samples_dir = _resolve_samples_dir(args)

    if args.size:
        print(consolidate_section_size(args.chain, samples_dir))
        return 0

    results = consolidate_section(args.chain, samples_dir)

    if args.count:
        print(len(results))
        return 0

    if not results:
        print(f"No samples contain chain key {args.chain!r}", file=sys.stderr)
        return 0

    if args.show_content:
        for path, content in results:
            print(f"=== {path.name} ===")
            print(content)
            print()
    else:
        for path, _ in results:
            print(path.name)

    return 0


def _resolve_consolidated_path(samples_dir: Path, override: str | None) -> Path:
    """Find a `_CONSOLIDATED*.md` in samples_dir, or accept an explicit override.

    Single-match auto-resolves; multi-match raises with available names;
    no match raises with corrective guidance.
    """
    if override:
        path = Path(override).resolve()
        if not path.is_file():
            raise _SubtopicResolutionError(f"Consolidated file not found: {path}")
        return path

    matches = sorted(samples_dir.glob("_CONSOLIDATED*.md"))
    if not matches:
        raise _SubtopicResolutionError(
            f"No `_CONSOLIDATED*.md` found in {samples_dir} — "
            f"pass --consolidated <path> or initialize one"
        )
    if len(matches) > 1:
        names = ", ".join(m.name for m in matches)
        raise _SubtopicResolutionError(
            f"Multiple `_CONSOLIDATED*.md` files in {samples_dir}: {names}; "
            f"pass --consolidated <path> to disambiguate"
        )
    return matches[0]


def _dispatch_research_diff(args: argparse.Namespace) -> int:
    """Diff sample heading trees against the running consolidated.

    Reports growth candidates (chains in samples not yet in
    consolidated — corpus signals tree should grow), pruning candidates
    (chains in consolidated with no sample support), and well-supported
    chains (in both).
    """
    samples_dir = _resolve_samples_dir(args)
    consolidated_path = _resolve_consolidated_path(samples_dir, args.consolidated)

    summary = diff_summary(samples_dir, consolidated_path)

    print(f"Samples: {summary.sample_count}")
    print(f"Consolidated: {consolidated_path}")
    print(f"Chain keys in consolidated: {len(summary.consolidated_chains)}")
    print(f"Chain keys in samples (union): {len(summary.chain_to_files)}")
    print(f"Well-supported (in both): {len(summary.well_supported)}")
    print(f"Growth candidates (in samples, not consolidated): {len(summary.growth_candidates)}")
    print(f"Pruning candidates (in consolidated, not samples): {len(summary.pruning_candidates)}")
    print()

    cap = None if args.show_all else 50

    if summary.growth_candidates:
        print("Growth candidates — chain keys in samples not yet in consolidated:")
        sorted_growth = sorted(summary.growth_candidates.items(), key=lambda kv: -len(kv[1]))
        shown = sorted_growth if cap is None else sorted_growth[:cap]
        for chain_key, files in shown:
            print(f"  {len(files):3d}  {chain_key}")
        if cap is not None and len(sorted_growth) > cap:
            print(f"  ...({len(sorted_growth) - cap} more — pass --show-all)")
        print()

    if summary.pruning_candidates:
        print("Pruning candidates — consolidated chain keys with no sample support:")
        shown_prune = summary.pruning_candidates if cap is None else summary.pruning_candidates[:cap]
        for chain_key in shown_prune:
            print(f"  {chain_key}")
        if cap is not None and len(summary.pruning_candidates) > cap:
            print(f"  ...({len(summary.pruning_candidates) - cap} more — pass --show-all)")

    return 0


def _dispatch_research_quantify(args: argparse.Namespace) -> int:
    """Compute adoption tables for branching points in the consolidated.

    Default — print rendered tables to stdout. `--write` inserts (or
    replaces) tables in the consolidated in place, using sentinel
    comments so the operation is idempotent.
    """
    samples_dir = _resolve_samples_dir(args)
    consolidated_path = _resolve_consolidated_path(samples_dir, args.consolidated)

    if args.write:
        written = write_tables(consolidated_path, samples_dir)
        print(f"Wrote {written} adoption table(s) into {consolidated_path}")
        return 0

    branch_points = find_branch_points(consolidated_path, samples_dir)
    if not branch_points:
        print(f"No branching points found in {consolidated_path}")
        return 0

    for bp in branch_points:
        print(f"### {bp.parent_chain}")
        print()
        print(render_table(bp))

    return 0


def _add_samples_location_args(p: argparse.ArgumentParser) -> None:
    """Attach `--subject NAME [--subtopic NAME]` / `--dir PATH` argument surface.

    `--subject` and `--dir` are mutually exclusive; one is required.
    `--subtopic` is optional and only meaningful with `--subject` —
    selects one `<subtopic>-samples/` folder when the subject has more
    than one. Single-subtopic subjects auto-resolve.
    """
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--subject",
        help="Research subject name — resolves to <project>/logs/research/<name>/<subtopic>-samples/",
    )
    group.add_argument(
        "--dir",
        help="Explicit path to a samples directory",
    )
    p.add_argument(
        "--subtopic",
        help="Subtopic name when --subject has multiple <subtopic>-samples/ folders",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="log",
        description=(
            "Log system CLI — research corpus analysis.\n"
            "\n"
            "Subcommand groups:\n"
            "  research   Analyze markdown samples under logs/research/<subject>/<subtopic>-samples/\n"
            "\n"
            "Legacy verbs (add/list/remove) remain as skill-level workflow fragments\n"
            "dispatched by the /log skill; they are not reachable via this CLI."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    research = sub.add_parser(
        "research",
        help="Analyze research corpora under logs/research/<subject>/<subtopic>-samples/",
        description=(
            "Research corpus analysis.\n"
            "\n"
            "Verbs:\n"
            "  check        Verify a markdown file has no sibling-duplicate headings\n"
            "  sections     Print the chain-key tree; --count and --size add columns\n"
            "  references   List sample files containing a section at a given chain key; --show-content includes bodies\n"
            "  diff         Diff sample heading trees against the running _CONSOLIDATED*.md\n"
            "  quantify     Compute adoption tables for branching points in _CONSOLIDATED*.md; --write inserts in place\n"
            "\n"
            "Samples-directory locators (sections, references, diff):\n"
            "  --subject <name>    <project>/logs/research/<name>/<subtopic>-samples/\n"
            "                        Auto-resolves single-subtopic subjects;\n"
            "                        multi-subtopic requires --subtopic <name>.\n"
            "  --subtopic <name>   Subtopic selector (paired with --subject)\n"
            "  --dir <path>        Explicit directory path\n"
            "\n"
            "Usage:\n"
            "  log research check <path>\n"
            "  log research sections --subject <name>\n"
            "  log research sections --subject <name> --count\n"
            "  log research sections --subject <name> --count --size\n"
            "  log research sections --dir <path> --size\n"
            "  log research references '<chain>' --subject <name>\n"
            "  log research references '<chain>' --subject <name> --count\n"
            "  log research references '<chain>' --subject <name> --show-content\n"
            "  log research references '<chain>' --dir <path>\n"
            "  log research diff --subject <name>\n"
            "  log research diff --subject <name> --show-all\n"
            "  log research diff --dir <path> --consolidated <path>\n"
            "  log research quantify --subject <name>\n"
            "  log research quantify --subject <name> --write\n"
            "  log research quantify --dir <path> --consolidated <path> --write"
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

    r_sections = rsub.add_parser(
        "sections",
        help="Print the chain-key tree; --count and --size add columns",
    )
    _add_samples_location_args(r_sections)
    r_sections.add_argument(
        "--count",
        action="store_true",
        help="Add adoption-count and coverage columns; sort by coverage descending",
    )
    r_sections.add_argument(
        "--size",
        action="store_true",
        help="Add UTF-8 byte-count column (cost when calling `references <chain> --show-content`)",
    )
    r_sections.set_defaults(_dispatch=_dispatch_research_sections)

    r_references = rsub.add_parser(
        "references",
        help="List sample files containing a section at the given chain key; --show-content includes bodies",
    )
    _add_samples_location_args(r_references)
    r_references.add_argument(
        "chain",
        help="Chain key like 'Sample > Transport > Configuration' (' > ' separator)",
    )
    r_references.add_argument(
        "--count",
        action="store_true",
        help="Print just the integer count of matching files",
    )
    r_references.add_argument(
        "--size",
        action="store_true",
        help="Print UTF-8 byte count of section bodies under the chain (companion for budgeting)",
    )
    r_references.add_argument(
        "--show-content",
        action="store_true",
        help="Include each file's section body inline, separated by `=== <filename> ===` markers",
    )
    r_references.set_defaults(_dispatch=_dispatch_research_references)

    r_diff = rsub.add_parser(
        "diff",
        help="Diff sample heading trees against the running consolidated; report growth and pruning candidates",
    )
    _add_samples_location_args(r_diff)
    r_diff.add_argument(
        "--consolidated",
        help="Path to the consolidated markdown (default: glob `_CONSOLIDATED*.md` in samples dir)",
    )
    r_diff.add_argument(
        "--show-all",
        action="store_true",
        help="Print every growth/pruning candidate (default caps each list at 50)",
    )
    r_diff.set_defaults(_dispatch=_dispatch_research_diff)

    r_quantify = rsub.add_parser(
        "quantify",
        help="Compute adoption tables for branching points in _CONSOLIDATED*.md; --write inserts in place",
    )
    _add_samples_location_args(r_quantify)
    r_quantify.add_argument(
        "--consolidated",
        help="Path to the consolidated markdown (default: glob `_CONSOLIDATED*.md` in samples dir)",
    )
    r_quantify.add_argument(
        "--write",
        action="store_true",
        help="Insert/replace adoption tables in the consolidated in place (idempotent via sentinel comments)",
    )
    r_quantify.set_defaults(_dispatch=_dispatch_research_quantify)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "_dispatch"):
        try:
            sys.exit(args._dispatch(args))
        except _SubtopicResolutionError as exc:
            print(str(exc), file=sys.stderr)
            sys.exit(1)
    parser.print_help()
    sys.exit(1)


if __name__ == "__main__":
    main()
