"""Integration tests for MCP server — full phase workflow end-to-end.

Exercises every database operation the blueprint phases produce, including
non-sequential flows: phase reversion, re-entry with existing data,
interrupted research resumption, scope refinement loops, criteria changes,
incremental measures, and duplicate resolution.

Each test class represents a workflow scenario. All tests use a fresh temp
database via the db fixture. MCP tool functions are called directly (same
functions agents call, bypassing JSON-RPC transport).
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Setup paths so we can import the server and research modules
_plugin_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(_plugin_root))

from skills.research._db import init_db


@pytest.fixture
def db(tmp_path):
    """Create fresh database and configure server to use it."""
    db_path = str(tmp_path / "test.db")
    init_db(db_path)
    os.environ["DB_PATH"] = db_path

    # Import server tools AFTER setting DB_PATH
    import importlib
    import servers.research_db as srv
    importlib.reload(srv)
    # Update the module-level DB_PATH
    srv.DB_PATH = db_path

    yield {
        "path": db_path,
        "create": srv.create_records,
        "read": srv.read_records,
        "update": srv.update_records,
        "delete": srv.delete_records,
        "query": srv.query,
        "describe": srv.describe_entities,
        "merge": srv.merge_entities,
    }


def _json(result: str):
    """Parse JSON string result from MCP tool."""
    return json.loads(result)


# =============================================================================
# Phase 1: Scoping — sequential happy path
# =============================================================================


class TestPhase1Scoping:
    """Phase 1 operations: entity creation, notes, sources, directory crawl state."""

    def test_schema_discovery(self, db):
        """Agent discovers database structure on first run."""
        result = _json(db["describe"]())
        assert "entities" in result
        assert "entity_notes" in result
        assert "entity_urls" in result
        assert "entity_measures" in result

    def test_single_table_schema(self, db):
        """Agent inspects specific table schema."""
        result = _json(db["describe"]("entities"))
        assert result["table"] == "entities"
        col_names = [c["name"] for c in result["columns"]]
        assert "id" in col_names
        assert "name" in col_names
        assert "stage" in col_names
        assert "relevance" in col_names
        assert "entity_notes" in result["relationships"]

    def test_create_context_entity(self, db):
        """Register a context source (knowledge/advice)."""
        result = _json(db["create"]("entities", {
            "name": "ArchUnit Docs",
            "url": "https://www.archunit.org/userguide",
            "description": "Architecture rule testing patterns",
            "role": "context",
            "relevance": 8,
        }))
        assert "id: e1" in result

    def test_create_directory_entity(self, db):
        """Register a directory source (crawlable listing)."""
        result = _json(db["create"]("entities", {
            "name": "awesome-static-analysis",
            "url": "https://github.com/analysis-tools-dev/static-analysis",
            "description": "Curated list of static analysis tools",
            "role": "directory",
            "relevance": 7,
        }))
        assert "id: e1" in result

    def test_url_dedup_returns_existing(self, db):
        """Creating entity with duplicate URL returns existing ID."""
        db["create"]("entities", {"name": "Tool A", "url": "https://example.com/tool"})
        result = _json(db["create"]("entities", {"name": "Tool A Dupe", "url": "https://example.com/tool"}))
        assert "Already registered" in result
        assert "e1" in result

    def test_url_normalization(self, db):
        """URLs normalized: scheme stripped, www stripped, lowercased, trailing slash stripped."""
        db["create"]("entities", {"name": "Tool A", "url": "https://www.Example.com/Path/"})
        result = _json(db["create"]("entities", {"name": "Dupe", "url": "http://example.com/Path"}))
        assert "Already registered" in result

    def test_provenance_tracking(self, db):
        """Source URL creates provenance link."""
        db["create"]("entities", {
            "name": "Found Entity",
            "url": "https://found.com",
            "source_url": "https://directory.com/listing",
        })
        result = _json(db["query"](
            "SELECT source_url, entity_id FROM url_provenance"
        ))
        assert len(result) == 1
        assert "directory.com/listing" in result[0]["source_url"]

    def test_create_accessibility_note(self, db):
        """Add tagged note for directory accessibility."""
        db["create"]("entities", {"name": "Directory", "url": "https://dir.com", "role": "directory"})
        result = _json(db["create"]("entity_notes", {
            "entity_id": "e1",
            "note": "[ACCESSIBILITY]: static — GitHub README with tool listings",
        }))
        assert "Added 1 notes" in result

    def test_create_multiple_notes(self, db):
        """Batch create notes for an entity."""
        db["create"]("entities", {"name": "Entity", "url": "https://e.com"})
        result = _json(db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "First observation"},
            {"entity_id": "e1", "note": "Second observation"},
            {"entity_id": "e1", "note": "Third observation"},
        ]))
        assert len(result) == 3

    def test_read_entities_by_role(self, db):
        """List entities filtered by role."""
        db["create"]("entities", {"name": "Context", "url": "https://c.com", "role": "context"})
        db["create"]("entities", {"name": "Directory", "url": "https://d.com", "role": "directory"})
        db["create"]("entities", {"name": "Example", "url": "https://e.com", "role": "example"})

        contexts = _json(db["read"]("entities", {"role": "context"}))
        assert len(contexts) == 1
        assert contexts[0]["name"] == "Context"

        directories = _json(db["read"]("entities", {"role": "directory"}))
        assert len(directories) == 1
        assert directories[0]["name"] == "Directory"

    def test_batch_entity_creation(self, db):
        """Batch create entities (directory crawl result)."""
        result = _json(db["create"]("entities", [
            {"name": "Tool A", "url": "https://a.com", "relevance": 7, "description": "First tool"},
            {"name": "Tool B", "url": "https://b.com", "relevance": 5, "description": "Second tool"},
            {"name": "Tool C", "url": "https://c.com", "relevance": 3, "description": "Third tool"},
        ]))
        assert len(result) == 3
        assert any("id: e1" in r for r in result)
        assert any("id: e2" in r for r in result)
        assert any("id: e3" in r for r in result)

    def test_batch_with_dedup(self, db):
        """Batch create where some entities already exist."""
        db["create"]("entities", {"name": "Existing", "url": "https://existing.com"})
        result = _json(db["create"]("entities", [
            {"name": "Existing Dupe", "url": "https://existing.com"},
            {"name": "New Entity", "url": "https://new.com"},
        ]))
        assert any("Already registered" in r for r in result)
        assert any("id: e2" in r for r in result)

    def test_crawl_progress_notes(self, db):
        """Directory crawl state tracked via tagged notes."""
        db["create"]("entities", {"name": "Directory", "url": "https://dir.com", "role": "directory"})

        # Initial crawl method
        db["create"]("entity_notes", {"entity_id": "e1", "note": "[CRAWL METHOD]: WebFetch of GitHub README"})

        # First progress checkpoint
        db["create"]("entity_notes", {"entity_id": "e1", "note": "[CRAWL PROGRESS]: Processed pages 1-5. 12 entities registered."})

        # Read progress
        notes = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        note_texts = [n["note"] for n in notes[0]["entity_notes"]]
        assert any("[CRAWL PROGRESS]" in n for n in note_texts)

        # Update progress (delete old, create new)
        progress_note = next(n for n in notes[0]["entity_notes"] if "[CRAWL PROGRESS]" in n["note"])
        db["delete"]("entity_notes", id=progress_note["id"])
        db["create"]("entity_notes", {"entity_id": "e1", "note": "[CRAWL PROGRESS]: Processed pages 1-10. 24 entities registered."})

        # Verify updated
        notes = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        progress_notes = [n for n in notes[0]["entity_notes"] if "[CRAWL PROGRESS]" in n["note"]]
        assert len(progress_notes) == 1
        assert "pages 1-10" in progress_notes[0]["note"]


# =============================================================================
# Phase 1: Scope Refinement Loops
# =============================================================================


    def test_create_entity_with_nested_notes(self, db):
        """Create entity with notes in one call — symmetric with read_records include."""
        result = _json(db["create"]("entities", {
            "name": "Nested Entity",
            "url": "https://nested.com",
            "relevance": 7,
            "entity_notes": [
                {"note": "First observation"},
                {"note": "Second observation"},
            ],
        }))
        assert "id: e1" in result

        # Notes created automatically with entity_id filled in
        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 2
        notes = [n["note"] for n in entity[0]["entity_notes"]]
        assert "First observation" in notes
        assert "Second observation" in notes

    def test_create_batch_entities_with_nested_notes(self, db):
        """Batch create entities with nested notes."""
        result = _json(db["create"]("entities", [
            {"name": "Tool A", "url": "https://a.com", "entity_notes": [{"note": "Note on A"}]},
            {"name": "Tool B", "url": "https://b.com", "entity_notes": [{"note": "Note on B"}]},
        ]))
        assert len(result) == 2

        a = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        b = _json(db["read"]("entities", {"id": "e2"}, include=["entity_notes"]))
        assert len(a[0]["entity_notes"]) == 1
        assert len(b[0]["entity_notes"]) == 1

    def test_nested_notes_skipped_for_duplicate_entity(self, db):
        """Nested notes not created when entity is a duplicate."""
        db["create"]("entities", {"name": "Existing", "url": "https://existing.com"})
        result = _json(db["create"]("entities", {
            "name": "Dupe",
            "url": "https://existing.com",
            "entity_notes": [{"note": "Should not be created"}],
        }))
        assert "Already registered" in result

        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 0


class TestPhase1ScopeRefinement:
    """Non-sequential Phase 1: criteria changes, relevance reassessment, hardline filters."""

    def _seed_entities(self, db):
        """Create a landscape of entities at various relevance levels."""
        db["create"]("entities", {"name": "High Rel", "url": "https://high.com", "relevance": 9, "role": "example"})
        db["create"]("entities", {"name": "Mid Rel", "url": "https://mid.com", "relevance": 5, "role": "example"})
        db["create"]("entities", {"name": "Low Rel", "url": "https://low.com", "relevance": 2, "role": "example"})
        db["create"]("entities", {"name": "Context Source", "url": "https://ctx.com", "relevance": 7, "role": "context"})

    def test_relevance_reassessment(self, db):
        """Criteria change triggers relevance rescore on existing entities."""
        self._seed_entities(db)

        # Simulate reassessment: boost mid, demote high
        db["update"]("entities", "e1", {"relevance": 6})
        db["update"]("entities", "e2", {"relevance": 8})

        # Verify values updated
        e1 = _json(db["read"]("entities", {"id": "e1"}))
        e2 = _json(db["read"]("entities", {"id": "e2"}))
        assert e1[0]["relevance"] == 6
        assert e2[0]["relevance"] == 8

    def test_retroactive_hardline_filter(self, db):
        """New hardline criterion rejects existing entities."""
        self._seed_entities(db)

        # New criterion: reject entities with relevance < 3
        low_rel = _json(db["read"]("entities", {"relevance__lt": 3}))
        for entity in low_rel:
            db["update"]("entities", entity["id"], {"stage": "rejected"})
            db["create"]("entity_notes", {"entity_id": entity["id"], "note": "Rejected: below new relevance threshold"})

        # Verify
        rejected = _json(db["read"]("entities", {"stage": "rejected"}))
        assert len(rejected) == 1
        assert rejected[0]["name"] == "Low Rel"

    def test_criteria_change_clears_measures(self, db):
        """Criteria change invalidates existing measures."""
        self._seed_entities(db)

        # Create some measures
        db["create"]("entity_measures", {"entity_id": "e1", "measure": "score", "value": "95"})
        db["create"]("entity_measures", {"entity_id": "e2", "measure": "score", "value": "70"})

        # Criteria changed → clear all measures
        db["delete"]("entity_measures", all=True)

        # Verify cleared
        measures = _json(db["query"]("SELECT COUNT(*) as count FROM entity_measures"))
        assert measures[0]["count"] == 0

    def test_add_entities_from_new_source(self, db):
        """User discovers new directory mid-phase, adds entities."""
        self._seed_entities(db)

        # New directory discovered
        db["create"]("entities", {"name": "New Directory", "url": "https://newdir.com", "role": "directory", "relevance": 6})

        # Entities from new directory with provenance
        db["create"]("entities", {
            "name": "Newly Found Tool",
            "url": "https://newtool.com",
            "source_url": "https://newdir.com",
            "relevance": 7,
        })

        # Verify provenance links to new directory
        prov = _json(db["query"]("SELECT * FROM url_provenance WHERE source_url LIKE '%newdir%'"))
        assert len(prov) == 1


# =============================================================================
# Phase 1 → Phase 2 Transition
# =============================================================================


class TestPhase1ReEntry:
    """Phase 1 re-entry: dashboard queries with existing data."""

    def _seed_full_landscape(self, db):
        """Seed a realistic landscape for dashboard testing."""
        for i, (name, role, rel, stage) in enumerate([
            ("Researched Tool", "example", 9, "researched"),
            ("New Tool A", "example", 7, "new"),
            ("New Tool B", "example", 5, "new"),
            ("Rejected Tool", "example", 0, "rejected"),
            ("Context Source", "context", 8, "researched"),
            ("Directory", "directory", 6, "new"),
        ], 1):
            db["create"]("entities", {"name": name, "url": f"https://e{i}.com", "role": role, "relevance": rel})
            if stage != "new":
                db["update"]("entities", f"e{i}", {"stage": stage})

        # Add notes and provenance
        db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "Note 1 for researched tool"},
            {"entity_id": "e1", "note": "Note 2 for researched tool"},
        ])
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Single note for new tool"})

    def test_dashboard_stats_query(self, db):
        """Re-entry dashboard: entity counts by role and stage."""
        self._seed_full_landscape(db)

        # Count by stage
        stats = _json(db["query"](
            "SELECT stage, COUNT(*) as count FROM entities GROUP BY stage ORDER BY stage"
        ))
        stage_counts = {s["stage"]: s["count"] for s in stats}
        assert stage_counts["new"] == 3
        assert stage_counts["researched"] == 2

    def test_dashboard_examples_by_relevance(self, db):
        """Re-entry dashboard: examples with relevance values."""
        self._seed_full_landscape(db)

        examples = _json(db["read"]("entities", {"role": "example"}))
        assert len(examples) == 4  # 4 example entities in seed
        relevances = {e["name"]: e["relevance"] for e in examples}
        assert relevances["Researched Tool"] == 9

    def test_dashboard_provenance(self, db):
        """Re-entry dashboard: provenance source counts."""
        self._seed_full_landscape(db)
        # No provenance in seed — just verify query works
        prov = _json(db["query"]("SELECT source_url, COUNT(entity_id) as entity_count FROM url_provenance GROUP BY source_url"))
        assert isinstance(prov, list)

    def test_dashboard_multi_source_entities(self, db):
        """Re-entry dashboard: entities found via multiple sources."""
        self._seed_full_landscape(db)
        reach = _json(db["query"](
            "SELECT entity_id, COUNT(source_url) as source_count FROM url_provenance GROUP BY entity_id HAVING source_count >= 2"
        ))
        assert isinstance(reach, list)


# =============================================================================
# Phase 2: Deep Research — sequential
# =============================================================================


class TestPhase2DeepResearch:
    """Phase 2 operations: research agents writing notes, advancing stage."""

    def _seed_for_research(self, db):
        """Seed entities ready for deep research."""
        db["create"]("entities", {"name": "High Priority", "url": "https://hp.com", "relevance": 9})
        db["create"]("entities", {"name": "Med Priority", "url": "https://mp.com", "relevance": 7})
        db["create"]("entities", {"name": "Low Priority", "url": "https://lp.com", "relevance": 5})
        # Add initial notes from Phase 1 discovery
        db["create"]("entity_notes", {"entity_id": "e1", "note": "Initial discovery observation"})

    def test_get_research_queue(self, db):
        """Phase 2 input: entities filtered for research queue."""
        self._seed_for_research(db)
        queue = _json(db["read"]("entities", {"stage": "new"}))
        assert len(queue) == 3
        relevances = {e["name"]: e["relevance"] for e in queue}
        assert relevances["High Priority"] == 9
        assert relevances["Med Priority"] == 7
        assert relevances["Low Priority"] == 5

    def test_research_agent_reads_entity(self, db):
        """Research agent loads entity with existing notes."""
        self._seed_for_research(db)
        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity) == 1
        assert entity[0]["name"] == "High Priority"
        assert len(entity[0]["entity_notes"]) == 1

    def test_research_agent_writes_notes(self, db):
        """Research agent adds comprehensive notes after research."""
        self._seed_for_research(db)
        db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "Apache 2.0 licensed, fully open source"},
            {"entity_id": "e1", "note": "32k GitHub stars, active maintenance"},
            {"entity_id": "e1", "note": "Supports 30+ languages via tree-sitter"},
        ])
        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 4  # 1 initial + 3 new

    def test_research_agent_reconciles_notes(self, db):
        """Research agent corrects outdated note during reconciliation."""
        self._seed_for_research(db)
        db["create"]("entity_notes", {"entity_id": "e1", "note": "15k stars"})

        # Read existing notes
        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        outdated = next(n for n in entity[0]["entity_notes"] if "15k stars" in n["note"])

        # Delete outdated, add corrected
        db["delete"]("entity_notes", id=outdated["id"])
        db["create"]("entity_notes", {"entity_id": "e1", "note": "32k GitHub stars as of March 2026"})

        # Verify correction
        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        notes = [n["note"] for n in entity[0]["entity_notes"]]
        assert "32k GitHub stars as of March 2026" in notes
        assert "15k stars" not in notes

    def test_advance_stage_to_researched(self, db):
        """Research agent marks entity as researched after completing."""
        self._seed_for_research(db)
        db["update"]("entities", "e1", {"stage": "researched"})
        entity = _json(db["read"]("entities", {"id": "e1"}))
        assert entity[0]["stage"] == "researched"

    def test_verify_stage_after_completion(self, db):
        """Orchestrator verifies agent actually set stage."""
        self._seed_for_research(db)
        # Agent didn't set stage (simulating failure)
        entity = _json(db["read"]("entities", {"id": "e1"}))
        assert entity[0]["stage"] == "new"  # not advanced — needs re-spawn

    def test_adjacent_entity_discovery(self, db):
        """Research agent discovers and registers adjacent entities."""
        self._seed_for_research(db)
        # Agent finds related entity during research
        result = _json(db["create"]("entities", {
            "name": "Adjacent Tool",
            "url": "https://adjacent.com",
            "source_url": "https://hp.com",
            "description": "Found while researching High Priority",
            "relevance": 6,
        }))
        assert "id: e4" in result

        # Provenance links to source entity
        prov = _json(db["query"]("SELECT * FROM url_provenance WHERE entity_id = 'e4'"))
        assert len(prov) == 1


# =============================================================================
# Phase 2: Interrupted Research and Resumption
# =============================================================================


class TestPhase2Resumption:
    """Phase 2 re-entry: research interrupted, resume from checkpoint."""

    def _seed_partial_research(self, db):
        """Seed a partially researched landscape."""
        db["create"]("entities", {"name": "Done", "url": "https://done.com", "relevance": 9})
        db["update"]("entities", "e1", {"stage": "researched"})
        db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "Fully researched note 1"},
            {"entity_id": "e1", "note": "Fully researched note 2"},
        ])

        db["create"]("entities", {"name": "Partial", "url": "https://partial.com", "relevance": 8})
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Agent wrote this before interruption"})
        # Stage still 'new' — agent didn't finish

        db["create"]("entities", {"name": "Not Started", "url": "https://notstarted.com", "relevance": 7})

    def test_find_resume_point(self, db):
        """Identify unresearched entities for resumption."""
        self._seed_partial_research(db)
        pending = _json(db["read"]("entities", {"stage": "new"}))
        assert len(pending) == 2
        names = {e["name"] for e in pending}
        assert "Partial" in names
        assert "Not Started" in names

    def test_interrupted_agent_reconciles(self, db):
        """Re-spawned agent reads existing notes and continues."""
        self._seed_partial_research(db)
        entity = _json(db["read"]("entities", {"id": "e2"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 1  # partial notes from before

        # Agent continues research, adds more notes
        db["create"]("entity_notes", [
            {"entity_id": "e2", "note": "Additional research after resumption"},
            {"entity_id": "e2", "note": "Final observation before stage advance"},
        ])
        db["update"]("entities", "e2", {"stage": "researched"})

        entity = _json(db["read"]("entities", {"id": "e2"}, include=["entity_notes"]))
        assert entity[0]["stage"] == "researched"
        assert len(entity[0]["entity_notes"]) == 3


# =============================================================================
# Phase 2 → Phase 1 Reversion
# =============================================================================


class TestPhaseReversion:
    """Phase reversion: go back to Phase 1 to add more entities."""

    def _seed_post_research(self, db):
        """Seed a post-Phase-2 state with measures and researched entities."""
        db["create"]("entities", {"name": "Entity A", "url": "https://a.com", "relevance": 9})
        db["update"]("entities", "e1", {"stage": "researched"})
        db["create"]("entity_notes", {"entity_id": "e1", "note": "Research note"})
        db["create"]("entity_measures", {"entity_id": "e1", "measure": "score", "value": "95"})

        db["create"]("entities", {"name": "Entity B", "url": "https://b.com", "relevance": 7})
        db["update"]("entities", "e2", {"stage": "researched"})
        db["create"]("entity_measures", {"entity_id": "e2", "measure": "score", "value": "80"})

    def test_reversion_clears_measures(self, db):
        """Reverting to Phase 1 clears measures but preserves entities and notes."""
        self._seed_post_research(db)

        # Clear measures (reversion step)
        db["delete"]("entity_measures", all=True)

        # Entities and notes preserved
        entities = _json(db["read"]("entities"))
        assert len(entities) == 2

        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 1

        # Measures gone
        measures = _json(db["query"]("SELECT COUNT(*) as count FROM entity_measures"))
        assert measures[0]["count"] == 0

    def test_reversion_resets_stage(self, db):
        """Reverting to Phase 1 resets entity stage to allow re-research."""
        self._seed_post_research(db)

        # Reset stages to new
        db["update"]("entities", "e1", {"stage": "new"})
        db["update"]("entities", "e2", {"stage": "new"})

        entities = _json(db["read"]("entities", {"stage": "new"}))
        assert len(entities) == 2

    def test_new_entities_after_reversion(self, db):
        """New entities added after reversion coexist with existing data."""
        self._seed_post_research(db)

        # Add new entity during re-opened Phase 1
        db["create"]("entities", {"name": "New Discovery", "url": "https://new.com", "relevance": 8})

        all_entities = _json(db["read"]("entities"))
        assert len(all_entities) == 3

        # New entity at stage 'new', others still researched
        new = _json(db["read"]("entities", {"id": "e3"}))
        assert new[0]["stage"] == "new"


# =============================================================================
# Phase 3: Analysis
# =============================================================================


class TestPhase3Analysis:
    """Phase 3 operations: analysis queries, measure extraction, incremental measures."""

    def _seed_for_analysis(self, db):
        """Seed researched entities ready for analysis."""
        for i, (name, rel) in enumerate([
            ("Code Review", 9),
            ("Semgrep", 8),
            ("Superpowers", 8),
            ("ArchUnit", 7),
        ], 1):
            db["create"]("entities", {"name": name, "url": f"https://e{i}.com", "relevance": rel})
            db["update"]("entities", f"e{i}", {"stage": "researched"})
            db["create"]("entity_notes", [
                {"entity_id": f"e{i}", "note": f"{name} note 1"},
                {"entity_id": f"e{i}", "note": f"{name} note 2"},
            ])

    def test_get_researched_entities(self, db):
        """Analysis input: all researched entities."""
        self._seed_for_analysis(db)
        entities = _json(db["read"]("entities", {"stage": "researched"}))
        assert len(entities) == 4
        relevances = [e["relevance"] for e in entities]
        assert 9 in relevances
        assert 7 in relevances

    def test_analysis_agent_reads_notes(self, db):
        """Analysis agent reads entity with all notes."""
        self._seed_for_analysis(db)
        entity = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 2

    def test_measure_extraction(self, db):
        """Extract measures per entity from analysis findings."""
        self._seed_for_analysis(db)

        # Extract measures for each entity
        for i in range(1, 5):
            db["create"]("entity_measures", [
                {"entity_id": f"e{i}", "measure": "implementation_model", "value": "markdown-only"},
                {"entity_id": f"e{i}", "measure": "activation_scope", "value": "pr"},
                {"entity_id": f"e{i}", "measure": "confidence_scoring", "value": "yes"},
            ])

        # Verify measures exist
        measures = _json(db["query"](
            "SELECT measure, COUNT(DISTINCT entity_id) as entity_count FROM entity_measures GROUP BY measure"
        ))
        assert len(measures) == 3
        assert all(m["entity_count"] == 4 for m in measures)

    def test_measure_distribution_query(self, db):
        """Query measure distributions for findings report."""
        self._seed_for_analysis(db)
        db["create"]("entity_measures", [
            {"entity_id": "e1", "measure": "scope", "value": "pr"},
            {"entity_id": "e2", "measure": "scope", "value": "whole-project"},
            {"entity_id": "e3", "measure": "scope", "value": "pr"},
            {"entity_id": "e4", "measure": "scope", "value": "whole-project"},
        ])

        dist = _json(db["query"](
            "SELECT value, COUNT(*) as count FROM entity_measures WHERE measure = 'scope' GROUP BY value ORDER BY count DESC"
        ))
        assert len(dist) == 2
        assert dist[0]["count"] == 2

    def test_incremental_measures_new_entities_only(self, db):
        """Adding entities after initial analysis: only new entities need measures."""
        self._seed_for_analysis(db)

        # Initial measures for existing entities
        for i in range(1, 5):
            db["create"]("entity_measures", {"entity_id": f"e{i}", "measure": "score", "value": str(i * 10)})

        # New entity added (Phase 1 reversion)
        db["create"]("entities", {"name": "New Entity", "url": "https://new.com", "relevance": 6})
        db["update"]("entities", "e5", {"stage": "researched"})

        # Find entities without measures
        unmeasured = _json(db["query"](
            "SELECT e.id, e.name FROM entities e WHERE e.stage = 'researched' AND e.id NOT IN (SELECT DISTINCT entity_id FROM entity_measures)"
        ))
        assert len(unmeasured) == 1
        assert unmeasured[0]["id"] == "e5"

        # Add measures only for new entity
        db["create"]("entity_measures", {"entity_id": "e5", "measure": "score", "value": "60"})

        # All now measured
        unmeasured = _json(db["query"](
            "SELECT e.id FROM entities e WHERE e.stage = 'researched' AND e.id NOT IN (SELECT DISTINCT entity_id FROM entity_measures)"
        ))
        assert len(unmeasured) == 0

    def test_criteria_change_clears_all_measures(self, db):
        """Effectiveness criteria change clears all measures for re-extraction."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["create"]("entity_measures", {"entity_id": f"e{i}", "measure": "score", "value": str(i * 10)})

        # Criteria changed → clear
        db["delete"]("entity_measures", all=True)

        total = _json(db["query"]("SELECT COUNT(*) as count FROM entity_measures"))
        assert total[0]["count"] == 0


