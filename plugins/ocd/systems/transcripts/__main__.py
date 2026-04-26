"""Transcripts subsystem CLI.

Presentation layer: argument parsing and dispatch. Business logic
lives in `_transcripts` and is exposed via the package facade.

Usage:
    ocd-run transcripts project_list
    ocd-run transcripts project_path
    ocd-run transcripts chat_export [NAME ...] [--all]
    ocd-run transcripts chat_clean  [NAME ...] [--all]

`chat_export` and `chat_clean` default to the current project (resolved via
`project_path`) when no NAME is given. `--all` operates on every project
under ~/.claude/projects/.

Encoded project names start with `-` (e.g., `-home-dev-projects-foo`).
The leading-dash workaround in `main()` lets users pass them as positionals
without `--` or `=` syntax.
"""

import argparse
import sys

from . import chat_clean, chat_export, project_list, project_path


def cmd_project_list() -> int:
    """Print the encoded folder name of every project, one per line."""
    for name in project_list():
        print(name)
    return 0


def cmd_project_path() -> int:
    """Print the absolute path to the current project's transcripts directory."""
    path = project_path()
    if path is None:
        print(
            "Current project has no transcripts under ~/.claude/projects/.",
            file=sys.stderr,
        )
        return 1
    print(path)
    return 0


def cmd_chat_export(projects: list[str]) -> int:
    """Export top-level chat for the given projects in place."""
    if not projects:
        print("No projects to export.", file=sys.stderr)
        return 1

    counts = chat_export(projects)
    report = (
        f"Exported {counts['written']} transcripts "
        f"({counts['skipped']} unchanged"
    )
    if counts["missing"]:
        report += f", {counts['missing']} project(s) missing"
    report += ")"
    print(report, file=sys.stderr)

    return 0 if counts["missing"] == 0 else 1


def cmd_chat_clean(projects: list[str]) -> int:
    """Remove chat extracts for the given projects."""
    if not projects:
        print("No projects to clean.", file=sys.stderr)
        return 1

    counts = chat_clean(projects)
    report = f"Removed {counts['removed']} chat extract(s)"
    if counts["missing"]:
        report += f" ({counts['missing']} project(s) missing)"
    print(report, file=sys.stderr)

    return 0 if counts["missing"] == 0 else 1


def _dispatch_project_list(_args: argparse.Namespace) -> int:
    _ = _args
    return cmd_project_list()


def _dispatch_project_path(_args: argparse.Namespace) -> int:
    _ = _args
    return cmd_project_path()


def _resolve_projects(args: argparse.Namespace, action: str) -> list[str] | None:
    """Resolve the project name list for chat_export / chat_clean.

    Returns None if the invocation is invalid; caller should return 1.
    """
    if args.all and args.projects:
        print("Cannot combine project names with --all.", file=sys.stderr)
        return None

    if args.all:
        projects = project_list()
        if not projects:
            print("No projects found under ~/.claude/projects/", file=sys.stderr)
            return None
        return projects

    if args.projects:
        return list(args.projects)

    current = project_path()
    if current is None:
        print(
            f"Could not resolve current project for {action}. "
            "This project has no transcripts in ~/.claude/projects/. "
            "Pass project names as arguments or use --all.",
            file=sys.stderr,
        )
        return None
    return [current.name]


def _dispatch_chat_export(args: argparse.Namespace) -> int:
    projects = _resolve_projects(args, "chat_export")
    if projects is None:
        return 1
    return cmd_chat_export(projects)


def _dispatch_chat_clean(args: argparse.Namespace) -> int:
    projects = _resolve_projects(args, "chat_clean")
    if projects is None:
        return 1
    return cmd_chat_clean(projects)


def _build_parser() -> argparse.ArgumentParser:
    # Disable the default -h short flag so leading-dash project names (e.g.,
    # `-home-dev-projects-foo`) don't trigger help via short-flag bundling.
    # --help still works.
    parser = argparse.ArgumentParser(
        prog="transcripts",
        description="Extract simplified chat from Claude Code transcripts",
        add_help=False,
    )
    parser.add_argument("--help", action="help", help="show this help message and exit")
    commands = parser.add_subparsers(dest="command", required=True)

    list_p = commands.add_parser(
        "project_list",
        help="List encoded folder names of all projects under ~/.claude/projects/",
        add_help=False,
    )
    list_p.add_argument("--help", action="help", help="show this help message and exit")
    list_p.set_defaults(_dispatch=_dispatch_project_list)

    path_p = commands.add_parser(
        "project_path",
        help="Print the absolute path to the current project's transcripts directory",
        add_help=False,
    )
    path_p.add_argument("--help", action="help", help="show this help message and exit")
    path_p.set_defaults(_dispatch=_dispatch_project_path)

    export_p = commands.add_parser(
        "chat_export",
        help="Extract top-level chat for one or more projects "
             "(default: current project)",
        add_help=False,
    )
    export_p.add_argument("--help", action="help", help="show this help message and exit")
    export_p.add_argument(
        "projects", nargs="*", metavar="NAME",
        help="Encoded project folder name(s). Omit for current project.",
    )
    export_p.add_argument(
        "--all", action="store_true",
        help="Export every project under ~/.claude/projects/ "
             "(mutually exclusive with named projects)",
    )
    export_p.set_defaults(_dispatch=_dispatch_chat_export)

    clean_p = commands.add_parser(
        "chat_clean",
        help="Remove chat extracts for one or more projects "
             "(default: current project)",
        add_help=False,
    )
    clean_p.add_argument("--help", action="help", help="show this help message and exit")
    clean_p.add_argument(
        "projects", nargs="*", metavar="NAME",
        help="Encoded project folder name(s). Omit for current project.",
    )
    clean_p.add_argument(
        "--all", action="store_true",
        help="Clean every project under ~/.claude/projects/ "
             "(mutually exclusive with named projects)",
    )
    clean_p.set_defaults(_dispatch=_dispatch_chat_clean)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args, unknown = parser.parse_known_args(argv)

    # Forward leading-single-dash unknowns to positional `projects`
    # (chat_export / chat_clean only). Double-dash unknowns (likely typos)
    # still error. Lets users type project names that start with `-`
    # (Claude Code's path-encoded format) without needing `=` or `--`.
    for token in unknown:
        if token.startswith("--"):
            parser.error(f"unrecognized argument: {token}")
        if args.command in ("chat_export", "chat_clean") and hasattr(args, "projects"):
            args.projects.append(token)
        else:
            parser.error(f"unrecognized argument: {token}")

    return args._dispatch(args)


if __name__ == "__main__":
    sys.exit(main())
