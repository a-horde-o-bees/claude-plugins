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

from .research._compliance import compliance_summary
from .research._sample_tools import (
    DuplicateHeadingError,
    check_no_duplicate_headings,
    consolidate_section,
    count_sections,
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


def _dispatch_research_count_sections(args: argparse.Namespace) -> int:
    """Print per-chain-key coverage across a samples directory."""
    samples_dir = _resolve_samples_dir(args)
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
    results = consolidate_section(args.chain, samples_dir)
    if not results:
        print(f"No samples contain chain key {args.chain!r}")
        return 0
    for path, content in results:
        print(f"=== {path} ===")
        print(content)
        print()
    return 0


def _dispatch_research_compliance(args: argparse.Namespace) -> int:
    """Compare every sample (and `_CONSOLIDATED.md` if present) against a template."""
    samples_dir = _resolve_samples_dir(args)
    template_path = Path(args.template).resolve() if args.template else samples_dir / "_TEMPLATE.md"
    if not template_path.is_file():
        print(f"Template not found: {template_path}", file=sys.stderr)
        return 1

    summary = compliance_summary(samples_dir, template_path)
    clean = sum(1 for r in summary.reports if r.is_clean)
    total = len(summary.reports)
    print(f"Samples: {total}    Clean: {clean}    With outliers: {total - clean}")
    if summary.consolidated_report is None:
        print("Consolidated: not present")
    elif summary.consolidated_report.is_clean:
        print("Consolidated: clean")
    else:
        cr = summary.consolidated_report
        print(f"Consolidated: {len(cr.outliers)} outliers, {len(cr.out_of_order)} order violations")
    print(f"Template: {template_path}")
    print()

    if summary.outlier_counts:
        sorted_outliers = sorted(summary.outlier_counts.items(), key=lambda kv: -len(kv[1]))
        print("Outliers — chain keys present in samples but not in template:")
        for chain_key, files in sorted_outliers:
            print(f"  {len(files):3d}  {chain_key}")
            if args.show_files:
                for f in files:
                    print(f"         {f.name}")
        print()
    else:
        print("No outliers across the corpus.\n")

    order_violations = [(r, v) for r in summary.reports for v in r.out_of_order]
    if order_violations:
        print("Order violations:")
        for report, violation in order_violations:
            ctx = f"{violation.chain_key}: " if violation.chain_key else ""
            print(f"  {report.sample_path.name}: {ctx}'{violation.heading}' should come after "
                  f"'{violation.expected_after}', not '{violation.appears_after}'")
        print()

    consolidated_outliers: list[str] = []
    consolidated_order: list = []
    if summary.consolidated_report is not None and not summary.consolidated_report.is_clean:
        cr = summary.consolidated_report
        consolidated_outliers = [o.chain_key for o in cr.outliers]
        consolidated_order = list(cr.out_of_order)
        if consolidated_outliers:
            print("_CONSOLIDATED.md outliers:")
            for chain_key in consolidated_outliers:
                print(f"  {chain_key}")
            print()
        if consolidated_order:
            print("_CONSOLIDATED.md order violations:")
            for v in consolidated_order:
                ctx = f"{v.chain_key}: " if v.chain_key else ""
                print(f"  {ctx}'{v.heading}' should come after "
                      f"'{v.expected_after}', not '{v.appears_after}'")
            print()

    if args.show_missing and summary.missing_counts:
        print("Missing template chain keys (informational — sections are optional):")
        sorted_missing = sorted(summary.missing_counts.items(), key=lambda kv: -kv[1])
        for chain_key, count in sorted_missing:
            print(f"  {count:3d}  {chain_key}")

    sample_failure = bool(summary.outlier_counts) or bool(order_violations)
    consolidated_failure = bool(consolidated_outliers) or bool(consolidated_order)
    return 0 if not sample_failure and not consolidated_failure else 1


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
            "  check           Verify a markdown file has no sibling-duplicate headings\n"
            "  count-sections  Print chain-key coverage across a samples directory\n"
            "  consolidate     Print per-sample content under a given chain key\n"
            "  compliance      Diff every sample against the subject's _TEMPLATE.md\n"
            "\n"
            "Samples-directory locators (count-sections, consolidate, compliance):\n"
            "  --subject <name>    <project>/logs/research/<name>/<subtopic>-samples/\n"
            "                        Auto-resolves single-subtopic subjects;\n"
            "                        multi-subtopic requires --subtopic <name>.\n"
            "  --subtopic <name>   Subtopic selector (paired with --subject)\n"
            "  --dir <path>        Explicit directory path\n"
            "\n"
            "Usage:\n"
            "  log research check <path>\n"
            "  log research count-sections --subject <name>\n"
            "  log research count-sections --subject <name> --subtopic <topic>\n"
            "  log research count-sections --dir <path>\n"
            "  log research consolidate --chain <key> --subject <name>\n"
            "  log research consolidate --chain <key> --dir <path>\n"
            "  log research compliance --subject <name>\n"
            "  log research compliance --subject <name> --show-missing --show-files\n"
            "  log research compliance --dir <path> --template <template-path>"
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

    r_compliance = rsub.add_parser(
        "compliance",
        help="Diff every sample under a directory against a template; report outliers",
    )
    _add_samples_location_args(r_compliance)
    r_compliance.add_argument(
        "--template",
        help="Path to template markdown (default: <samples-dir>/_TEMPLATE.md)",
    )
    r_compliance.add_argument(
        "--show-missing",
        action="store_true",
        help="Also list template chain keys missing across the corpus (informational)",
    )
    r_compliance.add_argument(
        "--show-files",
        action="store_true",
        help="List the sample filenames where each outlier appears",
    )
    r_compliance.set_defaults(_dispatch=_dispatch_research_compliance)

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
