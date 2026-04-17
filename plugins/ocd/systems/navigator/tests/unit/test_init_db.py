"""Unit tests for init_db database initialization."""

from pathlib import Path

from systems.navigator._db import get_connection, init_db


class TestInitDb:
    def test_creates_database(self, tmp_path):
        path = str(tmp_path / "new.db")
        result = init_db(path)
        assert "Initialized" in result
        assert Path(path).exists()

    def test_creates_expected_tables(self, tmp_path):
        path = str(tmp_path / "new.db")
        init_db(path)
        conn = get_connection(path)
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        conn.close()
        assert {"paths", "path_patterns", "path_pattern_sources", "config"}.issubset(tables)

    def test_idempotent(self, tmp_path):
        path = str(tmp_path / "new.db")
        init_db(path)
        conn = get_connection(path)
        conn.execute("INSERT INTO paths (path, entry_type) VALUES ('test', 'file')")
        conn.commit()
        conn.close()
        init_db(path)  # second run — should not error
        conn = get_connection(path)
        row = conn.execute("SELECT * FROM paths WHERE path = 'test'").fetchone()
        assert row is not None
        conn.close()

    def test_seeds_config_defaults(self, tmp_path):
        path = str(tmp_path / "new.db")
        init_db(path)
        conn = get_connection(path)
        rows = dict(conn.execute("SELECT key, value FROM config").fetchall())
        conn.close()
        assert rows["lines_warn_threshold"] == "500"
        assert rows["lines_fail_threshold"] == "2000"
