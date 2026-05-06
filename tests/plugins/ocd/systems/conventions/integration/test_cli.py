"""Integration tests for the conventions CLI verb dispatch.

Exercises `ocd-run conventions list|for` argparse + output shape through
the real bin wrapper. The underlying facade (governance_list,
governance_match) is covered by test_governance.py and
test_frontmatter.py; this suite locks the user-facing CLI surface.
"""

import subprocess
from pathlib import Path


def _run(ocd_run: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ocd_run), "conventions", *args],
        capture_output=True, text=True,
    )


class TestListVerb:
    def test_lists_governance_entries(self, ocd_run: Path):
        result = _run(ocd_run, "list")
        assert result.returncode == 0, result.stderr
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        assert lines, "expected at least one governance entry"
        assert any("[rule]" in line or "[convention]" in line for line in lines)


class TestForVerb:
    def test_no_match_reports_none(self, ocd_run: Path):
        """A path matching nothing reports 'No governance matches.'"""
        result = _run(ocd_run, "for", "some/path/that/matches/nothing.xyz")
        assert result.returncode == 0, result.stderr
        assert "No governance matches." in result.stdout

    def test_include_rules_flag(self, ocd_run: Path):
        """--include-rules adds rules to the match output."""
        target = "plugins/ocd/systems/pdf/_generate.py"
        result = _run(ocd_run, "for", target, "--include-rules")
        assert result.returncode == 0, result.stderr
        # With rules included, at least one rules/ file appears in the match
        assert "/rules/" in result.stdout

    def test_requires_at_least_one_file(self, ocd_run: Path):
        """nargs='+' rejects zero files."""
        result = _run(ocd_run, "for")
        assert result.returncode != 0


class TestDispatchBoundary:
    def test_missing_command_exits_nonzero(self, ocd_run: Path):
        result = _run(ocd_run)
        assert result.returncode != 0
