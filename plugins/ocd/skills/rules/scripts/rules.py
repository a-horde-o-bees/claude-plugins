"""Rules skill — manage always-on agent guidance deployment.

Verbs:

- ``list`` — print the bundled rule catalog with one-line descriptions
- ``show <name>`` — print the full body of one rule
- ``status [--scope <user|project>]`` — report per-rule deployment state at each scope
- ``install <name>... --scope <user|project> [--force]`` — deploy rule canonicals
  as always-on at the chosen scope. Target path:
  ``<scope>/rules/dependencies/<name>.md``
- ``uninstall <name>... --scope <user|project>`` — remove deployed rules from scope

Catalog source: ``<skill>/dependencies/`` — auto-propagated from project-root
``shared/dependencies/`` via pre-commit. Each file is a complete rule canonical
with ``# Title`` heading followed by a description paragraph per markdown.md.

Deploy targets follow markdown-dependency-resolution: ``<scope>/rules/dependencies/<name>.md``
is the always-on path Claude Code auto-loads. The lazy ``<scope>/dependencies/<name>.md``
path is not managed here — move files there manually if needed.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _environment import get_claude_home, get_project_dir  # noqa: E402


SUPPORTED_SCOPES = ("user", "project")


def _skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _catalog_dir() -> Path:
    """The bundled rule catalog — also serves as this skill's own dep bundle."""
    return _skill_root() / "dependencies"


def _scope_root(scope: str) -> Path:
    if scope == "user":
        return get_claude_home()
    if scope == "project":
        return get_project_dir() / ".claude"
    raise ValueError(f"unsupported scope: {scope}")


def _target_dir(scope: str) -> Path:
    return _scope_root(scope) / "rules" / "dependencies"


def _deployed_rel(scope: str) -> str:
    if scope == "user":
        return "~/.claude/rules/dependencies"
    return ".claude/rules/dependencies"


def _available_rules() -> list[str]:
    src_dir = _catalog_dir()
    if not src_dir.is_dir():
        return []
    return sorted(p.stem for p in src_dir.glob("*.md") if p.is_file())


def _description_of(rule_path: Path) -> str:
    """Return the first non-empty body line after the ``#`` heading.

    Pattern (per markdown.md):
        # <Title>

        Description paragraph.

    Falls back to ``(no description)`` if the file deviates from the pattern.
    """
    text = rule_path.read_text()
    in_body = False
    for line in text.splitlines():
        stripped = line.strip()
        if not in_body:
            if stripped.startswith("# "):
                in_body = True
            continue
        if not stripped:
            continue
        return stripped
    return "(no description)"


def _compare(src: Path, dst: Path) -> str:
    if not dst.exists():
        return "absent"
    if src.read_bytes() == dst.read_bytes():
        return "current"
    return "divergent"


