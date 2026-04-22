"""Integration tests for the governance CLI verb dispatch.

Exercises `ocd-run governance list|for|order` argparse + output shape
through the real bin wrapper. The underlying facade (governance_list,
governance_match, governance_order) is covered by test_governance.py
and test_frontmatter.py; this suite locks the user-facing CLI surface.
"""

import json
import subprocess
from pathlib import Path


def _run(ocd_run: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ocd_run), "governance", *args],
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
    def test_matches_python_file_to_conventions(
        self, ocd_run: Path, project_root: Path,
    ):
        """A .py path matches at least the ocd python convention."""
        target = "plugins/ocd/systems/pdf/_generate.py"
        assert (project_root / target).is_file()

        result = _run(ocd_run, "for", target)

        assert result.returncode == 0, result.stderr
        assert "Conventions:" in result.stdout
        assert "python.md" in result.stdout
        assert f"{target} follows:" in result.stdout

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


class TestOrderVerb:
    def test_emits_levels(self, ocd_run: Path):
        result = _run(ocd_run, "order")
        assert result.returncode == 0, result.stderr
        assert "Level 0:" in result.stdout

    def test_json_output_parses(self, ocd_run: Path):
        result = _run(ocd_run, "order", "--json")
        assert result.returncode == 0, result.stderr
        payload = json.loads(result.stdout)
        assert set(payload.keys()) == {"levels", "dangling"}


class TestDispatchBoundary:
    def test_missing_command_exits_nonzero(self, ocd_run: Path):
        result = _run(ocd_run)
        assert result.returncode != 0
