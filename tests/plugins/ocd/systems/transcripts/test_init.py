"""Tests for _init: plugin contract (ready/init/reset/status)."""

from systems.transcripts import _init


class TestReady:
    def test_returns_false_when_db_absent(self):
        # Project dir is fresh — DB not yet created.
        assert _init.ready() is False

    def test_returns_true_after_init(self):
        _init.init()
        assert _init.ready() is True


class TestInit:
    def test_creates_db_at_canonical_path(self, project_dir):
        result = _init.init()
        assert _init._db_path().exists()
        assert _init._db_path() == project_dir / ".claude" / "ocd" / "transcripts" / "transcripts.db"
        assert result["files"][0]["after"] == "current"

    def test_init_idempotent(self):
        _init.init()
        result = _init.init()
        assert _init.ready() is True
        # Re-running init keeps the schema current.
        assert all(f["after"] == "current" for f in result["files"])

    def test_status_envelope_shape(self):
        _init.init()
        s = _init.status()
        assert "files" in s
        assert "extra" in s
        assert isinstance(s["files"], list)
        assert isinstance(s["extra"], list)


class TestStatus:
    def test_reports_absent_when_uninitialized(self):
        s = _init.status()
        assert s["files"][0]["before"] == "absent"
        assert any("not initialized" in e["value"] for e in s["extra"])

    def test_reports_operational_when_ready(self):
        _init.init()
        s = _init.status()
        assert s["files"][0]["before"] == "current"
        assert any("operational" in e["value"] for e in s["extra"])


class TestReset:
    def test_reset_backs_up_existing_db(self):
        _init.init()
        # Seed something into the DB so the backup is non-trivial.
        from systems.transcripts._db import get_connection
        conn = get_connection(str(_init._db_path()))
        conn.execute("UPDATE settings SET threshold_min = 99")
        conn.commit()
        conn.close()

        result = _init.reset()
        # After reset, schema is current and threshold_min reverted to default.
        assert _init.ready() is True
        conn = get_connection(str(_init._db_path()))
        try:
            value = conn.execute("SELECT threshold_min FROM settings").fetchone()[0]
        finally:
            conn.close()
        assert value == 15
        # Backup file recorded in result.
        assert any("backup" in f["path"] for f in result["files"])

    def test_reset_when_db_absent_creates_fresh(self):
        # Reset on absent DB should still produce a current schema.
        result = _init.reset()
        assert _init.ready() is True
        assert any(f["after"] == "current" for f in result["files"])
