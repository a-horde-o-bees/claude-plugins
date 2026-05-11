"""Shared MCP server helpers.

Pure utility functions used by every server module in this package:
JSON serialization for success and error responses.

Also bootstraps CLAUDE_PROJECT_DIR at import time. Claude Code launches
MCP servers with cwd set to the project root but does not propagate
CLAUDE_PROJECT_DIR to the subprocess environment, and variable
references inside `.mcp.json` env block values are NOT expanded (the
literal string ${CLAUDE_PROJECT_DIR} passes through unchanged, which
causes silent writes to a garbage path named ${CLAUDE_PROJECT_DIR}
under cwd). Setting the variable from cwd at import time is a
scope-limited bridge: it respects the "MCP cwd is project root"
invariant that Claude Code guarantees for plugin-launched servers
without reintroducing a general-purpose cwd fallback in plugin
framework helpers used outside MCP context.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

if "CLAUDE_PROJECT_DIR" not in os.environ:
    os.environ["CLAUDE_PROJECT_DIR"] = str(Path.cwd().resolve())


def _ok(result: Any) -> str:
    """Serialize a successful result as a JSON string."""
    return json.dumps(result, default=str)


def _err(e: Exception) -> str:
    """Wrap an exception as a JSON error response."""
    return json.dumps({"error": str(e)})
