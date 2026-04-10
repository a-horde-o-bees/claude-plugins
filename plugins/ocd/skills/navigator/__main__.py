"""Navigator CLI.

Presentation layer: argument parsing and dispatch wrappers only.
Business logic lives in __init__.py facade.
"""

import argparse
import os
import sys

from . import *  # noqa: F403 — __all__ defines the public API


DEFAULT_DB = ".claude/ocd/navigator/navigator.db"


def _auto_scan(args: argparse.Namespace) -> None:
    """Run scan before command execution. Silent — discards output."""
    path = getattr(args, "path", None) or "."
    scan_path(args.db, path)


def _format_describe(result: dict) -> str:
    """Format paths_describe result for CLI display."""
    if result["type"] == "file":
        lines = [result["path"]]
        if result["description"] is None:
            lines.append("[?]")
        elif result["stale"]:
            lines.append(f"[~] {result['description']}")
        elif result["description"]:
            lines.append(result["description"])
        return "\n".join(lines)

    # Directory
    lines = [result["path"]]
    if result["description"] is None:
        lines.append("[?]")
    elif result["stale"] and result["description"]:
        lines.append(f"[~] {result['description']}")
    elif result["description"]:
        lines.append(result["description"])

    children = result.get("children")
    if children is None:
        lines.append("(no entries)")
    elif children:
        if result["description"]:
            lines.append("")
        for child in children:
            display = child["path"]
            if child["type"] == "directory":
                display += "/"
            desc = child["description"]
            if desc is None:
                lines.append(f"- {display} [?]")
            elif child["stale"] and desc:
                lines.append(f"- {display} [~] {desc}")
            elif desc:
                lines.append(f"- {display} - {desc}")
            else:
                lines.append(f"- {display}")

    return "\n".join(lines)


def _dispatch_describe(args: argparse.Namespace) -> None:
    _auto_scan(args)
    print(_format_describe(paths_get(args.db, args.path)))


def _dispatch_list(args: argparse.Namespace) -> None:
    _auto_scan(args)
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
    print(scan_path(args.db, args.path))


