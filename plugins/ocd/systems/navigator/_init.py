"""Navigator skill infrastructure.

Initialize the navigator database (paths, path_patterns, and
path_pattern_sources tables), deploy navigator-owned rule files, and
report DB health. Governance (rules, conventions, dependency graph) is
owned by the separate governance skill and initialized there.

The schema-aware init contract is owned by `tools.db.rectify`; this
module declares where the DB lives and what schema it should have, then
composes that helper alongside the file-deploy helpers
(`setup.deploy_files`, `setup.deploy_paths_csv`).

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

from systems import setup
from tools import db as dbtools
from tools import environment
from tools.errors import NotReadyError

from . import _db


def _plugin_name() -> str:
    return setup.get_plugin_name(environment.get_plugin_root())


def _db_path() -> Path:
    return (
        environment.get_project_dir()
        / ".claude"
        / _plugin_name()
        / "navigator"
        / "navigator.db"
    )


def _db_rel_path() -> str:
    return f".claude/{_plugin_name()}/navigator/navigator.db"


def _build_schema(target_path: str) -> None:
    """Build navigator's canonical schema at target_path."""
    _db.init_db(target_path)


def _rules_src_dir() -> Path:
    return environment.get_plugin_root() / "systems" / "navigator" / "rules"


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


def ready(db_path: Path | None = None) -> bool:
    """Return True when the navigator database structurally matches expected."""
    target = db_path if db_path is not None else _db_path()
    return target.exists() and dbtools.matches_expected(target, _build_schema)


def ensure_ready(db_path: Path | None = None) -> None:
    """Raise NotReadyError when navigator is not operational."""
    if not ready(db_path):
        raise NotReadyError(
            "Navigator is dormant — run /ocd:setup init to initialize."
        )


def _status_extra() -> list[dict]:
    """Check DB health and return the overall status line."""
    db_path = _db_path()

    if not db_path.exists():
        return [{"label": "overall status", "value": "not initialized"}]
    if not ready(db_path):
        return [{"label": "overall status", "value": "error — divergent schema"}]

    try:
        conn = _db.get_connection(str(db_path))
        total = conn.execute(
            "SELECT COUNT(*) as c FROM paths",
        ).fetchone()["c"]
        undescribed = conn.execute(
            "SELECT COUNT(*) as c FROM paths WHERE purpose IS NULL",
        ).fetchone()["c"]
        stale = conn.execute(
            "SELECT COUNT(*) as c FROM paths WHERE stale = 1",
        ).fetchone()["c"]
        conn.close()
        return [
            {
                "label": "overall status",
                "value": (
                    f"operational — {total} paths, "
                    f"{undescribed} undescribed, {stale} stale"
                ),
            },
        ]
    except sqlite3.Error as e:
        return [{"label": "overall status", "value": f"error — {e}"}]


def _deploy_rules(force: bool) -> list[dict]:
    """Deploy navigator-owned rule files to the plugin's rule corpus."""
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
    """Report current state of each navigator-owned rule file."""
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
    """Rectify navigator infrastructure to current templates and schema."""
    files = dbtools.rectify(
        _db_path(), _build_schema, _db_rel_path(), force=force,
    )

    paths_entry = setup.deploy_paths_csv(
        environment.get_plugin_root(),
        environment.get_project_dir(),
        "navigator",
        force=force,
    )
    if paths_entry is not None:
        files.append(paths_entry)

    files.extend(_deploy_rules(force))
    return {"files": files, "extra": _status_extra()}


def reset() -> dict:
    """Backup, wipe, and rebuild the navigator database.

    File-deploy paths (paths.csv + rules) run with force=True for full
    rectification alongside the destructive DB rebuild.
    """
    files = dbtools.reset_db(_db_path(), _build_schema, _db_rel_path())

    paths_entry = setup.deploy_paths_csv(
        environment.get_plugin_root(),
        environment.get_project_dir(),
        "navigator",
        force=True,
    )
    if paths_entry is not None:
        files.append(paths_entry)

    files.extend(_deploy_rules(True))
    return {"files": files, "extra": _status_extra()}


def status() -> dict:
    """Check navigator DB and rule deployment state."""
    db = _db_path()
    rel_path = _db_rel_path()

    if not db.exists():
        state = "absent"
    elif ready(db):
        state = "current"
    else:
        state = "divergent"

    files = [{"path": rel_path, "before": state, "after": state}]
    files.extend(_rule_status_entries())
    return {"files": files, "extra": _status_extra()}
