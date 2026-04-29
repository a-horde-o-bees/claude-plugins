"""Tests for _stats: derived statistics computed on demand."""

import pytest

from systems.transcripts import _ingest, _stats

from .conftest import make_assistant_text, make_user_msg


class TestAvgUserTime:
    def test_returns_zero_when_no_data(self, conn):
        assert _stats.avg_user_time(conn, threshold_s=900) == 0.0

    def test_excludes_above_threshold_pauses(self, conn, seeded_project):
        # Seed two user_msg events with a 30-min compose pause between them
        # (above the 15-min threshold) — the compose pause should NOT count.
        seeded_project("-p", {
            "s1": [
                make_user_msg("2026-04-28T10:00:00Z", "first", uuid="u1"),
                make_assistant_text("2026-04-28T10:00:05Z", "ok", uuid="a1"),
                make_user_msg("2026-04-28T10:30:05Z", "after long pause", uuid="u2"),
            ],
        })
        _ingest.sync(conn)
        # Only the very-first user_msg's gap (which is NULL because no prior
        # event) and the second one's gap (30 min, above threshold) exist.
        # Above-threshold is excluded; NULL is excluded; result is 0.
        assert _stats.avg_user_time(conn, threshold_s=900) == 0.0

    def test_averages_below_threshold_pauses(self, conn, seeded_project):
        # Three user_msg events with below-threshold compose pauses:
        # gap on u2 = 60s, gap on u3 = 120s. Average = 90s.
        seeded_project("-p", {
            "s1": [
                make_user_msg("2026-04-28T10:00:00Z", "first", uuid="u1"),
                make_assistant_text("2026-04-28T10:00:05Z", "ok", uuid="a1"),
                make_user_msg("2026-04-28T10:01:05Z", "second", uuid="u2"),
                make_assistant_text("2026-04-28T10:01:10Z", "ok", uuid="a2"),
                make_user_msg("2026-04-28T10:03:10Z", "third", uuid="u3"),
            ],
        })
        _ingest.sync(conn)
        avg = _stats.avg_user_time(conn, threshold_s=900)
        # u2's gap = 60s (10:01:05 - 10:00:05), u3's gap = 120s (10:03:10 - 10:01:10).
        assert avg == pytest.approx(90.0, abs=0.01)

    def test_threshold_change_affects_average(self, conn, seeded_project):
        # One pause is 60s (always below); another is 600s (10 min).
        seeded_project("-p", {
            "s1": [
                make_user_msg("2026-04-28T10:00:00Z", "first", uuid="u1"),
                make_assistant_text("2026-04-28T10:00:05Z", "ok", uuid="a1"),
                make_user_msg("2026-04-28T10:01:05Z", "60s gap", uuid="u2"),
                make_assistant_text("2026-04-28T10:01:10Z", "ok", uuid="a2"),
                make_user_msg("2026-04-28T10:11:10Z", "600s gap", uuid="u3"),
            ],
        })
        _ingest.sync(conn)
        # At 5-min threshold (300s), 600s pause is above-threshold and
        # excluded; only 60s counts.
        assert _stats.avg_user_time(conn, threshold_s=300) == pytest.approx(60.0, abs=0.01)
        # At 15-min threshold (900s), both pauses count: avg = (60 + 600) / 2 = 330.
        assert _stats.avg_user_time(conn, threshold_s=900) == pytest.approx(330.0, abs=0.01)
