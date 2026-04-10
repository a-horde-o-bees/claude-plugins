"""Server wiring tests for stash MCP server.

Verifies that the thin server layer correctly resolves scope to db_path,
delegates to skill functions, wraps results with _ok/_err, and handles
cross-DB promotion logic. Skill functions are mocked — business logic
is tested in skills/stash/tests/.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import servers.stash as server


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_project_db(tmp_path, monkeypatch):
    """Point the project DB to a tmp path."""
    db = str(tmp_path / "project.db")
    monkeypatch.setattr(server, "_project_db", lambda: db)
    return db


@pytest.fixture
def mock_user_db(tmp_path, monkeypatch):
    """Point the user DB to a tmp path."""
    db = str(tmp_path / "user.db")
    monkeypatch.setattr(server, "_user_db", lambda: db)
    return db


# ---------------------------------------------------------------------------
# Normal delegation
# ---------------------------------------------------------------------------


class TestDelegation:
    def test_add_delegates_to_skill(self, mock_project_db):
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_add.return_value = {"id": 1, "summary": "test"}
            result = server.stash_add(summary="test", scope="project")
            mock_skill.stash_add.assert_called_once_with(
                mock_project_db, summary="test", detail_md=None,
            )
            assert '"id": 1' in result

    def test_list_delegates_to_skill(self, mock_project_db):
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_list.return_value = {"total": 0, "entries": []}
            result = server.stash_list(scope="project")
            mock_skill.stash_list.assert_called_once_with(
                mock_project_db, ids=None, limit=None,
            )
            assert '"total": 0' in result

    def test_get_delegates_to_skill(self, mock_project_db):
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_get.return_value = {"entries": []}
            result = server.stash_get(ids=[1], scope="project")
            mock_skill.stash_get.assert_called_once_with(
                mock_project_db, ids=[1],
            )
            assert '"entries": []' in result

    def test_remove_delegates_to_skill(self, mock_project_db):
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_remove.return_value = {"removed": {"id": 1}, "remaining": 0}
            result = server.stash_remove(id=1, scope="project")
            mock_skill.stash_remove.assert_called_once_with(
                mock_project_db, id=1,
            )
            assert '"remaining": 0' in result

    def test_user_scope_resolves_user_db(self, mock_user_db):
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_list.return_value = {"total": 0, "entries": []}
            server.stash_list(scope="user")
            mock_skill.stash_list.assert_called_once_with(
                mock_user_db, ids=None, limit=None,
            )


# ---------------------------------------------------------------------------
# Error wrapping
# ---------------------------------------------------------------------------


class TestErrorWrapping:
    def test_skill_exception_wrapped_as_err(self, mock_project_db):
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_add.side_effect = RuntimeError("db locked")
            result = server.stash_add(summary="test", scope="project")
            assert '"error"' in result
            assert "db locked" in result


# ---------------------------------------------------------------------------
# Cross-DB promotion
# ---------------------------------------------------------------------------


class TestCrossDbPromotion:
    def test_update_promotes_from_user_to_project(
        self, mock_project_db, mock_user_db
    ):
        """When entry is not in project DB but exists in user DB, promote it."""
        with patch("servers.stash.stash_skill") as mock_skill:
            # First call: stash_update on project DB raises (not found)
            mock_skill.stash_update.side_effect = ValueError("not found")

            # Second call: stash_get on user DB finds the entry
            mock_skill.stash_get.return_value = {
                "entries": [{
                    "id": 5,
                    "summary": "cross-project idea",
                    "detail_md": "context here",
                    "created_at": "2026-01-01T00:00:00+00:00",
                    "updated_at": "2026-01-01T00:00:00+00:00",
                }]
            }

            # stash_add to project DB succeeds
            new_entry = {
                "id": 1,
                "summary": "cross-project idea",
                "has_detail": True,
                "created_at": "2026-04-09T00:00:00+00:00",
                "updated_at": "2026-04-09T00:00:00+00:00",
            }
            mock_skill.stash_add.return_value = new_entry

            # stash_remove from user DB succeeds
            mock_skill.stash_remove.return_value = {"removed": {}, "remaining": 0}

            result = server.stash_update(id=5, scope="project")

            # Verify add was called on project DB
            mock_skill.stash_add.assert_called_once_with(
                mock_project_db,
                summary="cross-project idea",
                detail_md="context here",
            )
            # Verify remove was called on user DB
            mock_skill.stash_remove.assert_called_once_with(
                mock_user_db, id=5,
            )
            assert "promoted" in result

    def test_update_not_found_in_either_scope(
        self, mock_project_db, mock_user_db
    ):
        """When entry is not found in either scope, return error."""
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_update.side_effect = ValueError("not found")
            mock_skill.stash_get.return_value = {"entries": []}

            result = server.stash_update(id=999, scope="project")
            assert '"error"' in result
            assert "either scope" in result

    def test_normal_update_does_not_check_other_scope(
        self, mock_project_db, mock_user_db
    ):
        """When entry is found in the target scope, no cross-DB logic runs."""
        with patch("servers.stash.stash_skill") as mock_skill:
            mock_skill.stash_update.return_value = {
                "id": 1, "summary": "updated", "has_detail": False,
                "created_at": "t1", "updated_at": "t2",
            }
            result = server.stash_update(id=1, summary="updated", scope="project")
            # stash_get should NOT have been called
            mock_skill.stash_get.assert_not_called()
            assert '"updated"' in result
