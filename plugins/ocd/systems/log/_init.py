"""Logs subsystem.

Deploy log-type templates from systems/log/templates/<type>/ into
logs/<type>/ at project root — unnamespaced by plugin. Each plugin
contributes log types to a shared project-level pool; the user authors
log entries alongside the templates, so deployment uses keep_orphans
to preserve user content. Logs sit at project root rather than inside
.claude/ because they are project notes authored by the agent, not
Claude Code infrastructure — the sensitivity envelope around .claude/
does not apply to user content.

Also deploys log-owned rule files (log-routing) to the plugin's rule
corpus so the log routing prescription only reaches the agent once the
log system is deployed — see System Dormancy in the project
architecture.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

from pathlib import Path

from systems import setup
from tools import environment


def _plugin_name() -> str:
    return setup.get_plugin_name(environment.get_plugin_root())


def _templates_dir() -> Path:
    return environment.get_plugin_root() / "systems" / "log" / "templates"


def _target_dir() -> Path:
    return environment.get_project_dir() / "logs"


def _deployed_rel() -> str:
    return "logs"


def _rules_src_dir() -> Path:
    return environment.get_plugin_root() / "systems" / "log" / "rules"


def _rules_dst_dir() -> Path:
    return (
        environment.get_project_dir()
        / ".claude"
        / "rules"
        / _plugin_name()
        / "systems"
    )


def _rules_rel_prefix() -> str:
    return f".claude/rules/{_plugin_name()}/systems"


def _deploy_rules(force: bool) -> list[dict]:
    """Deploy log-owned rule files to the plugin's rule corpus."""
    rel = _rules_rel_prefix()
    results = setup.deploy_files(
        src_dir=_rules_src_dir(),
        dst_dir=_rules_dst_dir(),
        pattern="*.md",
        force=force,
        keep_orphans=True,
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
        state = setup.compare_deployed(src, dst_dir / src.name)
        entries.append({
            "path": f"{rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return entries


def init(force: bool = False) -> dict:
    """Deploy log-type templates, log-owned rules, and log's paths.csv.

    paths.csv carries the log system's pre-described path patterns for
    the `logs/` tree (entry directories, templates, research subject
    shape with traverse=0 on samples/ and context/ so per-entity files
    aren't individually indexed). Navigator's scan aggregates every
    system's deployed paths.csv via its `.claude/*/*/paths.csv`
    pattern, so deploying this file is how the log system registers
    its own domain's pre-descriptions.
    """
    src_dir = _templates_dir()
    target = _target_dir()
    rel = _deployed_rel()
    files = []

    if src_dir.is_dir():
        for type_dir in sorted(src_dir.iterdir()):
            if not type_dir.is_dir():
                continue
            type_name = type_dir.name
            results = setup.deploy_files(
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

    paths_entry = setup.deploy_paths_csv(
        environment.get_plugin_root(),
        environment.get_project_dir(),
        "log",
        force=force,
    )
    if paths_entry is not None:
        files.append(paths_entry)

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
                state = setup.compare_deployed(src, dst)
                files.append({
                    "path": f"{rel}/{type_name}/{src.name}",
                    "before": state,
                    "after": state,
                })

    files.extend(_rule_status_entries())

    return {"files": files, "extra": []}
