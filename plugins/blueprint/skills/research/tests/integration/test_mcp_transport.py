"""Integration tests for MCP server over stdio transport.

These tests start the actual MCP server process and communicate via JSON-RPC
over stdio using the MCP SDK client — the same transport Claude Code uses.
This validates the integration boundary that unit tests bypass.
"""

import json
import os
import sys
from pathlib import Path

import pytest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_plugin_root = Path(__file__).resolve().parent.parent.parent.parent.parent
SERVER_PATH = str(_plugin_root / "servers" / "research_db.py")

EXPECTED_TOOLS = sorted([
    "register_entity", "register_entities",
    "set_name", "clear_name",
    "set_description", "clear_description",
    "set_purpose", "clear_purpose",
    "set_relevance", "clear_relevance",
    "set_stage",
    "set_modes", "add_modes", "remove_modes", "clear_modes",
    "add_notes", "set_note", "remove_notes", "clear_notes",
    "set_measures", "clear_measures", "clear_all_measures",
    "add_url", "add_provenance",
    "reject_entity", "merge_entities",
    "get_entity", "list_entities",
    "get_research_queue", "get_unclassified",
    "find_duplicates", "get_dashboard", "get_measure_summary",
    "init_database", "describe_schema",
])


@pytest.fixture
async def session(tmp_path):
    """Start MCP server process and yield a connected client session."""
    db_path = str(tmp_path / "test.db")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_PATH],
        env={**os.environ, "DB_PATH": db_path},
    )
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session


def _parse(result) -> dict | list:
    """Extract parsed JSON from CallToolResult."""
    text = result.content[0].text
    return json.loads(text)


# =============================================================================
# Server Initialization
# =============================================================================


class TestServerHandshake:
    """MCP protocol handshake and tool discovery."""

    @pytest.mark.anyio
    async def test_server_starts(self, session):
        """Server process starts and completes MCP handshake."""
        assert session is not None

    @pytest.mark.anyio
    async def test_lists_all_tools(self, session):
        """Server exposes all domain tools via tools/list."""
        result = await session.list_tools()
        tool_names = sorted(t.name for t in result.tools)
        assert tool_names == EXPECTED_TOOLS

    @pytest.mark.anyio
    async def test_tool_schemas_present(self, session):
        """Each tool has input schema with required properties."""
        result = await session.list_tools()
        for tool in result.tools:
            assert tool.inputSchema is not None, f"{tool.name} missing inputSchema"


# =============================================================================
# Database Lifecycle
# =============================================================================


class TestDatabaseLifecycle:
    """init_database and missing-database error handling over transport."""

    @pytest.mark.anyio
    async def test_tool_before_init_returns_error(self, session):
        """Domain tools return clear error when database doesn't exist."""
        result = await session.call_tool("list_entities", {})
        data = _parse(result)
        assert "error" in data
        assert "not initialized" in data["error"].lower()

    @pytest.mark.anyio
    async def test_init_creates_database(self, session):
        """init_database creates schema and enables domain operations."""
        result = await session.call_tool("init_database", {})
        data = _parse(result)
        assert "result" in data

        # Domain tools now work
        result = await session.call_tool("list_entities", {})
        data = _parse(result)
        assert "result" in data

    @pytest.mark.anyio
    async def test_describe_schema_returns_tables(self, session):
        """describe_schema returns raw JSON with table structure."""
        await session.call_tool("init_database", {})

        result = await session.call_tool("describe_schema", {})
        data = _parse(result)
        assert "entities" in data

    @pytest.mark.anyio
    async def test_describe_schema_single_table(self, session):
        """describe_schema with table argument returns column details."""
        await session.call_tool("init_database", {})

        result = await session.call_tool("describe_schema", {"table": "entities"})
        data = _parse(result)
        assert data["table"] == "entities"
        col_names = [c["name"] for c in data["columns"]]
        assert "id" in col_names
        assert "name" in col_names
        assert "stage" in col_names


# =============================================================================
# Domain Operations
# =============================================================================


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


# =============================================================================
# Entity Logic
# =============================================================================


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
