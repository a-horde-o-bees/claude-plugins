"""Tests for `ocd-run`'s self-update mechanism — runs install_deps.sh when source manifest drifts from cached manifest.

Eliminates the session-restart-required UX after plugin upgrades. When the cached pyproject.toml in the data dir differs from the source's pyproject.toml, ocd-run invokes install_deps.sh synchronously before exec'ing the venv python. flock serializes concurrent invocations.

Tests use a synthetic plugin tree with stubbed install_deps.sh and run.py so the actual venv install is bypassed; the stubs write marker files that prove which paths fired.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT_PATH = Path(__file__).resolve().parents[4] / "plugins" / "ocd"
OCD_RUN_SH = PLUGIN_ROOT_PATH / "bin" / "ocd-run"

SOURCE_PYPROJECT = '[project]\nname = "test-plugin"\nversion = "0.0.1"\ndependencies = []\n'
STALE_PYPROJECT = '[project]\nname = "test-plugin"\nversion = "0.0.0"\ndependencies = []\n'

INSTALL_DEPS_STUB = """#!/bin/bash
# Stub install_deps.sh — writes a marker showing it was invoked, then mimics the real script's
# post-conditions enough that ocd-run can proceed (venv exists, cached manifest written).
set -euo pipefail

mkdir -p "$CLAUDE_PLUGIN_DATA/venv/bin"
touch "$CLAUDE_PLUGIN_DATA/venv/bin/python3"
chmod +x "$CLAUDE_PLUGIN_DATA/venv/bin/python3"
cp "$CLAUDE_PLUGIN_ROOT/pyproject.toml" "$CLAUDE_PLUGIN_DATA/pyproject.toml"
echo "$$" >> "$CLAUDE_PLUGIN_DATA/.install-deps-invocations"
"""

# Stub python3 — replaces the venv python so exec'd run.py doesn't actually
# require a real Python installation. Just needs to exit 0 so ocd-run's exec
# completes cleanly.
PYTHON_STUB = """#!/bin/bash
exit 0
"""


@pytest.fixture
def fake_plugin(tmp_path: Path) -> tuple[Path, Path]:
    """Synthetic plugin tree + data dir. ocd-run is the real script; install_deps.sh and python3 are stubs."""
    plugin_root = tmp_path / "plugin"
    plugin_data = tmp_path / "data"
    plugin_root.mkdir()
    plugin_data.mkdir()

    (plugin_root / ".claude-plugin").mkdir()
    (plugin_root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "test-plugin", "version": "0.0.1"}),
    )
    (plugin_root / "pyproject.toml").write_text(SOURCE_PYPROJECT)

    (plugin_root / "bin").mkdir()
    shutil.copy(OCD_RUN_SH, plugin_root / "bin" / "ocd-run")
    (plugin_root / "bin" / "ocd-run").chmod(0o755)

    (plugin_root / "hooks").mkdir()
    (plugin_root / "hooks" / "install_deps.sh").write_text(INSTALL_DEPS_STUB)
    (plugin_root / "hooks" / "install_deps.sh").chmod(0o755)

    # No-op run.py — ocd-run execs `<python3> <plugin_root>/run.py <args>`; the
    # stubbed python3 ignores the run.py argument and exits 0.
    (plugin_root / "run.py").write_text("# stub\n")

    return plugin_root, plugin_data


def _run_ocd_run(plugin_root: Path, plugin_data: Path, *args: str) -> subprocess.CompletedProcess:
    """Invoke the synthetic plugin's ocd-run with explicit env vars + a stubbed python3 on PATH."""
    bin_dir = plugin_root / "bin"
    # Drop a python3 stub next to ocd-run so the venv exec resolves to a no-op.
    (plugin_data / "venv" / "bin").mkdir(parents=True, exist_ok=True)
    python_stub = plugin_data / "venv" / "bin" / "python3"
    if not python_stub.exists():
        python_stub.write_text(PYTHON_STUB)
        python_stub.chmod(0o755)

    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    env["CLAUDE_PLUGIN_DATA"] = str(plugin_data)
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    return subprocess.run(
        [str(bin_dir / "ocd-run"), "noop"],
        env=env,
        capture_output=True,
        text=True,
    )


def _install_invocation_count(plugin_data: Path) -> int:
    marker = plugin_data / ".install-deps-invocations"
    if not marker.exists():
        return 0
    return len([line for line in marker.read_text().splitlines() if line.strip()])


class TestDriftTriggersInstall:
    def test_first_run_with_no_cached_manifest_runs_install(self, fake_plugin: tuple[Path, Path]) -> None:
        plugin_root, plugin_data = fake_plugin
        result = _run_ocd_run(plugin_root, plugin_data)

        assert result.returncode == 0, result.stderr
        assert _install_invocation_count(plugin_data) == 1

    def test_drifted_manifest_triggers_install(self, fake_plugin: tuple[Path, Path]) -> None:
        plugin_root, plugin_data = fake_plugin
        # Pre-populate cached manifest with a STALE version
        (plugin_data / "pyproject.toml").write_text(STALE_PYPROJECT)

        result = _run_ocd_run(plugin_root, plugin_data)

        assert result.returncode == 0, result.stderr
        assert _install_invocation_count(plugin_data) == 1
        # Cached manifest should now match source
        assert (plugin_data / "pyproject.toml").read_text() == SOURCE_PYPROJECT


class TestNoDriftSkipsInstall:
    def test_matching_manifest_skips_install(self, fake_plugin: tuple[Path, Path]) -> None:
        plugin_root, plugin_data = fake_plugin
        # Pre-populate cached manifest matching source
        (plugin_data / "pyproject.toml").write_text(SOURCE_PYPROJECT)

        result = _run_ocd_run(plugin_root, plugin_data)

        assert result.returncode == 0, result.stderr
        assert _install_invocation_count(plugin_data) == 0


class TestGracefulDegradation:
    def test_plugin_without_install_deps_skips_self_update(self, fake_plugin: tuple[Path, Path]) -> None:
        plugin_root, plugin_data = fake_plugin
        # Remove install_deps.sh — plugin doesn't ship the dep-install pattern
        (plugin_root / "hooks" / "install_deps.sh").unlink()

        result = _run_ocd_run(plugin_root, plugin_data)

        # Should still complete cleanly (no install_deps.sh to invoke; venv discovery + exec)
        assert result.returncode == 0, result.stderr
        # No marker because there was no install_deps.sh to write it
        assert _install_invocation_count(plugin_data) == 0


class TestIdempotency:
    def test_second_invocation_after_install_skips(self, fake_plugin: tuple[Path, Path]) -> None:
        plugin_root, plugin_data = fake_plugin

        # First run: drift exists (no cached manifest), install fires
        first = _run_ocd_run(plugin_root, plugin_data)
        assert first.returncode == 0, first.stderr
        assert _install_invocation_count(plugin_data) == 1

        # Second run: cached manifest now matches source, install should NOT fire
        second = _run_ocd_run(plugin_root, plugin_data)
        assert second.returncode == 0, second.stderr
        assert _install_invocation_count(plugin_data) == 1, "second invocation should not re-trigger install"