def cmd_list(_args: argparse.Namespace) -> int:
    src_dir = _catalog_dir()
    if not src_dir.is_dir():
        print("(catalog directory missing)", file=sys.stderr)
        return 1
    rules = _available_rules()
    if not rules:
        print("(catalog empty)")
        return 0
    name_width = max(len(r) for r in rules)
    for name in rules:
        desc = _description_of(src_dir / f"{name}.md")
        print(f"{name:<{name_width}}  {desc}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    name = args.name
    target = name if name.endswith(".md") else f"{name}.md"
    src = _catalog_dir() / target
    if not src.is_file():
        available = ", ".join(_available_rules())
        print(f"unknown rule: {name} — available: {available}", file=sys.stderr)
        return 1
    sys.stdout.write(src.read_text())
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    scope = args.scope
    if scope and scope not in SUPPORTED_SCOPES:
        print(f"unsupported scope: {scope}", file=sys.stderr)
        return 1
    scopes = list((scope,) if scope else SUPPORTED_SCOPES)
    rules = _available_rules()
    if not rules:
        print("(catalog empty)")
        return 0

    name_width = max(len("name"), max(len(r) for r in rules))
    col_widths = {s: max(len(s), len("divergent")) for s in scopes}
    header = [f"{'name':<{name_width}}"] + [f"{s:<{col_widths[s]}}" for s in scopes]
    print("  ".join(header))

    src_dir = _catalog_dir()
    for name in rules:
        cells = [f"{name:<{name_width}}"]
        for s in scopes:
            state = _compare(src_dir / f"{name}.md", _target_dir(s) / f"{name}.md")
            cells.append(f"{state:<{col_widths[s]}}")
        print("  ".join(cells))
    return 0


def _resolve_targets(args: argparse.Namespace, src_dir: Path) -> tuple[list[str], int]:
    """Return (filenames, exit_code). exit_code is nonzero on bad input."""
    if args.all:
        return [f"{stem}.md" for stem in _available_rules()], 0
    names: list[str] = []
    unknown: list[str] = []
    for t in args.targets:
        name = t if t.endswith(".md") else f"{t}.md"
        if (src_dir / name).is_file():
            names.append(name)
        else:
            unknown.append(t)
    if unknown:
        available = ", ".join(_available_rules())
        print(
            f"unknown rule(s): {', '.join(unknown)} — available: {available}",
            file=sys.stderr,
        )
        return [], 1
    if not names:
        print("no rules specified — pass rule names or --all", file=sys.stderr)
        return [], 1
    return names, 0


def cmd_install(args: argparse.Namespace) -> int:
    scope = args.scope
    if scope not in SUPPORTED_SCOPES:
        print(f"unsupported scope: {scope} — expected user or project", file=sys.stderr)
        return 1

    src_dir = _catalog_dir()
    dst_dir = _target_dir(scope)
    rel = _deployed_rel(scope)

    names, code = _resolve_targets(args, src_dir)
    if code:
        return code

    dst_dir.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = src_dir / name
        dst = dst_dir / name
        before = _compare(src, dst)
        if before == "absent":
            shutil.copy2(src, dst)
            after = "current"
        elif before == "divergent" and args.force:
            shutil.copy2(src, dst)
            after = "current"
        else:
            after = before
        print(f"{rel}/{name}: {before} → {after}")
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    scope = args.scope
    if scope not in SUPPORTED_SCOPES:
        print(f"unsupported scope: {scope} — expected user or project", file=sys.stderr)
        return 1

    dst_dir = _target_dir(scope)
    rel = _deployed_rel(scope)
    if not dst_dir.is_dir():
        print(f"nothing deployed at {rel}")
        return 0

    if args.all:
        deployed = sorted(dst_dir.glob("*.md"))
    else:
        deployed = []
        unknown: list[str] = []
        for t in args.targets:
            name = t if t.endswith(".md") else f"{t}.md"
            candidate = dst_dir / name
            if candidate.is_file():
                deployed.append(candidate)
            else:
                unknown.append(t)
        if unknown:
            print(
                f"not deployed at {rel}: {', '.join(unknown)}",
                file=sys.stderr,
            )
            return 1
        if not deployed:
            print("no matching deployed rules — pass rule names or --all", file=sys.stderr)
            return 1

    for md in deployed:
        print(f"{rel}/{md.name}: current → absent")
        md.unlink()

    if dst_dir.exists() and not any(dst_dir.iterdir()):
        dst_dir.rmdir()
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="rules")
    sub = parser.add_subparsers(dest="verb", required=True)

    sub.add_parser("list", help="print the catalog with one-line descriptions")

    p_show = sub.add_parser("show", help="print one rule's full body")
    p_show.add_argument("name")

    p_status = sub.add_parser("status", help="report deployment state per scope")
    p_status.add_argument("--scope", choices=SUPPORTED_SCOPES)

    p_install = sub.add_parser("install", help="deploy rules as always-on")
    p_install.add_argument("targets", nargs="*")
    p_install.add_argument("--scope", choices=SUPPORTED_SCOPES, required=True)
    p_install.add_argument("--all", action="store_true")
    p_install.add_argument("--force", action="store_true")

    p_uninstall = sub.add_parser("uninstall", help="remove always-on rules")
    p_uninstall.add_argument("targets", nargs="*")
    p_uninstall.add_argument("--scope", choices=SUPPORTED_SCOPES, required=True)
    p_uninstall.add_argument("--all", action="store_true")

    args = parser.parse_args(argv)

    handlers = {
        "list": cmd_list,
        "show": cmd_show,
        "status": cmd_status,
        "install": cmd_install,
        "uninstall": cmd_uninstall,
    }
    return handlers[args.verb](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
