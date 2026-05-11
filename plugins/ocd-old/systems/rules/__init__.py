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
from dependencies import environment


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


def _tagline_of(rule_path: Path) -> str:
    """Read the `tagline:` field from a rule template's YAML frontmatter.

    The tagline is the brief one-liner shown in `setup rules list` so the
    catalog stays scannable. Templates without a tagline fall back to a
    placeholder so the missing field surfaces during review.
    """
    text = rule_path.read_text()
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "(no tagline)"
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("tagline:"):
            return line.split(":", 1)[1].strip().strip('"').strip("'")
    return "(no tagline)"


def _body_of(rule_path: Path) -> str:
    """Return the rule template body with YAML frontmatter stripped."""
    text = rule_path.read_text()
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            body = "".join(lines[i + 1:])
            return body.lstrip("\n")
    return text


def purpose() -> str:
    """One-line purpose statement for setup-level discovery."""
    return (
        "Always-on agent guidance — install rule files at user or project "
        "scope so they auto-load into every session."
    )


def list_items() -> dict:
    """List available rule templates with one-line taglines.

    Returns {items: [{name, tagline}, ...], extra: []}. The catalog drives
    the discovery surface so an agent or user can scan rules at a glance
    and reach for `show <name>` to read a full template.
    """
    src_dir = _templates_dir()
    items: list[dict] = []
    if not src_dir.is_dir():
        return {"items": items, "extra": []}
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        items.append({"name": src.stem, "tagline": _tagline_of(src)})
    return {"items": items, "extra": []}


def show(name: str) -> dict:
    """Return the full body of a named rule template.

    name accepts either bare basename or `<name>.md`. Returns
    {content: str, extra: []} with frontmatter stripped on success, or
    {content: "", extra: [{"label": "error", ...}]} when the name does
    not match any template.
    """
    target = name if name.endswith(".md") else f"{name}.md"
    src = _templates_dir() / target
    if not src.is_file():
        available = ", ".join(_available_rules())
        return {
            "content": "",
            "extra": [{
                "label": "error",
                "value": f"unknown rule: {name} — available: {available}",
            }],
        }
    return {"content": _body_of(src), "extra": []}


def status(scope: str | None = None) -> dict:
    """Report install state per template across requested scopes.

    scope=None reports both user and project scopes; scope='user' or
    'project' narrows to one. Uses `setup.status_table` to produce the
    wide per-rule × per-scope table shared across migrated systems.
    """
    if scope and scope not in SUPPORTED_SCOPES:
        return {
            "rows": [],
            "columns": [],
            "extra": [{"label": "error", "value": f"unsupported scope: {scope}"}],
        }

    scopes = list((scope,) if scope else SUPPORTED_SCOPES)
    src_dir = _templates_dir()
    items = [p.stem for p in sorted(src_dir.glob("*.md")) if p.is_file()] if src_dir.is_dir() else []

    def state_of(name: str, scope_name: str) -> str:
        src = src_dir / f"{name}.md"
        dst = _target_dir(scope_name) / f"{name}.md"
        return setup.compare_deployed(src, dst)

    return setup.status_table(items, scopes, state_of)


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
