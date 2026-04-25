"""Navigator skill infrastructure.

Initialize the navigator database (paths, path_patterns, and
path_pattern_sources tables), deploy navigator-owned rule files, and
report DB health. Governance (rules, conventions, dependency graph) is
owned by the separate governance skill and initialized there.

Interface contract: init() and status() return
{"files": [...], "extra": [...]}.
"""

import sqlite3
from pathlib import Path

from systems import setup
from tools import environment
from tools.errors import NotReadyError

from . import _db


EXPECTED_TABLES = {"paths", "path_patterns", "path_pattern_sources", "config"}


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
    """Return True when the navigator database exists and has the full schema.

    Zero-arg form resolves the DB location via plugin helpers
    (CLAUDE_PROJECT_DIR). Pass an explicit path when checking a non-default
    location — tests, MCP server startup with DB_PATH override. Validates
    schema subset, not just file existence — a present DB with divergent
    schema counts as not ready.
    """
    target = db_path if db_path is not None else _db_path()
    if not target.exists():
        return False
    try:
        conn = _db.get_connection(str(target))
        actual_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
        }
        conn.close()
        return EXPECTED_TABLES.issubset(actual_tables)
    except sqlite3.Error:
        return False


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

    try:
        conn = _db.get_connection(str(db_path))

        actual_tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'",
            ).fetchall()
        }
        if not EXPECTED_TABLES.issubset(actual_tables):
            conn.close()
            return [{"label": "overall status", "value": "error \u2014 divergent schema"}]

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
                    f"operational \u2014 {total} paths, "
                    f"{undescribed} undescribed, {stale} stale"
                ),
            },
        ]

    except sqlite3.Error as e:
        return [{"label": "overall status", "value": f"error \u2014 {e}"}]


def _deploy_rules(force: bool) -> list[dict]:
    """Deploy navigator-owned rule files to the plugin's rule corpus.

    Navigator's rule lives with navigator's init rather than the plugin-wide
    rules pool so the prescription only reaches the agent once navigator is
    actually deployed — see System Dormancy in the project architecture.
    """
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
    """Initialize the navigator database, deploy paths.csv, and deploy rules.

    Captures the DB's state before any mutation so the reported transition
    reflects what the user saw, not the intermediate wipe state. A
    force-rebuild of an existing DB emits `current → reinstalled`; a
    fresh install emits `absent → current`. paths.csv deploys alongside
    the DB so the navigator scan can aggregate navigator's own declared
    artifacts into path_patterns on first walk. Rule files deploy to the
    plugin's rule corpus so navigator-specific guidance is only present
    when navigator is operational.
    """
    db = _db_path()
    rel_path = _db_rel_path()

    existed_before = db.exists()
    before = "current" if existed_before else "absent"

    if force and existed_before:
        db.unlink()

    _db.init_db(str(db))

    after = "reinstalled" if existed_before and force else "current"

    files = [{"path": rel_path, "before": before, "after": after}]

    paths_entry = setup.deploy_paths_csv(
        environment.get_plugin_root(),
        environment.get_project_dir(),
        "navigator",
        force=force,
    )
    if paths_entry is not None:
        files.append(paths_entry)

    files.extend(_deploy_rules(force))

    extra = _status_extra()
    return {"files": files, "extra": extra}


def status() -> dict:
    """Check navigator DB and rule deployment state."""
    db = _db_path()
    rel_path = _db_rel_path()

    state = "current" if db.exists() else "absent"
    files = [{"path": rel_path, "before": state, "after": state}]
    files.extend(_rule_status_entries())

    extra = _status_extra()
    return {"files": files, "extra": extra}
