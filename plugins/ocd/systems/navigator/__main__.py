"""Navigator CLI.

Presentation layer: argument parsing and dispatch wrappers only.
Business logic lives in __init__.py facade. The facade guarantees
the navigator database is populated before each read or write — CLI
dispatch does not pre-scan.
"""

import argparse
import sys
from pathlib import Path

from . import *  # noqa: F403 — underscore-prefixed names are internal; bare names are public


DEFAULT_DB = ".claude/ocd/navigator/navigator.db"


def _format_describe(result: dict) -> str:
    """Format paths_get result for CLI display."""
    if result["type"] == "file":
        lines = [result["path"]]
        if result["purpose"] is None:
            lines.append("[?]")
        elif result["stale"]:
            lines.append(f"[~] {result['purpose']}")
        elif result["purpose"]:
            lines.append(result["purpose"])
        return "\n".join(lines)

    # Directory
    lines = [result["path"]]
    if result["purpose"] is None:
        lines.append("[?]")
    elif result["stale"] and result["purpose"]:
        lines.append(f"[~] {result['purpose']}")
    elif result["purpose"]:
        lines.append(result["purpose"])

    children = result.get("children")
    if children is None:
        lines.append("(no paths)")
    elif children:
        if result["purpose"]:
            lines.append("")
        for child in children:
            display = child["path"]
            if child["type"] == "directory":
                display += "/"
            purpose = child["purpose"]
            if purpose is None:
                lines.append(f"- {display} [?]")
            elif child["stale"] and purpose:
                lines.append(f"- {display} [~] {purpose}")
            elif purpose:
                lines.append(f"- {display} - {purpose}")
            else:
                lines.append(f"- {display}")

    return "\n".join(lines)


def _dispatch_describe(args: argparse.Namespace) -> None:
    print(_format_describe(paths_get(args.db, args.path)))


def _dispatch_list(args: argparse.Namespace) -> None:
    result = paths_list(
        args.db, args.path, patterns=args.pattern, excludes=args.exclude,
        sizes=args.sizes,
    )
    for entry in result:
        if "line_count" in entry:
            print(f"{entry['path']}\t{entry['line_count']}\t{entry['char_count']}")
        else:
            print(entry["path"])


def _dispatch_scan(args: argparse.Namespace) -> None:
    print(scan_path(args.db, args.path or ""))


def _dispatch_get_undescribed(args: argparse.Namespace) -> None:
    result = paths_undescribed(args.db)
    if result["done"]:
        print("No work remaining.")
        return
    print(f"[{result['remaining']} remaining across {result['directories']} directories]")
    print(_format_describe(result["listing"]))


def _dispatch_set(args: argparse.Namespace) -> None:
    exclude = int(args.exclude) if args.exclude is not None else None
    traverse = int(args.traverse) if args.traverse is not None else None
    result = paths_upsert(
        args.db,
        args.path,
        purpose=args.purpose,
        exclude=exclude,
        traverse=traverse,
    )
    if result["action"] == "none":
        print(f"No changes: {result['path']}")
    elif result["action"] == "updated":
        print(f"Updated: {result['path']}")
    elif result["action"] == "added":
        print(f"Added: {result['path']} ({result['type']})")


def _dispatch_remove(args: argparse.Namespace) -> None:
    path = getattr(args, "path", None)
    if getattr(args, "all", False):
        mode = "all"
    elif args.recursive:
        mode = "recursive"
    else:
        mode = "single"
    result = paths_remove(
        args.db,
        entry_path=path or "",
        mode=mode,
    )
    if result["action"] == "removed_all":
        print(f"Removed all {result['count']} paths (rules preserved)")
    elif result["action"] == "error":
        print(f"Error: {result['message']}")
    elif result["action"] == "not_found":
        print(f"Not found: {result['path']}")
    elif result["action"] == "removed_recursive":
        print(f"Removed {result['count']} paths under {result['path']}/")
    elif result["action"] == "removed":
        print(f"Removed: {result['path']}")


