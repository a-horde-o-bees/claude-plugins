"""Phase 1-4 sequential happy path — entity creation, research, analysis, blueprint.

Tests exercise the same functions agents call during each phase, verifying
database operations produce correct state for downstream phases.
"""

import json
import sqlite3


def parse(result: str):
    return json.loads(result)


def result_text(result: str) -> str:
    """Extract result string from _ok() wrapper."""
    return json.loads(result)["result"]


# =============================================================================
# Phase 1: Scoping
# =============================================================================


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


# =============================================================================
# Phase 2: Deep Research
# =============================================================================


class TestPhase2DeepResearch:
    """Phase 2 operations: research agents writing notes, advancing stage."""

    def _seed_for_research(self, db):
        db["register_entity"]({"name": "High Priority", "url": "https://hp.com", "relevance": 9})
        db["register_entity"]({"name": "Med Priority", "url": "https://mp.com", "relevance": 7})
        db["register_entity"]({"name": "Low Priority", "url": "https://lp.com", "relevance": 5})
        db["add_notes"]("e1", ["Initial discovery observation"])

    def test_get_research_queue(self, db):
        """Phase 2 input: entities filtered for research queue."""
        self._seed_for_research(db)
        text = result_text(db["list_entities"](stage="new"))
        assert "High Priority" in text
        assert "Med Priority" in text
        assert "Low Priority" in text

    def test_research_agent_reads_entity(self, db):
        """Research agent loads entity with existing notes."""
        self._seed_for_research(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "High Priority" in detail
        assert "Initial discovery observation" in detail

    def test_research_agent_writes_notes(self, db):
        """Research agent adds comprehensive notes after research."""
        self._seed_for_research(db)
        db["add_notes"]("e1", [
            "Apache 2.0 licensed, fully open source",
            "32k GitHub stars, active maintenance",
            "Supports 30+ languages via tree-sitter",
        ])
        detail = result_text(db["get_entity"]("e1"))
        assert "Apache 2.0" in detail
        assert "32k GitHub stars" in detail
        assert "tree-sitter" in detail
        # Should have 4 notes total: 1 initial + 3 new
        assert "Notes (4)" in detail

    def test_research_agent_reconciles_notes(self, db):
        """Research agent corrects outdated note during reconciliation."""
        self._seed_for_research(db)
        db["add_notes"]("e1", ["15k stars"])

        # Find the outdated note ID
        conn = sqlite3.connect(db["path"])
        conn.row_factory = sqlite3.Row
        outdated = conn.execute(
            "SELECT id FROM entity_notes WHERE entity_id = 'e1' AND note = '15k stars'"
        ).fetchone()
        conn.close()

        db["remove_notes"]("e1", [outdated["id"]])
        db["add_notes"]("e1", ["32k GitHub stars as of March 2026"])

        detail = result_text(db["get_entity"]("e1"))
        assert "32k GitHub stars as of March 2026" in detail
        assert "15k stars" not in detail

    def test_advance_stage_to_researched(self, db):
        """Research agent marks entity as researched after completing."""
        self._seed_for_research(db)
        db["set_stage"]("e1", "researched")
        detail = result_text(db["get_entity"]("e1"))
        assert "Stage: researched" in detail

    def test_verify_stage_after_completion(self, db):
        """Orchestrator verifies agent actually set stage."""
        self._seed_for_research(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "Stage: new" in detail  # not advanced — needs re-spawn

    def test_adjacent_entity_discovery(self, db):
        """Research agent discovers and registers adjacent entities."""
        self._seed_for_research(db)
        text = result_text(db["register_entity"]({
            "name": "Adjacent Tool",
            "url": "https://adjacent.com",
            "source_url": "https://hp.com",
            "description": "Found while researching High Priority",
            "relevance": 6,
        }))
        assert "id: e4" in text

        detail = result_text(db["get_entity"]("e4"))
        assert "Found via" in detail


# =============================================================================
# Phase 3: Analysis
# =============================================================================


class TestPhase3Analysis:
    """Phase 3 operations: analysis queries, measure extraction, incremental measures."""

    def _seed_for_analysis(self, db):
        for i, (name, rel) in enumerate([
            ("Code Review", 9),
            ("Semgrep", 8),
            ("Superpowers", 8),
            ("ArchUnit", 7),
        ], 1):
            db["register_entity"]({"name": name, "url": f"https://e{i}.com", "relevance": rel})
            db["set_stage"](f"e{i}", "researched")
            db["add_notes"](f"e{i}", [
                f"{name} note 1",
                f"{name} note 2",
            ])

    def test_get_researched_entities(self, db):
        """Analysis input: all researched entities."""
        self._seed_for_analysis(db)
        text = result_text(db["list_entities"](stage="researched"))
        assert "Code Review" in text
        assert "ArchUnit" in text

    def test_analysis_agent_reads_notes(self, db):
        """Analysis agent reads entity with all notes."""
        self._seed_for_analysis(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "Notes (2)" in detail

    def test_measure_extraction(self, db):
        """Extract measures per entity from analysis findings."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["set_measures"](f"e{i}", [
                {"measure": "implementation_model", "value": "markdown-only"},
                {"measure": "activation_scope", "value": "pr"},
                {"measure": "confidence_scoring", "value": "yes"},
            ])

        summary = result_text(db["get_measure_summary"]())
        assert "implementation_model" in summary
        assert "activation_scope" in summary
        assert "confidence_scoring" in summary

    def test_measure_distribution_query(self, db):
        """Query measure distributions for findings report."""
        self._seed_for_analysis(db)
        db["set_measures"]("e1", [{"measure": "scope", "value": "pr"}])
        db["set_measures"]("e2", [{"measure": "scope", "value": "whole-project"}])
        db["set_measures"]("e3", [{"measure": "scope", "value": "pr"}])
        db["set_measures"]("e4", [{"measure": "scope", "value": "whole-project"}])

        summary = result_text(db["get_measure_summary"]())
        assert "scope" in summary

    def test_incremental_measures_new_entities_only(self, db):
        """Adding entities after initial analysis: only new entities need measures."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["set_measures"](f"e{i}", [{"measure": "score", "value": str(i * 10)}])

        db["register_entity"]({"name": "New Entity", "url": "https://new.com", "relevance": 6})
        db["set_stage"]("e5", "researched")

        # e5 has no measures yet — verify via get_entity
        detail = result_text(db["get_entity"]("e5"))
        assert "Measures" not in detail

        db["set_measures"]("e5", [{"measure": "score", "value": "60"}])

        detail = result_text(db["get_entity"]("e5"))
        assert "score: 60" in detail

    def test_criteria_change_clears_all_measures(self, db):
        """Effectiveness criteria change clears all measures for re-extraction."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["set_measures"](f"e{i}", [{"measure": "score", "value": str(i * 10)}])

        db["clear_all_measures"]()

        # Verify no measures on any entity
        for i in range(1, 5):
            detail = result_text(db["get_entity"](f"e{i}"))
            assert "Measures" not in detail


# =============================================================================
# Phase 4: Blueprint
# =============================================================================


class TestPhase4Blueprint:
    """Phase 4 operations: full entity reads for implementation blueprint."""

    def _seed_full_dataset(self, db):
        db["register_entity"]({"name": "Top Entity", "url": "https://top.com", "relevance": 9})
        db["set_stage"]("e1", "researched")
        db["add_notes"]("e1", [
            "Key architectural pattern: markdown-as-code",
            "Multi-agent parallel dispatch via Task tool",
        ])
        db["set_measures"]("e1", [
            {"measure": "implementation_model", "value": "markdown-only"},
            {"measure": "activation_scope", "value": "pr"},
        ])

    def test_full_entity_with_all_includes(self, db):
        """Phase 4 reads entity with notes, measures, and URLs."""
        self._seed_full_dataset(db)
        detail = result_text(db["get_entity"]("e1"))
        assert "Top Entity" in detail
        assert "Notes (2)" in detail
        assert "Measures (2)" in detail
        assert "URLs" in detail

    def test_read_all_researched_with_notes(self, db):
        """Phase 4 bulk read: all researched entities listed."""
        self._seed_full_dataset(db)
        db["register_entity"]({"name": "Second", "url": "https://second.com", "relevance": 7})
        db["set_stage"]("e2", "researched")
        db["add_notes"]("e2", ["Note for second entity"])

        text = result_text(db["list_entities"](stage="researched"))
        assert "Top Entity" in text
        assert "Second" in text
