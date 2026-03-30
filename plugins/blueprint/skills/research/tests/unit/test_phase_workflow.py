"""Phase 1-4 sequential happy path — entity creation, research, analysis, blueprint.

Tests exercise the same functions agents call during each phase, verifying
database operations produce correct state for downstream phases.
"""

import json


def parse(result: str):
    return json.loads(result)


# =============================================================================
# Phase 1: Scoping
# =============================================================================


class TestPhase1Scoping:
    """Phase 1 operations: entity creation, notes, sources, directory crawl state."""

    def test_schema_discovery(self, db):
        """Agent discovers database structure on first run."""
        result = parse(db["describe"]())
        assert "entities" in result
        assert "entity_notes" in result
        assert "entity_urls" in result
        assert "entity_measures" in result

    def test_single_table_schema(self, db):
        """Agent inspects specific table schema."""
        result = parse(db["describe"]("entities"))
        assert result["table"] == "entities"
        col_names = [c["name"] for c in result["columns"]]
        assert "id" in col_names
        assert "name" in col_names
        assert "stage" in col_names
        assert "relevance" in col_names
        assert "entity_notes" in result["relationships"]

    def test_create_context_entity(self, db):
        """Register a context source (knowledge/advice)."""
        result = parse(db["create"]("entities", {
            "name": "ArchUnit Docs",
            "url": "https://www.archunit.org/userguide",
            "description": "Architecture rule testing patterns",
            "role": "context",
            "relevance": 8,
        }))
        assert "id: e1" in result

    def test_create_directory_entity(self, db):
        """Register a directory source (crawlable listing)."""
        result = parse(db["create"]("entities", {
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
        result = parse(db["create"]("entities", {"name": "Tool A Dupe", "url": "https://example.com/tool"}))
        assert "Already registered" in result
        assert "e1" in result

    def test_url_normalization(self, db):
        """URLs normalized: scheme stripped, www stripped, lowercased, trailing slash stripped."""
        db["create"]("entities", {"name": "Tool A", "url": "https://www.Example.com/Path/"})
        result = parse(db["create"]("entities", {"name": "Dupe", "url": "http://example.com/Path"}))
        assert "Already registered" in result

    def test_provenance_tracking(self, db):
        """Source URL creates provenance link."""
        db["create"]("entities", {
            "name": "Found Entity",
            "url": "https://found.com",
            "source_url": "https://directory.com/listing",
        })
        result = parse(db["query"](
            "SELECT source_url, entity_id FROM url_provenance"
        ))
        assert len(result) == 1
        assert "directory.com/listing" in result[0]["source_url"]

    def test_create_accessibility_note(self, db):
        """Add tagged note for directory accessibility."""
        db["create"]("entities", {"name": "Directory", "url": "https://dir.com", "role": "directory"})
        result = parse(db["create"]("entity_notes", {
            "entity_id": "e1",
            "note": "[ACCESSIBILITY]: static — GitHub README with tool listings",
        }))
        assert "Added 1 notes" in result

    def test_create_multiple_notes(self, db):
        """Batch create notes for an entity."""
        db["create"]("entities", {"name": "Entity", "url": "https://e.com"})
        result = parse(db["create"]("entity_notes", [
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

        contexts = parse(db["read"]("entities", {"role": "context"}))
        assert len(contexts) == 1
        assert contexts[0]["name"] == "Context"

        directories = parse(db["read"]("entities", {"role": "directory"}))
        assert len(directories) == 1
        assert directories[0]["name"] == "Directory"

    def test_batch_entity_creation(self, db):
        """Batch create entities (directory crawl result)."""
        result = parse(db["create"]("entities", [
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
        result = parse(db["create"]("entities", [
            {"name": "Existing Dupe", "url": "https://existing.com"},
            {"name": "New Entity", "url": "https://new.com"},
        ]))
        assert any("Already registered" in r for r in result)
        assert any("id: e2" in r for r in result)

    def test_crawl_progress_notes(self, db):
        """Directory crawl state tracked via tagged notes."""
        db["create"]("entities", {"name": "Directory", "url": "https://dir.com", "role": "directory"})

        db["create"]("entity_notes", {"entity_id": "e1", "note": "[CRAWL METHOD]: WebFetch of GitHub README"})
        db["create"]("entity_notes", {"entity_id": "e1", "note": "[CRAWL PROGRESS]: Processed pages 1-5. 12 entities registered."})

        notes = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        note_texts = [n["note"] for n in notes[0]["entity_notes"]]
        assert any("[CRAWL PROGRESS]" in n for n in note_texts)

        # Update progress (delete old, create new)
        progress_note = next(n for n in notes[0]["entity_notes"] if "[CRAWL PROGRESS]" in n["note"])
        db["delete"]("entity_notes", id=progress_note["id"])
        db["create"]("entity_notes", {"entity_id": "e1", "note": "[CRAWL PROGRESS]: Processed pages 1-10. 24 entities registered."})

        notes = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        progress_notes = [n for n in notes[0]["entity_notes"] if "[CRAWL PROGRESS]" in n["note"]]
        assert len(progress_notes) == 1
        assert "pages 1-10" in progress_notes[0]["note"]

    def test_create_entity_with_nested_notes(self, db):
        """Create entity with notes in one call — symmetric with read_records include."""
        result = parse(db["create"]("entities", {
            "name": "Nested Entity",
            "url": "https://nested.com",
            "relevance": 7,
            "entity_notes": [
                {"note": "First observation"},
                {"note": "Second observation"},
            ],
        }))
        assert "id: e1" in result

        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 2
        notes = [n["note"] for n in entity[0]["entity_notes"]]
        assert "First observation" in notes
        assert "Second observation" in notes

    def test_create_batch_entities_with_nested_notes(self, db):
        """Batch create entities with nested notes."""
        result = parse(db["create"]("entities", [
            {"name": "Tool A", "url": "https://a.com", "entity_notes": [{"note": "Note on A"}]},
            {"name": "Tool B", "url": "https://b.com", "entity_notes": [{"note": "Note on B"}]},
        ]))
        assert len(result) == 2

        a = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        b = parse(db["read"]("entities", {"id": "e2"}, include=["entity_notes"]))
        assert len(a[0]["entity_notes"]) == 1
        assert len(b[0]["entity_notes"]) == 1

    def test_nested_notes_skipped_for_duplicate_entity(self, db):
        """Nested notes not created when entity is a duplicate."""
        db["create"]("entities", {"name": "Existing", "url": "https://existing.com"})
        result = parse(db["create"]("entities", {
            "name": "Dupe",
            "url": "https://existing.com",
            "entity_notes": [{"note": "Should not be created"}],
        }))
        assert "Already registered" in result

        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 0


# =============================================================================
# Phase 2: Deep Research
# =============================================================================


class TestPhase2DeepResearch:
    """Phase 2 operations: research agents writing notes, advancing stage."""

    def _seed_for_research(self, db):
        db["create"]("entities", {"name": "High Priority", "url": "https://hp.com", "relevance": 9})
        db["create"]("entities", {"name": "Med Priority", "url": "https://mp.com", "relevance": 7})
        db["create"]("entities", {"name": "Low Priority", "url": "https://lp.com", "relevance": 5})
        db["create"]("entity_notes", {"entity_id": "e1", "note": "Initial discovery observation"})

    def test_get_research_queue(self, db):
        """Phase 2 input: entities filtered for research queue."""
        self._seed_for_research(db)
        queue = parse(db["read"]("entities", {"stage": "new"}))
        assert len(queue) == 3
        relevances = {e["name"]: e["relevance"] for e in queue}
        assert relevances["High Priority"] == 9
        assert relevances["Med Priority"] == 7
        assert relevances["Low Priority"] == 5

    def test_research_agent_reads_entity(self, db):
        """Research agent loads entity with existing notes."""
        self._seed_for_research(db)
        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
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
        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 4  # 1 initial + 3 new

    def test_research_agent_reconciles_notes(self, db):
        """Research agent corrects outdated note during reconciliation."""
        self._seed_for_research(db)
        db["create"]("entity_notes", {"entity_id": "e1", "note": "15k stars"})

        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        outdated = next(n for n in entity[0]["entity_notes"] if "15k stars" in n["note"])

        db["delete"]("entity_notes", id=outdated["id"])
        db["create"]("entity_notes", {"entity_id": "e1", "note": "32k GitHub stars as of March 2026"})

        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        notes = [n["note"] for n in entity[0]["entity_notes"]]
        assert "32k GitHub stars as of March 2026" in notes
        assert "15k stars" not in notes

    def test_advance_stage_to_researched(self, db):
        """Research agent marks entity as researched after completing."""
        self._seed_for_research(db)
        db["update"]("entities", "e1", {"stage": "researched"})
        entity = parse(db["read"]("entities", {"id": "e1"}))
        assert entity[0]["stage"] == "researched"

    def test_verify_stage_after_completion(self, db):
        """Orchestrator verifies agent actually set stage."""
        self._seed_for_research(db)
        entity = parse(db["read"]("entities", {"id": "e1"}))
        assert entity[0]["stage"] == "new"  # not advanced — needs re-spawn

    def test_adjacent_entity_discovery(self, db):
        """Research agent discovers and registers adjacent entities."""
        self._seed_for_research(db)
        result = parse(db["create"]("entities", {
            "name": "Adjacent Tool",
            "url": "https://adjacent.com",
            "source_url": "https://hp.com",
            "description": "Found while researching High Priority",
            "relevance": 6,
        }))
        assert "id: e4" in result

        prov = parse(db["query"]("SELECT * FROM url_provenance WHERE entity_id = 'e4'"))
        assert len(prov) == 1


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
            db["create"]("entities", {"name": name, "url": f"https://e{i}.com", "relevance": rel})
            db["update"]("entities", f"e{i}", {"stage": "researched"})
            db["create"]("entity_notes", [
                {"entity_id": f"e{i}", "note": f"{name} note 1"},
                {"entity_id": f"e{i}", "note": f"{name} note 2"},
            ])

    def test_get_researched_entities(self, db):
        """Analysis input: all researched entities."""
        self._seed_for_analysis(db)
        entities = parse(db["read"]("entities", {"stage": "researched"}))
        assert len(entities) == 4
        relevances = [e["relevance"] for e in entities]
        assert 9 in relevances
        assert 7 in relevances

    def test_analysis_agent_reads_notes(self, db):
        """Analysis agent reads entity with all notes."""
        self._seed_for_analysis(db)
        entity = parse(db["read"]("entities", {"id": "e1"}, include=["entity_notes"]))
        assert len(entity[0]["entity_notes"]) == 2

    def test_measure_extraction(self, db):
        """Extract measures per entity from analysis findings."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["create"]("entity_measures", [
                {"entity_id": f"e{i}", "measure": "implementation_model", "value": "markdown-only"},
                {"entity_id": f"e{i}", "measure": "activation_scope", "value": "pr"},
                {"entity_id": f"e{i}", "measure": "confidence_scoring", "value": "yes"},
            ])

        measures = parse(db["query"](
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

        dist = parse(db["query"](
            "SELECT value, COUNT(*) as count FROM entity_measures WHERE measure = 'scope' GROUP BY value ORDER BY count DESC"
        ))
        assert len(dist) == 2
        assert dist[0]["count"] == 2

    def test_incremental_measures_new_entities_only(self, db):
        """Adding entities after initial analysis: only new entities need measures."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["create"]("entity_measures", {"entity_id": f"e{i}", "measure": "score", "value": str(i * 10)})

        db["create"]("entities", {"name": "New Entity", "url": "https://new.com", "relevance": 6})
        db["update"]("entities", "e5", {"stage": "researched"})

        unmeasured = parse(db["query"](
            "SELECT e.id, e.name FROM entities e WHERE e.stage = 'researched' AND e.id NOT IN (SELECT DISTINCT entity_id FROM entity_measures)"
        ))
        assert len(unmeasured) == 1
        assert unmeasured[0]["id"] == "e5"

        db["create"]("entity_measures", {"entity_id": "e5", "measure": "score", "value": "60"})

        unmeasured = parse(db["query"](
            "SELECT e.id FROM entities e WHERE e.stage = 'researched' AND e.id NOT IN (SELECT DISTINCT entity_id FROM entity_measures)"
        ))
        assert len(unmeasured) == 0

    def test_criteria_change_clears_all_measures(self, db):
        """Effectiveness criteria change clears all measures for re-extraction."""
        self._seed_for_analysis(db)
        for i in range(1, 5):
            db["create"]("entity_measures", {"entity_id": f"e{i}", "measure": "score", "value": str(i * 10)})

        db["delete"]("entity_measures", all=True)

        total = parse(db["query"]("SELECT COUNT(*) as count FROM entity_measures"))
        assert total[0]["count"] == 0


# =============================================================================
# Phase 4: Blueprint
# =============================================================================


class TestPhase4Blueprint:
    """Phase 4 operations: full entity reads for implementation blueprint."""

    def _seed_full_dataset(self, db):
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
        entity = parse(db["read"](
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

        entities = parse(db["read"](
            "entities", {"stage": "researched"},
            include=["entity_notes"]
        ))
        assert len(entities) == 2
        assert all("entity_notes" in e for e in entities)
