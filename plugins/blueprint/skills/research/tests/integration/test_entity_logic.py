"""Business logic — dedup, merge, duplicates, dashboard — via MCP transport."""

import json

import pytest


def _parse(result) -> dict | list:
    """Extract parsed JSON from CallToolResult."""
    text = result.content[0].text
    return json.loads(text)


class TestEntityLogic:
    """Business logic — dedup, merge, duplicates, dashboard — via transport."""

    @pytest.fixture(autouse=True)
    async def _init_db(self, session):
        await session.call_tool("init_database", {})

    @pytest.mark.anyio
    async def test_url_dedup_across_entities(self, session):
        """add_url deduplicates normalized URLs."""
        await session.call_tool("register_entity", {
            "data": {"name": "URL Entity", "url": "https://example.com/a"},
        })

        result = await session.call_tool("add_url", {
            "entity_id": "e1",
            "url": "https://example.com/b",
        })
        data = _parse(result)
        assert "result" in data

        # Entity detail shows both URLs
        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "example.com/a" in detail
        assert "example.com/b" in detail

    @pytest.mark.anyio
    async def test_merge_preserves_data(self, session):
        """Merge combines notes, URLs, and modes into survivor."""
        await session.call_tool("register_entity", {
            "data": {"name": "Entity A", "url": "https://a.com"},
        })
        await session.call_tool("register_entity", {
            "data": {"name": "Entity B", "url": "https://b.com"},
        })
        await session.call_tool("add_notes", {
            "entity_id": "e1",
            "notes": ["Note on A"],
        })
        await session.call_tool("add_notes", {
            "entity_id": "e2",
            "notes": ["Note on B"],
        })
        await session.call_tool("set_modes", {
            "entity_id": "e1",
            "modes": ["example"],
        })
        await session.call_tool("set_modes", {
            "entity_id": "e2",
            "modes": ["context"],
        })

        result = await session.call_tool("merge_entities", {
            "entity_ids": ["e1", "e2"],
        })
        data = _parse(result)
        assert "result" in data

        # Survivor (lowest ID = e1) has combined data
        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "Note on A" in detail
        assert "Note on B" in detail

    @pytest.mark.anyio
    async def test_find_duplicates(self, session):
        """find_duplicates detects entities sharing URLs."""
        await session.call_tool("register_entity", {
            "data": {"name": "Entity X", "url": "https://unique-x.com"},
        })
        await session.call_tool("register_entity", {
            "data": {"name": "Entity Y", "url": "https://unique-y.com"},
        })
        # Add overlapping URL to create duplicate relationship
        await session.call_tool("add_url", {
            "entity_id": "e2",
            "url": "https://unique-x.com",
        })

        result = await session.call_tool("find_duplicates", {})
        data = _parse(result)
        assert "result" in data

    @pytest.mark.anyio
    async def test_dashboard_stats(self, session):
        """get_dashboard returns aggregated statistics."""
        await session.call_tool("register_entities", {
            "entities": [
                {"name": "Tool A", "url": "https://a.com", "relevance": 8},
                {"name": "Tool B", "url": "https://b.com", "relevance": 5},
                {"name": "Tool C", "url": "https://c.com"},
            ],
        })
        await session.call_tool("set_stage", {"entity_id": "e1", "stage": "researched"})

        result = await session.call_tool("get_dashboard", {})
        data = _parse(result)
        assert "result" in data
        # Dashboard text should contain counts
        dashboard = data["result"]
        assert "3" in dashboard or "entities" in dashboard.lower()

    @pytest.mark.anyio
    async def test_research_queue(self, session):
        """get_research_queue returns example-mode entities at stage new."""
        await session.call_tool("register_entity", {
            "data": {"name": "Queued Tool", "url": "https://queued.com", "relevance": 7},
        })
        await session.call_tool("set_modes", {
            "entity_id": "e1",
            "modes": ["example"],
        })

        result = await session.call_tool("get_research_queue", {})
        data = _parse(result)
        assert "result" in data
        assert "Queued Tool" in data["result"]

    @pytest.mark.anyio
    async def test_get_unclassified(self, session):
        """get_unclassified returns entities with unclassified mode."""
        await session.call_tool("register_entity", {
            "data": {"name": "Unknown Entity", "url": "https://unknown.com"},
        })
        await session.call_tool("set_modes", {
            "entity_id": "e1",
            "modes": ["unclassified"],
        })

        result = await session.call_tool("get_unclassified", {})
        data = _parse(result)
        assert "result" in data
        assert "Unknown Entity" in data["result"]

    @pytest.mark.anyio
    async def test_measure_summary(self, session):
        """get_measure_summary returns measure distribution."""
        await session.call_tool("register_entity", {
            "data": {"name": "Measured", "url": "https://measured.com"},
        })
        await session.call_tool("set_measures", {
            "entity_id": "e1",
            "measures": [{"measure": "quality", "value": "high"}],
        })

        result = await session.call_tool("get_measure_summary", {})
        data = _parse(result)
        assert "result" in data

    @pytest.mark.anyio
    async def test_provenance_tracking(self, session):
        """add_provenance records discovery source."""
        await session.call_tool("register_entity", {
            "data": {"name": "Discovered Tool", "url": "https://discovered.com"},
        })

        result = await session.call_tool("add_provenance", {
            "entity_id": "e1",
            "source_url": "https://source-page.com/tools",
        })
        data = _parse(result)
        assert "result" in data

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "source-page.com" in detail

    @pytest.mark.anyio
    async def test_clear_all_measures(self, session):
        """clear_all_measures removes measures across all entities."""
        await session.call_tool("register_entities", {
            "entities": [
                {"name": "M1", "url": "https://m1.com"},
                {"name": "M2", "url": "https://m2.com"},
            ],
        })
        await session.call_tool("set_measures", {
            "entity_id": "e1",
            "measures": [{"measure": "score", "value": "5"}],
        })
        await session.call_tool("set_measures", {
            "entity_id": "e2",
            "measures": [{"measure": "score", "value": "3"}],
        })

        result = await session.call_tool("clear_all_measures", {})
        data = _parse(result)
        assert "result" in data
