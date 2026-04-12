"""MCP protocol handshake and tool discovery over stdio transport."""

import pytest


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
    "set_criteria", "add_criterion", "remove_criterion", "get_criteria",
    "link_criterion_note", "unlink_criterion_note", "clear_criterion_links",
    "get_assessment", "compute_relevance",
    "get_entity", "list_entities",
    "get_research_queue", "get_unclassified",
    "find_duplicates", "get_dashboard", "get_measure_summary",
    "set_domains", "add_domain", "remove_domain", "get_domains",
    "link_domain_criterion", "unlink_domain_criterion",
    "set_goals", "add_goal", "remove_goal", "get_goals",
    "link_goal_domain", "unlink_goal_domain",
    "get_coverage", "get_criteria_effectiveness",
    "init_database", "describe_schema",
])


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
