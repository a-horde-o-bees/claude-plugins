"""Governance skill infrastructure.

Deploy convention templates, initialize the governance database, and
load governance data from frontmatter. Check DB health and report
convention deployment state.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
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
        / "governance"
        / "governance.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/governance/governance.db"


def _status_extra() -> list[dict]:
    """Check governance DB health and return extra status lines."""
    db_path = _db_path()

    if not db_path.exists():
        return [
            {"label": "overall status", "value": "not initialized"},
            {"label": "action needed", "value": "/init"},
        ]

    try:
        conn = _db.get_connection(str(db_path))

        expected_tables = {
            "conventions",
            "convention_includes",
            "convention_excludes",
            "rules",
            "governance_depends_on",
            "config",
        }
        actual_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
        }
        if not expected_tables.issubset(actual_tables):
            conn.close()
            return [
                {"label": "overall status", "value": "error \u2014 divergent schema"},
                {"label": "action needed", "value": "/init --force"},
            ]

        rule_count = conn.execute(
            "SELECT COUNT(*) as c FROM rules"
        ).fetchone()["c"]
        conv_count = conn.execute(
            "SELECT COUNT(*) as c FROM conventions"
        ).fetchone()["c"]
        edge_count = conn.execute(
            "SELECT COUNT(*) as c FROM governance_depends_on"
        ).fetchone()["c"]

        conn.close()

        return [
            {
                "label": "overall status",
                "value": (
                    f"operational \u2014 {rule_count} rules, "
                    f"{conv_count} conventions, {edge_count} dependency edges"
                ),
            },
            {"label": "action needed", "value": "/evaluate-governance"},
        ]

    except sqlite3.Error as e:
        return [
            {"label": "overall status", "value": f"error \u2014 {e}"},
            {"label": "action needed", "value": "/init --force"},
        ]


_FRAMEWORK_DOCS = {"README.md", "architecture.md"}


def _deploy_conventions(force: bool) -> list[dict]:
    """Deploy convention templates to .claude/conventions/<plugin>/. Returns file status list."""
    plugin_name = _plugin_name()
    conv_src = plugin.get_plugin_root() / "conventions"
    conv_dst = plugin.get_project_dir() / ".claude" / "conventions" / plugin_name

    files = []
    results = plugin.deploy_files(
        src_dir=conv_src,
        dst_dir=conv_dst,
        pattern="*",
        force=force,
        exclude=_FRAMEWORK_DOCS,
    )
    for r in results:
        files.append(
            {
                "path": f".claude/conventions/{plugin_name}/{r['name']}",
                "before": r["before"],
                "after": r["after"],
            }
        )

    return files


def _conventions_status() -> list[dict]:
    """Check convention deployment states. Returns file status list."""
    plugin_name = _plugin_name()
    conv_src = plugin.get_plugin_root() / "conventions"
    conv_dst = plugin.get_project_dir() / ".claude" / "conventions" / plugin_name

    files = []
    if conv_src.is_dir():
        for src in sorted(conv_src.glob("*")):
            if not src.is_file():
                continue
            if src.name in _FRAMEWORK_DOCS:
                continue
            dst = conv_dst / src.name
            state = plugin.compare_deployed(src, dst)
            files.append(
                {
                    "path": f".claude/conventions/{plugin_name}/{src.name}",
                    "before": state,
                    "after": state,
                }
            )

    return files


def init(force: bool = False) -> dict:
    """Deploy conventions and initialize governance database."""
    files = _deploy_conventions(force)

    db = _db_path()
    rel_path = _db_rel_path()

    before = "current" if db.exists() else "absent"

    if force and db.exists():
        db.unlink()
        before = "absent"

    _db.init_db(str(db))
    governance_load(str(db))

    files.append({"path": rel_path, "before": before, "after": "current"})
    extra = [{"label": "overall status", "value": "initialized"}]

    status_extra = _status_extra()
    for item in status_extra:
        if item["label"] == "action needed":
            extra.append(item)

    return {"files": files, "extra": extra}


def status() -> dict:
    """Check convention deployment and governance DB state."""
    files = _conventions_status()

    db = _db_path()
    rel_path = _db_rel_path()

    state = "current" if db.exists() else "absent"
    files.append({"path": rel_path, "before": state, "after": state})

    extra = _status_extra()
    return {"files": files, "extra": extra}
