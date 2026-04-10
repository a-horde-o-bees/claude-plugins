"""Server wiring tests for friction MCP server.

Verifies the server layer delegates correctly to skill functions and
wraps results with _ok/_err. Does not test business logic — that
belongs in skills/friction/tests/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(PLUGIN_ROOT) not in sys.path:
    sys.path.insert(0, str(PLUGIN_ROOT))

from servers import friction as friction_server


class TestFrictionAddDelegates:
    def test_success_wraps_ok(self) -> None:
        mock_result = {"id": 1, "system": "nav", "summary": "x", "has_detail": False, "created_at": "t", "updated_at": "t"}
        with patch.object(friction_server, "friction_skill") as mock_skill:
            mock_skill.friction_add.return_value = mock_result
            result = friction_server.friction_add("nav", "x")
        parsed = json.loads(result)
        assert parsed == mock_result
        mock_skill.friction_add.assert_called_once_with(
            friction_server.FRICTION_DB, "nav", "x", detail_md=None
        )

    def test_error_wraps_err(self) -> None:
        with patch.object(friction_server, "friction_skill") as mock_skill:
            mock_skill.friction_add.side_effect = ValueError("bad system")
            result = friction_server.friction_add("bad/name", "x")
        parsed = json.loads(result)
        assert "error" in parsed
        assert "bad system" in parsed["error"]


class TestFrictionListDelegates:
    def test_success_wraps_ok(self) -> None:
        mock_result = {"total": 1, "entries": [{"id": 1, "system": "nav", "summary": "x", "has_detail": False, "created_at": "t", "updated_at": "t"}]}
        with patch.object(friction_server, "friction_skill") as mock_skill:
            mock_skill.friction_list.return_value = mock_result
            result = friction_server.friction_list(system="nav")
        parsed = json.loads(result)
        assert parsed["total"] == 1
        mock_skill.friction_list.assert_called_once_with(
            friction_server.FRICTION_DB, system="nav", ids=None, limit=None
        )


class TestFrictionGetDelegates:
    def test_success_wraps_ok(self) -> None:
        mock_result = {"entries": [{"id": 1, "system": "nav", "summary": "x", "detail_md": None, "created_at": "t", "updated_at": "t"}]}
        with patch.object(friction_server, "friction_skill") as mock_skill:
            mock_skill.friction_get.return_value = mock_result
            result = friction_server.friction_get([1])
        parsed = json.loads(result)
        assert len(parsed["entries"]) == 1
        mock_skill.friction_get.assert_called_once_with(
            friction_server.FRICTION_DB, [1]
        )


class TestFrictionRemoveDelegates:
    def test_error_wraps_err(self) -> None:
        with patch.object(friction_server, "friction_skill") as mock_skill:
            mock_skill.friction_remove.side_effect = ValueError("not found")
            result = friction_server.friction_remove(999)
        parsed = json.loads(result)
        assert "error" in parsed
        assert "not found" in parsed["error"]
