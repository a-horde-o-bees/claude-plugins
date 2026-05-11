"""Tests for _db: schema, connection, derived views."""

from systems.transcripts._db import (
    EXPECTED_TABLES,
    SCHEMA,
    current_project_name,
    get_connection,
    init_db,
)


class TestSchema:
    def test_init_creates_events_table(self, db_path):
        conn = get_connection(db_path)
        try:
            tables = {
                row[0] for row in conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                ).fetchall()
            }
        finally:
            conn.close()
        assert EXPECTED_TABLES.issubset(tables)

    def test_events_with_gaps_view_exists(self, conn):
        views = {
            row[0] for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='view'"
            ).fetchall()
        }
        assert "events_with_gaps" in views
        assert "chat_messages" in views

    def test_init_db_idempotent(self, db_path):
        # Re-running init_db on the same path must not raise.
        init_db(db_path)
        init_db(db_path)
        conn = get_connection(db_path)
        try:
            n = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        finally:
            conn.close()
        assert n == 0

    def test_schema_constant_includes_indexes(self):
        # Spot check — agent-facing assumption is that lookup-heavy columns
        # are indexed, so the SCHEMA constant should declare them.
        assert "idx_events_session" in SCHEMA
        assert "idx_events_project" in SCHEMA


class TestCurrentProjectName:
    def test_encodes_project_root_path(self, project_dir):
        name = current_project_name()
        # Encoding replaces / with -.
        assert name.startswith("-")
        assert "/" not in name
        # The project_dir fixture sets CLAUDE_PROJECT_DIR; the encoding
        # should derive from it.
        assert str(project_dir).replace("/", "-") == name
