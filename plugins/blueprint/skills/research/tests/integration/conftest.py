"""Shared fixtures for MCP transport integration tests."""

import os
import sys
from pathlib import Path

import pytest

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_plugin_root = Path(__file__).resolve().parent.parent.parent.parent.parent
LAUNCHER_PATH = str(_plugin_root / "run.py")


@pytest.fixture
async def session(tmp_path):
    """Start MCP server process and yield a connected client session."""
    db_path = str(tmp_path / "test.db")
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[LAUNCHER_PATH, "servers.research_db"],
        env={**os.environ, "DB_PATH": db_path},
    )
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            yield session
