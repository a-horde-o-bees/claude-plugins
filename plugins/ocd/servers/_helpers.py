"""Shared MCP server helpers.

Pure utility functions used by every server module in this package:
JSON serialization for success and error responses.
"""

from __future__ import annotations

import json


def _ok(result) -> str:
    """Serialize a successful result as a JSON string."""
    return json.dumps(result, default=str)


def _err(e: Exception) -> str:
    """Wrap an exception as a JSON error response."""
    return json.dumps({"error": str(e)})
