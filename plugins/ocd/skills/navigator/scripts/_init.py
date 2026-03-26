"""Navigator skill infrastructure.

Initialize database with seeds and check DB health.
Interface contract: init() and status() return {"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

import _db  # type: ignore[import-not-found]
import plugin  # type: ignore[import-not-found]


def _db_path(plugin_name: str, project_dir: Path) -> Path:
    return project_dir / ".claude" / plugin_name / "navigator" / "navigator.db"


def _db_rel_path(plugin_name: str) -> str:
    return f".claude/{plugin_name}/navigator/navigator.db"


def _status_extra(plugin_name: str, project_dir: Path) -> list[dict]:
    """Check DB health and return extra lines."""
    db_path = _db_path(plugin_name, project_dir)

    if not db_path.exists():
        return [
            {"label": "overall status", "value": "adopted \u2014 database not found"},
            {"label": "action needed", "value": "Run /ocd-init to create navigator database"},
        ]

    try:
        conn = _db.get_connection(str(db_path))

        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='entries'",
        ).fetchone()
        if not tables:
            conn.close()
            return [
                {"label": "overall status", "value": "error \u2014 missing entries table"},
                {"label": "action needed", "value": "Run /ocd-init to reinitialize navigator database"},
            ]

        total = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE path NOT LIKE '%*%'",
        ).fetchone()["c"]

        if total == 0:
            conn.close()
            return [
                {"label": "overall status", "value": "ready \u2014 no entries"},
                {"label": "action needed", "value": "Run /ocd-navigator to scan and describe project"},
            ]

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

        if undescribed > 0 or stale > 0:
            parts = []
            if undescribed > 0:
                parts.append(f"describe {undescribed} entries")
            if stale > 0:
                parts.append(f"review {stale} stale entries")
            extra.append({"label": "action needed", "value": f"Run /ocd-navigator to {' and '.join(parts)}"})

        return extra

    except sqlite3.Error as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "Run /ocd-init to reinitialize navigator database"},
        ]


def init(plugin_root: Path, project_dir: Path, force: bool = False) -> dict:
    """Initialize navigator database. Returns {files, extra}."""
    plugin_name = plugin.get_plugin_name(plugin_root)
    db = _db_path(plugin_name, project_dir)
    rel_path = _db_rel_path(plugin_name)

    before = "current" if db.exists() else "absent"

    if force and db.exists():
        db.unlink()
        before = "absent"

    result_msg = _db.init_db(str(db))

    after = "current"
    summary = ""
    if "(seed rules:" in result_msg:
        seed_part = result_msg.split("(seed rules: ")[1].rstrip(")")
        summary = f"initialized \u2014 seed rules: {seed_part}"
    elif "(no seed file)" in result_msg:
        summary = "initialized \u2014 no seed file"
    else:
        summary = "initialized"

    files = [{"path": rel_path, "before": before, "after": after}]
    extra = [{"label": "overall status", "value": summary}]

    # Add action needed from status check
    status_extra = _status_extra(plugin_name, project_dir)
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status(plugin_root: Path, project_dir: Path) -> dict:
    """Check navigator DB state. Returns {files, extra}."""
    plugin_name = plugin.get_plugin_name(plugin_root)
    db = _db_path(plugin_name, project_dir)
    rel_path = _db_rel_path(plugin_name)

    state = "current" if db.exists() else "absent"
    files = [{"path": rel_path, "before": state, "after": state}]

    extra = _status_extra(plugin_name, project_dir)
    return {"files": files, "extra": extra}
