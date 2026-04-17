"""Logs subsystem.

Deploy log-type templates from systems/log/templates/<type>/ into
.claude/logs/<type>/ — unnamespaced by plugin. Each plugin contributes
log types to a shared project-level pool; the user authors log entries
alongside the templates, so deployment uses keep_orphans to preserve
user content.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from pathlib import Path

import plugin


def _templates_dir() -> Path:
    return plugin.get_plugin_root() / "systems" / "log" / "templates"


def _target_dir() -> Path:
    return plugin.get_project_dir() / ".claude" / "logs"


def _deployed_rel() -> str:
    return ".claude/logs"


def init(force: bool = False) -> dict:
    """Deploy log-type templates."""
    src_dir = _templates_dir()
    target = _target_dir()
    rel = _deployed_rel()
    files = []

    if not src_dir.is_dir():
        return {"files": files, "extra": []}

    for type_dir in sorted(src_dir.iterdir()):
        if not type_dir.is_dir():
            continue
        type_name = type_dir.name
        results = plugin.deploy_files(
            src_dir=type_dir,
            dst_dir=target / type_name,
            pattern="*.md",
            force=force,
            keep_orphans=True,
        )
        for r in results:
            r["path"] = f"{rel}/{type_name}/{r.pop('name')}"
            files.append(r)

    return {"files": files, "extra": []}


def status() -> dict:
    """Report log-type deployment state."""
    src_dir = _templates_dir()
    if not src_dir.is_dir():
        return {"files": [], "extra": []}

    target = _target_dir()
    rel = _deployed_rel()
    files = []
    for type_dir in sorted(src_dir.iterdir()):
        if not type_dir.is_dir():
            continue
        type_name = type_dir.name
        for src in sorted(type_dir.glob("*.md")):
            if not src.is_file():
                continue
            dst = target / type_name / src.name
            state = plugin.compare_deployed(src, dst)
            files.append({
                "path": f"{rel}/{type_name}/{src.name}",
                "before": state,
                "after": state,
            })
    return {"files": files, "extra": []}
