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
        # session fixture already called initialize() — reaching here means success
        assert session is not None

    @pytest.mark.anyio
    async def test_lists_all_tools(self, session):
        """Server exposes all 8 tools via tools/list."""
        result = await session.list_tools()
        tool_names = sorted(t.name for t in result.tools)
        expected = sorted([
            "create_records", "read_records", "update_records", "delete_records",
            "query", "describe_entities", "merge_entities", "init_database",
        ])
        assert tool_names == expected

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
    async def test_read_before_init_returns_error(self, session):
        """Tools return clear error when database doesn't exist."""
        result = await session.call_tool("read_records", {"table": "entities"})
        data = _parse(result)
        assert "error" in data
        assert "not initialized" in data["error"].lower()

    @pytest.mark.anyio
    async def test_init_creates_database(self, session):
        """init_database creates schema and enables CRUD."""
        result = await session.call_tool("init_database", {})
        data = _parse(result)
        assert "initialized" in data.get("status", "")

        # CRUD now works
        result = await session.call_tool("describe_entities", {})
        data = _parse(result)
        assert "entities" in data


# =============================================================================
# CRUD Over Transport
# =============================================================================


class TestCrudOverTransport:
    """Create, read, update, delete operations via JSON-RPC."""

    @pytest.fixture(autouse=True)
    async def _init_db(self, session):
        await session.call_tool("init_database", {})

    @pytest.mark.anyio
    async def test_create_and_read_entity(self, session):
        """Round-trip: create entity, read it back."""
        result = await session.call_tool("create_records", {
            "table": "entities",
            "data": {
                "name": "Test Tool",
                "url": "https://example.com/tool",
                "description": "Created via MCP transport",
                "relevance": 8,
            },
        })
        data = _parse(result)
        assert "id: e1" in data

        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"name": "Test Tool"},
        })
        records = _parse(result)
        assert len(records) == 1
        assert records[0]["name"] == "Test Tool"
        assert records[0]["relevance"] == 8

    @pytest.mark.anyio
    async def test_update_entity(self, session):
        """Update entity fields and verify."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Original", "url": "https://example.com/orig"},
        })

        await session.call_tool("update_records", {
            "table": "entities",
            "id": "e1",
            "data": {"description": "Updated description"},
        })

        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
        })
        records = _parse(result)
        assert records[0]["description"] == "Updated description"

    @pytest.mark.anyio
    async def test_delete_child_record(self, session):
        """Delete a child record (note) and verify removal."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Parent", "url": "https://example.com/parent"},
        })
        await session.call_tool("create_records", {
            "table": "entity_notes",
            "data": {"entity_id": "e1", "note": "To be deleted"},
        })

        # Get the note ID
        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
            "include": ["entity_notes"],
        })
        records = _parse(result)
        note_id = records[0]["entity_notes"][0]["id"]

        result = await session.call_tool("delete_records", {
            "table": "entity_notes",
            "id": str(note_id),
        })
        delete_response = _parse(result)
        assert delete_response.get("status") == "deleted"

        # Verify note removed
        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
            "include": ["entity_notes"],
        })
        records = _parse(result)
        assert len(records[0]["entity_notes"]) == 0

    @pytest.mark.anyio
    async def test_delete_entity_cascades_children(self, session):
        """Deleting entity cascades to all child records via FK introspection."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Has Children", "url": "https://example.com/fk"},
        })
        await session.call_tool("create_records", {
            "table": "entity_notes",
            "data": {"entity_id": "e1", "note": "Orphan candidate"},
        })
        await session.call_tool("create_records", {
            "table": "entity_measures",
            "data": {"entity_id": "e1", "measure": "score", "value": "5"},
        })

        result = await session.call_tool("delete_records", {
            "table": "entities",
            "id": "e1",
        })
        data = _parse(result)
        assert data.get("status") == "deleted"

        # Entity gone
        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
        })
        assert len(_parse(result)) == 0

        # All children gone — no orphans
        for child_table in ["entity_notes", "entity_urls", "entity_measures"]:
            result = await session.call_tool("query", {
                "sql": f"SELECT COUNT(*) as cnt FROM {child_table} WHERE entity_id = 'e1'",
            })
            assert _parse(result)[0]["cnt"] == 0, f"Orphans in {child_table}"

    @pytest.mark.anyio
    async def test_describe_entities(self, session):
        """Schema introspection returns table structure."""
        result = await session.call_tool("describe_entities", {"table": "entities"})
        data = _parse(result)
        assert data["table"] == "entities"
        col_names = [c["name"] for c in data["columns"]]
        assert "id" in col_names
        assert "name" in col_names

    @pytest.mark.anyio
    async def test_read_only_query(self, session):
        """query tool executes SELECT and returns results."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Queryable", "url": "https://example.com/q"},
        })

        result = await session.call_tool("query", {
            "sql": "SELECT COUNT(*) as cnt FROM entities",
        })
        data = _parse(result)
        assert data[0]["cnt"] == 1

    @pytest.mark.anyio
    async def test_query_rejects_write(self, session):
        """query tool blocks INSERT/UPDATE/DELETE."""
        result = await session.call_tool("query", {
            "sql": "INSERT INTO entities (name) VALUES ('bad')",
        })
        data = _parse(result)
        assert "error" in data


