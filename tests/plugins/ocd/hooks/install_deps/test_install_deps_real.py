"""Integration tests for install_deps.sh against real `uv`.

Distinct from test_install_deps.py, which uses stubbed uv + pip binaries
to validate the script's branching logic. This suite exercises the
actual SessionStart install flow — real venv creation, real `uv pip
install` against a synthetic pyproject.toml, real filesystem state.
Skipped when `uv` is not on PATH so local dev without uv still passes.

Covers two classes of failure that stubbed tests can't catch:

- Command-shape drift — the `uv pip install --requirement <pyproject>
  --python <venv>/bin/python3` invocation is validated against real uv.
  If uv's CLI shape changes, real invocation fails here immediately;
  stubbed tests keep passing.
- Real failure path — install against a nonexistent package actually
  fails (vs. stub that returns exit 1 without running). Verifies the
  ERR-trap rm invariant fires under genuine install errors.

Requires network — `uv pip install` pulls packages from PyPI.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT_PATH = Path(__file__).resolve().parents[5] / "plugins" / "ocd"
INSTALL_DEPS_SH = PLUGIN_ROOT_PATH / "hooks" / "install_deps.sh"

_MIN_DEPS_PYPROJECT = """\
[project]
name = "install-deps-real-test"
version = "0.0.0"
requires-python = ">=3.12"
dependencies = ["six"]
"""

_INVALID_DEPS_PYPROJECT = """\
[project]
name = "install-deps-real-test"
version = "0.0.0"
requires-python = ">=3.12"
dependencies = ["xyz-nonexistent-package-claude-plugins-89a0b"]
"""

pytestmark = pytest.mark.skipif(
    shutil.which("uv") is None,
    reason="uv not installed on this runner",
)


def _run(plugin_root: Path, plugin_data: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    env["CLAUDE_PLUGIN_DATA"] = str(plugin_data)
    return subprocess.run(
        ["bash", str(INSTALL_DEPS_SH)],
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def plugin_tree(tmp_path: Path) -> tuple[Path, Path]:
    plugin_root = tmp_path / "plugin"
    plugin_data = tmp_path / "data"
    plugin_root.mkdir()
    (plugin_root / ".claude-plugin").mkdir()
    (plugin_root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "install-deps-real-test", "version": "0.0.1"}),
    )
    (plugin_root / "pyproject.toml").write_text(_MIN_DEPS_PYPROJECT)
    return plugin_root, plugin_data


class TestRealInstall:
    def test_fresh_install_produces_importable_dependency(
        self, plugin_tree: tuple[Path, Path],
    ) -> None:
        """End-to-end: fresh tree → install runs → declared dep is importable
        against the resulting venv's python. Validates uv CLI shape + venv
        layout together."""
        plugin_root, plugin_data = plugin_tree
        result = _run(plugin_root, plugin_data)
        assert result.returncode == 0, result.stderr
        python = plugin_data / "venv" / "bin" / "python3"
        assert python.is_file()
        check = subprocess.run(
            [str(python), "-c", "import six"],
            capture_output=True,
            text=True,
        )
        assert check.returncode == 0, check.stderr

    def test_cached_manifest_mirrors_bundled_after_success(
        self, plugin_tree: tuple[Path, Path],
    ) -> None:
        """After successful install the cached copy in $CLAUDE_PLUGIN_DATA
        is a byte-for-byte copy of the bundled manifest — the precondition
        for diff -q to skip the next session's install."""
        plugin_root, plugin_data = plugin_tree
        result = _run(plugin_root, plugin_data)
        assert result.returncode == 0, result.stderr
        cached = plugin_data / "pyproject.toml"
        bundled = plugin_root / "pyproject.toml"
        assert cached.is_file()
        assert cached.read_text() == bundled.read_text()

    def test_unchanged_manifest_second_run_is_skip(
        self, plugin_tree: tuple[Path, Path],
    ) -> None:
        """Second run with unchanged pyproject.toml must not re-invoke
        uv pip install — the diff -q short-circuit branch. Detected by
        the venv's python3 mtime holding steady across runs."""
        plugin_root, plugin_data = plugin_tree
        _run(plugin_root, plugin_data)
        python = plugin_data / "venv" / "bin" / "python3"
        first_mtime = python.stat().st_mtime

        result = _run(plugin_root, plugin_data)
        assert result.returncode == 0, result.stderr
        assert python.stat().st_mtime == first_mtime


class TestRealFailureRetry:
    def test_install_failure_removes_cached_manifest(
        self, plugin_tree: tuple[Path, Path],
    ) -> None:
        """Inject a nonexistent package so uv pip install fails for real.
        The ERR trap removes the cached manifest so the next session's
        diff -q triggers a retry. Script exits non-zero; subsequent retry
        reproduces the failure without poisoning the cache."""
        plugin_root, plugin_data = plugin_tree
        (plugin_root / "pyproject.toml").write_text(_INVALID_DEPS_PYPROJECT)

        result = _run(plugin_root, plugin_data)
        assert result.returncode != 0
        assert not (plugin_data / "pyproject.toml").exists()

        # Retry idempotency: same failure, cached manifest remains absent.
        result2 = _run(plugin_root, plugin_data)
        assert result2.returncode != 0
        assert not (plugin_data / "pyproject.toml").exists()
