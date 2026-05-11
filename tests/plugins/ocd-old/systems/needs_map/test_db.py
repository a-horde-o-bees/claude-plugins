"""Unit tests for database infrastructure — schema, id generation, existence checks."""

import pytest

from systems.needs_map._db import (
    EXPECTED_TABLES,
    check_component,
    check_need,
    get_connection,
    init_db,
    next_id,
)


class TestInitDb:
    def test_creates_database(self, tmp_path):
        path = str(tmp_path / "new.db")
        result = init_db(path)
        assert "Initialized" in result

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
        assert EXPECTED_TABLES.issubset(tables)

    def test_idempotent(self, tmp_path):
        path = str(tmp_path / "new.db")
        init_db(path)
        conn = get_connection(path)
        conn.execute(
            "INSERT INTO components (id, description) VALUES (?, ?)",
            ("c1", "test"),
        )
        conn.commit()
        conn.close()
        init_db(path)  # second run — should not wipe
        conn = get_connection(path)
        row = conn.execute(
            "SELECT description FROM components WHERE id = 'c1'"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row[0] == "test"


class TestNextId:
    def test_starts_at_one(self, conn):
        assert next_id(conn, "c", "components") == "c1"

    def test_increments_from_existing(self, conn):
        conn.execute(
            "INSERT INTO components (id, description) VALUES ('c1', 'a')"
        )
        conn.execute(
            "INSERT INTO components (id, description) VALUES ('c2', 'b')"
        )
        conn.commit()
        assert next_id(conn, "c", "components") == "c3"

    def test_gaps_are_not_reused(self, conn):
        conn.execute(
            "INSERT INTO components (id, description) VALUES ('c1', 'a')"
        )
        conn.execute(
            "INSERT INTO components (id, description) VALUES ('c5', 'b')"
        )
        conn.commit()
        assert next_id(conn, "c", "components") == "c6"

    def test_needs_prefix_independent(self, conn):
        conn.execute(
            "INSERT INTO needs (id, description) VALUES ('n1', 'a')"
        )
        conn.commit()
        assert next_id(conn, "c", "components") == "c1"


class TestCheckers:
    def test_check_component_passes_when_present(self, conn):
        conn.execute(
            "INSERT INTO components (id, description) VALUES ('c1', 'a')"
        )
        conn.commit()
        check_component(conn, "c1")  # no exception

    def test_check_component_raises_when_absent(self, conn):
        with pytest.raises(LookupError, match="c99"):
            check_component(conn, "c99")

    def test_check_need_passes_when_present(self, conn):
        conn.execute(
            "INSERT INTO needs (id, description) VALUES ('n1', 'a')"
        )
        conn.commit()
        check_need(conn, "n1")

    def test_check_need_raises_when_absent(self, conn):
        with pytest.raises(LookupError, match="n99"):
            check_need(conn, "n99")


class TestConnection:
    def test_foreign_keys_enabled(self, db_path):
        conn = get_connection(db_path)
        row = conn.execute("PRAGMA foreign_keys").fetchone()
        conn.close()
        assert row[0] == 1

    def test_cascade_delete_clears_edges(self, conn):
        conn.execute("INSERT INTO components (id, description) VALUES ('c1', 'a')")
        conn.execute("INSERT INTO components (id, description) VALUES ('c2', 'b')")
        conn.execute(
            "INSERT INTO depends_on (component_id, dependency_id) VALUES ('c1', 'c2')"
        )
        conn.commit()
        conn.execute("DELETE FROM components WHERE id = 'c1'")
        conn.commit()
        remaining = conn.execute(
            "SELECT COUNT(*) FROM depends_on"
        ).fetchone()[0]
        assert remaining == 0
