"""Logs subsystem.

Deploy log-type templates from systems/log/templates/<type>/ into
.claude/logs/<type>/ — unnamespaced by plugin. Each plugin contributes
log types to a shared project-level pool; the user authors log entries
alongside the templates, so deployment uses keep_orphans to preserve
user content.

Also deploys log-owned rule files (log-routing) to the plugin's rule
corpus so the log routing prescription only reaches the agent once the
log system is deployed — see System Dormancy in the project
architecture.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from pathlib import Path

import plugin


def _plugin_name() -> str:
    return plugin.get_plugin_name(plugin.get_plugin_root())


def _templates_dir() -> Path:
    return plugin.get_plugin_root() / "systems" / "log" / "templates"


def _target_dir() -> Path:
    return plugin.get_project_dir() / ".claude" / "logs"


def _deployed_rel() -> str:
    return ".claude/logs"


def _rules_src_dir() -> Path:
    return plugin.get_plugin_root() / "systems" / "log" / "rules"


def _rules_dst_dir() -> Path:
    return (
        plugin.get_project_dir()
        / ".claude"
        / "rules"
        / _plugin_name()
        / "log"
    )


def _rules_rel_prefix() -> str:
    return f".claude/rules/{_plugin_name()}/log"


def _deploy_rules(force: bool) -> list[dict]:
    """Deploy log-owned rule files to the plugin's rule corpus."""
    rel = _rules_rel_prefix()
    results = plugin.deploy_files(
        src_dir=_rules_src_dir(),
        dst_dir=_rules_dst_dir(),
        pattern="*.md",
        force=force,
    )
    return [{"path": f"{rel}/{r.pop('name')}", **r} for r in results]


def _rule_status_entries() -> list[dict]:
    """Report current state of each log-owned rule file."""
    src_dir = _rules_src_dir()
    if not src_dir.is_dir():
        return []

    rel = _rules_rel_prefix()
    dst_dir = _rules_dst_dir()
    entries = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        state = plugin.compare_deployed(src, dst_dir / src.name)
        entries.append({
            "path": f"{rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return entries


def init(force: bool = False) -> dict:
    """Deploy log-type templates and log-owned rules."""
    src_dir = _templates_dir()
    target = _target_dir()
    rel = _deployed_rel()
    files = []

    if src_dir.is_dir():
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

    files.extend(_deploy_rules(force))

    return {"files": files, "extra": []}


def status() -> dict:
    """Report log-type deployment and rule deployment state."""
    src_dir = _templates_dir()
    target = _target_dir()
    rel = _deployed_rel()
    files = []

    if src_dir.is_dir():
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

    files.extend(_rule_status_entries())

    return {"files": files, "extra": []}
