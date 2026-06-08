"""SQLite schema management primitives for the transcripts DB.

Drives the schema-aware init/reset contract under canonical-as-floor
semantics: the canonical schema is a *minimum* the live DB must contain,
not an exact spec. Inventory the live DB, no-op when it satisfies the
floor (extras tolerated), add missing tables in place when only whole
tables are absent, and refuse a genuine conflict (a present table missing
a prescribed column/index) without force. `rectify` is the standard flow
used by `init()`; `reset_db` is the always-destructive variant for the
explicit `reset` verb.

Vendored subset of the legacy ocd-old shared schema helper — only the
functions transcripts' init flow uses (satisfies_expected, rectify,
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
            # Drop the positional cid (row[0]) so column comparison is
            # order-independent — an extra column elsewhere must not shift identity.
            columns = [
                tuple(row[1:])
                for row in conn.execute(f'PRAGMA table_info("{name}")').fetchall()
            ]
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


def satisfies_expected(db_path: Path, schema_builder: SchemaBuilder) -> bool:
    """True when db_path *satisfies* the canonical schema as a floor.

    The canonical schema is a minimum contract, not an exact spec: the DB is
    valid when it contains at least the prescribed tables, and each carries at
    least the prescribed columns, indexes, and foreign keys. Extra tables and
    extra columns are tolerated and ignored — so a user extension, or a table
    added by a newer skill version then seen by an older one (downgrade), does
    not read as divergence. This is what keeps reconciliation from ever needing
    to wipe non-derivable state.

    The canonical signature for a given schema_builder is memoized at the
    process level — schema_builder is deterministic, so building a fresh
    expected DB on every call is wasted work.
    """
    if not db_path.exists():
        return False
    try:
        return _satisfies(_canonical_signature(schema_builder), schema_signature(db_path))
    except sqlite3.Error:
        return False


def schema_state(db_path: Path, schema_builder: SchemaBuilder) -> str:
    """Public schema classification: absent | current | upgradable | conflict | error."""
    return _schema_state(db_path, schema_builder)


def _table_satisfied(canonical_table: dict, live_table: dict) -> bool:
    """True when a live table carries at least the canonical table's structure.

    Columns and foreign keys compare as set containment (canonical ⊆ live);
    each prescribed index must exist in live with an identical definition.
    Extras on the live side are tolerated.
    """
    if not set(canonical_table["columns"]) <= set(live_table["columns"]):
        return False
    if not set(canonical_table["foreign_keys"]) <= set(live_table["foreign_keys"]):
        return False
    live_indexes = live_table["indexes"]
    return all(
        live_indexes.get(idx_name) == idx_def
        for idx_name, idx_def in canonical_table["indexes"].items()
    )


def _satisfies(canonical: dict, live: dict) -> bool:
    """True when every canonical table is present in live and satisfied."""
    return all(
        name in live and _table_satisfied(ctable, live[name])
        for name, ctable in canonical.items()
    )


def _only_missing_tables(canonical: dict, live: dict) -> bool:
    """True when the only deficiency is entirely-absent canonical tables.

    Every canonical table that *is* present in live satisfies the contract, so
    re-running the idempotent builder (`CREATE TABLE IF NOT EXISTS`) closes the
    gap additively. False means a present table is missing a prescribed column
    or index — which `CREATE TABLE IF NOT EXISTS` cannot repair, so it's a
    genuine conflict requiring backup-and-rebuild.
    """
    return all(
        _table_satisfied(ctable, live[name])
        for name, ctable in canonical.items()
        if name in live
    )


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
    """Bring a SQLite DB up to the canonical floor (canonical-as-floor contract).

    The canonical schema is a minimum: the DB must contain at least the
    prescribed tables/columns/indexes; extra tables and columns are tolerated.

    Behavior by state:
    - `absent`     → build fresh; emit `absent → current`
    - `current`    → no-op (already satisfies, extras and all); `current → current`
    - `upgradable` → re-run the idempotent builder in place (no backup, no wipe
      — existing rows untouched), creating the missing tables; `upgradable → upgraded`
    - `conflict` + not force → raise InitError (a prescribed column/index is
      missing from a present table; `CREATE TABLE IF NOT EXISTS` can't add it)
    - `conflict` + force → timestamped backup, wipe, rebuild; backup entry plus
      `conflict → reinstalled`

    The upgradable path is what lets new tables (e.g. `refs`, `blocks`) land on
    an already-populated DB without destroying non-derivable state like
    `exchanges.description`; the floor semantics extend the same protection to
    user-added tables and to downgrades (an older skill ignores newer tables).
    """
    state = _schema_state(db_path, schema_builder)

    if state == "current":
        return [{"path": rel_path, "before": "current", "after": "current"}]

    if state == "upgradable":
        schema_builder(str(db_path))  # CREATE IF NOT EXISTS only — additive
        if not satisfies_expected(db_path, schema_builder):
            raise InitError(
                f"{rel_path} could not be upgraded in place. Re-run with "
                f"--force to back up and rebuild, or invoke `reset`."
            )
        return [{"path": rel_path, "before": "upgradable", "after": "upgraded"}]

    if state == "conflict":
        if not force:
            raise InitError(
                f"{rel_path} is missing a prescribed column or index and can't "
                f"be upgraded additively. Re-run with --force to back up the "
                f"current file and rebuild, or invoke the system's `reset` verb "
                f"to wipe and start fresh."
            )
        files: list[dict] = []
        backup = write_backup(db_path)
        backup_rel = _relative_backup_path(backup, rel_path)
        files.append({"path": backup_rel, "before": "absent", "after": "current"})
        db_path.unlink()
        schema_builder(str(db_path))
        files.append({"path": rel_path, "before": "conflict", "after": "reinstalled"})
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
    """Classify the live DB against the canonical floor.

    - `absent`     — no file
    - `current`    — satisfies the contract (extras tolerated)
    - `upgradable` — only whole canonical tables are missing; builder can add them
    - `conflict`   — a present table lacks a prescribed column/index; needs --force
    - `error`      — schema unreadable
    """
    if not db_path.exists():
        return "absent"
    try:
        canonical = _canonical_signature(schema_builder)
        live = schema_signature(db_path)
    except sqlite3.Error:
        return "error"
    if _satisfies(canonical, live):
        return "current"
    if _only_missing_tables(canonical, live):
        return "upgradable"
    return "conflict"


def _relative_backup_path(backup: Path, rel_path: str) -> str:
    parent_rel = "/".join(rel_path.split("/")[:-1])
    return f"{parent_rel}/{backup.name}"