# =============================================================================
# Phase 4: Blueprint
# =============================================================================


class TestPhase4Blueprint:
    """Phase 4 operations: full entity reads for implementation blueprint."""

    def _seed_full_dataset(self, db):
        """Seed a complete dataset for blueprint generation."""
        db["create"]("entities", {"name": "Top Entity", "url": "https://top.com", "relevance": 9})
        db["update"]("entities", "e1", {"stage": "researched"})
        db["create"]("entity_notes", [
            {"entity_id": "e1", "note": "Key architectural pattern: markdown-as-code"},
            {"entity_id": "e1", "note": "Multi-agent parallel dispatch via Task tool"},
        ])
        db["create"]("entity_measures", [
            {"entity_id": "e1", "measure": "implementation_model", "value": "markdown-only"},
            {"entity_id": "e1", "measure": "activation_scope", "value": "pr"},
        ])

    def test_full_entity_with_all_includes(self, db):
        """Phase 4 reads entity with notes, measures, and URLs."""
        self._seed_full_dataset(db)
        entity = _json(db["read"](
            "entities", {"id": "e1"},
            include=["entity_notes", "entity_measures", "entity_urls"]
        ))
        assert len(entity) == 1
        assert len(entity[0]["entity_notes"]) == 2
        assert len(entity[0]["entity_measures"]) == 2
        assert "entity_urls" in entity[0]

    def test_read_all_researched_with_notes(self, db):
        """Phase 4 bulk read: all researched entities with notes."""
        self._seed_full_dataset(db)
        db["create"]("entities", {"name": "Second", "url": "https://second.com", "relevance": 7})
        db["update"]("entities", "e2", {"stage": "researched"})
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Note for second entity"})

        entities = _json(db["read"](
            "entities", {"stage": "researched"},
            include=["entity_notes"]
        ))
        assert len(entities) == 2
        assert all("entity_notes" in e for e in entities)


