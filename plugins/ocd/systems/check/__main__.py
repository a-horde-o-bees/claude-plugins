"""Check CLI.

Presentation layer: argument parsing and dispatch. Business logic lives
in _dormancy and future dimension modules. Output is structured per
system — one header line, per-check pass/fail/skip lines, trailing
summary. Exit 0 when all checks pass, 1 when any fail.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import framework

from . import check_dormancy, scan_system
from ._allowlist import filter_allowed, load_allowlist
from ._markdown import scan_paths as scan_markdown_paths
from ._python import scan_paths as scan_python_paths


DIMENSIONS = {"dormancy", "markdown", "python"}

# __main__.py is a per-system CLI dispatcher — it may anchor to its own
# directory to read sibling config (`allowlist.csv`). This is the only
# path where `Path(__file__).parent` appears in this module; it is
# allowlisted via the `plugins/*/systems/*/__main__.py` pattern.
ALLOWLIST_CSV = Path(__file__).parent / "allowlist.csv"


def _project_root_from(paths: list[Path]) -> Path:
    """Resolve a project root for allowlist matching.

    Walks upward from the first path until a `.git` directory is
    found; falls back to the path itself. Used to render violation
    paths project-relative before fnmatch against allowlist patterns.
    """
    seed = paths[0] if paths else Path.cwd()
    current = seed.resolve() if seed.is_dir() else seed.resolve().parent
    for candidate in [current, *current.parents]:
        if (candidate / ".git").is_dir():
            return candidate
    return current


def _discover_systems(plugin_root: Path) -> list[Path]:
    """Return system directories under <plugin_root>/systems/ that have an _init.py."""
    systems_dir = plugin_root / "systems"
    if not systems_dir.is_dir():
        return []
    return [
        p
        for p in sorted(systems_dir.iterdir())
        if p.is_dir() and (p / "_init.py").is_file()
    ]


def _system_import_paths(plugin_root: Path, system_name: str) -> tuple[str, str]:
    """Dotted import paths for a system's facade and _init modules."""
    return f"systems.{system_name}", f"systems.{system_name}._init"


def _print_result(result) -> None:
    status = "PASS" if result.ok else "FAIL"
    print(f"[{status}] {result.system} — {result.dimension}")
    for p in result.passes:
        print(f"  + {p}")
    for f in result.failures:
        print(f"  - {f}")
    for s in result.skipped:
        print(f"  ~ {s}")


def _dispatch_dormancy(args: argparse.Namespace) -> None:
    plugin_root = Path(args.plugin).resolve() if args.plugin else framework.get_plugin_root()
    if args.system:
        systems = [plugin_root / "systems" / args.system]
        if not systems[0].is_dir():
            print(f"System not found: {args.system}", file=sys.stderr)
            sys.exit(1)
    else:
        systems = _discover_systems(plugin_root)

    any_fail = False
    for system_path in systems:
        surfaces = scan_system(system_path)
        if not surfaces.declares_init_contract:
            continue
        facade_import, init_import = _system_import_paths(plugin_root, surfaces.name)
        with tempfile.TemporaryDirectory() as tmp:
            result = check_dormancy(surfaces, facade_import, init_import, Path(tmp))
        _print_result(result)
        if not result.ok:
            any_fail = True

    if any_fail:
        sys.exit(1)


def _dispatch_markdown(args: argparse.Namespace) -> None:
    """Scan markdown files for literal-character and blank-line discipline violations.

    Reports with rule name, file:line:col, and surrounding context. Literal-
    char violations are judgment-required (never auto-fixed); blank-line
    violations are auto-fixable via the module's `fix_blank_lines`.
    """
    roots = [Path(p).resolve() for p in args.paths] if args.paths else [Path.cwd()]
    violations = scan_markdown_paths(roots, strict=args.strict)
    if not violations:
        print("Clean — no markdown violations found.")
        return
    by_path: dict[Path, list] = {}
    for v in violations:
        by_path.setdefault(v.path, []).append(v)
    for path in sorted(by_path):
        print(f"[FAIL] {path} — markdown")
        for v in by_path[path]:
            detail = f"literal '{v.char}'" if v.char else "blank-line discipline"
            print(f"  {path}:{v.line}:{v.col}: {v.rule} — {detail}")
            print(f"    {v.context.rstrip()}")
    total = len(violations)
    files = len(by_path)
    print(f"\n{total} violation(s) in {files} file(s)", file=sys.stderr)
    sys.exit(1)


