"""Tests for tools/db.py — schema introspection, comparison, backup, and the
rectify/reset_db orchestration helpers that DB-backed systems compose.

Schema-comparison primitives (signature, schemas_match, matches_expected)
back the rectify decision. The rectify/reset_db tests pin the contract
documented in python.md *Force semantics*: no-op on current,
backup-and-rebuild on divergent, refusal of divergent without force,
unconditional wipe-and-rebuild for reset.
"""

import sqlite3
from pathlib import Path

import pytest

from tools import db
from tools.errors import InitError


def _make_db(path: Path, schema: str) -> None:
    conn = sqlite3.connect(path)
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


SCHEMA_V1 = "CREATE TABLE t (id TEXT PRIMARY KEY, value TEXT)"
SCHEMA_V2 = "CREATE TABLE t (id TEXT PRIMARY KEY, value TEXT, extra TEXT)"


def _build_v1(target: str) -> None:
    _make_db(Path(target), SCHEMA_V1)


def _build_v2(target: str) -> None:
    _make_db(Path(target), SCHEMA_V2)


class TestSchemaSignature:
    def test_returns_dict_keyed_by_table(self, tmp_path):
        path = tmp_path / "x.db"
        _make_db(path, "CREATE TABLE alpha (id TEXT); CREATE TABLE beta (id TEXT)")
        sig = db.schema_signature(path)
        assert set(sig) == {"alpha", "beta"}

    def test_includes_columns_foreign_keys_and_indexes(self, tmp_path):
        path = tmp_path / "x.db"
        _make_db(path, """
            CREATE TABLE parent (id TEXT PRIMARY KEY);
            CREATE TABLE child (
                id TEXT PRIMARY KEY,
                parent_id TEXT REFERENCES parent(id),
                name TEXT
            );
            CREATE INDEX idx_name ON child (name);
        """)
        sig = db.schema_signature(path)
        assert "columns" in sig["child"]
        assert "foreign_keys" in sig["child"]
        assert "idx_name" in sig["child"]["indexes"]


class TestSchemasMatch:
    def test_whitespace_does_not_affect_match(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, """
            CREATE TABLE t (
                id TEXT PRIMARY KEY,
                description TEXT NOT NULL
            )
        """)
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY, description TEXT NOT NULL)")
        assert db.schemas_match(a, b)

    def test_quoting_does_not_affect_match(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, 'CREATE TABLE "t" ("id" TEXT PRIMARY KEY)')
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY)")
        assert db.schemas_match(a, b)

    def test_different_columns_diverge(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, "CREATE TABLE t (id TEXT PRIMARY KEY, description TEXT)")
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY, summary TEXT)")
        assert not db.schemas_match(a, b)

    def test_different_column_count_diverges(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, "CREATE TABLE t (id TEXT PRIMARY KEY, description TEXT)")
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY)")
        assert not db.schemas_match(a, b)

    def test_different_column_type_diverges(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, "CREATE TABLE t (id TEXT PRIMARY KEY, age INTEGER)")
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY, age TEXT)")
        assert not db.schemas_match(a, b)

    def test_foreign_key_diff_diverges(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, """
            CREATE TABLE parent (id TEXT PRIMARY KEY);
            CREATE TABLE child (id TEXT PRIMARY KEY, parent_id TEXT REFERENCES parent(id));
        """)
        _make_db(b, """
            CREATE TABLE parent (id TEXT PRIMARY KEY);
            CREATE TABLE child (id TEXT PRIMARY KEY, parent_id TEXT);
        """)
        assert not db.schemas_match(a, b)

    def test_user_index_diverges(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, """
            CREATE TABLE t (id TEXT PRIMARY KEY, key TEXT);
            CREATE INDEX idx_key ON t (key);
        """)
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY, key TEXT)")
        assert not db.schemas_match(a, b)

    def test_primary_key_auto_index_filtered_out(self, tmp_path):
        """Auto-indexes from PRIMARY KEY/UNIQUE constraints must not appear
        in the signature — they're derived, not declared."""
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, "CREATE TABLE t (id TEXT PRIMARY KEY, code TEXT UNIQUE)")
        _make_db(b, "CREATE TABLE t (id TEXT PRIMARY KEY, code TEXT UNIQUE)")
        assert db.schemas_match(a, b)

    def test_unique_index_uniqueness_matters(self, tmp_path):
        a = tmp_path / "a.db"
        b = tmp_path / "b.db"
        _make_db(a, """
            CREATE TABLE t (id TEXT PRIMARY KEY, code TEXT);
            CREATE UNIQUE INDEX idx_code ON t (code);
        """)
        _make_db(b, """
            CREATE TABLE t (id TEXT PRIMARY KEY, code TEXT);
            CREATE INDEX idx_code ON t (code);
        """)
        assert not db.schemas_match(a, b)


class TestMatchesExpected:
    def test_false_when_db_absent(self, tmp_path):
        path = tmp_path / "missing.db"
        assert db.matches_expected(path, _build_v1) is False

    def test_true_when_live_matches_init_output(self, tmp_path):
        path = tmp_path / "live.db"
        _build_v1(str(path))
        assert db.matches_expected(path, _build_v1) is True

    def test_false_when_live_diverges_from_init_output(self, tmp_path):
        path = tmp_path / "live.db"
        _build_v1(str(path))
        assert db.matches_expected(path, _build_v2) is False


