"""Patterns subsystem.

Deploy pattern markdown files from systems/patterns/templates/ into
.claude/patterns/{plugin}/ per-plugin subfolder. Patterns document
reusable workflow recipes — referenced by skills, not auto-loaded.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from pathlib import Path

import framework


CATEGORY = "patterns"


def _plugin_name() -> str:
    return framework.get_plugin_name(framework.get_plugin_root())


def _templates_dir() -> Path:
    return framework.get_plugin_root() / "systems" / CATEGORY / "templates"


def _target_dir() -> Path:
    return framework.get_project_dir() / ".claude" / CATEGORY / _plugin_name()


def _deployed_rel() -> str:
    return f".claude/{CATEGORY}/{_plugin_name()}"


def init(force: bool = False) -> dict:
    """Deploy pattern templates."""
    results = framework.deploy_files(
        src_dir=_templates_dir(),
        dst_dir=_target_dir(),
        pattern="*.md",
        force=force,
    )
    rel = _deployed_rel()
    files = [{"path": f"{rel}/{r.pop('name')}", **r} for r in results]
    return {"files": files, "extra": []}


def status() -> dict:
    """Report pattern deployment state."""
    src_dir = _templates_dir()
    if not src_dir.is_dir():
        return {"files": [], "extra": []}

    rel = _deployed_rel()
    target = _target_dir()
    files = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        dst = target / src.name
        state = framework.compare_deployed(src, dst)
        files.append({
            "path": f"{rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return {"files": files, "extra": []}
