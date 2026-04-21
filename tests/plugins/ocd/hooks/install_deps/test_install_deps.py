"""Tests for install_deps.sh — verify docs-prescribed idioms.

Exercises the SessionStart install hook against a fixture plugin tree with a stubbed `uv` binary that handles both `uv venv` and `uv pip install` subcommands. The stub materializes the venv directory structure without performing real Python installs, so tests run without network access and complete in milliseconds.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT_PATH = Path(__file__).resolve().parents[5] / "plugins" / "ocd"
INSTALL_DEPS_SH = PLUGIN_ROOT_PATH / "hooks" / "install_deps.sh"

_MIN_PYPROJECT = '[project]\nname = "test-plugin"\nversion = "0.0.0"\ndependencies = ["pytest"]\n'


def _write_uv_stub(bin_dir: Path, *, uv_venv_succeeds: bool = True, uv_pip_succeeds: bool = True) -> None:
    uv_path = bin_dir / "uv"
    venv_exit = 0 if uv_venv_succeeds else 1
    pip_exit = 0 if uv_pip_succeeds else 1
    uv_path.write_text(f"""#!/bin/bash
if [ "$1" = "venv" ]; then
    shift
    venv_dir=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --seed|--quiet|--allow-existing) shift ;;
            *) venv_dir="$1"; shift ;;
        esac
    done
    mkdir -p "$venv_dir/bin"
    touch "$venv_dir/bin/python3"
    chmod +x "$venv_dir/bin/python3"
    exit {venv_exit}
fi
if [ "$1" = "pip" ] && [ "$2" = "install" ]; then
    exit {pip_exit}
fi
exit 0
""")
    uv_path.chmod(0o755)


def _run_install(plugin_root: Path, plugin_data: Path, stub_bin: Path) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    env["CLAUDE_PLUGIN_DATA"] = str(plugin_data)
    env["PATH"] = f"{stub_bin}{os.pathsep}{env['PATH']}"
    return subprocess.run(
        ["bash", str(INSTALL_DEPS_SH)],
        env=env,
        capture_output=True,
        text=True,
    )


@pytest.fixture
def fake_plugin(tmp_path: Path) -> tuple[Path, Path, Path]:
    plugin_root = tmp_path / "plugin"
    plugin_data = tmp_path / "data"
    stub_bin = tmp_path / "bin"
    plugin_root.mkdir()
    stub_bin.mkdir()
    (plugin_root / ".claude-plugin").mkdir()
    (plugin_root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "test-plugin", "version": "0.0.1"}),
    )
    (plugin_root / "pyproject.toml").write_text(_MIN_PYPROJECT)
    return plugin_root, plugin_data, stub_bin


class TestFirstRun:
    def test_creates_venv_and_cached_manifest(self, fake_plugin: tuple[Path, Path, Path]) -> None:
        plugin_root, plugin_data, stub_bin = fake_plugin
        _write_uv_stub(stub_bin)

        result = _run_install(plugin_root, plugin_data, stub_bin)

        assert result.returncode == 0, result.stderr
        assert (plugin_data / "pyproject.toml").exists()
        assert (plugin_data / "venv" / "bin" / "python3").exists()
        assert (plugin_data / "pyproject.toml").read_text() == _MIN_PYPROJECT


class TestChangeDetection:
    def test_unchanged_manifest_skips_install(self, fake_plugin: tuple[Path, Path, Path]) -> None:
        plugin_root, plugin_data, stub_bin = fake_plugin
        (plugin_data / "venv" / "bin").mkdir(parents=True)
        (plugin_data / "venv" / "bin" / "python3").touch()
        (plugin_data / "venv" / "bin" / "python3").chmod(0o755)
        shutil.copy(plugin_root / "pyproject.toml", plugin_data / "pyproject.toml")

        # Failing uv stub: if the script runs uv, the script fails.
        _write_uv_stub(stub_bin, uv_venv_succeeds=False)
        result = _run_install(plugin_root, plugin_data, stub_bin)

        assert result.returncode == 0, result.stderr

    def test_changed_manifest_triggers_reinstall(self, fake_plugin: tuple[Path, Path, Path]) -> None:
        plugin_root, plugin_data, stub_bin = fake_plugin
        (plugin_data / "venv" / "bin").mkdir(parents=True)
        (plugin_data / "venv" / "bin" / "python3").touch()
        (plugin_data / "venv" / "bin" / "python3").chmod(0o755)
        (plugin_data / "pyproject.toml").write_text('[project]\nname = "stale"\nversion = "0.0.0"\ndependencies = []\n')

        _write_uv_stub(stub_bin)
        result = _run_install(plugin_root, plugin_data, stub_bin)

        assert result.returncode == 0, result.stderr
        assert (plugin_data / "pyproject.toml").read_text() == _MIN_PYPROJECT

    def test_missing_venv_triggers_reinstall(self, fake_plugin: tuple[Path, Path, Path]) -> None:
        plugin_root, plugin_data, stub_bin = fake_plugin
        plugin_data.mkdir()
        shutil.copy(plugin_root / "pyproject.toml", plugin_data / "pyproject.toml")

        _write_uv_stub(stub_bin)
        result = _run_install(plugin_root, plugin_data, stub_bin)

        assert result.returncode == 0, result.stderr
        assert (plugin_data / "venv" / "bin" / "python3").exists()


class TestRetryInvariant:
    def test_install_failure_removes_cached_manifest(self, fake_plugin: tuple[Path, Path, Path]) -> None:
        plugin_root, plugin_data, stub_bin = fake_plugin
        (plugin_data / "venv" / "bin").mkdir(parents=True)
        (plugin_data / "venv" / "bin" / "python3").touch()
        (plugin_data / "venv" / "bin" / "python3").chmod(0o755)
        cached = plugin_data / "pyproject.toml"
        cached.write_text('[project]\nname = "stale"\nversion = "0.0.0"\ndependencies = []\n')

        _write_uv_stub(stub_bin, uv_pip_succeeds=False)
        result = _run_install(plugin_root, plugin_data, stub_bin)

        assert result.returncode != 0
        assert not cached.exists()


class TestIdempotency:
    def test_repeat_invocation_is_noop(self, fake_plugin: tuple[Path, Path, Path]) -> None:
        plugin_root, plugin_data, stub_bin = fake_plugin
        _write_uv_stub(stub_bin)

        result1 = _run_install(plugin_root, plugin_data, stub_bin)
        assert result1.returncode == 0, result1.stderr

        # Second run under a failing uv stub — if install is re-triggered, the script fails.
        _write_uv_stub(stub_bin, uv_venv_succeeds=False)
        result2 = _run_install(plugin_root, plugin_data, stub_bin)
        assert result2.returncode == 0, result2.stderr