def _dispatch_get_undescribed(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = paths_undescribed(args.db)
    if result["done"]:
        print("No work remaining.")
        return
    print(f"[{result['remaining']} remaining across {result['directories']} directories]")
    print(_format_describe(result["listing"]))


def _dispatch_set(args: argparse.Namespace) -> None:
    _auto_scan(args)
    exclude = int(args.exclude) if args.exclude is not None else None
    traverse = int(args.traverse) if args.traverse is not None else None
    result = paths_upsert(
        args.db,
        args.path,
        description=args.description,
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
    _auto_scan(args)
    all_entries = getattr(args, "all", False)
    path = getattr(args, "path", None)
    result = paths_remove(
        args.db,
        entry_path=path or "",
        recursive=args.recursive,
        all_entries=all_entries,
    )
    if result["action"] == "removed_all":
        print(f"Removed all {result['count']} entries (rules preserved)")
    elif result["action"] == "error":
        print(f"Error: {result['message']}")
    elif result["action"] == "not_found":
        print(f"Not found: {result['path']}")
    elif result["action"] == "removed_recursive":
        print(f"Removed {result['count']} entries under {result['path']}/")
    elif result["action"] == "removed":
        print(f"Removed: {result['path']}")


def _dispatch_search(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = paths_search(args.db, args.pattern)
    if not result["results"]:
        print(f'No entries matching "{result["pattern"]}"')
        return
    print(f'Search: "{result["pattern"]}" ({len(result["results"])} results)')
    print()
    for entry in result["results"]:
        display = entry["path"]
        if entry["type"] == "directory":
            display += "/"
        print(f"- {display} - {entry['description']}")


def _dispatch_resolve_skill(args: argparse.Namespace) -> None:
    result = skills_resolve(args.name)
    if result:
        print(result)
    else:
        print(f"Skill not found: {args.name}", file=sys.stderr)
        sys.exit(1)


def _dispatch_list_skills(_args: argparse.Namespace) -> None:
    skills = skills_list()
    if not skills:
        print("No skills found.")
        return
    for skill in skills:
        print(f"{skill['name']}  [{skill['source']}]  {skill['path']}")


def _dispatch_governance(args: argparse.Namespace) -> None:
    _auto_scan(args)
    entries = governance_list(args.db)
    if not entries:
        print("No governance entries.")
        return
    for entry in entries:
        print(f"{entry['path']}  {entry['pattern']}  [{entry['mode']}]")


def _dispatch_governance_for(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = governance_match(args.db, args.files)
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


def _dispatch_governance_order(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = governance_order(args.db)
    if result["cycle"]:
        print(f"Cycle detected among: {', '.join(result['cycle'])}")
        return
    if not result["levels"]:
        print("No governance entries.")
        return
    for level in result["levels"]:
        print(f"Level {level['level']}:")
        for path in level["entries"]:
            print(f"  {path}")


def _dispatch_governance_load(args: argparse.Namespace) -> None:
    project_dir = args.project_dir or os.getcwd()
    result = governance_load(args.db, project_dir)
    print(f"Loaded {result['governance_entries']} governance entries, "
          f"{result['governs_relationships']} governs relationships")


def _dispatch_governance_graph(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = governance_graph(args.db)
    if not result["roots"] and not result["edges"]:
        print("No governance entries.")
        return
    if result["roots"]:
        print(f"Roots ({len(result['roots'])}):")
        for r in result["roots"]:
            print(f"  {r}")
        print()
    print(f"Edges ({len(result['edges'])}):")
    for edge in result["edges"]:
        print(f"  {edge['from']}  -->  {edge['to']}")
    if result["leaves"]:
        print()
        print(f"Leaves ({len(result['leaves'])}):")
        for l in result["leaves"]:
            print(f"  {l}")


def _dispatch_get_unclassified(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = governance_unclassified(args.db)
    if result["total"] == 0:
        print("All file entries have governance coverage.")
        return
    print(f"Unclassified: {result['total']} files without governance coverage")
    print()
    for ext in sorted(result["by_extension"]):
        files = result["by_extension"][ext]
        print(f"{ext} ({len(files)} files):")
        for path in files:
            print(f"  {path}")


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
            "Index of project files and directories with descriptions that\n"
            "answer: should I read this file? Each entry conveys scope and\n"
            "role so agents can route to right file without opening it.\n"
            "Complements Grep/Glob which search file contents — navigator\n"
            "search finds files by what they do.\n"
            "\n"
            "All commands except scan auto-scan before execution\n"
            "to ensure fresh data.\n"
            "\n"
            "Workflow: describe navigates tree with descriptions,\n"
            "list enumerates file paths for tool consumption,\n"
            "search finds entries by description, set writes descriptions.\n"
            "\n"
            "Output markers:\n"
            "  [?]  Entry not yet described — needs description\n"
            "  [~]  Entry stale — file changed since description was written\n"
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
            "Maintenance sequence (via /navigator skill):\n"
            "  1. scan .                    — sync filesystem to database\n"
            "  2. get-undescribed           — find entries needing descriptions\n"
            "  3. set <path> --description  — write description for entry\n"
            "  4. repeat 2-3 until 'No work remaining.'"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    commands = parser.add_subparsers(dest="command", required=True)

    # describe
    describe_p = commands.add_parser(
        "describe",
        help="Show entry at path with descriptions and markers",
        description=(
            "Navigate project structure by path. Start with `describe .`\n"
            "to see top-level directories and files, then drill into areas\n"
            "of interest. Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            "  Directories list children with descriptions.\n"
            "  Files show their description.\n"
            "  [?] markers indicate entries needing descriptions.\n"
            "  [~] markers indicate stale entries needing re-evaluation.\n"
            "\n"
            "Use when exploring unfamiliar area of codebase.\n"
            "Follow up with Grep/Glob once you know where to look."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    describe_p.add_argument("path", help="File or directory path")
    describe_p.set_defaults(_dispatch=_dispatch_describe)

    # list
    list_p = commands.add_parser(
        "list",
        help="List file paths under path; no descriptions, supports --pattern filtering",
        description=(
            "Enumerate non-excluded file paths under directory. Returns\n"
            "one path per line, sorted, no descriptions or markers.\n"
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

    # scan
    scan_p = commands.add_parser(
        "scan",
        help="Sync filesystem to database; auto-adds, auto-removes, detects changes",
        description=(
            "Walk filesystem and sync to database. New files and directories\n"
            "are added (with NULL description), deleted paths are removed, and\n"
            "changed files are flagged. Respects seed rules for exclusions and\n"
            "traversal limits.\n"
            "\n"
            "Traverses git submodules owned by this project. Excluded\n"
            "directories (.git, __pycache__, .venv, etc.) are defined by\n"
            "seed rules — run `init` to apply latest seed rules.\n"
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

    # get-undescribed
    gu_p = commands.add_parser(
        "get-undescribed",
        help="Return deepest directory with undescribed entries; call repeatedly until done",
        description=(
            "Returns one directory per call — deepest with undescribed\n"
            "entries. Output is directory listing with [?] markers on entries\n"
            "needing descriptions. Described siblings provide context.\n"
            "Auto-scans before execution.\n"
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
            "children never appear — describe directory itself only.\n"
            "\n"
            "Output paths match format expected by `set` — use directly."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gu_p.set_defaults(_dispatch=_dispatch_get_undescribed)

    # set
    set_p = commands.add_parser(
        "set",
        help="Create or update entry description, exclusion, or traversal flags",
        description=(
            "Write description for file or directory, or update its scan\n"
            "behavior flags. Primary tool for resolving [?] entries after scan.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Description semantics:\n"
            "  NULL (default)  Entry not yet reviewed; shows as [?]\n"
            '  Empty string    Self-explanatory name; marks as reviewed (use "")\n'
            "  Non-empty       Description of file's purpose\n"
            "\n"
            "Setting description also clears stale marker and updates\n"
            "stored hash — marks entry as reviewed against current contents.\n"
            "\n"
            "Descriptions answer: should I read this file? Convey scope and role,\n"
            "not internals or content listings."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    set_p.add_argument("path", help="File, directory, or glob pattern")
    set_p.add_argument("--description", default=None, help="Entry description")
    set_p.add_argument(
        "--exclude", default=None, choices=["0", "1"],
        help="Exclude from scan (1) or include (0)",
    )
    set_p.add_argument(
        "--traverse", default=None, choices=["0", "1"],
        help="Enter directory during scan (1) or list without entering (0)",
    )
    set_p.set_defaults(_dispatch=_dispatch_set)

    # remove
    remove_p = commands.add_parser(
        "remove",
        help="Remove entries from database",
        description=(
            "Remove entries from database. Rarely needed — scan handles\n"
            "cleanup of deleted files automatically. Use for manual corrections\n"
            "when database state diverges from filesystem.\n"
            "Auto-scans before execution.\n"
            "\n"
            "  path              Remove single entry\n"
            "  path --recursive  Remove directory and all children\n"
            "  --all             Remove all concrete entries (patterns table unaffected)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    remove_p.add_argument("path", nargs="?", default=None, help="File or directory path to remove")
    remove_p.add_argument("--recursive", action="store_true", default=False, help="Remove directory and all children")
    remove_p.add_argument("--all", action="store_true", default=False, help="Remove all concrete entries (patterns table unaffected)")
    remove_p.set_defaults(_dispatch=_dispatch_remove)

    # search
    search_p = commands.add_parser(
        "search",
        help="Search entry descriptions by keyword",
        description=(
            "Find files and directories by what they do, not what they're named.\n"
            "Searches descriptions written by humans, so queries like 'CLI',\n"
            "'business logic', or 'authentication' find relevant entries even\n"
            "when file names don't contain those words.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            '  Search: "<pattern>" (N results)\n'
            "  - <path> - <description>\n"
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

    # resolve-skill
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

    # list-skills
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

    # governance
    gov_p = commands.add_parser(
        "governance",
        help="List all governance entries with patterns and loading mode",
        description=(
            "List governance entries (rules and conventions) registered in\n"
            "the database. Shows entry path, glob pattern, and loading mode\n"
            "(rule = auto-loaded every session, convention = on-demand).\n"
            "\n"
            "Output format:\n"
            "  <path>  <pattern>  [rule|convention]"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gov_p.set_defaults(_dispatch=_dispatch_governance)

    # governance-for
    gf_p = commands.add_parser(
        "governance-for",
        help="Find which governance entries govern given files",
        description=(
            "Match file paths against governance patterns to find which\n"
            "rules and conventions apply. Replaces conventions list-matching.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            "  Criteria: (sorted unique list)\n"
            "  <file> follows: (per-file governance list)\n"
            "\n"
            "Line count tags [warn: N lines] and [fail: N lines] appear\n"
            "when file exceeds configured thresholds."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gf_p.add_argument("files", nargs="+", help="File paths to check governance for")
    gf_p.set_defaults(_dispatch=_dispatch_governance_for)

    # governance-order
    go_p = commands.add_parser(
        "governance-order",
        help="Topological ordering of governance entries for evaluation sequence",
        description=(
            "Show governance entries ordered by dependency level.\n"
            "Level 0 has no governors; level N is governed only by\n"
            "levels 0..N-1. Replaces conventions list-self.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            "  Level 0:\n"
            "    <path>\n"
            "  Level 1:\n"
            "    <path>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    go_p.set_defaults(_dispatch=_dispatch_governance_order)

    # governance-load
    gl_p = commands.add_parser(
        "governance-load",
        help="Load governance data from frontmatter in rules and conventions",
        description=(
            "Scan .claude/rules/ and .claude/conventions/ for files with\n"
            "governance frontmatter (pattern + depends fields). Populates\n"
            "governance table with patterns and governs table with\n"
            "dependency relationships.\n"
            "\n"
            "Idempotent — safe to rerun. Existing data is updated,\n"
            "not duplicated."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gl_p.add_argument("--project-dir", default=None, help="Project root (default: cwd)")
    gl_p.set_defaults(_dispatch=_dispatch_governance_load)

    # governance-graph
    gg_p = commands.add_parser(
        "governance-graph",
        help="Show governance-to-governance edges, roots, and leaves",
        description=(
            "Display which governance entries govern which other governance\n"
            "entries. Shows roots (no governor), edges (governs relationships),\n"
            "and leaves (govern no other governance entries).\n"
            "Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            "  Roots (N):\n"
            "    <path>\n"
            "  Edges (N):\n"
            "    <governor>  -->  <governed>\n"
            "  Leaves (N):\n"
            "    <path>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gg_p.set_defaults(_dispatch=_dispatch_governance_graph)

    # get-unclassified (governance coverage)
    gu2_p = commands.add_parser(
        "get-unclassified",
        help="Find file entries with no governance coverage",
        description=(
            "List files that match no governance pattern. Groups by\n"
            "file extension to surface which file types lack conventions.\n"
            "Auto-scans before execution.\n"
            "\n"
            "Output format:\n"
            "  Unclassified: N files without governance coverage\n"
            "  .ext (N files):\n"
            "    <path>"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    gu2_p.set_defaults(_dispatch=_dispatch_get_unclassified)

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