def _dispatch_python(args: argparse.Namespace) -> None:
    """Scan Python files for parent-walking patterns.

    Flags any `.parent`, `.parents[N]`, or `os.path.dirname(...)`
    traversal whose chain roots at `__file__`. Known anchor files
    (conftest.py, plugin entry-points, per-system CLI dispatchers)
    are suppressed via `allowlist.csv`. `--show-allowed` surfaces the
    suppressed entries so reviewers can audit the allowlist.
    """
    roots = [Path(p).resolve() for p in args.paths] if args.paths else [Path.cwd()]
    raw = scan_python_paths(roots)
    allowlist = load_allowlist(ALLOWLIST_CSV)
    project_root = _project_root_from(roots)
    violations, suppressed = filter_allowed(raw, allowlist, project_root)

    if not violations and not suppressed:
        print("Clean — no parent-walking patterns found.")
        return

    if violations:
        by_path: dict[Path, list] = {}
        for v in violations:
            by_path.setdefault(v.path, []).append(v)
        for path in sorted(by_path):
            print(f"[FAIL] {path} — python")
            for v in by_path[path]:
                print(f"  {path}:{v.line}:{v.col}: {v.rule}")
                print(f"    {v.snippet}")

    if args.show_allowed and suppressed:
        print(f"\nSuppressed by allowlist ({len(suppressed)}):")
        for v in suppressed:
            print(f"  {v.path}:{v.line}:{v.col}: {v.rule}")
            print(f"    {v.snippet}")

    total = len(violations)
    allowed_n = len(suppressed)
    files = len({v.path for v in violations})
    if total:
        print(
            f"\n{total} violation(s) in {files} file(s); "
            f"{allowed_n} suppressed by allowlist",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print(
            f"Clean — no parent-walking patterns found "
            f"({allowed_n} suppressed by allowlist)."
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check",
        description=(
            "Run universal discipline checks against plugin systems or project files.\n"
            "\n"
            "Dimensions available:\n"
            "  dormancy  Verify System Dormancy contract — readiness interface,\n"
            "            rule deployment, MCP dormancy gate pattern.\n"
            "  markdown  Scan .md files for literal {, }, <, >, (and optionally *, _)\n"
            "            outside backtick-delimited inline/fenced code — enforces the\n"
            "            markdown.md rule to prevent renderer consumption.\n"
            "  python    Scan .py files for parent-walking patterns — chained\n"
            "            .parent.parent…, .parents[N>=1], or nested os.path.dirname\n"
            "            calls that couple files to their disk location.\n"
            "\n"
            "Usage:\n"
            "  check dormancy                     Run dormancy on all systems in the plugin\n"
            "  check dormancy <system-name>       Run dormancy on one system\n"
            "  check dormancy --plugin <path>     Target a different plugin's systems\n"
            "  check markdown                     Scan current working directory\n"
            "  check markdown <path> [<path>...]  Scan given files and/or directories\n"
            "  check markdown --strict            Also flag unescaped * and _ (emphasis)\n"
            "  check python                       Scan current working directory\n"
            "  check python <path> [<path>...]    Scan given files and/or directories"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="dimension", required=True)

    d_p = sub.add_parser("dormancy", help="Run dormancy checks")
    d_p.add_argument("system", nargs="?", default=None, help="System name; omit to check all")
    d_p.add_argument("--plugin", default=None, help="Plugin root override (default: current plugin)")
    d_p.set_defaults(_dispatch=_dispatch_dormancy)

    m_p = sub.add_parser("markdown", help="Scan markdown for unprotected literals")
    m_p.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to scan (default: current working directory)",
    )
    m_p.add_argument(
        "--strict",
        action="store_true",
        help="Also flag unescaped * and _ (often intentional emphasis — review each)",
    )
    m_p.set_defaults(_dispatch=_dispatch_markdown)

    p_p = sub.add_parser("python", help="Scan Python for parent-walking patterns")
    p_p.add_argument(
        "paths",
        nargs="*",
        help="Files or directories to scan (default: current working directory)",
    )
    p_p.add_argument(
        "--show-allowed",
        action="store_true",
        help="Also print violations suppressed by allowlist.csv (for audit)",
    )
    p_p.set_defaults(_dispatch=_dispatch_python)

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
