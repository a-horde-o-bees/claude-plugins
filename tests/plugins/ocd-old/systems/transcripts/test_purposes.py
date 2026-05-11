"""Tests for _purposes: per-exchange purpose summaries."""

import pytest

from systems.transcripts import _ingest, _purposes, _scope

from .conftest import make_assistant_text, make_user_msg


@pytest.fixture
def populated_conn(conn, seeded_project):
    """Populated DB with one session and three exchanges."""
    seeded_project("-proj", {
        "s1": [
            make_user_msg("2026-04-28T10:00:00Z", "first", uuid="u1"),
            make_assistant_text("2026-04-28T10:00:05Z", "ok", uuid="a1"),
            make_user_msg("2026-04-28T10:01:00Z", "second", uuid="u2"),
            make_assistant_text("2026-04-28T10:01:05Z", "ok", uuid="a2"),
            make_user_msg("2026-04-28T10:02:00Z", "third", uuid="u3"),
        ],
    })
    _ingest.sync(conn)
    return conn


class TestSetAndGet:
    def test_set_then_get_round_trip(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "Initial setup question.")
        assert _purposes.get(populated_conn, "s1", 1) == "Initial setup question."

    def test_get_returns_none_when_unset(self, populated_conn):
        assert _purposes.get(populated_conn, "s1", 1) is None

    def test_set_strips_whitespace(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "  hello  ")
        assert _purposes.get(populated_conn, "s1", 1) == "hello"

    def test_set_empty_raises(self, populated_conn):
        with pytest.raises(ValueError):
            _purposes.set_purpose(populated_conn, "s1", 1, "")
        with pytest.raises(ValueError):
            _purposes.set_purpose(populated_conn, "s1", 1, "   ")

    def test_set_overwrites_existing(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "first version")
        _purposes.set_purpose(populated_conn, "s1", 1, "second version")
        assert _purposes.get(populated_conn, "s1", 1) == "second version"

    def test_set_isolates_by_exchange(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "purpose for one")
        _purposes.set_purpose(populated_conn, "s1", 2, "purpose for two")
        assert _purposes.get(populated_conn, "s1", 1) == "purpose for one"
        assert _purposes.get(populated_conn, "s1", 2) == "purpose for two"


class TestClear:
    def test_clear_removes_existing(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "to be removed")
        removed = _purposes.clear(populated_conn, "s1", 1)
        assert removed is True
        assert _purposes.get(populated_conn, "s1", 1) is None

    def test_clear_when_unset_returns_false(self, populated_conn):
        assert _purposes.clear(populated_conn, "s1", 99) is False


class TestListAndCount:
    def test_list_empty_when_no_purposes(self, populated_conn):
        assert _purposes.list_for_session(populated_conn, "s1") == []

    def test_list_returns_sorted_by_exchange(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 3, "third")
        _purposes.set_purpose(populated_conn, "s1", 1, "first")
        _purposes.set_purpose(populated_conn, "s1", 2, "second")
        out = _purposes.list_for_session(populated_conn, "s1")
        assert [p["exchange"] for p in out] == [1, 2, 3]
        assert [p["purpose"] for p in out] == ["first", "second", "third"]

    def test_count_for_session(self, populated_conn):
        assert _purposes.count_for_session(populated_conn, "s1") == 0
        _purposes.set_purpose(populated_conn, "s1", 1, "a")
        _purposes.set_purpose(populated_conn, "s1", 2, "b")
        assert _purposes.count_for_session(populated_conn, "s1") == 2

    def test_count_isolates_by_session(self, conn, seeded_project):
        seeded_project("-p", {
            "sa": [make_user_msg("2026-04-28T10:00:00Z", "a")],
            "sb": [make_user_msg("2026-04-28T11:00:00Z", "b")],
        })
        _ingest.sync(conn)
        _purposes.set_purpose(conn, "sa", 1, "a-purpose")
        assert _purposes.count_for_session(conn, "sa") == 1
        assert _purposes.count_for_session(conn, "sb") == 0


class TestScopeIntegration:
    def test_sessions_includes_n_purposed(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "first")
        _purposes.set_purpose(populated_conn, "s1", 2, "second")
        data = _scope.sessions(populated_conn)
        s = data["sessions"][0]
        assert s["n_purposed"] == 2

    def test_exchanges_includes_purpose_when_set(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 2, "exchange 2 purpose")
        data = _scope.exchanges(populated_conn, threshold_s=900, session_id="s1")
        by_ex = {e["exchange"]: e for e in data}
        assert by_ex[1]["purpose"] is None
        assert by_ex[2]["purpose"] == "exchange 2 purpose"
        assert by_ex[3]["purpose"] is None

    def test_exchanges_purpose_field_present_when_unset(self, populated_conn):
        # The field must exist (as None) even when no purposes are stored.
        data = _scope.exchanges(populated_conn, threshold_s=900, session_id="s1")
        for e in data:
            assert "purpose" in e
            assert e["purpose"] is None


class TestPersistence:
    def test_purposes_survive_resync(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "should persist")
        # Re-sync only adds new events; should not touch purposes.
        _ingest.sync(populated_conn)
        assert _purposes.get(populated_conn, "s1", 1) == "should persist"


class TestSetMany:
    def test_writes_all_keys(self, populated_conn):
        written = _purposes.set_many(populated_conn, "s1", {1: "a", 2: "b", 3: "c"})
        assert written == {1: "a", 2: "b", 3: "c"}
        assert _purposes.get(populated_conn, "s1", 1) == "a"
        assert _purposes.get(populated_conn, "s1", 3) == "c"

    def test_strips_whitespace_in_batch(self, populated_conn):
        written = _purposes.set_many(populated_conn, "s1", {1: "  hello  "})
        assert written[1] == "hello"

    def test_empty_dict_is_noop(self, populated_conn):
        assert _purposes.set_many(populated_conn, "s1", {}) == {}
        assert _purposes.count_for_session(populated_conn, "s1") == 0

    def test_empty_value_raises(self, populated_conn):
        with pytest.raises(ValueError, match="must be non-empty"):
            _purposes.set_many(populated_conn, "s1", {1: "ok", 2: "   "})

    def test_overwrites_existing_in_batch(self, populated_conn):
        _purposes.set_purpose(populated_conn, "s1", 1, "old")
        _purposes.set_many(populated_conn, "s1", {1: "new", 2: "added"})
        assert _purposes.get(populated_conn, "s1", 1) == "new"
        assert _purposes.get(populated_conn, "s1", 2) == "added"


class TestClearMany:
    def test_clears_all_set_purposes(self, populated_conn):
        _purposes.set_many(populated_conn, "s1", {1: "a", 2: "b", 3: "c"})
        cleared = _purposes.clear_many(populated_conn, "s1", [1, 3])
        assert sorted(cleared) == [1, 3]
        assert _purposes.get(populated_conn, "s1", 1) is None
        assert _purposes.get(populated_conn, "s1", 2) == "b"
        assert _purposes.get(populated_conn, "s1", 3) is None

    def test_skips_unset_silently(self, populated_conn):
        _purposes.set_many(populated_conn, "s1", {1: "a"})
        cleared = _purposes.clear_many(populated_conn, "s1", [1, 2, 3])
        assert cleared == [1]

    def test_empty_list_is_noop(self, populated_conn):
        assert _purposes.clear_many(populated_conn, "s1", []) == []
