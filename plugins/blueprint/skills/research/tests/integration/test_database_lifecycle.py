"""init_database and missing-database error handling over MCP transport."""

import json

import pytest


def _parse(result) -> dict | list:
    """Extract parsed JSON from CallToolResult."""
    text = result.content[0].text
    return json.loads(text)


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