# =============================================================================
# Entity Business Logic Over Transport
# =============================================================================


class TestEntityLogicOverTransport:
    """Entity-specific behavior (dedup, provenance, merge) via transport."""

    @pytest.fixture(autouse=True)
    async def _init_db(self, session):
        await session.call_tool("init_database", {})

    @pytest.mark.anyio
    async def test_url_dedup(self, session):
        """Duplicate URL returns existing entity instead of creating new."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Original", "url": "https://example.com/tool"},
        })
        result = await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Duplicate", "url": "https://example.com/tool"},
        })
        data = _parse(result)
        assert "Already registered" in data

    @pytest.mark.anyio
    async def test_batch_create(self, session):
        """Batch entity creation via array data."""
        result = await session.call_tool("create_records", {
            "table": "entities",
            "data": [
                {"name": "Tool A", "url": "https://a.com"},
                {"name": "Tool B", "url": "https://b.com"},
            ],
        })
        data = _parse(result)
        assert len(data) == 2

    @pytest.mark.anyio
    async def test_nested_notes_on_create(self, session):
        """Entity creation with nested notes in single call."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {
                "name": "With Notes",
                "url": "https://example.com/notes",
                "entity_notes": [
                    {"note": "First observation"},
                    {"note": "Second observation"},
                ],
            },
        })

        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
            "include": ["entity_notes"],
        })
        records = _parse(result)
        assert len(records[0]["entity_notes"]) == 2

    @pytest.mark.anyio
    async def test_star_schema_include(self, session):
        """read_records with include joins related tables."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Parent", "url": "https://example.com/parent"},
        })
        await session.call_tool("create_records", {
            "table": "entity_notes",
            "data": [
                {"entity_id": "e1", "note": "Note 1"},
                {"entity_id": "e1", "note": "Note 2"},
            ],
        })

        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
            "include": ["entity_notes", "entity_measures", "entity_urls"],
        })
        records = _parse(result)
        assert len(records[0]["entity_notes"]) == 2
        assert records[0]["entity_measures"] == []
        # entity_urls populated by entity registration (normalized URL stored there)
        assert len(records[0]["entity_urls"]) >= 1

    @pytest.mark.anyio
    async def test_merge_entities(self, session):
        """Merge duplicates into survivor via transport."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Entity A", "url": "https://a.com"},
        })
        await session.call_tool("create_records", {
            "table": "entities",
            "data": {"name": "Entity B", "url": "https://b.com"},
        })
        await session.call_tool("create_records", {
            "table": "entity_notes",
            "data": {"entity_id": "e1", "note": "Note on A"},
        })
        await session.call_tool("create_records", {
            "table": "entity_notes",
            "data": {"entity_id": "e2", "note": "Note on B"},
        })

        await session.call_tool("merge_entities", {"ids": ["e1", "e2"]})

        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"id": "e1"},
            "include": ["entity_notes"],
        })
        survivor = _parse(result)
        assert len(survivor[0]["entity_notes"]) == 2

    @pytest.mark.anyio
    async def test_condition_operators(self, session):
        """Django __operator conditions work over transport."""
        await session.call_tool("create_records", {
            "table": "entities",
            "data": [
                {"name": "High", "url": "https://h.com", "relevance": 9},
                {"name": "Low", "url": "https://l.com", "relevance": 3},
            ],
        })

        result = await session.call_tool("read_records", {
            "table": "entities",
            "conditions": {"relevance__gte": 7},
        })
        records = _parse(result)
        assert len(records) == 1
        assert records[0]["name"] == "High"
