"""Tests for _settings: typed config storage."""

import pytest

from systems.transcripts import _settings


@pytest.fixture
def settings_conn(conn):
    """Initialize the settings table on the conn fixture."""
    _settings.init_settings(conn)
    return conn


class TestInitSettings:
    def test_creates_settings_table_with_defaults(self, settings_conn):
        row = settings_conn.execute(
            "SELECT threshold_min FROM settings"
        ).fetchone()
        assert row[0] == 15  # default

    def test_idempotent(self, settings_conn):
        # Re-running init_settings must not duplicate the row or change values.
        _settings.set_value(settings_conn, "threshold_min", 30)
        _settings.init_settings(settings_conn)
        rows = settings_conn.execute(
            "SELECT * FROM settings"
        ).fetchall()
        assert len(rows) == 1
        assert _settings.get(settings_conn, "threshold_min") == 30


class TestGet:
    def test_returns_default_after_init(self, settings_conn):
        assert _settings.get(settings_conn, "threshold_min") == 15

    def test_returns_native_type(self, settings_conn):
        # threshold_min is INTEGER; result should be int, not str.
        assert isinstance(_settings.get(settings_conn, "threshold_min"), int)

    def test_unknown_key_raises(self, settings_conn):
        with pytest.raises(KeyError):
            _settings.get(settings_conn, "no_such_setting")


class TestSetValue:
    def test_persists_value(self, settings_conn):
        _settings.set_value(settings_conn, "threshold_min", 30)
        assert _settings.get(settings_conn, "threshold_min") == 30

    def test_coerces_string_to_int(self, settings_conn):
        # CLI passes strings; the setter must coerce.
        result = _settings.set_value(settings_conn, "threshold_min", "20")
        assert result == 20
        assert _settings.get(settings_conn, "threshold_min") == 20

    def test_unknown_key_raises(self, settings_conn):
        with pytest.raises(KeyError):
            _settings.set_value(settings_conn, "no_such_setting", 5)

    def test_invalid_value_for_type_raises(self, settings_conn):
        with pytest.raises(ValueError):
            _settings.set_value(settings_conn, "threshold_min", "not-a-number")


class TestListAll:
    def test_returns_metadata_envelope(self, settings_conn):
        out = _settings.list_all(settings_conn)
        assert "threshold_min" in out
        entry = out["threshold_min"]
        assert entry["value"] == 15
        assert entry["default"] == 15
        assert "Idle-gap threshold" in entry["description"]

    def test_reflects_current_values(self, settings_conn):
        _settings.set_value(settings_conn, "threshold_min", 25)
        out = _settings.list_all(settings_conn)
        assert out["threshold_min"]["value"] == 25
        # Default unchanged.
        assert out["threshold_min"]["default"] == 15
