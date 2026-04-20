"""Integration tests for the dormancy checker.

Exercises the checker against synthetic fixture systems that represent
each combination of surfaces and each class of failure. Real plugin
systems are not used as fixtures — they drift, and the checker must
hold its own ground truth.
"""

import sys
from pathlib import Path


FIXTURES_DIR = Path(__file__).parent / "fixtures"
if str(FIXTURES_DIR) not in sys.path:
    sys.path.insert(0, str(FIXTURES_DIR))

from systems.check import check_dormancy, scan_system  # noqa: E402


def _run(fixture_name: str, tmp_project_dir: Path):
    fixture_path = FIXTURES_DIR / fixture_name
    surfaces = scan_system(fixture_path)
    return check_dormancy(
        surfaces,
        facade_import_path=fixture_name,
        init_import_path=f"{fixture_name}._init",
        tmp_project_dir=tmp_project_dir,
    )


class TestCompliantRuntime:
    """Fixture with full readiness interface passes every check."""

    def test_passes(self, tmp_path):
        result = _run("compliant_runtime", tmp_path)
        assert result.ok, f"unexpected failures: {result.failures}"
        assert "ready() returns False when infrastructure absent" in result.passes
        assert any("ensure_ready() raises NotReadyError" in p for p in result.passes)
        assert "ready() returns True after init" in result.passes
        assert "ensure_ready() does not raise after init" in result.passes


class TestDeployOnly:
    """Fixture without readiness interface passes — treated as deploy-only."""

    def test_passes(self, tmp_path):
        result = _run("deploy_only", tmp_path)
        assert result.ok, f"unexpected failures: {result.failures}"
        assert any("deploy-only" in s for s in result.skipped)


class TestBrokenReadyAlwaysTrue:
    """Fixture whose ready() returns True even in absent state fails."""

    def test_flags_lying_predicate(self, tmp_path):
        result = _run("broken_ready_always_true", tmp_path)
        assert not result.ok, "expected failures but result.ok is True"
        assert any(
            "ready() returned True against an empty project dir" in f
            for f in result.failures
        ), f"missing expected failure; got: {result.failures}"

    def test_flags_ensure_ready_not_raising(self, tmp_path):
        result = _run("broken_ready_always_true", tmp_path)
        assert any(
            "ensure_ready() did not raise" in f for f in result.failures
        ), f"missing expected failure; got: {result.failures}"
