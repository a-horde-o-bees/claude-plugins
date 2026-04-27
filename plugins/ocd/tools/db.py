"""Schema-aware initialization helpers for SQLite-backed systems.

DB-backed systems compose these helpers the same way file-backed systems
compose `setup.deploy_files` — the system declares its DB location and
schema builder, and the helper resolves the schema-aware contract:
inventory the live DB, no-op when current, refuse divergent without
force, back up and rebuild when force authorizes destruction. See
python.md *Init/Status Contract* and *Force semantics*.

Primitives (schema_signature, schemas_match, matches_expected,
write_backup, backup_path) are exposed for tests and for systems that
need to compose around the standard rectify/reset_db flow.
"""

import functools
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from tools.errors import InitError


# Schema builder: callable that creates/upgrades a DB at the given path.
# Used by rectify(), reset_db(), and matches_expected() to know what
# the canonical schema looks like without hardcoding it here.
SchemaBuilder = Callable[[str], object]


def schema_signature(db_path: Path) -> dict:
    """Return canonical schema structure derived from SQLite introspection.

    sqlite_master.sql preserves the original DDL text — whitespace,
    quoting, default-expression formatting — all syntactic choices that
    don't affect schema semantics. Comparing those strings flags
    style-only edits as schema migrations. This walks the tables via
    PRAGMA queries and builds a structural signature: columns with
    their types and constraints, foreign keys, and user-declared
    indexes. Auto-indexes from PRIMARY KEY/UNIQUE constraints are
    filtered out so they don't register as user-declared schema
    differences.
    """
    conn = sqlite3.connect(db_path)
    try:
        tables: dict = {}
        for (name,) in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        ).fetchall():
            columns = conn.execute(f'PRAGMA table_info("{name}")').fetchall()
            foreign_keys = conn.execute(
                f'PRAGMA foreign_key_list("{name}")'
            ).fetchall()
            index_rows = conn.execute(
                f'PRAGMA index_list("{name}")'
            ).fetchall()
            user_indexes: dict = {}
            for idx in index_rows:
                idx_name, unique, origin = idx[1], idx[2], idx[3]
                if origin != "c":
                    continue
                idx_info = conn.execute(
                    f'PRAGMA index_info("{idx_name}")'
                ).fetchall()
                user_indexes[idx_name] = {
                    "unique": unique,
                    "columns": sorted(idx_info),
                }
            tables[name] = {
                "columns": sorted(columns),
                "foreign_keys": sorted(foreign_keys),
                "indexes": user_indexes,
            }
        return tables
    finally:
        conn.close()


def schemas_match(a: Path, b: Path) -> bool:
    """True when two SQLite DBs produce equal structural signatures."""
    return schema_signature(a) == schema_signature(b)


def matches_expected(db_path: Path, schema_builder: SchemaBuilder) -> bool:
    """True when db_path's schema matches what schema_builder would produce.

    The canonical signature for a given schema_builder is cached at the
    process level — schema_builder is deterministic, so building a fresh
    expected DB on every call is wasted work. First call pays the
    full build-and-introspect cost (~15ms for typical schemas);
    subsequent calls only signature the live DB (~3ms).

    Returns False for non-SQLite files and any other state that prevents
    a clean signature comparison — readiness checks should never raise on
    a present-but-broken DB file.
    """
    if not db_path.exists():
        return False
    try:
        return schema_signature(db_path) == _canonical_signature(schema_builder)
    except sqlite3.Error:
        return False


@functools.cache
def _canonical_signature(schema_builder: SchemaBuilder) -> dict:
    """Build the schema_builder's canonical DB once and return its signature.

    Memoized per schema_builder identity. Process-scoped — cache resets
    on process boundary, which is the right granularity since
    schema_builder code can change across processes but is deterministic
    within one.
    """
    with tempfile.TemporaryDirectory() as tmp:
        expected = Path(tmp) / "expected.db"
        schema_builder(str(expected))
        return schema_signature(expected)


def backup_path(db_path: Path) -> Path:
    """Backup filename with ISO-8601 UTC timestamp beside the DB."""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    return db_path.with_name(f"{db_path.name}.backup-{ts}")


def write_backup(db_path: Path) -> Path:
    """Copy db_path to a timestamped backup beside it. Returns backup path."""
    target = backup_path(db_path)
    shutil.copy2(db_path, target)
    return target


def rectify(
    db_path: Path,
    schema_builder: SchemaBuilder,
    rel_path: str,
    force: bool = False,
) -> list[dict]:
    """Bring a SQLite DB into structural alignment with schema_builder.

    Mirrors `setup.deploy_files` for DB rectification — the system
    declares where its DB lives and what schema it should have; this
    helper resolves the inventory + no-op + backup + rebuild flow
    described in python.md *Force semantics*.

    Behavior:
    - Schema absent → build fresh; emit `absent → current`
    - Schema current → no-op; emit `current → current`
    - Schema divergent + not force → raise InitError
    - Schema divergent + force → write timestamped backup beside the
      live DB, wipe, rebuild; emit a backup entry plus
      `divergent → reinstalled`

    Returns `files` entries for the system to fold into its init result.
    """
    state = _schema_state(db_path, schema_builder)

    if state == "current":
        return [{"path": rel_path, "before": "current", "after": "current"}]

    if state == "divergent" and not force:
        raise InitError(
            f"{rel_path} has a divergent schema. Re-run with --force to "
            f"back up the current file and rebuild, or invoke the system's "
            f"`reset` verb to wipe and start fresh."
        )

    files: list[dict] = []

    if state == "divergent":
        backup = write_backup(db_path)
        backup_rel = _relative_backup_path(backup, rel_path)
        files.append({"path": backup_rel, "before": "absent", "after": "current"})
        db_path.unlink()
        before = "divergent"
        after = "reinstalled"
    else:
        before = "absent"
        after = "current"

    schema_builder(str(db_path))
    files.append({"path": rel_path, "before": before, "after": after})
    return files


def reset_db(
    db_path: Path,
    schema_builder: SchemaBuilder,
    rel_path: str,
) -> list[dict]:
    """Always-destructive rebuild — backup, wipe, rebuild regardless of schema state.

    The explicit destructive verb that `init(force=True)` no longer
    carries. Use when a user wants to start fresh regardless of whether
    the live schema matches expected.

    Returns `files` entries reporting the backup (when present) and the
    DB transition.
    """
    files: list[dict] = []

    if db_path.exists():
        backup = write_backup(db_path)
        backup_rel = _relative_backup_path(backup, rel_path)
        files.append({"path": backup_rel, "before": "absent", "after": "current"})
        db_path.unlink()
        before = "current"
        after = "reinstalled"
    else:
        before = "absent"
        after = "current"

    schema_builder(str(db_path))
    files.append({"path": rel_path, "before": before, "after": after})
    return files


def _schema_state(
    db_path: Path, schema_builder: SchemaBuilder,
) -> str:
    """Return 'absent', 'current', 'divergent', or 'error'."""
    if not db_path.exists():
        return "absent"
    try:
        if matches_expected(db_path, schema_builder):
            return "current"
        return "divergent"
    except sqlite3.Error:
        return "error"


def _relative_backup_path(backup: Path, rel_path: str) -> str:
    """Return a project-relative path for a backup file.

    The backup sits beside the live DB (same parent), so its
    project-relative form is rel_path's parent + the backup filename.
    """
    parent_rel = "/".join(rel_path.split("/")[:-1])
    return f"{parent_rel}/{backup.name}"
