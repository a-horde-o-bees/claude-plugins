"""Shared MCP server helpers.

Pure utility functions used by every server module in this package:
JSON serialization for success and error responses, and project-root
resolution from the standard environment variable.
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def _ok(result) -> str:
    """Serialize a successful result as a JSON string."""
    return json.dumps(result, default=str)


def _err(e: Exception) -> str:
    """Wrap an exception as a JSON error response."""
    return json.dumps({"error": str(e)})


def _project_root() -> Path:
    """Resolve the project root. CLAUDE_PROJECT_DIR wins; else cwd."""
    env_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if env_dir:
        return Path(env_dir).resolve()
    return Path.cwd().resolve()
