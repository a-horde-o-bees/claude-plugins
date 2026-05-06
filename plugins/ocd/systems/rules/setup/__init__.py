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


def purpose() -> str:
    """One-line purpose statement for setup-level discovery."""
    return (
        "Always-on agent guidance — install rule files at user or project "
        "scope so they auto-load into every session."
    )


def status(scope: str | None = None) -> dict:
    """Report install state per template across requested scopes.

    scope=None reports both user and project scopes; scope='user' or
    'project' narrows to one. Each rule template appears as a file
    entry per scope it was queried against.
    """
    scopes = (scope,) if scope else SUPPORTED_SCOPES
    if scope and scope not in SUPPORTED_SCOPES:
        return {
            "files": [],
            "extra": [{"label": "error", "value": f"unsupported scope: {scope}"}],
        }

    src_dir = _templates_dir()
    files: list[dict] = []
    if not src_dir.is_dir():
        return {"files": files, "extra": []}

    for s in scopes:
        rel = _deployed_rel(s)
        target = _target_dir(s)
        for src in sorted(src_dir.glob("*.md")):
            if not src.is_file():
                continue
            dst = target / src.name
            state = setup.compare_deployed(src, dst)
            files.append({
                "path": f"{rel}/{src.name}",
                "before": state,
                "after": state,
            })

    return {"files": files, "extra": []}


def install(scope: str, target: str | None = None, force: bool = False) -> dict:
    """Deploy one or more rule templates to the chosen scope.

    target='all' or None deploys every template; otherwise target is a
    rule basename (with or without .md extension) and only that one
    deploys. force=True overwrites divergent deployed copies.
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

    if target in (None, "all"):
        pattern = "*.md"
    else:
        name = target if target.endswith(".md") else f"{target}.md"
        if not (src_dir / name).is_file():
            available = ", ".join(_available_rules())
            return {
                "files": [],
                "extra": [{
                    "label": "error",
                    "value": f"unknown rule: {target} — available: {available}",
                }],
            }
        pattern = name

    results = setup.deploy_files(
        src_dir=src_dir,
        dst_dir=dst_dir,
        pattern=pattern,
        force=force,
    )
    files = [{"path": f"{rel}/{r.pop('name')}", **r} for r in results]
    return {"files": files, "extra": []}


def uninstall(scope: str, target: str | None = None) -> dict:
    """Remove one or more deployed rule files from the chosen scope.

    target='all' or None removes every deployed template; otherwise
    target is a rule basename and only that one is removed.
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

    if target in (None, "all"):
        deployed = sorted(dst_dir.glob("*.md"))
    else:
        name = target if target.endswith(".md") else f"{target}.md"
        candidate = dst_dir / name
        deployed = [candidate] if candidate.is_file() else []

    for md in deployed:
        files.append({
            "path": f"{rel}/{md.name}",
            "before": "current",
            "after": "absent",
        })
        md.unlink()

    if not any(dst_dir.iterdir()):
        dst_dir.rmdir()

    return {"files": files, "extra": []}
