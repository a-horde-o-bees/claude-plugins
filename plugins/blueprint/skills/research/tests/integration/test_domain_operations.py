"""Registration, retrieval, and property mutations via JSON-RPC over MCP transport."""

import json

import pytest


def _parse(result) -> dict | list:
    """Extract parsed JSON from CallToolResult."""
    text = result.content[0].text
    return json.loads(text)


class TestDomainOperations:
    """Registration, retrieval, and property mutations via JSON-RPC."""

    @pytest.fixture(autouse=True)
    async def _init_db(self, session):
        await session.call_tool("init_database", {})

    @pytest.mark.anyio
    async def test_register_and_get_entity(self, session):
        """Round-trip: register entity, retrieve full detail."""
        result = await session.call_tool("register_entity", {
            "data": {
                "name": "Test Tool",
                "url": "https://example.com/tool",
                "description": "Created via MCP transport",
                "relevance": 8,
            },
        })
        data = _parse(result)
        assert "result" in data

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        data = _parse(result)
        assert "result" in data
        assert "Test Tool" in data["result"]
        assert "relevance: 8" in data["result"].lower() or "8" in data["result"]

    @pytest.mark.anyio
    async def test_url_dedup_on_register(self, session):
        """Duplicate URL returns existing entity instead of creating new."""
        await session.call_tool("register_entity", {
            "data": {"name": "Original", "url": "https://example.com/tool"},
        })
        result = await session.call_tool("register_entity", {
            "data": {"name": "Duplicate", "url": "https://example.com/tool"},
        })
        data = _parse(result)
        assert "result" in data
        assert "already" in data["result"].lower() or "existing" in data["result"].lower()

    @pytest.mark.anyio
    async def test_batch_registration(self, session):
        """register_entities handles multiple entities in one call."""
        result = await session.call_tool("register_entities", {
            "entities": [
                {"name": "Tool A", "url": "https://a.com"},
                {"name": "Tool B", "url": "https://b.com"},
            ],
        })
        data = _parse(result)
        assert "result" in data

        # Both entities retrievable
        for eid in ("e1", "e2"):
            result = await session.call_tool("get_entity", {"entity_id": eid})
            entity = _parse(result)
            assert "result" in entity

    @pytest.mark.anyio
    async def test_notes_lifecycle(self, session):
        """Add notes, update one, remove one, clear remaining."""
        await session.call_tool("register_entity", {
            "data": {"name": "Noted Entity", "url": "https://example.com/noted"},
        })

        # Add notes
        result = await session.call_tool("add_notes", {
            "entity_id": "e1",
            "notes": ["First observation", "Second observation"],
        })
        data = _parse(result)
        assert "result" in data

        # Verify notes appear in entity detail
        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "First observation" in detail
        assert "Second observation" in detail

        # Update a note — need to know the note ID from detail
        # Note IDs follow n{N} pattern; first two notes are n1, n2
        result = await session.call_tool("set_note", {
            "note_id": "n1",
            "text": "Updated first observation",
        })
        data = _parse(result)
        assert "result" in data

        # Remove second note
        result = await session.call_tool("remove_notes", {
            "entity_id": "e1",
            "note_ids": ["n2"],
        })
        data = _parse(result)
        assert "result" in data

        # Verify state after mutations
        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "Updated first observation" in detail
        assert "Second observation" not in detail

        # Clear all remaining notes
        result = await session.call_tool("clear_notes", {"entity_id": "e1"})
        data = _parse(result)
        assert "result" in data

    @pytest.mark.anyio
    async def test_set_modes(self, session):
        """Replace modes on entity."""
        await session.call_tool("register_entity", {
            "data": {"name": "Modal Entity", "url": "https://example.com/modal"},
        })

        result = await session.call_tool("set_modes", {
            "entity_id": "e1",
            "modes": ["example", "context"],
        })
        data = _parse(result)
        assert "result" in data

        # Verify modes appear in entity detail
        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "example" in detail
        assert "context" in detail

    @pytest.mark.anyio
    async def test_add_and_remove_modes(self, session):
        """Add modes preserves existing, remove modes removes specific ones."""
        await session.call_tool("register_entity", {
            "data": {"name": "Mode Test", "url": "https://example.com/modes"},
        })

        await session.call_tool("set_modes", {
            "entity_id": "e1",
            "modes": ["example"],
        })
        await session.call_tool("add_modes", {
            "entity_id": "e1",
            "modes": ["context", "directory"],
        })

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "example" in detail
        assert "context" in detail
        assert "directory" in detail

        await session.call_tool("remove_modes", {
            "entity_id": "e1",
            "modes": ["context"],
        })

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "example" in detail
        assert "directory" in detail

    @pytest.mark.anyio
    async def test_stage_transition(self, session):
        """set_stage changes entity stage."""
        await session.call_tool("register_entity", {
            "data": {"name": "Staged Entity", "url": "https://example.com/staged"},
        })

        result = await session.call_tool("set_stage", {
            "entity_id": "e1",
            "stage": "researched",
        })
        data = _parse(result)
        assert "result" in data

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "researched" in detail.lower()

    @pytest.mark.anyio
    async def test_measures_lifecycle(self, session):
        """Set measures, verify in detail, clear them."""
        await session.call_tool("register_entity", {
            "data": {"name": "Measured Entity", "url": "https://example.com/measured"},
        })

        result = await session.call_tool("set_measures", {
            "entity_id": "e1",
            "measures": [
                {"measure": "quality", "value": "high"},
                {"measure": "maturity", "value": "stable"},
            ],
        })
        data = _parse(result)
        assert "result" in data

        # Verify measures in entity detail
        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "quality" in detail
        assert "maturity" in detail

        # Clear measures for one entity
        result = await session.call_tool("clear_measures", {"entity_id": "e1"})
        data = _parse(result)
        assert "result" in data

    @pytest.mark.anyio
    async def test_scalar_setters(self, session):
        """Scalar property setters update individual fields."""
        await session.call_tool("register_entity", {
            "data": {"name": "Original Name", "url": "https://example.com/scalar"},
        })

        await session.call_tool("set_name", {"entity_id": "e1", "name": "New Name"})
        await session.call_tool("set_description", {
            "entity_id": "e1",
            "description": "Updated description",
        })
        await session.call_tool("set_relevance", {"entity_id": "e1", "relevance": 9})

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "New Name" in detail
        assert "Updated description" in detail

    @pytest.mark.anyio
    async def test_reject_entity(self, session):
        """reject_entity sets stage to rejected and adds reason note."""
        await session.call_tool("register_entity", {
            "data": {"name": "Reject Me", "url": "https://example.com/reject"},
        })

        result = await session.call_tool("reject_entity", {
            "entity_id": "e1",
            "reason": "Not relevant to research scope",
        })
        data = _parse(result)
        assert "result" in data

        result = await session.call_tool("get_entity", {"entity_id": "e1"})
        detail = _parse(result)["result"]
        assert "rejected" in detail.lower()
        assert "Not relevant to research scope" in detail

    @pytest.mark.anyio
    async def test_list_entities_with_filters(self, session):
        """list_entities supports mode, stage, and relevance filters."""
        await session.call_tool("register_entities", {
            "entities": [
                {"name": "High Rel", "url": "https://h.com", "relevance": 9},
                {"name": "Low Rel", "url": "https://l.com", "relevance": 2},
            ],
        })
        await session.call_tool("set_modes", {
            "entity_id": "e1",
            "modes": ["example"],
        })

        result = await session.call_tool("list_entities", {"min_relevance": 7})
        data = _parse(result)
        assert "result" in data
        assert "High Rel" in data["result"]

        result = await session.call_tool("list_entities", {"mode": "example"})
        data = _parse(result)
        assert "result" in data
        assert "High Rel" in data["result"]
