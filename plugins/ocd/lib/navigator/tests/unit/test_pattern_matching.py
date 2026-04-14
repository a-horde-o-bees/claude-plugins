"""Unit tests for _matches_pattern_any pattern matching."""

from lib.navigator._scanner import _matches_pattern_any


class TestMatchesAnyPattern:
    def _make_patterns(self, items):
        """Create mock pattern rows from (glob, description) pairs."""
        return [
            {"pattern": pat, "exclude": 0, "traverse": 1, "description": desc}
            for pat, desc in items
        ]

    def test_double_star_matches_nested(self):
        pats = self._make_patterns([("**/__init__.py", "Package marker")])
        result = _matches_pattern_any("src/lib/__init__.py", pats)
        assert result is not None
        assert result["description"] == "Package marker"

    def test_double_star_matches_top_level(self):
        pats = self._make_patterns([("**/tests", "Test suites")])
        result = _matches_pattern_any("tests", pats)
        assert result is not None

    def test_no_match(self):
        pats = self._make_patterns([("**/__init__.py", "Package marker")])
        result = _matches_pattern_any("src/main.py", pats)
        assert result is None

    def test_literal_pattern(self):
        pats = self._make_patterns([("src/main.py", "Entry point")])
        result = _matches_pattern_any("src/main.py", pats)
        assert result is not None

    def test_literal_no_match(self):
        pats = self._make_patterns([("src/main.py", "Entry point")])
        result = _matches_pattern_any("src/other.py", pats)
        assert result is None

    def test_empty_patterns(self):
        result = _matches_pattern_any("src/main.py", [])
        assert result is None
