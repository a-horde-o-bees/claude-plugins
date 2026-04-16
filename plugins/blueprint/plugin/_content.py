"""Content deployment and state tracking.

Deploy and query state for rules, conventions, patterns, and log
templates between plugin source directories and project targets.
"""

from pathlib import Path

from ._deployment import compare_deployed, deploy_files
from ._metadata import get_plugin_name


# --- Rules ---


def deploy_rules(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy rule files. Returns [{path, before, after}] with relative deployed paths.

    Rules deploy to .claude/rules/{plugin_name}/ per-plugin subfolder for
    cross-plugin collision avoidance. Templates live at lib/rules/templates/.
    """
    plugin_name = get_plugin_name(plugin_root)
    deployed_rel = f".claude/rules/{plugin_name}"
    results = deploy_files(
        src_dir=plugin_root / "lib" / "rules" / "templates",
        dst_dir=project_dir / ".claude" / "rules" / plugin_name,
        pattern="*.md",
        force=force,
    )
    for r in results:
        r["path"] = f"{deployed_rel}/{r.pop('name')}"
    return results


def get_rules_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each rule file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "lib" / "rules" / "templates"
    if not src_dir.is_dir():
        return []

    plugin_name = get_plugin_name(plugin_root)
    deployed_rel = f".claude/rules/{plugin_name}"
    results = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        dst = project_dir / ".claude" / "rules" / plugin_name / src.name
        state = compare_deployed(src, dst)
        results.append({
            "path": f"{deployed_rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return results


# --- Conventions ---


def deploy_conventions(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy convention files. Returns [{path, before, after}] with relative deployed paths.

    Conventions deploy to .claude/conventions/{plugin_name}/ per-plugin subfolder.
    Templates live at lib/conventions/templates/.
    """
    plugin_name = get_plugin_name(plugin_root)
    deployed_rel = f".claude/conventions/{plugin_name}"
    results = deploy_files(
        src_dir=plugin_root / "lib" / "conventions" / "templates",
        dst_dir=project_dir / ".claude" / "conventions" / plugin_name,
        pattern="*.md",
        force=force,
    )
    for r in results:
        r["path"] = f"{deployed_rel}/{r.pop('name')}"
    return results


def get_conventions_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each convention file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "lib" / "conventions" / "templates"
    if not src_dir.is_dir():
        return []

    plugin_name = get_plugin_name(plugin_root)
    deployed_rel = f".claude/conventions/{plugin_name}"
    results = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        dst = project_dir / ".claude" / "conventions" / plugin_name / src.name
        state = compare_deployed(src, dst)
        results.append({
            "path": f"{deployed_rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return results


# --- Patterns ---


def deploy_patterns(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy pattern files. Returns [{path, before, after}] with relative deployed paths.

    Patterns deploy to .claude/patterns/{plugin_name}/ per-plugin subfolder.
    Templates live at lib/patterns/templates/.
    """
    plugin_name = get_plugin_name(plugin_root)
    deployed_rel = f".claude/patterns/{plugin_name}"
    results = deploy_files(
        src_dir=plugin_root / "lib" / "patterns" / "templates",
        dst_dir=project_dir / ".claude" / "patterns" / plugin_name,
        pattern="*.md",
        force=force,
    )
    for r in results:
        r["path"] = f"{deployed_rel}/{r.pop('name')}"
    return results


def get_patterns_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each pattern file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "lib" / "patterns" / "templates"
    if not src_dir.is_dir():
        return []

    plugin_name = get_plugin_name(plugin_root)
    deployed_rel = f".claude/patterns/{plugin_name}"
    results = []
    for src in sorted(src_dir.glob("*.md")):
        if not src.is_file():
            continue
        dst = project_dir / ".claude" / "patterns" / plugin_name / src.name
        state = compare_deployed(src, dst)
        results.append({
            "path": f"{deployed_rel}/{src.name}",
            "before": state,
            "after": state,
        })
    return results


# --- Logs ---


def deploy_logs(plugin_root: Path, project_dir: Path, force: bool = False) -> list[dict]:
    """Deploy log type templates. Returns [{path, before, after}] with relative deployed paths.

    Deploys _template.md from each type subdirectory in lib/logs/templates/
    to .claude/logs/{type}/_template.md. No plugin namespacing; logs are
    project-level infrastructure owned by the user after first deployment.
    """
    src_dir = plugin_root / "lib" / "logs" / "templates"
    dst_dir = project_dir / ".claude" / "logs"
    deployed_rel = ".claude/logs"
    results = []

    if not src_dir.is_dir():
        return results

    for type_dir in sorted(src_dir.iterdir()):
        if not type_dir.is_dir():
            continue
        type_name = type_dir.name
        for item in deploy_files(type_dir, dst_dir / type_name, pattern="*.md", force=force, keep_orphans=True):
            item["path"] = f"{deployed_rel}/{type_name}/{item.pop('name')}"
            results.append(item)

    return results


def get_logs_states(plugin_root: Path, project_dir: Path) -> list[dict]:
    """Get state of each log type template file. Returns [{path, before, after}]."""
    src_dir = plugin_root / "lib" / "logs" / "templates"
    if not src_dir.is_dir():
        return []

    dst_dir = project_dir / ".claude" / "logs"
    deployed_rel = ".claude/logs"
    results = []

    for type_dir in sorted(src_dir.iterdir()):
        if not type_dir.is_dir():
            continue
        type_name = type_dir.name
        for src in sorted(type_dir.glob("*.md")):
            if not src.is_file():
                continue
            dst = dst_dir / type_name / src.name
            state = compare_deployed(src, dst)
            results.append({
                "path": f"{deployed_rel}/{type_name}/{src.name}",
                "before": state,
                "after": state,
            })

    return results
