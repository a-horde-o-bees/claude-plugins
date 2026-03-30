"""Unit tests for research CLI.

Tests: init, register, update entities, get entity, get entities, get stats,
export, URL dedup, notes, update note, urls, provenance, reach, clear measures,
source data, merge, search notes. Uses temporary database per test via
tmp_path fixture.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
RUN_PY = str(PLUGIN_ROOT / "run.py")


def run_cli(*args: str, db: str) -> subprocess.CompletedProcess:
    """Run research CLI with --db flag via launcher."""
    cmd = [sys.executable, RUN_PY, "skills.research", args[0], *args[1:], "--db", db]
    return subprocess.run(cmd, capture_output=True, text=True)


def init_db(tmp_path: Path) -> str:
    """Init database and return db path."""
    db = str(tmp_path / "test.db")
    run_cli("init", db=db)
    return db


def register_entity(
    db: str,
    name: str,
    url: str | None = None,
    source_url: str | None = None,
    relevance: int | None = None,
    description: str | None = None,
    role: str | None = None,
) -> str:
    """Register entity and return prefixed id (e.g., 'e1')."""
    args = ["register", "--name", name]
    if url:
        args += ["--url", url]
    if source_url:
        args += ["--source-url", source_url]
    if relevance is not None:
        args += ["--relevance", str(relevance)]
    if description is not None:
        args += ["--description", description]
    if role is not None:
        args += ["--role", role]
    result = run_cli(*args, db=db)
    return result.stdout.split("id: ")[1].split(")")[0]


class TestInit:
    def test_creates_database(self, tmp_path: Path) -> None:
        db = str(tmp_path / "test.db")
        result = run_cli("init", db=db)
        assert result.returncode == 0
        assert "Database initialized" in result.stdout
        assert Path(db).exists()

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        db = str(tmp_path / "nested" / "dir" / "test.db")
        result = run_cli("init", db=db)
        assert result.returncode == 0
        assert Path(db).exists()

    def test_idempotent(self, tmp_path: Path) -> None:
        db = str(tmp_path / "test.db")
        run_cli("init", db=db)
        result = run_cli("init", db=db)
        assert result.returncode == 0
        assert "Database initialized" in result.stdout


class TestRegister:
    def test_registers_entity(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        result = run_cli(
            "register", "--name", "Test Org",
            "--url", "https://test.org",
            db=db,
        )
        assert result.returncode == 0
        assert "Registered: Test Org" in result.stdout
        assert "id:" in result.stdout

    def test_returns_prefixed_id(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Test Org", "https://test.org")
        assert eid.startswith("e")
        assert int(eid[1:]) >= 1

    def test_shows_in_list(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Test Org", "https://test.org")
        result = run_cli("get", "entities", db=db)
        assert "Test Org" in result.stdout

    def test_default_role_is_example(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Test Org", "https://test.org")
        result = run_cli("get", "entity", eid, db=db)
        assert "Role: example" in result.stdout
        assert "Stage: new" in result.stdout

    def test_url_optional(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        result = run_cli("register", "--name", "No URL Org", db=db)
        assert result.returncode == 0
        assert "Registered: No URL Org" in result.stdout

    def test_with_source_url(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(
            db, "Test Org", "https://test.org",
            source_url="https://directory.com/list",
        )
        result = run_cli("get", "entity", eid, db=db)
        assert "Found via (1)" in result.stdout
        assert "directory.com/list" in result.stdout

    def test_with_relevance(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Test Org", "https://test.org", relevance=8)
        result = run_cli("get", "entity", eid, db=db)
        assert "Relevance: 8" in result.stdout

    def test_with_description(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(
            db, "Test Org", "https://test.org",
            description="Platform for distributed task scheduling",
        )
        result = run_cli("get", "entity", eid, db=db)
        assert "Description: Platform for distributed task scheduling" in result.stdout

    def test_with_role(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Test Dir", "https://dir.com", role="directory")
        result = run_cli("get", "entity", eid, db=db)
        assert "Role: directory" in result.stdout

    def test_autoincrement(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        id1 = register_entity(db, "Org A", "https://a.org")
        id2 = register_entity(db, "Org B", "https://b.org")
        assert int(id2[1:]) == int(id1[1:]) + 1


class TestURLDedup:
    def test_normalize_strips_scheme(self) -> None:
        from skills.research._db import normalize_url
        assert normalize_url("https://example.com") == "example.com"
        assert normalize_url("http://example.com") == "example.com"

    def test_normalize_strips_www(self) -> None:
        from skills.research._db import normalize_url
        assert normalize_url("https://www.example.com") == "example.com"

    def test_normalize_keeps_path(self) -> None:
        from skills.research._db import normalize_url
        assert normalize_url("https://example.com/about/team") == "example.com/about/team"

    def test_normalize_strips_trailing_slash(self) -> None:
        from skills.research._db import normalize_url
        assert normalize_url("https://example.com/") == "example.com"
        assert normalize_url("https://example.com/about/") == "example.com/about"

    def test_normalize_lowercases(self) -> None:
        from skills.research._db import normalize_url
        assert normalize_url("https://Example.COM") == "example.com"

    def test_normalize_none_for_empty(self) -> None:
        from skills.research._db import normalize_url
        assert normalize_url(None) is None
        assert normalize_url("") is None

    def test_dedup_on_register(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://example.org")
        result = run_cli(
            "register", "--name", "Org B",
            "--url", "https://www.example.org",
            db=db,
        )
        assert "Already registered: Org A" in result.stdout

    def test_different_paths_not_matched(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://example.org")
        result = run_cli(
            "register", "--name", "Org B",
            "--url", "https://example.org/different",
            db=db,
        )
        assert "Registered: Org B" in result.stdout

    def test_dedup_adds_provenance(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(
            db, "Org A", "https://example.org",
            source_url="https://source1.com",
        )
        run_cli(
            "register", "--name", "Org B",
            "--url", "https://example.org",
            "--source-url", "https://source2.com",
            db=db,
        )
        result = run_cli("get", "provenance", "--entity-id", eid, db=db)
        assert "source1.com" in result.stdout
        assert "source2.com" in result.stdout

    def test_no_url_creates_separate_entities(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        id1 = register_entity(db, "Target A")
        id2 = register_entity(db, "Target B")
        assert id1 != id2


class TestUpdateEntity:
    def test_update_stage(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        id1 = register_entity(db, "Org A", "https://a.org")
        id2 = register_entity(db, "Org B", "https://b.org")
        result = run_cli("update", "entities", "--ids", f"{id1},{id2}", "--stage", "rejected", db=db)
        assert result.returncode == 0
        assert "Updated 2 entities" in result.stdout
        assert "stage: rejected" in result.stdout

    def test_update_relevance(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        result = run_cli("update", "entities", "--ids", eid, "--relevance", "7", db=db)
        assert result.returncode == 0
        detail = run_cli("get", "entity", eid, db=db)
        assert "Relevance: 7" in detail.stdout

    def test_update_description(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("update", "entities", "--ids", eid, "--description", "Updated desc", db=db)
        detail = run_cli("get", "entity", eid, db=db)
        assert "Description: Updated desc" in detail.stdout

    def test_not_found_updates_zero(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        result = run_cli("update", "entities", "--ids", "e999", "--stage", "rejected", db=db)
        assert "Updated 0 entities" in result.stdout

    def test_stage_filter(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://a.org")
        id_b = register_entity(db, "Org B", "https://b.org")
        run_cli("update", "entities", "--ids", id_b, "--stage", "rejected", db=db)
        result = run_cli("get", "entities", "--filter", "stage=rejected", db=db)
        assert "Org B" in result.stdout
        assert "Org A" not in result.stdout

    def test_requires_at_least_one_field(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        result = run_cli("update", "entities", "--ids", eid, db=db)
        assert result.returncode != 0


class TestNotes:
    def test_upsert_notes(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        result = run_cli(
            "upsert", "notes", "--entity-id", eid,
            "--notes", "First observation", "Second observation",
            db=db,
        )
        assert result.returncode == 0
        assert "Added 2 notes" in result.stdout
        detail = run_cli("get", "entity", eid, db=db)
        assert "First observation" in detail.stdout
        assert "Second observation" in detail.stdout

    def test_upsert_skips_duplicates(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "notes", "--entity-id", eid, "--notes", "Same fact", db=db)
        result = run_cli("upsert", "notes", "--entity-id", eid, "--notes", "Same fact", db=db)
        assert "Added 0 notes" in result.stdout or "skipped 1" in result.stdout.lower()

    def test_update_note(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "notes", "--entity-id", eid, "--notes", "Old fact", db=db)
        detail = run_cli("get", "entity", eid, db=db)
        note_id = [line for line in detail.stdout.splitlines() if "Old fact" in line][0].split("]")[0].split("[")[1]
        result = run_cli("update", "note", "--note-id", note_id, "--note", "Corrected fact", db=db)
        assert result.returncode == 0
        detail = run_cli("get", "entity", eid, db=db)
        assert "Corrected fact" in detail.stdout
        assert "Old fact" not in detail.stdout

    def test_remove_notes(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "notes", "--entity-id", eid, "--notes", "Keep this", "Remove this", db=db)
        detail = run_cli("get", "entity", eid, db=db)
        note_id = [line for line in detail.stdout.splitlines() if "Remove this" in line][0].split("]")[0].split("[")[1]
        run_cli("remove", "notes", "--entity-id", eid, "--note-ids", note_id, db=db)
        detail = run_cli("get", "entity", eid, db=db)
        assert "Keep this" in detail.stdout
        assert "Remove this" not in detail.stdout


class TestGetEntity:
    def test_shows_detail(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org", relevance=5, description="Test platform")
        run_cli("upsert", "notes", "--entity-id", eid, "--notes", "Key observation", db=db)
        result = run_cli("get", "entity", eid, db=db)
        assert result.returncode == 0
        assert "Org A" in result.stdout
        assert "Key observation" in result.stdout
        assert "Relevance: 5" in result.stdout
        assert "Description: Test platform" in result.stdout

    def test_shows_urls(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        result = run_cli("get", "entity", eid, db=db)
        assert "URLs (1)" in result.stdout
        assert "a.org" in result.stdout

    def test_not_found(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        result = run_cli("get", "entity", "e999", db=db)
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()


class TestGetEntities:
    def test_empty(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        result = run_cli("get", "entities", db=db)
        assert result.returncode == 0
        assert "No entities" in result.stdout

    def test_with_entities(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://a.org", relevance=8)
        register_entity(db, "Org B", "https://b.org", relevance=3)
        result = run_cli("get", "entities", db=db)
        assert "Org A" in result.stdout
        assert "Org B" in result.stdout

    def test_role_filter(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Example", "https://ex.org")
        register_entity(db, "Directory", "https://dir.org", role="directory")
        result = run_cli("get", "entities", "--filter", "role=directory", db=db)
        assert "Directory" in result.stdout
        assert "Example" not in result.stdout


class TestStats:
    def test_shows_summary(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://a.org")
        register_entity(db, "Org B", "https://b.org")
        result = run_cli("get", "stats", db=db)
        assert result.returncode == 0
        assert "2" in result.stdout


class TestExport:
    def test_json_export(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://a.org")
        result = run_cli("export", "--format", "json", db=db)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["name"] == "Org A"

    def test_csv_export(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        register_entity(db, "Org A", "https://a.org")
        result = run_cli("export", "--format", "csv", db=db)
        assert result.returncode == 0
        assert "Org A" in result.stdout


class TestProvenance:
    def test_upsert_provenance(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        result = run_cli("upsert", "provenance", "--entity-id", eid, "--source-url", "https://source.com", db=db)
        assert result.returncode == 0
        detail = run_cli("get", "entity", eid, db=db)
        assert "source.com" in detail.stdout

    def test_reach(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "provenance", "--entity-id", eid, "--source-url", "https://s1.com", db=db)
        run_cli("upsert", "provenance", "--entity-id", eid, "--source-url", "https://s2.com", db=db)
        result = run_cli("get", "reach", "--min", "2", db=db)
        assert "Org A" in result.stdout


class TestURL:
    def test_upsert_url(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "url", "--entity-id", eid, "--url", "https://a-secondary.org", db=db)
        detail = run_cli("get", "entity", eid, db=db)
        assert "URLs (2)" in detail.stdout
        assert "a-secondary.org" in detail.stdout


class TestMerge:
    def test_merge_entities(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        id1 = register_entity(db, "Org A", "https://a.org")
        id2 = register_entity(db, "Org B", "https://b.org")
        run_cli("upsert", "notes", "--entity-id", id1, "--notes", "Note on A", db=db)
        run_cli("upsert", "notes", "--entity-id", id2, "--notes", "Note on B", db=db)
        result = run_cli("merge", "entities", "--ids", f"{id1},{id2}", db=db)
        assert result.returncode == 0
        detail = run_cli("get", "entity", id1, db=db)
        assert "Note on A" in detail.stdout
        assert "Note on B" in detail.stdout
        assert "merged" in detail.stdout.lower()


class TestMeasures:
    def test_upsert_and_get_measures(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "measures", "--entity-id", eid, "--measures", "score=95", "rating=A", db=db)
        result = run_cli("get", "measures", db=db)
        assert "score" in result.stdout

    def test_clear_measures(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "measures", "--entity-id", eid, "--measures", "score=95", db=db)
        result = run_cli("clear", "measures", db=db)
        assert result.returncode == 0


class TestSourceData:
    def test_upsert_and_list(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli(
            "upsert", "source-data", "--entity-id", eid,
            "--source-type", "github", "--data", "stars=100", "forks=20",
            db=db,
        )
        result = run_cli("get", "source-data", "--entity-id", eid, db=db)
        assert "stars" in result.stdout
        assert "forks" in result.stdout


class TestSearchNotes:
    def test_search_pattern(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        eid = register_entity(db, "Org A", "https://a.org")
        run_cli("upsert", "notes", "--entity-id", eid, "--notes", "Uses React framework", db=db)
        result = run_cli("search", "notes", "--pattern", "React", db=db)
        assert result.returncode == 0
        assert "React" in result.stdout


class TestRegisterBatch:
    def test_batch_register(self, tmp_path: Path) -> None:
        db = init_db(tmp_path)
        entities = [
            {"name": "Batch A", "url": "https://batch-a.org", "description": "First batch entity"},
            {"name": "Batch B", "url": "https://batch-b.org", "description": "Second batch entity"},
        ]
        result = run_cli("register-batch", "--json", json.dumps(entities), db=db)
        assert result.returncode == 0
        listing = run_cli("get", "entities", db=db)
        assert "Batch A" in listing.stdout
        assert "Batch B" in listing.stdout


class TestNormalizeURLCLI:
    def test_normalize_url_command(self) -> None:
        cmd = [sys.executable, RUN_PY, "skills.research", "normalize-url", "https://www.Example.COM/path/"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        assert "example.com/path" in result.stdout