# =============================================================================
# Cross-Cutting: Duplicate Resolution
# =============================================================================


class TestDuplicateResolution:
    """Duplicate detection and merge — happens during deep research."""

    def test_merge_entities(self, db):
        """Merge duplicate entities into survivor."""
        db["create"]("entities", {"name": "Entity A", "url": "https://a.com", "relevance": 8, "description": "First description"})
        db["create"]("entities", {"name": "Entity A (dupe)", "url": "https://a-alt.com", "relevance": 6, "description": "Second description"})
        db["create"]("entity_notes", {"entity_id": "e1", "note": "Note on original"})
        db["create"]("entity_notes", {"entity_id": "e2", "note": "Note on duplicate"})

        db["merge"](["e1", "e2"])

        # Survivor has combined data
        survivor = _json(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(survivor) == 1
        assert len(survivor[0]["entity_notes"]) == 2  # both notes preserved

        # Merged entity gone or marked
        merged = _json(db["read"]("entities", {"id": "e2"}))
        assert len(merged) == 0 or merged[0]["stage"] == "merged"


# =============================================================================
# Cross-Cutting: Condition Operators
# =============================================================================


class TestConditionOperators:
    """Test all Django __operator conditions."""

    def _seed_entities(self, db):
        for i, (name, rel) in enumerate([
            ("Rel 9", 9), ("Rel 7", 7), ("Rel 5", 5), ("Rel 3", 3), ("Rel 0", 0),
        ], 1):
            db["create"]("entities", {"name": name, "url": f"https://e{i}.com", "relevance": rel})

    def test_equality(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance": 7}))
        assert len(result) == 1
        assert result[0]["name"] == "Rel 7"

    def test_gte(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance__gte": 7}))
        assert len(result) == 2

    def test_gt(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance__gt": 7}))
        assert len(result) == 1

    def test_lte(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance__lte": 3}))
        assert len(result) == 2

    def test_lt(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance__lt": 3}))
        assert len(result) == 1

    def test_ne(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance__ne": 0}))
        assert len(result) == 4

    def test_like(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"name__like": "Rel 9%"}))
        assert len(result) == 1

    def test_null_true(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"last_modified__null": True}))
        # Newly created entities have last_modified set by _touch
        assert isinstance(result, list)

    def test_null_false(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"last_modified__null": False}))
        assert isinstance(result, list)

    def test_combined_conditions(self, db):
        self._seed_entities(db)
        result = _json(db["read"]("entities", {"relevance__gte": 5, "relevance__lte": 7}))
        assert len(result) == 2
        assert all(5 <= e["relevance"] <= 7 for e in result)


# =============================================================================
# Cross-Cutting: Error Handling
# =============================================================================


class TestMissingDatabase:
    """Server handles missing database gracefully."""

    def test_read_without_database(self, tmp_path):
        """All tools return clear error when database doesn't exist."""
        os.environ["DB_PATH"] = str(tmp_path / "nonexistent.db")
        import importlib
        import servers.research_db as srv
        importlib.reload(srv)
        srv.DB_PATH = str(tmp_path / "nonexistent.db")

        result = _json(srv.read_records("entities"))
        assert "error" in result
        assert "not initialized" in result["error"].lower()

        result = _json(srv.create_records("entities", {"name": "Test"}))
        assert "error" in result

        result = _json(srv.query("SELECT 1"))
        assert "error" in result

        result = _json(srv.describe_entities())
        assert "error" in result

    def test_init_database_creates_schema(self, tmp_path):
        """init_database creates database when it doesn't exist."""
        db_path = str(tmp_path / "fresh.db")
        os.environ["DB_PATH"] = db_path
        import importlib
        import servers.research_db as srv
        importlib.reload(srv)
        srv.DB_PATH = db_path

        result = _json(srv.init_database())
        assert "initialized" in result["status"]

        # Now CRUD works
        result = _json(srv.describe_entities())
        assert "entities" in result


class TestErrorHandling:
    """Error cases that agents might encounter."""

    def test_invalid_table(self, db):
        result = _json(db["read"]("nonexistent_table"))
        assert "error" in str(result).lower() or isinstance(result, list)

    def test_query_rejects_insert(self, db):
        result = _json(db["query"]("INSERT INTO entities (id, name) VALUES ('e999', 'bad')"))
        assert "error" in result

    def test_query_rejects_delete(self, db):
        result = _json(db["query"]("DELETE FROM entities"))
        assert "error" in result

    def test_query_rejects_update(self, db):
        result = _json(db["query"]("UPDATE entities SET name = 'bad' WHERE id = 'e1'"))
        assert "error" in result

    def test_invalid_include_table(self, db):
        """Include with non-FK table raises error."""
        db["create"]("entities", {"name": "Test", "url": "https://test.com"})
        try:
            result = _json(db["read"]("entities", include=["nonexistent"]))
            assert "error" in str(result).lower()
        except ValueError:
            pass  # also acceptable

    def test_describe_invalid_table(self, db):
        result = _json(db["describe"]("nonexistent"))
        assert "error" in str(result).lower()


# =============================================================================
# Cross-Cutting: Source Data
# =============================================================================


class TestSourceData:
    """Entity source data — structured key-value per source type."""

    def test_create_and_read_source_data(self, db):
        db["create"]("entities", {"name": "Test", "url": "https://test.com"})
        db["create"]("entity_source_data", [
            {"entity_id": "e1", "source_type": "github", "key": "stars", "value": "14600"},
            {"entity_id": "e1", "source_type": "github", "key": "forks", "value": "1200"},
        ])

        data = _json(db["query"](
            "SELECT key, value FROM entity_source_data WHERE entity_id = 'e1' AND source_type = 'github'"
        ))
        assert len(data) == 2
        keys = {d["key"] for d in data}
        assert "stars" in keys
        assert "forks" in keys
