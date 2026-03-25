"""Conventions initialization and status.

Template deployment, manifest management, and infrastructure health checks.
"""

import logging
import os
import shutil
from pathlib import Path

try:
    from . import conventions
except ImportError:
    import conventions  # type: ignore[import-not-found]

logger = logging.getLogger(__name__)


def get_project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))


def get_plugin_root() -> Path:
    """Resolve plugin root from environment or script location."""
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    return Path(__file__).parent.parent.parent.parent


def get_conventions_dir(project_dir: Path) -> Path:
    return project_dir / ".claude" / "ocd" / "conventions"


def get_manifest_path(project_dir: Path) -> Path:
    return get_conventions_dir(project_dir) / "manifest.yaml"


def init(plugin_root: Path, project_dir: Path, force: bool = False) -> list[str]:
    """Deploy convention templates and manifest. Returns status lines."""
    templates_src = plugin_root / "templates" / "conventions"
    conventions_dst = get_conventions_dir(project_dir)
    conventions_dst.mkdir(parents=True, exist_ok=True)

    lines = []

    if not templates_src.is_dir():
        lines.append("No convention templates found in plugin")
        return lines

    for src in sorted(templates_src.iterdir()):
        if not src.is_file():
            continue
        dst = conventions_dst / src.name
        if dst.exists() and not force:
            lines.append(f"Skipped (exists): {src.name}")
            continue
        if dst.exists() and src.read_bytes() == dst.read_bytes():
            lines.append(f"Current: {src.name}")
            continue
        action = "Replaced" if dst.exists() else "New"
        shutil.copy2(src, dst)
        lines.append(f"{action}: {src.name}")

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
