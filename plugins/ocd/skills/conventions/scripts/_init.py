"""Conventions initialization and status.

Template deployment, manifest management, and infrastructure health checks.
Business logic for deploy operations lives in _deploy.py.
"""

import logging
from pathlib import Path

try:
    from . import conventions
except ImportError:
    import conventions  # type: ignore[import-not-found]

try:
    from _deploy import deploy_files, get_plugin_root, get_project_dir
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))
    from _deploy import deploy_files, get_plugin_root, get_project_dir  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


def get_conventions_dir(project_dir: Path) -> Path:
    return project_dir / ".claude" / "ocd" / "conventions"


def get_manifest_path(project_dir: Path) -> Path:
    return get_conventions_dir(project_dir) / "manifest.yaml"


def init(plugin_root: Path, project_dir: Path, force: bool = False) -> list[str]:
    """Deploy convention templates and manifest. Returns status lines."""
    templates_src = plugin_root / "templates" / "conventions"

    if not templates_src.is_dir():
        return ["No convention templates found in plugin"]

    results = deploy_files(
        src_dir=templates_src,
        dst_dir=get_conventions_dir(project_dir),
        pattern="*",
        force=force,
    )

    lines = []
    for r in results:
        if r["before"] == r["after"]:
            state = r["after"].capitalize()
        else:
            state = f"{r['before']} → {r['after']}"
        lines.append(f"{state}: {r['name']}")

    return lines


def status(project_dir: Path) -> dict:
    """Check conventions infrastructure state.

    Returns dict with:
    - state: "operational" | "adopted" | "error"
    - details: list of human-readable status lines
    - actions: list of actionable commands
    """
    manifest_path = get_manifest_path(project_dir)

    if not manifest_path.exists():
        return {
            "state": "adopted",
            "details": ["Manifest: not found"],
            "actions": ["Run /ocd-init to deploy conventions"],
        }

    try:
        manifest = conventions.load_manifest(manifest_path)
    except Exception as e:
        return {
            "state": "error",
            "details": [f"Manifest: {e}"],
            "actions": ["Run /ocd-init --force to redeploy conventions"],
        }

    validation = conventions.validate_manifest(manifest_path)
    missing = validation["missing"]
    untracked = validation["untracked"]

    details = [f"Conventions: {len(manifest)} in manifest"]
    actions = []

    if missing:
        details.append(f"Missing from disk: {', '.join(Path(p).name for p in missing)}")
        actions.append("Run /ocd-init to deploy missing convention files")

    if untracked:
        details.append(f"Untracked: {', '.join(Path(p).name for p in untracked)}")
        actions.append("Add untracked files to manifest.yaml or remove from conventions dir")

    state = "operational"
    if missing:
        state = "error"

    return {
        "state": state,
        "details": details,
        "actions": actions,
    }
