"""Unit tests for plugin._content deployment path resolution.

Regression guard: deployment paths must resolve the plugin name from
plugin.json's `name` field, not from `plugin_root.name` (the last
filesystem segment). When the plugin is installed via a marketplace
cache, the last path segment is the version (`0.0.257`), not the
plugin name — using it as plugin_name produces deployed paths like
`.claude/rules/0.0.257/` instead of `.claude/rules/ocd/`.

Covers rules, conventions, patterns, and log templates.
"""

import json
from pathlib import Path

from plugin._content import (
    deploy_conventions,
    deploy_patterns,
    deploy_rules,
    get_conventions_states,
    get_patterns_states,
    get_rules_states,
)


def _make_plugin(plugin_root: Path, plugin_name: str) -> None:
    """Create a plugin.json with the given name."""
    claude_plugin = plugin_root / ".claude-plugin"
    claude_plugin.mkdir(parents=True)
    (claude_plugin / "plugin.json").write_text(
        json.dumps({"name": plugin_name, "version": "0.0.1"}),
    )


def _write_template(plugin_root: Path, kind: str, name: str, body: str = "x") -> None:
    """Drop a template file under plugin_root/templates/<kind>/."""
    target = plugin_root / "templates" / kind
    target.mkdir(parents=True, exist_ok=True)
    (target / name).write_text(body)


class TestDeploymentPathUsesFrontmatterName:
    """Deployment paths must use plugin.json `name`, not directory basename."""

    def test_rules_deploy_to_plugin_name_subfolder(self, tmp_path: Path) -> None:
        # Simulate marketplace cache layout: .../cache/a-horde-o-bees/ocd/0.0.257
        plugin_root = tmp_path / "cache" / "a-horde-o-bees" / "ocd" / "0.0.257"
        _make_plugin(plugin_root, "ocd")
        _write_template(plugin_root, "rules", "example.md")
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        results = deploy_rules(plugin_root, project_dir)

        assert (project_dir / ".claude" / "rules" / "ocd" / "example.md").exists()
        assert not (project_dir / ".claude" / "rules" / "0.0.257").exists()
        assert results[0]["path"] == ".claude/rules/ocd/example.md"

    def test_conventions_deploy_to_plugin_name_subfolder(self, tmp_path: Path) -> None:
        plugin_root = tmp_path / "cache" / "a-horde-o-bees" / "ocd" / "0.0.257"
        _make_plugin(plugin_root, "ocd")
        _write_template(plugin_root, "conventions", "example.md")
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        results = deploy_conventions(plugin_root, project_dir)

        assert (project_dir / ".claude" / "conventions" / "ocd" / "example.md").exists()
        assert not (project_dir / ".claude" / "conventions" / "0.0.257").exists()
        assert results[0]["path"] == ".claude/conventions/ocd/example.md"

    def test_patterns_deploy_to_plugin_name_subfolder(self, tmp_path: Path) -> None:
        plugin_root = tmp_path / "cache" / "a-horde-o-bees" / "ocd" / "0.0.257"
        _make_plugin(plugin_root, "ocd")
        _write_template(plugin_root, "patterns", "example.md")
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        results = deploy_patterns(plugin_root, project_dir)

        assert (project_dir / ".claude" / "patterns" / "ocd" / "example.md").exists()
        assert not (project_dir / ".claude" / "patterns" / "0.0.257").exists()
        assert results[0]["path"] == ".claude/patterns/ocd/example.md"

    def test_rules_state_reports_plugin_name_path(self, tmp_path: Path) -> None:
        plugin_root = tmp_path / "cache" / "a-horde-o-bees" / "ocd" / "0.0.257"
        _make_plugin(plugin_root, "ocd")
        _write_template(plugin_root, "rules", "example.md")
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        results = get_rules_states(plugin_root, project_dir)

        assert results[0]["path"] == ".claude/rules/ocd/example.md"

    def test_conventions_state_reports_plugin_name_path(self, tmp_path: Path) -> None:
        plugin_root = tmp_path / "cache" / "a-horde-o-bees" / "ocd" / "0.0.257"
        _make_plugin(plugin_root, "ocd")
        _write_template(plugin_root, "conventions", "example.md")
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        results = get_conventions_states(plugin_root, project_dir)

        assert results[0]["path"] == ".claude/conventions/ocd/example.md"

    def test_patterns_state_reports_plugin_name_path(self, tmp_path: Path) -> None:
        plugin_root = tmp_path / "cache" / "a-horde-o-bees" / "ocd" / "0.0.257"
        _make_plugin(plugin_root, "ocd")
        _write_template(plugin_root, "patterns", "example.md")
        project_dir = tmp_path / "project"
        project_dir.mkdir()

        results = get_patterns_states(plugin_root, project_dir)

        assert results[0]["path"] == ".claude/patterns/ocd/example.md"
