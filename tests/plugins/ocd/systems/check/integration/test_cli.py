"""Integration tests for the check CLI verb dispatch.

Exercises `ocd-run check dormancy` argparse + dispatch wiring. The
underlying checker is covered by test_dormancy_check.py against
synthetic fixtures; this suite locks the argparse surface so the
user-facing command contract cannot regress silently.
"""

import subprocess
from pathlib import Path


def _run(ocd_run: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ocd_run), "check", *args],
        capture_output=True, text=True,
    )


class TestDormancyVerb:
    def test_dormancy_runs_and_reports_per_system(self, ocd_run: Path):
        """CLI dispatches to the dormancy checker and emits one
        `[PASS]` or `[FAIL]` line per system. Exit code reflects the
        check's verdict (0 when all pass, 1 when any fail); this test
        asserts the report shape, not the verdict — verdict depends on
        the current deployed state, which is a separate concern."""
        result = _run(ocd_run, "dormancy")
        assert result.returncode in (0, 1)
        # At least one system must have reported a result
        assert "[PASS]" in result.stdout or "[FAIL]" in result.stdout
        # Dimension name surfaces per-system
        assert "— dormancy" in result.stdout

    def test_dormancy_on_unknown_system_exits_1(self, ocd_run: Path):
        result = _run(ocd_run, "dormancy", "not_a_real_system")
        assert result.returncode == 1
        assert "System not found" in result.stderr

    def test_missing_dimension_exits_nonzero(self, ocd_run: Path):
        """Argparse `required=True` on the subparser rejects a bare
        `check` invocation."""
        result = _run(ocd_run)
        assert result.returncode != 0
