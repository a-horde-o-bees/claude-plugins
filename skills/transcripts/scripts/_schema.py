"""SQLite schema management primitives for the transcripts DB.

Drives the schema-aware init/reset contract: inventory the live DB,
no-op when current, refuse divergent without force, back up and rebuild
when force authorizes destruction. `rectify` is the standard flow used
by `init()`; `reset_db` is the always-destructive variant for the
explicit `reset` verb.

Vendored subset of the legacy ocd-old shared schema helper — only the
three functions transcripts' init flow uses (matches_expected, rectify,
reset_db) and their helpers are kept.
"""

import functools
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from ._errors import InitError


SchemaBuilder = Callable[[str], object]


def schema_signature(db_path: Path) -> dict:
    """Return canonical schema structure derived from SQLite introspection.

    sqlite_master.sql preserves the original DDL text — whitespace,
    quoting, default-expression formatting — all syntactic choices that
    don't affect schema semantics. This walks the tables via PRAGMA
    queries and builds a structural signature: columns with their types
    and constraints, foreign keys, and user-declared indexes.
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


def matches_expected(db_path: Path, schema_builder: SchemaBuilder) -> bool:
    """True when db_path's schema matches what schema_builder would produce.

    The canonical signature for a given schema_builder is memoized at the
    process level — schema_builder is deterministic, so building a fresh
    expected DB on every call is wasted work.
    """
    if not db_path.exists():
        return False
    try:
        return schema_signature(db_path) == _canonical_signature(schema_builder)
    except sqlite3.Error:
        return False


def _is_additive_upgrade(live: dict, canonical: dict) -> bool:
    """True when canonical differs from live only by added whole tables.

    The divergence is *additive* — and so safe to resolve by re-running the
    idempotent builder, which only `CREATE TABLE IF NOT EXISTS` — exactly
    when every table the live DB already has is present in canonical with an
    identical definition, and the sole differences are tables canonical
    declares that live lacks. Any shared table whose definition differs, or
    any live table canonical doesn't declare, is a genuine conflict: the
    builder can't reconcile it without dropping data, so it falls to the
    backup-and-wipe path.

    Callers reach this only after `matches_expected` returned False, so an
    exact match (nothing to add) is impossible here; a True result always
    means there is at least one table to create.
    """
    for name, live_table in live.items():
        if name not in canonical or canonical[name] != live_table:
            return False
    return True


@functools.cache
def _canonical_signature(schema_builder: SchemaBuilder) -> dict:
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

    Behavior:
    - Schema absent → build fresh; emit `absent → current`
    - Schema current → no-op; emit `current → current`
    - Schema divergent by added tables only → re-run the idempotent builder
      in place (no backup, no wipe — existing rows are untouched); emit
      `divergent → upgraded`
    - Schema divergent by a genuine conflict + not force → raise InitError
    - Schema divergent by a genuine conflict + force → write timestamped
      backup beside the live DB, wipe, rebuild; emit a backup entry plus
      `divergent → reinstalled`

    The additive path is what lets new tables (e.g. `references`, `blocks`)
    land on an already-populated DB without destroying user-authored state
    like `exchanges.description`, which is non-derivable.
    """
    state = _schema_state(db_path, schema_builder)

    if state == "current":
        return [{"path": rel_path, "before": "current", "after": "current"}]

    if state == "divergent":
        if _is_additive_upgrade(
            schema_signature(db_path), _canonical_signature(schema_builder)
        ):
            schema_builder(str(db_path))  # CREATE IF NOT EXISTS only — additive
            if not matches_expected(db_path, schema_builder):
                raise InitError(
                    f"{rel_path} could not be upgraded in place. Re-run with "
                    f"--force to back up and rebuild, or invoke `reset`."
                )
            return [{"path": rel_path, "before": "divergent", "after": "upgraded"}]

        if not force:
            raise InitError(
                f"{rel_path} has a divergent schema that can't be upgraded "
                f"additively. Re-run with --force to back up the current file "
                f"and rebuild, or invoke the system's `reset` verb to wipe and "
                f"start fresh."
            )

        files: list[dict] = []
        backup = write_backup(db_path)
        backup_rel = _relative_backup_path(backup, rel_path)
        files.append({"path": backup_rel, "before": "absent", "after": "current"})
        db_path.unlink()
        schema_builder(str(db_path))
        files.append({"path": rel_path, "before": "divergent", "after": "reinstalled"})
        return files

    schema_builder(str(db_path))
    return [{"path": rel_path, "before": "absent", "after": "current"}]


def reset_db(
    db_path: Path,
    schema_builder: SchemaBuilder,
    rel_path: str,
) -> list[dict]:
    """Always-destructive rebuild — backup, wipe, rebuild regardless of schema state."""
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


def _schema_state(db_path: Path, schema_builder: SchemaBuilder) -> str:
    if not db_path.exists():
        return "absent"
    try:
        if matches_expected(db_path, schema_builder):
            return "current"
        return "divergent"
    except sqlite3.Error:
        return "error"


def _relative_backup_path(backup: Path, rel_path: str) -> str:
    parent_rel = "/".join(rel_path.split("/")[:-1])
    return f"{parent_rel}/{backup.name}"
