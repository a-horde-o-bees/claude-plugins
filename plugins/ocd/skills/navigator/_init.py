"""Navigator skill infrastructure.

Deploy conventions, initialize database with seeds, and load governance
from frontmatter. Check DB health.
Interface contract: init() and status() return {"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

import plugin

from . import _db, governance_load


def _plugin_name() -> str:
    return plugin.get_plugin_name(plugin.get_plugin_root())


def _db_path() -> Path:
    return (
        plugin.get_project_dir()
        / ".claude"
        / _plugin_name()
        / "navigator"
        / "navigator.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/navigator/navigator.db"


def _status_extra() -> list[dict]:
    """Check DB health and return extra lines."""
    db_path = _db_path()

    if not db_path.exists():
        return [
            {"label": "overall status", "value": "not initialized"},
            {"label": "action needed", "value": "/ocd-init"},
        ]

    try:
        conn = _db.get_connection(str(db_path))

        expected_tables = {"entries", "conventions", "rules", "config"}
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
            "SELECT COUNT(*) as c FROM entries",
        ).fetchone()["c"]

        undescribed = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE description IS NULL",
        ).fetchone()["c"]

        stale = conn.execute(
            "SELECT COUNT(*) as c FROM entries WHERE stale = 1",
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


def _deploy_conventions(force: bool) -> list[dict]:
    """Deploy convention templates to .claude/conventions/. Returns file status list."""
    conv_src = plugin.get_plugin_root() / "conventions"
    conv_dst = plugin.get_project_dir() / ".claude" / "conventions"

    files = []
    results = plugin.deploy_files(
        src_dir=conv_src, dst_dir=conv_dst, pattern="*", force=force,
    )
    for r in results:
        files.append({"path": f".claude/conventions/{r['name']}", "before": r["before"], "after": r["after"]})

    return files


def _conventions_status() -> list[dict]:
    """Check convention deployment states. Returns file status list."""
    conv_src = plugin.get_plugin_root() / "conventions"
    conv_dst = plugin.get_project_dir() / ".claude" / "conventions"

    files = []
    if conv_src.is_dir():
        for src in sorted(conv_src.glob("*")):
            if not src.is_file():
                continue
            dst = conv_dst / src.name
            state = plugin.compare_deployed(src, dst)
            files.append({"path": f".claude/conventions/{src.name}", "before": state, "after": state})

    return files


def init(force: bool = False) -> dict:
    """Deploy conventions and initialize navigator database. Returns {files, extra}."""
    # Deploy conventions to .claude/conventions/
    files = _deploy_conventions(force)

    # Initialize database
    db = _db_path()
    rel_path = _db_rel_path()

    before = "current" if db.exists() else "absent"

    if force and db.exists():
        db.unlink()
        before = "absent"

    result_msg = _db.init_db(str(db))

    # Load governance from frontmatter in rules and conventions
    governance_load(str(db))

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
    status_extra = _status_extra()
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status() -> dict:
    """Check convention deployment and navigator DB state. Returns {files, extra}."""
    # Convention deployment states
    files = _conventions_status()

    # Database state
    db = _db_path()
    rel_path = _db_rel_path()

    state = "current" if db.exists() else "absent"
    files.append({"path": rel_path, "before": state, "after": state})

    extra = _status_extra()
    return {"files": files, "extra": extra}
