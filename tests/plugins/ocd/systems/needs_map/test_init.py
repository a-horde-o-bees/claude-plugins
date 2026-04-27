"""Unit tests for init() / reset() / status() — schema-aware contract.

Each test sits at the system level: needs_map's init() composes
`tools.db.rectify`, so this suite verifies the system-specific
behavior (status reporting, dormancy errors, the reset verb) while the
underlying rectify/reset_db semantics are pinned by tests in
tests/integration/test_db.py.
"""

import pytest

from systems import setup
from tools import environment
from tools.errors import InitError, NotReadyError

from systems.needs_map import _db, _init


@pytest.fixture
def plugin_root_shim(project_dir, monkeypatch):
    """Stub plugin root so _plugin_name() resolves without a real plugin layout."""
    monkeypatch.setattr(setup, "get_plugin_name", lambda _root: "ocd")
    plugin_root = project_dir.parent / "plugin"
    plugin_root.mkdir(exist_ok=True)
    monkeypatch.setattr(environment, "get_plugin_root", lambda: plugin_root)
    return plugin_root


class TestStatus:
    def test_reports_absent(self, plugin_root_shim):
        result = _init.status()
        entry = next(e for e in result["extra"] if e["label"] == "overall status")
        assert entry["value"] == "not initialized"

    def test_reports_operational(self, plugin_root_shim):
        _init.init()
        result = _init.status()
        entry = next(e for e in result["extra"] if e["label"] == "overall status")
        assert entry["value"].startswith("operational")

    def test_reports_divergent_schema(self, plugin_root_shim):
        db = _init._db_path()
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = _db.get_connection(str(db))
        conn.executescript("CREATE TABLE foreign_table (id TEXT)")
        conn.commit()
        conn.close()
        result = _init.status()
        entry = next(e for e in result["extra"] if e["label"] == "overall status")
        assert "divergent" in entry["value"]


class TestInit:
    def test_first_install_reports_absent_to_current(self, plugin_root_shim):
        result = _init.init()
        db_entry = next(f for f in result["files"] if f["path"].endswith("needs-map.db"))
        assert db_entry["before"] == "absent"
        assert db_entry["after"] == "current"

    def test_idempotent_no_op(self, plugin_root_shim):
        _init.init()
        result = _init.init()
        db_entry = next(f for f in result["files"] if f["path"].endswith("needs-map.db"))
        assert db_entry["before"] == "current"
        assert db_entry["after"] == "current"

    def test_force_on_current_is_no_op(self, plugin_root_shim):
        """Force does not wipe data when schema is already current."""
        _init.init()
        db = _init._db_path()
        existing = _db.get_connection(str(db))
        existing.execute(
            "INSERT INTO components (id, description) VALUES ('c1', 'kept')"
        )
        existing.commit()
        existing.close()

        _init.init(force=True)

        post = _db.get_connection(str(db))
        row = post.execute(
            "SELECT description FROM components WHERE id = 'c1'"
        ).fetchone()
        post.close()
        assert row[0] == "kept"

    def test_refuses_divergent_schema_without_force(self, plugin_root_shim):
        db = _init._db_path()
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = _db.get_connection(str(db))
        conn.executescript("CREATE TABLE unexpected (id TEXT)")
        conn.commit()
        conn.close()
        with pytest.raises(InitError, match="divergent"):
            _init.init()

    def test_force_recovers_divergent_schema(self, plugin_root_shim):
        db = _init._db_path()
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = _db.get_connection(str(db))
        conn.executescript("CREATE TABLE unexpected (id TEXT)")
        conn.commit()
        conn.close()

        _init.init(force=True)

        assert _init.ready()
        backups = list(db.parent.glob("needs-map.db.backup-*"))
        assert len(backups) == 1


class TestReset:
    def test_wipes_current_db(self, plugin_root_shim):
        _init.init()
        db = _init._db_path()
        existing = _db.get_connection(str(db))
        existing.execute(
            "INSERT INTO components (id, description) VALUES ('c1', 'gone')"
        )
        existing.commit()
        existing.close()

        _init.reset()

        post = _db.get_connection(str(db))
        count = post.execute("SELECT COUNT(*) FROM components").fetchone()[0]
        post.close()
        assert count == 0

    def test_writes_backup(self, plugin_root_shim):
        _init.init()
        db = _init._db_path()
        existing = _db.get_connection(str(db))
        existing.execute(
            "INSERT INTO components (id, description) VALUES ('c1', 'payload')"
        )
        existing.commit()
        existing.close()

        _init.reset()

        backups = list(db.parent.glob("needs-map.db.backup-*"))
        assert len(backups) == 1


class TestReady:
    def test_false_when_absent(self, plugin_root_shim):
        assert _init.ready() is False

    def test_true_after_init(self, plugin_root_shim):
        _init.init()
        assert _init.ready() is True

    def test_false_on_divergent_schema(self, plugin_root_shim):
        db = _init._db_path()
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = _db.get_connection(str(db))
        conn.executescript("CREATE TABLE unexpected (id TEXT)")
        conn.commit()
        conn.close()
        assert _init.ready() is False


class TestEnsureReady:
    def test_raises_when_absent(self, plugin_root_shim):
        with pytest.raises(NotReadyError, match="dormant"):
            _init.ensure_ready()

    def test_passes_when_ready(self, plugin_root_shim):
        _init.init()
        _init.ensure_ready()
