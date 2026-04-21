"""Integration test for install_deps.sh against real `uv`.

One test that validates what stubs can't: the actual `uv pip install
--requirement pyproject.toml --python <venv>/bin/python3` invocation
works end-to-end against real uv, and the resulting venv has the
declared dependency importable.

Does NOT duplicate the stub suite's branching-logic coverage
(change detection, rm-on-failure, idempotency) — those are fully
covered by test_install_deps.py with lower cost. Per testing.md's
Integration Tests overhead rule, real-uv coverage here is scoped to
the dispatch-class failure only unit-level stubs can't catch: real
CLI shape + real import resolution.

Skipped when `uv` is not on PATH. Requires network — uv pip install
pulls packages from PyPI.
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


def test_fresh_install_produces_importable_dependency(
    plugin_tree: tuple[Path, Path],
) -> None:
    """End-to-end: fresh tree → install runs → declared dep is importable
    against the resulting venv's python. Validates uv CLI shape + venv
    layout + plugin.toml-to-installed-dep chain together. This is the one
    validation stub tests cannot substitute."""
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
