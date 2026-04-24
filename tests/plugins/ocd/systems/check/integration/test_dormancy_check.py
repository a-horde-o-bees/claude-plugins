"""Integration tests for the dormancy checker.

Exercises the checker against synthetic fixture systems that represent
each combination of surfaces and each class of failure. Real plugin
systems are not used as fixtures — they drift, and the checker must
hold its own ground truth.

Fixture-path resolution and `sys.path` setup live in the local
conftest (`dormancy_fixtures_dir` fixture and its autouse companion),
so test bodies do not anchor to `__file__` directly.
"""

from pathlib import Path

from systems.check import check_dormancy, scan_system


def _run(fixture_name: str, fixtures_dir: Path, tmp_project_dir: Path):
    fixture_path = fixtures_dir / fixture_name
    surfaces = scan_system(fixture_path)
    return check_dormancy(
        surfaces,
        facade_import_path=fixture_name,
        init_import_path=f"{fixture_name}._init",
        tmp_project_dir=tmp_project_dir,
    )


class TestCompliantRuntime:
    """Fixture with full readiness interface passes every check."""

    def test_passes(self, tmp_path, dormancy_fixtures_dir):
        result = _run("compliant_runtime", dormancy_fixtures_dir, tmp_path)
        assert result.ok, f"unexpected failures: {result.failures}"
        assert "ready() returns False when infrastructure absent" in result.passes
        assert any("ensure_ready() raises NotReadyError" in p for p in result.passes)
        assert "ready() returns True after init" in result.passes
        assert "ensure_ready() does not raise after init" in result.passes


class TestDeployOnly:
    """Fixture without readiness interface passes — treated as deploy-only."""

    def test_passes(self, tmp_path, dormancy_fixtures_dir):
        result = _run("deploy_only", dormancy_fixtures_dir, tmp_path)
        assert result.ok, f"unexpected failures: {result.failures}"
        assert any("deploy-only" in s for s in result.skipped)


class TestBrokenReadyAlwaysTrue:
    """Fixture whose ready() returns True even in absent state fails."""

    def test_flags_lying_predicate(self, tmp_path, dormancy_fixtures_dir):
        result = _run("broken_ready_always_true", dormancy_fixtures_dir, tmp_path)
        assert not result.ok, "expected failures but result.ok is True"
        assert any(
            "ready() returned True against an empty project dir" in f
            for f in result.failures
        ), f"missing expected failure; got: {result.failures}"

    def test_flags_ensure_ready_not_raising(self, tmp_path, dormancy_fixtures_dir):
        result = _run("broken_ready_always_true", dormancy_fixtures_dir, tmp_path)
        assert any(
            "ensure_ready() did not raise" in f for f in result.failures
        ), f"missing expected failure; got: {result.failures}"
