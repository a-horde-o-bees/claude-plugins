"""Conventions skill infrastructure.

Deploy convention templates and validate manifest state.
Interface contract: init() and status() return {"files": [...], "extra": [...]}.
"""

from pathlib import Path

from . import *  # noqa: F403
from scripts import plugin


def _conventions_dir(plugin_name: str, project_dir: Path) -> Path:
    return project_dir / ".claude" / plugin_name / "conventions"


def _manifest_path(plugin_name: str, project_dir: Path) -> Path:
    return _conventions_dir(plugin_name, project_dir) / "manifest.yaml"


def _manifest_extra(plugin_name: str, project_dir: Path) -> list[dict]:
    """Validate manifest and return extra lines for overall status / action needed."""
    manifest_path = _manifest_path(plugin_name, project_dir)

    if not manifest_path.exists():
        return [
            {"label": "overall status", "value": "adopted \u2014 manifest not found"},
            {"label": "action needed", "value": "Run /ocd-init to deploy conventions"},
        ]

    try:
        manifest = load_manifest(manifest_path)
    except Exception as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "Run /ocd-init --force to redeploy conventions"},
        ]

    validation = validate_manifest(manifest_path)
    missing = validation["missing"]
    untracked = validation["untracked"]

    extra = []

    if missing:
        extra.append({"label": "overall status", "value": f"error \u2014 {len(manifest)} in manifest"})
        extra.append({"label": "action needed", "value": f"Missing from disk: {', '.join(Path(p).name for p in missing)}"})
        extra.append({"label": "action needed", "value": "Run /ocd-init to deploy missing convention files"})
    else:
        extra.append({"label": "overall status", "value": f"operational \u2014 {len(manifest)} in manifest"})

    if untracked:
        extra.append({"label": "action needed", "value": f"Untracked: {', '.join(Path(p).name for p in untracked)}"})
        extra.append({"label": "action needed", "value": "Add untracked files to manifest.yaml or remove from conventions dir"})

    return extra


def init(plugin_root: Path, project_dir: Path, force: bool = False) -> dict:
    """Deploy convention templates. Returns {files, extra}."""
    plugin_name = plugin.get_plugin_name(plugin_root)
    dst_dir = _conventions_dir(plugin_name, project_dir)

    results = plugin.deploy_files(
        src_dir=plugin_root / "templates" / "conventions",
        dst_dir=dst_dir,
        pattern="*",
        force=force,
    )

    rel_prefix = f".claude/{plugin_name}/conventions"
    files = []
    for r in results:
        files.append({"path": f"{rel_prefix}/{r['name']}", "before": r["before"], "after": r["after"]})

    extra = _manifest_extra(plugin_name, project_dir)
    return {"files": files, "extra": extra}


def status(plugin_root: Path, project_dir: Path) -> dict:
    """Check convention file states and manifest health. Returns {files, extra}."""
    plugin_name = plugin.get_plugin_name(plugin_root)
    src_dir = plugin_root / "templates" / "conventions"
    dst_dir = _conventions_dir(plugin_name, project_dir)
    rel_prefix = f".claude/{plugin_name}/conventions"

    files = []
    if src_dir.is_dir():
        for src in sorted(src_dir.glob("*")):
            if not src.is_file():
                continue
            dst = dst_dir / src.name
            state = plugin.compare_deployed(src, dst)
            files.append({"path": f"{rel_prefix}/{src.name}", "before": state, "after": state})

    extra = _manifest_extra(plugin_name, project_dir)
    return {"files": files, "extra": extra}