def _dispatch_search(args: argparse.Namespace) -> None:
    result = paths_search(args.db, args.pattern)
    if not result["results"]:
        print(f'No paths matching "{result["pattern"]}"')
        return
    print(f'Search: "{result["pattern"]}" ({len(result["results"])} results)')
    print()
    for entry in result["results"]:
        display = entry["path"]
        if entry["type"] == "directory":
            display += "/"
        print(f"- {display} - {entry['purpose']}")


def _dispatch_resolve_skill(args: argparse.Namespace) -> None:
    result = skills_resolve(args.name)
    if result:
        print(result)
    else:
        print(f"Skill not found: {args.name}", file=sys.stderr)
        sys.exit(1)


def _dispatch_ready(args: argparse.Namespace) -> None:
    if not db_ready(Path(args.db)):
        sys.exit(1)


def _dispatch_list_skills(_args: argparse.Namespace) -> None:
    skills = skills_list()
    if not skills:
        print("No skills found.")
        return
    for skill in skills:
        print(f"{skill['name']}  [{skill['source']}]  {skill['path']}")


def build_parser() -> argparse.ArgumentParser:
    """Build standalone argument parser for navigator CLI."""
    db_parent = argparse.ArgumentParser(add_help=False)
    db_parent.add_argument(
        "--db",
        default=DEFAULT_DB,
        help=f"Path to SQLite database (default: {DEFAULT_DB})",
    )

    parser = argparse.ArgumentParser(
        prog="navigator",
        description=(
            "Index of project paths and purposes that answer: should I\n"
            "read this file? Each path carries scope and role so agents\n"
            "can route to the right file without opening it. Complements\n"
            "Grep/Glob which search file contents — navigator search finds\n"
            "files by what they do.\n"
            "\n"
            "All commands except scan auto-scan before execution\n"
            "to ensure fresh data.\n"
            "\n"
            "Workflow: describe navigates tree with purposes,\n"
            "list enumerates file paths for tool consumption,\n"
            "search finds paths by purpose, set writes purposes.\n"
            "\n"
            "Output markers:\n"
            "  [?]  Path not yet described — needs purpose description\n"
            "  [~]  Path stale — file changed since purpose was written\n"
            "\n"
            "Typical exploration sequence:\n"
            "  1. describe .               — see top-level structure\n"
            "  2. describe <directory>      — drill into area of interest\n"
            "  3. search --pattern <term>   — find files by purpose across project\n"
            "\n"
            "File enumeration for tool consumption:\n"
            "  list .                       — all non-excluded files\n"
            "  list . --pattern '*.py'      — only Python files\n"
            "\n"
            "Maintenance sequence (via /ocd:navigator skill):\n"
            "  1. scan .                    — sync filesystem to database\n"
            "  2. get-undescribed           — find paths needing purpose description\n"
            "  3. set <path> --purpose      — write purpose for path\n"
            "  4. repeat 2-3 until 'No work remaining.'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    commands = parser.add_subparsers(dest="command", required=True)

    describe_p = commands.add_parser(
        "describe",
        help="Show path at location with purposes and markers",
        description=(
            "Navigate project structure by path. Start with `describe .`\n"
            "to see top-level directories and files, then drill into areas\n"
            "of interest. Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            "  Directories list children with purposes.\n"
            "  Files show their purpose.\n"
            "  [?] markers indicate paths needing purpose description.\n"
            "  [~] markers indicate stale paths needing re-evaluation.\n"
            "\n"
            "Use when exploring unfamiliar area of codebase.\n"
            "Follow up with Grep/Glob once you know where to look."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    describe_p.add_argument("path", help="File or directory path")
    describe_p.set_defaults(_dispatch=_dispatch_describe)

    list_p = commands.add_parser(
        "list",
        help="List file paths under path; no purposes, supports --pattern filtering",
        description=(
            "Enumerate non-excluded file paths under directory. Returns\n"
            "one path per line, sorted, no purposes or markers.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Designed for tool consumption — other CLIs call this to get\n"
            "filtered file lists without inventing their own enumeration.\n"
            "\n"
            "Output format:\n"
            "  One file path per line, sorted alphabetically.\n"
            "  Empty output means no files matched.\n"
            "\n"
            "Pattern filtering matches against basename (filename only).\n"
            "Multiple --pattern flags are OR-combined.\n"
            "\n"
            "Exclude filtering matches against full path.\n"
            "Multiple --exclude flags are OR-combined.\n"
            "\n"
            "Examples:\n"
            "  list .                        — all non-excluded files\n"
            "  list . --pattern '*.py'       — Python files only\n"
            "  list src --pattern '*.py' --pattern '*.md'\n"
            "  list . --exclude '.claude/*'  — exclude .claude/ tree"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    list_p.add_argument(
        "path", nargs="?", default=".",
        help="Directory to list (default: project root)",
    )
    list_p.add_argument(
        "--pattern", action="append", default=None,
        help="Glob pattern to filter by basename (repeatable, OR-combined)",
    )
    list_p.add_argument(
        "--exclude", action="append", default=None,
        help="Glob pattern to exclude by full path (repeatable, OR-combined)",
    )
    list_p.add_argument(
        "--sizes", action="store_true", default=False,
        help="Append line_count and char_count columns (tab-separated)",
    )
    list_p.set_defaults(_dispatch=_dispatch_list)

    scan_p = commands.add_parser(
        "scan",
        help="Sync filesystem to database; auto-adds, auto-removes, detects changes",
        description=(
            "Walk filesystem and sync to database. New files and directories\n"
            "are added (with NULL purpose), deleted paths are removed, and\n"
            "changed files are flagged. Respects path_patterns rules for\n"
            "exclusions and traversal limits; rules aggregate from every\n"
            "deployed .claude/*/*/paths.csv at scan time.\n"
            "\n"
            "Traverses git submodules owned by this project. Excluded\n"
            "directories (.git, __pycache__, .venv, etc.) are declared via\n"
            "the path_patterns rules.\n"
            "\n"
            "Output format:\n"
            "  Scan: <target>/\n"
            "  Added N, removed N[, changed N][, staled N parent(s)]\n"
            "\n"
            "Other commands auto-scan before execution, so explicit scan\n"
            "is rarely needed. Use when you want to see scan report."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    scan_p.add_argument(
        "path", nargs="?", default=".",
        help="Directory to scan (default: project root)",
    )
    scan_p.set_defaults(_dispatch=_dispatch_scan)

    gu_p = commands.add_parser(
        "get-undescribed",
        help="Return deepest directory with paths needing purpose description; call repeatedly until done",
        description=(
            "Returns one directory per call — deepest with paths needing\n"
            "purpose description. Output is directory listing with [?]\n"
            "markers on paths needing purpose description. Described\n"
            "siblings provide context. Auto-scans before execution.\n"
            "\n"
            "Call repeatedly until output is 'No work remaining.' — this is\n"
            "stop condition. Depth-first order ensures children are\n"
            "described before parents.\n"
            "\n"
            "Output format:\n"
            "  [N remaining across M directories]\n"
            "  <directory listing with [?] and [~] markers>\n"
            "\n"
            "Directories with traverse=0 (e.g., tests/) are listed but their\n"
            "children never appear — describe the directory itself only.\n"
            "\n"
            "Output paths match format expected by `set` — use directly."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gu_p.set_defaults(_dispatch=_dispatch_get_undescribed)

    set_p = commands.add_parser(
        "set",
        help="Create or update a path's purpose, exclusion, or traversal flags",
        description=(
            "Write purpose for file or directory, or update its scan\n"
            "behavior flags. Primary tool for resolving [?] paths after scan.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Purpose semantics:\n"
            "  NULL (default)  Path not yet reviewed; shows as [?]\n"
            '  Empty string    Self-explanatory name; marks as reviewed (use "")\n'
            "  Non-empty       Populate the purpose using the Purpose Statement principle\n"
            "\n"
            "Setting purpose also clears stale marker and updates\n"
            "stored hash — marks path as reviewed against current contents.\n"
            "\n"
            "Purposes answer: should I read this file? Convey scope and role,\n"
            "not internals or content listings."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    set_p.add_argument("path", help="File, directory, or glob pattern")
    set_p.add_argument("--purpose", default=None, help="Path purpose")
    set_p.add_argument(
        "--exclude", default=None, choices=["0", "1"],
        help="Exclude from scan (1) or include (0)",
    )
    set_p.add_argument(
        "--traverse", default=None, choices=["0", "1"],
        help="Enter directory during scan (1) or list without entering (0)",
    )
    set_p.set_defaults(_dispatch=_dispatch_set)

    remove_p = commands.add_parser(
        "remove",
        help="Remove paths from database",
        description=(
            "Remove paths from database. Rarely needed — scan handles\n"
            "cleanup of deleted files automatically. Use for manual corrections\n"
            "when database state diverges from filesystem.\n"
            "Auto-scans before execution.\n"
            "\n"
            "  path              Remove single path\n"
            "  path --recursive  Remove directory and all children\n"
            "  --all             Remove all concrete paths (path_patterns table unaffected)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    remove_p.add_argument("path", nargs="?", default=None, help="File or directory path to remove")
    remove_mode = remove_p.add_mutually_exclusive_group()
    remove_mode.add_argument("--recursive", action="store_true", default=False, help="Remove directory and all children")
    remove_mode.add_argument("--all", action="store_true", default=False, help="Remove all concrete paths (path_patterns table unaffected)")
    remove_p.set_defaults(_dispatch=_dispatch_remove)

    search_p = commands.add_parser(
        "search",
        help="Search path purposes by keyword",
        description=(
            "Find files and directories by what they do, not what they're named.\n"
            "Searches purposes written by humans, so queries like 'CLI',\n"
            "'business logic', or 'authentication' find relevant paths even\n"
            "when file names don't contain those words.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            '  Search: "<pattern>" (N results)\n'
            "  - <path> - <purpose>\n"
            "\n"
            "Complements Grep/Glob which search file contents and names.\n"
            "Use search when you know purpose but not path."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    search_p.add_argument(
        "--pattern", required=True,
        help="Case-insensitive substring pattern",
    )
    search_p.set_defaults(_dispatch=_dispatch_search)

    rs_p = commands.add_parser(
        "resolve-skill",
        help="Resolve skill name to SKILL.md path; searches all discovery locations in priority order",
        description=(
            "Resolve a skill name (e.g., ocd-conventions) to its SKILL.md\n"
            "file path. Searches discovery locations in Claude Code priority\n"
            "order — first match wins:\n"
            "\n"
            "  1. Personal:    ~/.claude/skills/\n"
            "  2. Project:     .claude/skills/\n"
            "  3. Plugin dir:  $CLAUDE_PLUGIN_ROOT/skills/\n"
            "  4. Marketplace: ~/.claude/plugins/ installed paths\n"
            "\n"
            "Matches by frontmatter name field in SKILL.md.\n"
            "Exits with code 1 if skill is not found."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    rs_p.add_argument("name", help="Skill name to resolve (e.g., ocd-conventions)")
    rs_p.set_defaults(_dispatch=_dispatch_resolve_skill)

    ready_p = commands.add_parser(
        "ready",
        help="Check whether navigator DB is initialized and schema is current; exit 0 if ready, 1 otherwise",
        description=(
            "Readiness probe for skill Route checks and other dormancy-gated\n"
            "callers. Validates that the database file exists and contains\n"
            "every expected table. No output; exit status is the result.\n"
            "\n"
            "Exit codes:\n"
            "  0  DB present with full schema — navigator is operational\n"
            "  1  DB absent, corrupt, or schema divergent — not operational\n"
            "\n"
            "Corrective action on exit 1: run /ocd:setup init."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    ready_p.set_defaults(_dispatch=_dispatch_ready)

    ls_p = commands.add_parser(
        "list-skills",
        help="List all discoverable skills with source and path",
        description=(
            "List all skills found across discovery locations. Shows skill\n"
            "name, source (personal, project, plugin-dir, marketplace),\n"
            "and file path. Higher-priority sources shadow lower ones —\n"
            "shadowed skills are not listed.\n"
            "\n"
            "Output format:\n"
            "  <name>  [<source>]  <path>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ls_p.set_defaults(_dispatch=_dispatch_list_skills)

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
