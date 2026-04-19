"""Template deployment primitives.

Core operations for deploying template files to project directories:
comparison, batch file deployment with force/orphan control, and
systems' paths.csv declaration deployment with placeholder substitution.
"""

import shutil
from pathlib import Path

from ._metadata import get_plugin_name


def compare_deployed(src: Path, dst: Path) -> str:
    """Compare single source template against deployed file.

    Returns:
    - "absent": dst does not exist
    - "current": dst matches src exactly
    - "divergent": dst exists but content differs from src
    """
    if not dst.exists():
        return "absent"
    if src.read_bytes() == dst.read_bytes():
        return "current"
    return "divergent"


def deploy_files(
    src_dir: Path,
    dst_dir: Path,
    pattern: str = "*.md",
    force: bool = False,
    exclude: set[str] | None = None,
    keep_orphans: bool = False,
) -> list[dict]:
    """Deploy template files from src_dir to dst_dir.

    Returns list of {name, before, after} dicts. Files whose names are in
    exclude are skipped entirely — used for source-only documentation that
    should not deploy.

    When force is True, overwrites divergent deployed files and removes
    files in dst_dir that have no matching source template. Set
    keep_orphans=True when user content coexists with templates (e.g. logs).
    """
    dst_dir.mkdir(parents=True, exist_ok=True)
    results = []

    if not src_dir.is_dir():
        return results

    skip_names = exclude or set()

    if force and not keep_orphans:
        src_names = {s.name for s in src_dir.glob(pattern) if s.is_file() and s.name not in skip_names}
        for existing in dst_dir.glob(pattern):
            if existing.is_file() and existing.name not in src_names:
                existing.unlink()

    for src in sorted(src_dir.glob(pattern)):
        if src.name in skip_names:
            continue
        if not src.is_file():
            continue
        dst = dst_dir / src.name
        before = compare_deployed(src, dst)

        if before == "absent":
            shutil.copy2(src, dst)
            after = "current"
        elif before == "divergent" and force:
            shutil.copy2(src, dst)
            after = "current"
        else:
            after = before

        results.append({"name": src.name, "before": before, "after": after})

    return results


def deploy_paths_csv(
    plugin_root: Path,
    project_dir: Path,
    system_name: str,
    force: bool = False,
) -> dict | None:
    """Deploy a system's paths.csv declaration to the project.

    Reads systems/<system_name>/paths.csv from the plugin source,
    substitutes `{plugin}` with the plugin's name, and writes the
    resolved copy to .claude/<plugin>/<system_name>/paths.csv. Navigator
    aggregates all such deployed files into its path_patterns table at
    scan time, so deploying paths.csv is how a system registers its
    owned artifacts for navigator auto-description.

    Returns {path, before, after} for the system's init() result, or
    None when the system has no source paths.csv to deploy.
    """
    source = plugin_root / "systems" / system_name / "paths.csv"
    if not source.is_file():
        return None

    plugin_name = get_plugin_name(plugin_root)
    dst = project_dir / ".claude" / plugin_name / system_name / "paths.csv"
    deployed_rel = f".claude/{plugin_name}/{system_name}/paths.csv"

    resolved = source.read_text().replace("{plugin}", plugin_name)

    if not dst.exists():
        before = "absent"
    elif dst.read_text() == resolved:
        before = "current"
    else:
        before = "divergent"

    if before == "absent" or (before == "divergent" and force):
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(resolved)
        after = "current"
    else:
        after = before

    return {"path": deployed_rel, "before": before, "after": after}
