"""Refactor subsystem infrastructure.

Deploy refactor-owned rule files to the plugin's rule corpus so the
agent is aware of when to reach for /ocd:refactor over manual sed or
Edit for multi-file identifier renames.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from pathlib import Path

import framework


def _plugin_name() -> str:
    return framework.get_plugin_name(framework.get_plugin_root())


def _rules_src_dir() -> Path:
    return framework.get_plugin_root() / "systems" / "refactor" / "rules"


def _rules_dst_dir() -> Path:
    return (
        framework.get_project_dir()
        / ".claude"
        / "rules"
        / _plugin_name()
        / "systems"
    )


def _rules_rel_prefix() -> str:
    return f".claude/rules/{_plugin_name()}/systems"


def init(force: bool = False) -> dict:
    """Deploy refactor-owned rule files."""
    rel = _rules_rel_prefix()
    results = framework.deploy_files(
        src_dir=_rules_src_dir(),
        dst_dir=_rules_dst_dir(),
        pattern="*.md",
        force=force,
        keep_orphans=True,
    )
    files = [{"path": f"{rel}/{r.pop('name')}", **r} for r in results]
    return {"files": files, "extra": []}


def status() -> dict:
    """Report refactor rule deployment state."""
    src_dir = _rules_src_dir()
    if not src_dir.is_dir():
        return {"files": [], "extra": []}

    rel = _rules_rel_prefix()
    dst_dir = _rules_dst_dir()
    files = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        state = framework.compare_deployed(src, dst_dir / src.name)
        files.append({
            "path": f"{rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return {"files": files, "extra": []}
