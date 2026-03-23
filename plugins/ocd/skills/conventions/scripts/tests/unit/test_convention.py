"""Unit tests for conventions module."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from skills.conventions.scripts.conventions import (
    _extract_pattern,
    sync_patterns,
    match_conventions,
    collect_rules,
)


@pytest.fixture
def tmp_env() -> Generator[dict[str, Path], None, None]:
    """Create temp directory with conventions dir, rules dir, and cache db path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        conv_dir = root / "conventions"
        conv_dir.mkdir()
        rules_dir = root / "rules"
        rules_dir.mkdir()
        db_path = root / "cache.db"
        yield {
            "tmpdir": root,
            "conv_dir": conv_dir,
            "rules_dir": rules_dir,
            "db_path": db_path,
        }


def _write_convention(conv_dir: Path, name: str, pattern: str, content: str = "# Test") -> Path:
    path = conv_dir / name
    path.write_text(f'---\npattern: "{pattern}"\n---\n\n{content}\n')
    return path


def _write_rule(rules_dir: Path, name: str, content: str = "# Rule") -> Path:
    path = rules_dir / name
    path.write_text(f"{content}\n")
    return path


class TestExtractPattern:
    def test_extracts_pattern_from_frontmatter(self, tmp_env: dict[str, Path]) -> None:
        path = _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        assert _extract_pattern(path) == "*.py"

    def test_returns_none_without_frontmatter(self, tmp_env: dict[str, Path]) -> None:
        path = tmp_env["conv_dir"] / "no_front.md"
        path.write_text("# No Frontmatter\nContent.\n")
        assert _extract_pattern(path) is None

    def test_returns_none_for_missing_pattern_field(self, tmp_env: dict[str, Path]) -> None:
        path = tmp_env["conv_dir"] / "no_pattern.md"
        path.write_text("---\nname: test\n---\n\n# Content\n")
        assert _extract_pattern(path) is None

    def test_handles_single_quoted_pattern(self, tmp_env: dict[str, Path]) -> None:
        path = tmp_env["conv_dir"] / "single.md"
        path.write_text("---\npattern: '*.py'\n---\n\n# Content\n")
        assert _extract_pattern(path) == "*.py"

    def test_handles_unquoted_pattern(self, tmp_env: dict[str, Path]) -> None:
        path = tmp_env["conv_dir"] / "unquoted.md"
        path.write_text("---\npattern: *.py\n---\n\n# Content\n")
        assert _extract_pattern(path) == "*.py"

    def test_returns_none_for_nonexistent_file(self) -> None:
        assert _extract_pattern(Path("/nonexistent/file.md")) is None


class TestSyncPatterns:
    def test_syncs_new_files(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        _write_convention(tmp_env["conv_dir"], "cli.md", "*_cli.*")

        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        names = {Path(k).name: v for k, v in patterns.items()}
        assert names == {"python.md": "*.py", "cli.md": "*_cli.*"}

    def test_uses_cache_on_second_call(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        patterns1 = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])
        patterns2 = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        assert patterns1 == patterns2

    def test_removes_stale_cache_entries(self, tmp_env: dict[str, Path]) -> None:
        path = _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        path.unlink()
        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        assert len(patterns) == 0

    def test_updates_changed_files(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        # Overwrite with new pattern
        _write_convention(tmp_env["conv_dir"], "python.md", "*.pyw")
        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        names = {Path(k).name: v for k, v in patterns.items()}
        assert names["python.md"] == "*.pyw"

    def test_empty_directory(self, tmp_env: dict[str, Path]) -> None:
        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])
        assert patterns == {}

    def test_nonexistent_directory(self, tmp_env: dict[str, Path]) -> None:
        patterns = sync_patterns(
            tmp_env["db_path"], tmp_env["tmpdir"] / "nonexistent"
        )
        assert patterns == {}

    def test_skips_files_without_pattern(self, tmp_env: dict[str, Path]) -> None:
        path = tmp_env["conv_dir"] / "no_pattern.md"
        path.write_text("---\nname: test\n---\n\n# No pattern field\n")

        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])
        assert len(patterns) == 0


class TestMatchConventions:
    def test_matches_by_extension(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.py"]
        )
        assert [Path(p).name for p in matched] == ["python.md"]

    def test_matches_by_filename(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "skill.md", "SKILL.md")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["SKILL.md"]
        )
        assert [Path(p).name for p in matched] == ["skill.md"]

    def test_multiple_patterns_match(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        _write_convention(tmp_env["conv_dir"], "cli.md", "*_cli.*")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo_cli.py"]
        )
        names = [Path(p).name for p in matched]
        assert "python.md" in names
        assert "cli.md" in names

    def test_no_match(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.js"]
        )
        assert matched == []

    def test_multiple_input_files(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        _write_convention(tmp_env["conv_dir"], "markdown.md", "*.md")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.py", "bar.md"]
        )
        names = [Path(p).name for p in matched]
        assert "python.md" in names
        assert "markdown.md" in names

    def test_deduplicates_matches(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.py", "bar.py"]
        )
        assert len(matched) == 1

    def test_cli_pattern_matches_any_extension(self, tmp_env: dict[str, Path]) -> None:
        _write_convention(tmp_env["conv_dir"], "cli.md", "*_cli.*")

        for filename in ["foo_cli.py", "bar_cli.sh", "baz_cli.rb"]:
            matched = match_conventions(
                tmp_env["conv_dir"], tmp_env["db_path"], [filename]
            )
            assert len(matched) == 1, f"Expected match for {filename}"


class TestCollectRules:
    def test_collects_ocd_rules(self, tmp_env: dict[str, Path]) -> None:
        _write_rule(tmp_env["rules_dir"], "ocd-workflow.md", "# Workflow")
        _write_rule(tmp_env["rules_dir"], "ocd-agent-authoring.md", "# Agent Authoring")

        rules = collect_rules(tmp_env["rules_dir"])
        names = [Path(p).name for p in rules]
        assert names == ["ocd-agent-authoring.md", "ocd-workflow.md"]

    def test_ignores_non_ocd_rules(self, tmp_env: dict[str, Path]) -> None:
        _write_rule(tmp_env["rules_dir"], "ocd-workflow.md", "# Workflow")
        _write_rule(tmp_env["rules_dir"], "other-rule.md", "# Other")

        rules = collect_rules(tmp_env["rules_dir"])
        names = [Path(p).name for p in rules]
        assert names == ["ocd-workflow.md"]

    def test_empty_directory(self, tmp_env: dict[str, Path]) -> None:
        rules = collect_rules(tmp_env["rules_dir"])
        assert rules == []

    def test_nonexistent_directory(self, tmp_env: dict[str, Path]) -> None:
        rules = collect_rules(tmp_env["tmpdir"] / "nonexistent")
        assert rules == []
