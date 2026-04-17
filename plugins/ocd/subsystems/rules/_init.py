"""Rules subsystem.

Deploy rule markdown files from subsystems/rules/templates/ into
.claude/rules/{plugin}/ per-plugin subfolder. Rules are always-on
agent context loaded by Claude Code at session start.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from pathlib import Path

import plugin


CATEGORY = "rules"


def _plugin_name() -> str:
    return plugin.get_plugin_name(plugin.get_plugin_root())


def _templates_dir() -> Path:
    return plugin.get_plugin_root() / "lib" / CATEGORY / "templates"


def _target_dir() -> Path:
    return plugin.get_project_dir() / ".claude" / CATEGORY / _plugin_name()


def _deployed_rel() -> str:
    return f".claude/{CATEGORY}/{_plugin_name()}"


def init(force: bool = False) -> dict:
    """Deploy rule templates."""
    results = plugin.deploy_files(
        src_dir=_templates_dir(),
        dst_dir=_target_dir(),
        pattern="*.md",
        force=force,
    )
    rel = _deployed_rel()
    files = [{"path": f"{rel}/{r.pop('name')}", **r} for r in results]
    return {"files": files, "extra": []}


def status() -> dict:
    """Report rule deployment state."""
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
        state = plugin.compare_deployed(src, dst)
        files.append({
            "path": f"{rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return {"files": files, "extra": []}
