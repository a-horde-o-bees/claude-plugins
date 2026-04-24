"""Check CLI.

Presentation layer: argument parsing and dispatch. Business logic lives
in per-dimension modules (`_dormancy`, `_markdown`, `_python`). Output
is structured per target — one header line, per-check pass/fail/skip
lines, trailing summary. Exit 0 when all checks pass, 1 when any fail.

Adding a dimension: write a `_dispatch_<name>` that returns an int
exit code, register it in `DIMENSIONS`, and add a subparser in
`build_parser`. The `all` dispatcher iterates `DIMENSIONS` and no
other code changes — SKILL.md step 7 is a single `ocd-run check all`.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from tools import environment

from . import check_dormancy, scan_system
from ._allowlist import filter_allowed, load_allowlist
from ._markdown import scan_paths as scan_markdown_paths
from ._python import scan_paths as scan_python_paths


# __main__.py is a per-system CLI dispatcher — it may anchor to its own
# directory to read sibling config (`allowlist.csv`). This is the only
# path where `Path(__file__).parent` appears in this module; it is
# allowlisted via the `plugins/*/systems/*/__main__.py` pattern.
ALLOWLIST_CSV = Path(__file__).parent / "allowlist.csv"


def _project_root_from(paths: list[Path]) -> Path:
    """Resolve a project root for allowlist matching.

    Delegates to `environment.get_git_root_for` from the first seed
    path; falls back to the seed itself when the seed is outside any
    git checkout. Used to render violation paths project-relative
    before fnmatch against allowlist patterns.
    """
    seed = paths[0] if paths else Path.cwd()
    try:
        return environment.get_git_root_for(seed)
    except RuntimeError:
        return seed.resolve() if seed.is_dir() else seed.resolve().parent


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


def _dispatch_dormancy(args: argparse.Namespace) -> int:
    plugin_root = (
        Path(args.plugin).resolve() if getattr(args, "plugin", None)
        else environment.get_plugin_root()
    )
    system = getattr(args, "system", None)
    if system:
        systems = [plugin_root / "systems" / system]
        if not systems[0].is_dir():
            print(f"System not found: {system}", file=sys.stderr)
            return 1
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

    return 1 if any_fail else 0


def _dispatch_markdown(args: argparse.Namespace) -> int:
    """Scan markdown files for literal-character and blank-line discipline violations.

    Reports with rule name, file:line:col, and surrounding context. Literal-
    char violations are judgment-required (never auto-fixed); blank-line
    violations are auto-fixable via the module's `fix_blank_lines`.
    Results pass through the shared allowlist so cross-dimension
    exemptions (e.g. `fixture_*.*`) suppress consistently.
    """
    paths = getattr(args, "paths", None) or []
    roots = [Path(p).resolve() for p in paths] if paths else [Path.cwd()]
    strict = getattr(args, "strict", False)
    raw = scan_markdown_paths(roots, strict=strict)
    allowlist = load_allowlist(ALLOWLIST_CSV)
    project_root = _project_root_from(roots)
    violations, _suppressed = filter_allowed(raw, allowlist, project_root)

    if not violations:
        print("Clean — no markdown violations found.")
        return 0
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
    return 1


def _dispatch_python(args: argparse.Namespace) -> int:
    """Scan Python files for parent-walking patterns.

    Flags any `.parent`, `.parents[N]`, or `os.path.dirname(...)`
    traversal whose chain roots at `__file__`. Known anchor files
    (conftest.py, plugin entry-points, per-system CLI dispatchers)
    are suppressed via `allowlist.csv`. `--show-allowed` surfaces the
    suppressed entries so reviewers can audit the allowlist.
    """
    paths = getattr(args, "paths", None) or []
    roots = [Path(p).resolve() for p in paths] if paths else [Path.cwd()]
    raw = scan_python_paths(roots)
    allowlist = load_allowlist(ALLOWLIST_CSV)
    project_root = _project_root_from(roots)
    violations, suppressed = filter_allowed(raw, allowlist, project_root)

    if not violations and not suppressed:
        print("Clean — no parent-walking patterns found.")
        return 0

    if violations:
        by_path: dict[Path, list] = {}
        for v in violations:
            by_path.setdefault(v.path, []).append(v)
        for path in sorted(by_path):
            print(f"[FAIL] {path} — python")
            for v in by_path[path]:
                print(f"  {path}:{v.line}:{v.col}: {v.rule}")
                print(f"    {v.snippet}")

    if getattr(args, "show_allowed", False) and suppressed:
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
        return 1
    print(
        f"Clean — no parent-walking patterns found "
        f"({allowed_n} suppressed by allowlist)."
    )
    return 0


DIMENSIONS = {
    "dormancy": _dispatch_dormancy,
    "markdown": _dispatch_markdown,
    "python": _dispatch_python,
}


def _dispatch_all(args: argparse.Namespace) -> int:
    """Run every registered dimension at its default scope.

    Each dispatcher reads its own fields from the passed Namespace via
    `getattr(..., default)` — an empty Namespace triggers default
    behavior for every dimension. Adding a new dispatcher to
    `DIMENSIONS` is all it takes for `all` to pick it up.
    """
    rc = 0
    for dispatch in DIMENSIONS.values():
        dim_args = argparse.Namespace()
        dim_rc = dispatch(dim_args)
        if dim_rc:
            rc = dim_rc
    return rc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check",
        description=(
            "Run universal discipline checks against plugin systems or project files.\n"
            "\n"
            "Dimensions available:\n"
            "  dormancy  Verify System Dormancy contract — readiness interface,\n"
            "            rule deployment, MCP dormancy gate pattern.\n"
            "  markdown  Scan .md files for unprotected literal characters and\n"
            "            blank-line discipline violations.\n"
            "  python    Scan .py files for parent-walking patterns — chained\n"
            "            .parent.parent…, .parents[N>=1], or nested os.path.dirname\n"
            "            calls that couple files to their disk location.\n"
            "  all       Run every dimension at its default scope.\n"
            "\n"
            "Usage:\n"
            "  check all                          Run every dimension\n"
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

    m_p = sub.add_parser("markdown", help="Scan markdown for unprotected literals and blank-line issues")
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

    a_p = sub.add_parser("all", help="Run every dimension at its default scope")
    a_p.set_defaults(_dispatch=_dispatch_all)

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
