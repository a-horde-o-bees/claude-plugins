"""Navigator skill infrastructure.

Deploy conventions and manifest, initialize database with seeds,
and check DB health.
Interface contract: init() and status() return {"files": [...], "extra": [...]}.
"""

import shutil
import sqlite3
from pathlib import Path

from . import _db, governance_load
import plugin


def _db_path(plugin_name: str, project_dir: Path) -> Path:
    return project_dir / ".claude" / plugin_name / "navigator" / "navigator.db"


def _db_rel_path(plugin_name: str) -> str:
    return f".claude/{plugin_name}/navigator/navigator.db"


def _status_extra(plugin_name: str, project_dir: Path) -> list[dict]:
    """Check DB health and return extra lines."""
    db_path = _db_path(plugin_name, project_dir)

    if not db_path.exists():
        return [
            {"label": "overall status", "value": "not initialized"},
            {"label": "action needed", "value": "/ocd-init"},
        ]

    try:
        conn = _db.get_connection(str(db_path))

        expected_tables = {"entries", "governance", "governs", "config"}
        actual_tables = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'",
        ).fetchall()}
        if not expected_tables.issubset(actual_tables):
            conn.close()
            return [
                {"label": "overall status", "value": "error \u2014 divergent schema"},
                {"label": "action needed", "value": "/ocd-init --force"},
            ]

        total = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE path NOT LIKE '%*%'",
        ).fetchone()["c"]

        undescribed = conn.execute(
            "SELECT COUNT(*) as c FROM entries "
            "WHERE path NOT LIKE '%*%' AND description IS NULL",
        ).fetchone()["c"]

        stale = conn.execute(
            "SELECT COUNT(*) as c FROM entries "
            "WHERE path NOT LIKE '%*%' AND stale = 1",
        ).fetchone()["c"]

        conn.close()

        extra = [{"label": "overall status", "value": f"operational \u2014 {total} entries, {undescribed} undescribed, {stale} stale"}]
        extra.append({"label": "action needed", "value": "/ocd-navigator"})

        return extra

    except sqlite3.Error as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "/ocd-init --force"},
        ]


def _deploy_conventions(
    plugin_root: Path, project_dir: Path, plugin_name: str, force: bool,
) -> list[dict]:
    """Deploy convention templates and manifest. Returns file status list."""
    conv_src = plugin_root / "conventions"
    conv_dst = project_dir / ".claude" / plugin_name / "conventions"
    rel_prefix = f".claude/{plugin_name}/conventions"

    files = []
    results = plugin.deploy_files(
        src_dir=conv_src, dst_dir=conv_dst, pattern="*", force=force,
    )
    for r in results:
        files.append({"path": f"{rel_prefix}/{r['name']}", "before": r["before"], "after": r["after"]})

    # Manifest lives at plugin level, not inside conventions
    manifest_src = plugin_root / "manifest.yaml"
    manifest_dst = project_dir / ".claude" / plugin_name / "manifest.yaml"
    if manifest_src.is_file():
        before = plugin.compare_deployed(manifest_src, manifest_dst)
        if before == "absent" or force:
            manifest_dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(manifest_src, manifest_dst)
            files.append({"path": f".claude/{plugin_name}/manifest.yaml", "before": before, "after": "current"})
        else:
            files.append({"path": f".claude/{plugin_name}/manifest.yaml", "before": before, "after": before})

    return files


def _conventions_status(
    plugin_root: Path, project_dir: Path, plugin_name: str,
) -> list[dict]:
    """Check convention and manifest deployment states. Returns file status list."""
    conv_src = plugin_root / "conventions"
    conv_dst = project_dir / ".claude" / plugin_name / "conventions"
    rel_prefix = f".claude/{plugin_name}/conventions"

    files = []
    if conv_src.is_dir():
        for src in sorted(conv_src.glob("*")):
            if not src.is_file():
                continue
            dst = conv_dst / src.name
            state = plugin.compare_deployed(src, dst)
            files.append({"path": f"{rel_prefix}/{src.name}", "before": state, "after": state})

    manifest_src = plugin_root / "manifest.yaml"
    manifest_dst = project_dir / ".claude" / plugin_name / "manifest.yaml"
    if manifest_src.is_file():
        state = plugin.compare_deployed(manifest_src, manifest_dst)
        files.append({"path": f".claude/{plugin_name}/manifest.yaml", "before": state, "after": state})

    return files


def init(plugin_root: Path, project_dir: Path, force: bool = False) -> dict:
    """Deploy conventions and initialize navigator database. Returns {files, extra}."""
    plugin_name = plugin.get_plugin_name(plugin_root)

    # Deploy conventions and manifest
    files = _deploy_conventions(plugin_root, project_dir, plugin_name, force)

    # Initialize database
    db = _db_path(plugin_name, project_dir)
    rel_path = _db_rel_path(plugin_name)

    before = "current" if db.exists() else "absent"

    if force and db.exists():
        db.unlink()
        before = "absent"

    result_msg = _db.init_db(str(db))

    # Load governance data from manifest if available
    manifest = project_dir / ".claude" / plugin_name / "manifest.yaml"
    if manifest.exists():
        governance_load(str(db), str(manifest))

    after = "current"
    summary = ""
    if "(seed rules:" in result_msg:
        seed_part = result_msg.split("(seed rules: ")[1].rstrip(")")
        summary = f"initialized \u2014 seed rules: {seed_part}"
    elif "(no seed file)" in result_msg:
        summary = "initialized \u2014 no seed file"
    else:
        summary = "initialized"

    files.append({"path": rel_path, "before": before, "after": after})
    extra = [{"label": "overall status", "value": summary}]

    # Add action needed from status check
    status_extra = _status_extra(plugin_name, project_dir)
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status(plugin_root: Path, project_dir: Path) -> dict:
    """Check convention deployment and navigator DB state. Returns {files, extra}."""
    plugin_name = plugin.get_plugin_name(plugin_root)

    # Convention and manifest deployment states
    files = _conventions_status(plugin_root, project_dir, plugin_name)

    # Database state
    db = _db_path(plugin_name, project_dir)
    rel_path = _db_rel_path(plugin_name)

    state = "current" if db.exists() else "absent"
    files.append({"path": rel_path, "before": state, "after": state})

    extra = _status_extra(plugin_name, project_dir)
    return {"files": files, "extra": extra}
