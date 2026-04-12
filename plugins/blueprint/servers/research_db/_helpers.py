"""Shared helpers for MCP server tool implementations.

Database check, JSON response wrappers, and configuration constants
used across all tool registration modules.
"""

from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "blueprint/data/research.db")

_NO_DB_MSG = json.dumps({
    "error": "Database not initialized.",
    "action": "Run /blueprint-init or /blueprint-research to create the database first.",
})


def _check_db() -> str | None:
    """Return error JSON if database doesn't exist, None if OK."""
    if not Path(DB_PATH).exists():
        return _NO_DB_MSG
    return None


def _ok(result) -> str:
    """Wrap result as JSON response."""
    if isinstance(result, str):
        return json.dumps({"result": result})
    return json.dumps(result, default=str)


def _handle_check_error(e: sqlite3.IntegrityError) -> str | None:
    """Extract CHECK constraint expression from IntegrityError.

    Returns user-friendly error message if CHECK constraint violation,
    None otherwise. Fully dynamic — works for any CHECK constraint on
    any table without per-field hardcoding.
    """
    msg = str(e)
    if "CHECK constraint failed:" in msg:
        expression = msg.split("CHECK constraint failed:", 1)[1].strip()
        return json.dumps({
            "error": f"Value rejected by database constraint: {expression}",
            "hint": "Check the allowed values and try again.",
        })
    return None


def _err(e: Exception) -> str:
    """Wrap exception as JSON error."""
    return json.dumps({"error": str(e)})
