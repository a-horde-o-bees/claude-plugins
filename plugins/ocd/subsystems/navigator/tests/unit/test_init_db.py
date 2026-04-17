"""Unit tests for init_db database initialization."""

from pathlib import Path

from subsystems.navigator._db import get_connection, init_db


class TestInitDb:
    def test_creates_database(self, tmp_path):
        path = str(tmp_path / "new.db")
        result = init_db(path)
        assert "Initialized" in result
        assert Path(path).exists()

    def test_idempotent(self, tmp_path):
        path = str(tmp_path / "new.db")
        init_db(path)
        # Manually add a non-seed entry
        conn = get_connection(path)
        conn.execute("INSERT INTO entries (path, entry_type) VALUES ('test', 'file')")
        conn.commit()
        conn.close()
        result = init_db(path)
        assert "all current" in result
        # Non-seed entry preserved
        conn = get_connection(path)
        row = conn.execute("SELECT * FROM entries WHERE path = 'test'").fetchone()
        assert row is not None
        conn.close()

    def test_seeds_from_csv(self, tmp_path):
        csv_path = tmp_path / "seed.csv"
        csv_path.write_text(
            "path,entry_type,exclude,traverse,description\n"
            "**/__pycache__,directory,1,0,\n"
            "**/tests,directory,0,0,Test suites\n"
        )
        db = str(tmp_path / "seeded.db")
        from subsystems.navigator import _db as db_ctx
        original = db_ctx.SEED_PATH
        try:
            db_ctx.SEED_PATH = csv_path
            result = init_db(db)
            assert "2 added" in result
            conn = get_connection(db)
            rows = conn.execute("SELECT * FROM patterns").fetchall()
            assert len(rows) == 2
            # Entries table should be empty — patterns don't leak in
            entry_rows = conn.execute("SELECT * FROM entries").fetchall()
            assert len(entry_rows) == 0
            conn.close()
        finally:
            db_ctx.SEED_PATH = original

    def test_upserts_changed_seed_patterns(self, tmp_path):
        csv_path = tmp_path / "seed.csv"
        csv_path.write_text(
            "path,entry_type,exclude,traverse,description\n"
            "**/tests,directory,0,0,Test suites\n"
        )
        db = str(tmp_path / "upsert.db")
        from subsystems.navigator import _db as db_ctx
        original = db_ctx.SEED_PATH
        try:
            db_ctx.SEED_PATH = csv_path
            init_db(db)
            # Change the seed pattern
            csv_path.write_text(
                "path,entry_type,exclude,traverse,description\n"
                "**/tests,directory,0,0,Updated description\n"
            )
            result = init_db(db)
            assert "1 updated" in result
            conn = get_connection(db)
            row = conn.execute(
                "SELECT description FROM patterns WHERE pattern = '**/tests'"
            ).fetchone()
            assert row[0] == "Updated description"
            conn.close()
        finally:
            db_ctx.SEED_PATH = original

    def test_adds_new_seed_patterns(self, tmp_path):
        csv_path = tmp_path / "seed.csv"
        csv_path.write_text(
            "path,entry_type,exclude,traverse,description\n"
            "**/tests,directory,0,0,Test suites\n"
        )
        db = str(tmp_path / "add.db")
        from subsystems.navigator import _db as db_ctx
        original = db_ctx.SEED_PATH
        try:
            db_ctx.SEED_PATH = csv_path
            init_db(db)
            # Add a new seed pattern
            csv_path.write_text(
                "path,entry_type,exclude,traverse,description\n"
                "**/tests,directory,0,0,Test suites\n"
                "**/.vscode,directory,1,0,\n"
            )
            result = init_db(db)
            assert "1 added" in result
            conn = get_connection(db)
            rows = conn.execute("SELECT * FROM patterns").fetchall()
            assert len(rows) == 2
            conn.close()
        finally:
            db_ctx.SEED_PATH = original
