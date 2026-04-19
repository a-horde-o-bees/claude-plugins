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


DIMENSIONS = {"dormancy"}


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="check",
        description=(
            "Run universal discipline checks against plugin systems.\n"
            "\n"
            "Dimensions available:\n"
            "  dormancy  Verify System Dormancy contract — readiness interface,\n"
            "            rule deployment, MCP dormancy gate pattern.\n"
            "\n"
            "Usage:\n"
            "  check dormancy                  Run dormancy on all systems in the plugin\n"
            "  check dormancy <system-name>    Run dormancy on one system\n"
            "  check dormancy --plugin <path>  Target a different plugin's systems"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="dimension", required=True)

    d_p = sub.add_parser("dormancy", help="Run dormancy checks")
    d_p.add_argument("system", nargs="?", default=None, help="System name; omit to check all")
    d_p.add_argument("--plugin", default=None, help="Plugin root override (default: current plugin)")
    d_p.set_defaults(_dispatch=_dispatch_dormancy)

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
