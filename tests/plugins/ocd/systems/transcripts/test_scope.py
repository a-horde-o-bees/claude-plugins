"""Tests for _scope: projects / sessions / exchanges queries."""

import pytest

from systems.transcripts import _ingest, _scope

from .conftest import make_assistant_text, make_user_msg


@pytest.fixture
def populated_conn(conn, seeded_project):
    """Populated DB with two projects, multiple sessions, multiple exchanges."""
    seeded_project("-proj-alpha", {
        "alpha-s1": [
            make_user_msg("2026-04-20T10:00:00Z", "alpha hello", uuid="a-u1"),
            make_assistant_text("2026-04-20T10:00:05Z", "hi", uuid="a-a1"),
            make_user_msg("2026-04-20T10:01:00Z", "alpha follow-up", uuid="a-u2"),
            make_assistant_text("2026-04-20T10:01:10Z", "yes", uuid="a-a2"),
        ],
    })
    seeded_project("-proj-beta", {
        "beta-s1": [
            make_user_msg("2026-04-21T15:00:00Z", "beta hello", uuid="b-u1"),
            make_assistant_text("2026-04-21T15:00:30Z", "hi", uuid="b-a1"),
        ],
    })
    _ingest.sync(conn)
    return conn


class TestProjects:
    def test_lists_projects_with_current_marker(self, populated_conn, project_dir):
        data = _scope.projects(populated_conn)
        assert "current" in data
        assert "projects" in data
        assert "-proj-alpha" in data["projects"]
        assert "-proj-beta" in data["projects"]
        # current is the encoded path of CLAUDE_PROJECT_DIR
        assert data["current"] == str(project_dir).replace("/", "-")


class TestSessions:
    def test_filter_by_project(self, populated_conn):
        data = _scope.sessions(populated_conn, project_filter="alpha")
        assert data["n_sessions"] == 1
        assert data["sessions"][0]["session"] == "alpha-s1"
        assert data["sessions"][0]["n_exchanges"] == 2

    def test_no_filter_returns_all_when_explicitly_widened(self, populated_conn):
        data = _scope.sessions(populated_conn, project_filter="")
        assert data["n_sessions"] == 2

    def test_default_lean_shape(self, populated_conn):
        data = _scope.sessions(populated_conn, project_filter="alpha")
        s = data["sessions"][0]
        assert set(s.keys()) == {"project", "session", "n_exchanges", "n_purposed"}

    def test_show_timeframes_adds_first_last_ts(self, populated_conn):
        data = _scope.sessions(
            populated_conn, project_filter="alpha", show=["timeframes"],
        )
        s = data["sessions"][0]
        assert "first_ts" in s and "last_ts" in s

    def test_show_bytes_adds_bytes(self, populated_conn):
        data = _scope.sessions(
            populated_conn, project_filter="alpha", show=["bytes"],
        )
        s = data["sessions"][0]
        assert s["bytes"] > 0

    def test_show_unknown_raises(self, populated_conn):
        with pytest.raises(ValueError, match="unknown show"):
            _scope.sessions(populated_conn, show=["bogus"])


class TestExchanges:
    def test_filter_by_session(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1",
        )
        assert len(data) == 2  # two user_msg events → two exchanges
        assert data[0]["exchange"] == 1
        assert data[1]["exchange"] == 2

    def test_range_within_session(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1", range_from=1, range_to=1,
        )
        assert len(data) == 1
        assert data[0]["exchange"] == 1

    def test_default_lean_shape(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1", range_from=1, range_to=1,
        )
        assert set(data[0].keys()) == {"project", "session", "exchange", "purpose"}

    def test_show_messages_adds_messages(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1", range_from=1, range_to=1,
            show=["messages"],
        )
        msgs = data[0]["messages"]
        assert len(msgs) == 2
        assert msgs[0]["type"] == "user"
        assert msgs[0]["message"] == "alpha hello"
        assert msgs[1]["type"] == "assistant"

    def test_show_active_adds_active_s_only(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1", range_from=1, range_to=1,
            show=["active"],
        )
        assert "active_s" in data[0]
        assert "user_s" not in data[0]
        assert "agent_s" not in data[0]
        assert "total_s" not in data[0]

    def test_show_breakdown_adds_user_agent_active(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1", range_from=1, range_to=1,
            show=["breakdown"],
        )
        row = data[0]
        assert "active_s" in row and "user_s" in row and "agent_s" in row
        assert "total_s" not in row and "idle_s" not in row

    def test_show_metrics_adds_full_metric_hierarchy(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1",
            show=["metrics"],
        )
        for row in data:
            assert {"active_s", "user_s", "agent_s", "total_s", "idle_s"} <= set(row.keys())

    def test_show_timeframes_adds_start_end(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1", range_from=1, range_to=1,
            show=["timeframes"],
        )
        assert "exchange_start" in data[0]
        assert "exchange_end" in data[0]

    def test_exchange_conservation(self, populated_conn):
        """For each exchange, total = user + agent + idle (with NULL user_s treated as 0)."""
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            session_id="alpha-s1",
            show=["metrics"],
        )
        for e in data:
            user = e["user_s"] or 0
            agent = e["agent_s"] or 0
            idle = e["idle_s"] or 0
            assert e["total_s"] == user + agent + idle
            assert e["active_s"] == user + agent

    def test_show_unknown_raises(self, populated_conn):
        with pytest.raises(ValueError, match="unknown show"):
            _scope.exchanges(
                populated_conn, threshold_s=900,
                session_id="alpha-s1", show=["bogus"],
            )

    def test_unknown_session_raises(self, populated_conn):
        with pytest.raises(LookupError):
            _scope.exchanges(
                populated_conn, threshold_s=900,
                session_id="nonexistent",
            )

    def test_filter_by_project(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            project_filter="alpha",
        )
        assert all(e["project"] == "-proj-alpha" for e in data)
        assert len(data) == 2  # two exchanges in alpha-s1

    def test_date_range_filter(self, populated_conn):
        data = _scope.exchanges(
            populated_conn, threshold_s=900,
            from_ts="2026-04-21T00:00:00",
            to_ts="2026-04-22T00:00:00",
        )
        # Only beta-s1 falls in this range.
        assert len(data) == 1
        assert data[0]["session"] == "beta-s1"


class TestResolveSession:
    def test_exact_match(self, populated_conn):
        assert _scope.resolve_session(populated_conn, "alpha-s1") == "alpha-s1"

    def test_unique_prefix(self, populated_conn):
        assert _scope.resolve_session(populated_conn, "alpha-") == "alpha-s1"

    def test_no_match_raises(self, populated_conn):
        with pytest.raises(LookupError):
            _scope.resolve_session(populated_conn, "missing")

    def test_ambiguous_prefix_raises(self, conn, seeded_project):
        seeded_project("-p", {
            "shared-1": [make_user_msg("2026-04-20T10:00:00Z", "a")],
            "shared-2": [make_user_msg("2026-04-20T11:00:00Z", "b")],
        })
        _ingest.sync(conn)
        with pytest.raises(LookupError) as exc:
            _scope.resolve_session(conn, "shared")
        assert "ambiguous" in str(exc.value)
