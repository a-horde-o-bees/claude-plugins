"""Navigator CLI.

Presentation layer: argument parsing and dispatch wrappers only.
Business logic lives in navigator.py and skill_resolver.py.
"""

import argparse
import sys

# Support both package import and direct execution
try:
    from . import navigator
    from . import skill_resolver
except ImportError:
    import navigator  # type: ignore[import-not-found]
    import skill_resolver  # type: ignore[import-not-found]


DEFAULT_DB = ".claude/ocd/navigator/navigator.db"


def _auto_scan(args: argparse.Namespace) -> None:
    """Run scan before command execution. Silent — discards output."""
    path = getattr(args, "path", None) or "."
    navigator.scan_path(args.db, path)


def _dispatch_describe(args: argparse.Namespace) -> None:
    _auto_scan(args)
    print(navigator.describe_path(args.db, args.path))


def _dispatch_list(args: argparse.Namespace) -> None:
    _auto_scan(args)
    result = navigator.list_files(
        args.db, args.path, patterns=args.pattern, excludes=args.exclude,
    )
    if result:
        print(result)


def _dispatch_scan(args: argparse.Namespace) -> None:
    print(navigator.scan_path(args.db, args.path))


def _dispatch_get_undescribed(args: argparse.Namespace) -> None:
    _auto_scan(args)
    print(navigator.get_undescribed(args.db))


def _dispatch_set(args: argparse.Namespace) -> None:
    _auto_scan(args)
    exclude = int(args.exclude) if args.exclude is not None else None
    traverse = int(args.traverse) if args.traverse is not None else None
    print(navigator.set_entry(
        args.db,
        args.path,
        description=args.description,
        exclude=exclude,
        traverse=traverse,
    ))


def _dispatch_remove(args: argparse.Namespace) -> None:
    _auto_scan(args)
    all_entries = getattr(args, "all", False)
    path = getattr(args, "path", None)
    print(navigator.remove_entry(
        args.db,
        entry_path=path or "",
        recursive=args.recursive,
        all_entries=all_entries,
    ))


def _dispatch_search(args: argparse.Namespace) -> None:
    _auto_scan(args)
    print(navigator.search_entries(args.db, args.pattern))


def _dispatch_resolve_skill(args: argparse.Namespace) -> None:
    result = skill_resolver.resolve_skill(args.name)
    if result:
        print(result)
    else:
        print(f"Skill not found: {args.name}", file=sys.stderr)
        sys.exit(1)


def _dispatch_list_skills(_args: argparse.Namespace) -> None:
    skills = skill_resolver.list_skills()
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
        prog="navigator_cli.py",
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
            "  --all             Remove all concrete entries (preserves pattern rules)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[db_parent],
    )
    remove_p.add_argument("path", nargs="?", default=None, help="File or directory path to remove")
    remove_p.add_argument("--recursive", action="store_true", default=False, help="Remove directory and all children")
    remove_p.add_argument("--all", action="store_true", default=False, help="Remove all concrete entries (preserves pattern rules)")
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
