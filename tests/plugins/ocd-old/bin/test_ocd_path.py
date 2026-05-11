"""Tests for `ocd-path` — the bin that returns absolute paths to system CLAUDE.md files in the current cache.

`ocd-path <system>` is invoked from deployed shim SKILL.md files via Claude Code's `!`...`` preprocessing. The shim body is `Call: !`ocd-path <system>``; the resolved path lets the agent Read the cached CLAUDE.md, with relative paths inside that file resolving against the cache. Plugin upgrades flow through automatically because the next invocation re-runs `ocd-path` against the new cache version.

Tests use a synthetic plugin tree fixture rather than the real plugin source so they're fully isolated from drift.
"""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

PLUGIN_ROOT_PATH = Path(__file__).resolve().parents[4] / "plugins" / "ocd"
OCD_PATH_SH = PLUGIN_ROOT_PATH / "bin" / "ocd-path"


@pytest.fixture
def fake_plugin(tmp_path: Path) -> Path:
    """Synthetic plugin tree with bin/ocd-path copied in and two systems (one with CLAUDE.md, one without)."""
    plugin_root = tmp_path / "plugin"
    (plugin_root / ".claude-plugin").mkdir(parents=True)
    (plugin_root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "test-plugin", "version": "0.0.1"}),
    )
    (plugin_root / "bin").mkdir()
    shutil.copy(OCD_PATH_SH, plugin_root / "bin" / "ocd-path")
    (plugin_root / "bin" / "ocd-path").chmod(0o755)
    (plugin_root / "systems" / "haspath").mkdir(parents=True)
    (plugin_root / "systems" / "haspath" / "CLAUDE.md").write_text("# haspath\n\nTest system.\n")
    (plugin_root / "systems" / "nopath").mkdir(parents=True)
    return plugin_root


def _run(plugin_root: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [str(plugin_root / "bin" / "ocd-path"), *args],
        capture_output=True,
        text=True,
    )


class TestSuccessfulResolution:
    def test_returns_absolute_path_to_system_claude_md(self, fake_plugin: Path) -> None:
        result = _run(fake_plugin, "haspath")

        assert result.returncode == 0, result.stderr
        assert result.stdout.strip() == str(fake_plugin / "systems" / "haspath" / "CLAUDE.md")
        assert result.stderr == ""


class TestErrorPaths:
    def test_missing_system_argument_errors(self, fake_plugin: Path) -> None:
        result = _run(fake_plugin)

        assert result.returncode != 0
        assert "ocd-path" in result.stderr.lower() or "usage" in result.stderr.lower()

    def test_unknown_system_errors(self, fake_plugin: Path) -> None:
        result = _run(fake_plugin, "nosuchsystem")

        assert result.returncode != 0
        assert "nosuchsystem" in result.stderr

    def test_system_without_claude_md_errors(self, fake_plugin: Path) -> None:
        result = _run(fake_plugin, "nopath")

        assert result.returncode != 0
        assert "nopath" in result.stderr
        assert "CLAUDE.md" in result.stderr


class TestPluginRootResolution:
    def test_errors_when_not_in_plugin_tree(self, tmp_path: Path) -> None:
        """ocd-path placed outside any plugin tree refuses with a clear marker-not-found message."""
        bare_bin = tmp_path / "bin"
        bare_bin.mkdir()
        shutil.copy(OCD_PATH_SH, bare_bin / "ocd-path")
        (bare_bin / "ocd-path").chmod(0o755)

        result = subprocess.run(
            [str(bare_bin / "ocd-path"), "anything"],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0
        assert ".claude-plugin" in result.stderr or "plugin tree" in result.stderr.lower()