class TestBackupHelpers:
    def test_backup_path_includes_timestamp(self, tmp_path):
        live = tmp_path / "x.db"
        backup = db.backup_path(live)
        assert backup.name.startswith("x.db.backup-")
        assert backup.name.endswith("Z")
        assert backup.parent == live.parent

    def test_write_backup_copies_contents(self, tmp_path):
        live = tmp_path / "x.db"
        _make_db(live, "CREATE TABLE t (id TEXT)")
        conn = sqlite3.connect(live)
        conn.execute("INSERT INTO t (id) VALUES ('payload')")
        conn.commit()
        conn.close()

        backup = db.write_backup(live)

        assert backup.exists()
        restored = sqlite3.connect(backup)
        row = restored.execute("SELECT id FROM t").fetchone()
        restored.close()
        assert row[0] == "payload"


class TestRectify:
    def test_absent_creates_db(self, tmp_path):
        live = tmp_path / "live.db"
        files = db.rectify(live, _build_v1, "rel/live.db")
        assert files == [{"path": "rel/live.db", "before": "absent", "after": "current"}]
        assert live.exists()

    def test_current_is_no_op(self, tmp_path):
        live = tmp_path / "live.db"
        _build_v1(str(live))
        conn = sqlite3.connect(live)
        conn.execute("INSERT INTO t (id, value) VALUES ('1', 'kept')")
        conn.commit()
        conn.close()

        files = db.rectify(live, _build_v1, "rel/live.db")

        assert files == [{"path": "rel/live.db", "before": "current", "after": "current"}]
        post = sqlite3.connect(live)
        row = post.execute("SELECT value FROM t WHERE id = '1'").fetchone()
        post.close()
        assert row[0] == "kept"

    def test_current_with_force_is_no_op(self, tmp_path):
        """Force does not wipe data when schema is already current."""
        live = tmp_path / "live.db"
        _build_v1(str(live))
        conn = sqlite3.connect(live)
        conn.execute("INSERT INTO t (id, value) VALUES ('1', 'kept')")
        conn.commit()
        conn.close()

        files = db.rectify(live, _build_v1, "rel/live.db", force=True)

        assert files == [{"path": "rel/live.db", "before": "current", "after": "current"}]
        backups = list(live.parent.glob("live.db.backup-*"))
        assert backups == []
        post = sqlite3.connect(live)
        row = post.execute("SELECT value FROM t WHERE id = '1'").fetchone()
        post.close()
        assert row[0] == "kept"

    def test_divergent_without_force_raises(self, tmp_path):
        live = tmp_path / "live.db"
        _build_v1(str(live))
        with pytest.raises(InitError, match="divergent"):
            db.rectify(live, _build_v2, "rel/live.db")

    def test_divergent_with_force_writes_backup_and_rebuilds(self, tmp_path):
        live = tmp_path / "live.db"
        _build_v1(str(live))
        conn = sqlite3.connect(live)
        conn.execute("INSERT INTO t (id, value) VALUES ('1', 'pre-rebuild')")
        conn.commit()
        conn.close()

        files = db.rectify(live, _build_v2, "rel/live.db", force=True)

        assert len(files) == 2
        backup_entry = next(f for f in files if "backup" in f["path"])
        assert backup_entry["before"] == "absent"
        assert backup_entry["after"] == "current"
        db_entry = next(f for f in files if "backup" not in f["path"])
        assert db_entry == {"path": "rel/live.db", "before": "divergent", "after": "reinstalled"}

        backups = list(live.parent.glob("live.db.backup-*"))
        assert len(backups) == 1
        restored = sqlite3.connect(backups[0])
        row = restored.execute("SELECT value FROM t WHERE id = '1'").fetchone()
        restored.close()
        assert row[0] == "pre-rebuild"

        # Live DB has new schema, no data
        post = sqlite3.connect(live)
        cols = [r[1] for r in post.execute('PRAGMA table_info("t")').fetchall()]
        post.close()
        assert "extra" in cols


class TestResetDb:
    def test_absent_creates_db(self, tmp_path):
        live = tmp_path / "live.db"
        files = db.reset_db(live, _build_v1, "rel/live.db")
        assert files == [{"path": "rel/live.db", "before": "absent", "after": "current"}]

    def test_current_writes_backup_and_rebuilds(self, tmp_path):
        live = tmp_path / "live.db"
        _build_v1(str(live))
        conn = sqlite3.connect(live)
        conn.execute("INSERT INTO t (id, value) VALUES ('1', 'gone')")
        conn.commit()
        conn.close()

        files = db.reset_db(live, _build_v1, "rel/live.db")

        backup_entry = next(f for f in files if "backup" in f["path"])
        assert backup_entry["before"] == "absent"
        assert backup_entry["after"] == "current"
        db_entry = next(f for f in files if "backup" not in f["path"])
        assert db_entry == {"path": "rel/live.db", "before": "current", "after": "reinstalled"}

        backups = list(live.parent.glob("live.db.backup-*"))
        assert len(backups) == 1
        restored = sqlite3.connect(backups[0])
        row = restored.execute("SELECT value FROM t WHERE id = '1'").fetchone()
        restored.close()
        assert row[0] == "gone"

        # Live DB is empty
        post = sqlite3.connect(live)
        count = post.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        post.close()
        assert count == 0

    def test_current_schema_match_still_wipes(self, tmp_path):
        """Reset is unconditionally destructive — schema match doesn't short-circuit
        the way it does for rectify."""
        live = tmp_path / "live.db"
        _build_v1(str(live))
        conn = sqlite3.connect(live)
        conn.execute("INSERT INTO t (id, value) VALUES ('1', 'gone')")
        conn.commit()
        conn.close()

        db.reset_db(live, _build_v1, "rel/live.db")

        post = sqlite3.connect(live)
        count = post.execute("SELECT COUNT(*) FROM t").fetchone()[0]
        post.close()
        assert count == 0
