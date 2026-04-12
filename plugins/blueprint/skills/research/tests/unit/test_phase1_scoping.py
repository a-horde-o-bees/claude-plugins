"""Phase 1 operations: entity creation, notes, sources, directory crawl state."""

import json
import sqlite3


def parse(result: str):
    return json.loads(result)


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


class TestPhase1Scoping:
    """Phase 1 operations: entity creation, notes, sources, directory crawl state."""

    def test_schema_discovery(self, db):
        """Agent discovers database structure on first run."""
        result = parse(db["describe_schema"]())
        assert "entities" in result
        assert "entity_notes" in result
        assert "entity_urls" in result
        assert "entity_measures" in result

    def test_single_table_schema(self, db):
        """Agent inspects specific table schema."""
        result = parse(db["describe_schema"](table="entities"))
        assert result["table"] == "entities"
        col_names = [c["name"] for c in result["columns"]]
        assert "id" in col_names
        assert "name" in col_names
        assert "stage" in col_names
        assert "relevance" in col_names

    def test_create_context_entity(self, db):
        """Register a context source (knowledge/advice)."""
        text = result_text(db["register_entity"]({
            "name": "ArchUnit Docs",
            "url": "https://www.archunit.org/userguide",
            "description": "Architecture rule testing patterns",
            "modes": ["context"],
            "relevance": 8,
        }))
        assert "id: e1" in text

    def test_create_directory_entity(self, db):
        """Register a directory source (crawlable listing)."""
        text = result_text(db["register_entity"]({
            "name": "awesome-static-analysis",
            "url": "https://github.com/analysis-tools-dev/static-analysis",
            "description": "Curated list of static analysis tools",
            "modes": ["directory"],
            "relevance": 7,
        }))
        assert "id: e1" in text

    def test_url_dedup_returns_existing(self, db):
        """Creating entity with duplicate URL returns existing ID."""
        db["register_entity"]({"name": "Tool A", "url": "https://example.com/tool"})
        text = result_text(db["register_entity"]({"name": "Tool A Dupe", "url": "https://example.com/tool"}))
        assert "Already registered" in text
        assert "e1" in text

    def test_url_normalization(self, db):
        """URLs normalized: scheme stripped, www stripped, lowercased, trailing slash stripped."""
        db["register_entity"]({"name": "Tool A", "url": "https://www.Example.com/Path/"})
        text = result_text(db["register_entity"]({"name": "Dupe", "url": "http://example.com/Path"}))
        assert "Already registered" in text

    def test_provenance_tracking(self, db):
        """Source URL creates provenance link."""
        db["register_entity"]({
            "name": "Found Entity",
            "url": "https://found.com",
            "source_url": "https://directory.com/listing",
        })
        # Verify provenance via get_entity detail
        detail = result_text(db["get_entity"]("e1"))
        assert "directory.com/listing" in detail

    def test_create_accessibility_note(self, db):
        """Add tagged note for directory accessibility."""
        db["register_entity"]({"name": "Directory", "url": "https://dir.com", "modes": ["directory"]})
        text = result_text(db["add_notes"]("e1", [
            "[ACCESSIBILITY]: static — GitHub README with tool listings",
        ]))
        assert "Added 1 notes" in text

    def test_create_multiple_notes(self, db):
        """Batch create notes for an entity."""
        db["register_entity"]({"name": "Entity", "url": "https://e.com"})
        text = result_text(db["add_notes"]("e1", [
            "First observation",
            "Second observation",
            "Third observation",
        ]))
        assert "Added 3 notes" in text

    def test_read_entities_by_mode(self, db):
        """List entities filtered by mode."""
        db["register_entity"]({"name": "Context", "url": "https://c.com", "modes": ["context"]})
        db["register_entity"]({"name": "Directory", "url": "https://d.com", "modes": ["directory"]})
        db["register_entity"]({"name": "Example", "url": "https://e.com", "modes": ["example"]})

        contexts = result_text(db["list_entities"](mode="context"))
        assert "Context" in contexts
        assert "Directory" not in contexts

        directories = result_text(db["list_entities"](mode="directory"))
        assert "Directory" in directories
        assert "Example" not in directories

    def test_batch_entity_creation(self, db):
        """Batch create entities (directory crawl result)."""
        text = result_text(db["register_entities"]([
            {"name": "Tool A", "url": "https://a.com", "relevance": 7, "description": "First tool"},
            {"name": "Tool B", "url": "https://b.com", "relevance": 5, "description": "Second tool"},
            {"name": "Tool C", "url": "https://c.com", "relevance": 3, "description": "Third tool"},
        ]))
        assert "3 new" in text

    def test_batch_with_dedup(self, db):
        """Batch create where some entities already exist."""
        db["register_entity"]({"name": "Existing", "url": "https://existing.com"})
        text = result_text(db["register_entities"]([
            {"name": "Existing Dupe", "url": "https://existing.com"},
            {"name": "New Entity", "url": "https://new.com"},
        ]))
        assert "1 new" in text
        assert "1 already registered" in text

    def test_crawl_progress_notes(self, db):
        """Directory crawl state tracked via tagged notes."""
        db["register_entity"]({"name": "Directory", "url": "https://dir.com", "modes": ["directory"]})

        db["add_notes"]("e1", ["[CRAWL METHOD]: WebFetch of GitHub README"])
        db["add_notes"]("e1", ["[CRAWL PROGRESS]: Processed pages 1-5. 12 entities registered."])

        detail = result_text(db["get_entity"]("e1"))
        assert "[CRAWL PROGRESS]" in detail

        # Find progress note ID from detail and update it
        # Detail format: [n2] [CRAWL PROGRESS]: ...
        conn = sqlite3.connect(db["path"])
        conn.row_factory = sqlite3.Row
        progress_note = conn.execute(
            "SELECT id FROM entity_notes WHERE entity_id = 'e1' AND note LIKE '%[CRAWL PROGRESS]%'"
        ).fetchone()
        conn.close()
        progress_note_id = progress_note["id"]

        db["remove_notes"]("e1", [progress_note_id])
        db["add_notes"]("e1", ["[CRAWL PROGRESS]: Processed pages 1-10. 24 entities registered."])

        detail = result_text(db["get_entity"]("e1"))
        assert "pages 1-10" in detail
        # Only one CRAWL PROGRESS note should remain
        assert detail.count("[CRAWL PROGRESS]") == 1

    def test_create_entity_with_notes(self, db):
        """Create entity then add notes — symmetric with get_entity detail view."""
        text = result_text(db["register_entity"]({
            "name": "Nested Entity",
            "url": "https://nested.com",
            "relevance": 7,
        }))
        assert "id: e1" in text

        db["add_notes"]("e1", ["First observation", "Second observation"])

        detail = result_text(db["get_entity"]("e1"))
        assert "First observation" in detail
        assert "Second observation" in detail

    def test_create_batch_entities_with_notes(self, db):
        """Batch create entities then add notes to each."""
        db["register_entities"]([
            {"name": "Tool A", "url": "https://a.com", "notes": ["Note on A"]},
            {"name": "Tool B", "url": "https://b.com", "notes": ["Note on B"]},
        ])

        detail_a = result_text(db["get_entity"]("e1"))
        detail_b = result_text(db["get_entity"]("e2"))
        assert "Note on A" in detail_a
        assert "Note on B" in detail_b

    def test_notes_not_created_for_duplicate_entity(self, db):
        """Notes not created when entity is a duplicate (register_batch skips notes for dupes)."""
        db["register_entity"]({"name": "Existing", "url": "https://existing.com"})
        text = result_text(db["register_entities"]([
            {"name": "Dupe", "url": "https://existing.com", "notes": ["Should not be created"]},
        ]))
        assert "already registered" in text.lower()

        detail = result_text(db["get_entity"]("e1"))
        assert "Should not be created" not in detail
