"""Rules subsystem setup.

Per-system setup handler — purpose statement, status, install, and
uninstall for the rules system. Rules are markdown files that
Claude Code auto-loads into every session at user-scope
(~/.claude/rules/<plugin>/) and project-scope
(<project>/.claude/rules/<plugin>/).

Install state is per-rule, per-scope: each rule template can be
deployed at user, project, both, or neither. Status reports across
both scopes; install/uninstall require an explicit scope.
"""

from __future__ import annotations

from pathlib import Path

from systems import setup
from tools import environment


CATEGORY = "rules"
SUPPORTED_SCOPES = ("user", "project")


def _plugin_name() -> str:
    return setup.get_plugin_name(environment.get_plugin_root())


def _templates_dir() -> Path:
    return environment.get_plugin_root() / "systems" / CATEGORY / "templates"


def _scope_root(scope: str) -> Path:
    if scope == "user":
        return environment.get_claude_home()
    if scope == "project":
        return environment.get_project_dir() / ".claude"
    raise ValueError(f"unsupported scope: {scope}")


def _target_dir(scope: str) -> Path:
    return _scope_root(scope) / CATEGORY / _plugin_name()


def _deployed_rel(scope: str) -> str:
    if scope == "user":
        return f"~/.claude/{CATEGORY}/{_plugin_name()}"
    return f".claude/{CATEGORY}/{_plugin_name()}"


def _available_rules() -> list[str]:
    """Return sorted list of rule template basenames (without .md extension)."""
    src_dir = _templates_dir()
    if not src_dir.is_dir():
        return []
    return sorted(p.stem for p in src_dir.glob("*.md") if p.is_file())


def _purpose_of(rule_path: Path) -> str:
    """Read the first non-heading paragraph from a rule template file.

    Skips YAML frontmatter (between `---` fences) and markdown headings,
    returning the first prose paragraph that follows the title.
    """
    text = rule_path.read_text()
    lines = text.splitlines()
    i = 0
    if lines and lines[0].strip() == "---":
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1  # past closing fence
    current: list[str] = []
    while i < len(lines):
        line = lines[i]
        i += 1
        if not line.strip():
            if current:
                return " ".join(current)
            continue
        if line.startswith("#"):
            continue
        current.append(line.strip())
    return " ".join(current) if current else "(no description)"


def purpose() -> str:
    """One-line purpose statement for setup-level discovery."""
    return (
        "Always-on agent guidance — install rule files at user or project "
        "scope so they auto-load into every session."
    )


def list_items() -> dict:
    """List available rule templates with first-paragraph purposes.

    Returns {items: [{name, purpose}, ...], extra: []}. The catalog drives
    the discovery surface so an agent or user can pick rules to install
    by name without reading every template file.
    """
    src_dir = _templates_dir()
    items: list[dict] = []
    if not src_dir.is_dir():
        return {"items": items, "extra": []}
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        items.append({"name": src.stem, "purpose": _purpose_of(src)})
    return {"items": items, "extra": []}


def status(scope: str | None = None) -> dict:
    """Report install state per template across requested scopes.

    scope=None reports both user and project scopes; scope='user' or
    'project' narrows to one. Returns a per-rule table with one column
    per requested scope so a reader sees each rule's state across
    scopes on a single row.
    """
    if scope and scope not in SUPPORTED_SCOPES:
        return {
            "rows": [],
            "columns": [],
            "extra": [{"label": "error", "value": f"unsupported scope: {scope}"}],
        }

    scopes = (scope,) if scope else SUPPORTED_SCOPES

    src_dir = _templates_dir()
    if not src_dir.is_dir():
        return {"rows": [], "columns": list(scopes), "extra": []}

    rows: list[dict] = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        row: dict = {"name": src.stem}
        for s in scopes:
            dst = _target_dir(s) / src.name
            row[s] = setup.compare_deployed(src, dst)
        rows.append(row)

    return {"rows": rows, "columns": list(scopes), "extra": []}


def install(scope: str, targets: list[str] | None = None, force: bool = False) -> dict:
    """Deploy one or more rule templates to the chosen scope.

    targets=None deploys every template; otherwise each entry is a rule
    basename (with or without .md extension) and only those deploy.
    force=True overwrites divergent deployed copies.
    """
    if scope not in SUPPORTED_SCOPES:
        return {
            "files": [],
            "extra": [{
                "label": "error",
                "value": f"unsupported scope: {scope} — expected user or project",
            }],
        }

    src_dir = _templates_dir()
    dst_dir = _target_dir(scope)
    rel = _deployed_rel(scope)

    if targets is None:
        names = [f"{stem}.md" for stem in _available_rules()]
    else:
        names = []
        unknown: list[str] = []
        for t in targets:
            name = t if t.endswith(".md") else f"{t}.md"
            if (src_dir / name).is_file():
                names.append(name)
            else:
                unknown.append(t)
        if unknown:
            available = ", ".join(_available_rules())
            return {
                "files": [],
                "extra": [{
                    "label": "error",
                    "value": f"unknown rule(s): {', '.join(unknown)} — available: {available}",
                }],
            }

    files: list[dict] = []
    for name in names:
        results = setup.deploy_files(
            src_dir=src_dir,
            dst_dir=dst_dir,
            pattern=name,
            force=force,
        )
        for r in results:
            files.append({"path": f"{rel}/{r.pop('name')}", **r})

    return {"files": files, "extra": []}


def uninstall(scope: str, targets: list[str] | None = None) -> dict:
    """Remove one or more deployed rule files from the chosen scope.

    targets=None removes every deployed template; otherwise each entry is
    a rule basename and only those are removed.
    """
    if scope not in SUPPORTED_SCOPES:
        return {
            "files": [],
            "extra": [{
                "label": "error",
                "value": f"unsupported scope: {scope} — expected user or project",
            }],
        }

    dst_dir = _target_dir(scope)
    rel = _deployed_rel(scope)
    files: list[dict] = []
    if not dst_dir.is_dir():
        return {"files": files, "extra": []}

    if targets is None:
        deployed = sorted(dst_dir.glob("*.md"))
    else:
        deployed = []
        for t in targets:
            name = t if t.endswith(".md") else f"{t}.md"
            candidate = dst_dir / name
            if candidate.is_file():
                deployed.append(candidate)

    for md in deployed:
        files.append({
            "path": f"{rel}/{md.name}",
            "before": "current",
            "after": "absent",
        })
        md.unlink()

    if dst_dir.exists() and not any(dst_dir.iterdir()):
        dst_dir.rmdir()

    return {"files": files, "extra": []}
