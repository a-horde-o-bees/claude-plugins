"""Unit tests for convention module."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Generator

import pytest

from skills.conventions.scripts.convention import (
    _extract_pattern,
    sync_patterns,
    match_conventions,
    get_convention_content,
)


@pytest.fixture
def tmp_env() -> Generator[dict[str, str], None, None]:
    """Create temp directory with conventions dir and cache db path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        conv_dir = os.path.join(tmpdir, "conventions")
        os.makedirs(conv_dir)
        db_path = os.path.join(tmpdir, "cache.db")
        yield {"tmpdir": tmpdir, "conv_dir": conv_dir, "db_path": db_path}


def _write_convention(conv_dir: str, name: str, pattern: str, content: str = "# Test") -> str:
    path = os.path.join(conv_dir, name)
    with open(path, "w") as f:
        f.write(f'---\npattern: "{pattern}"\n---\n\n{content}\n')
    return path


class TestExtractPattern:
    def test_extracts_pattern_from_frontmatter(self, tmp_env: dict[str, str]) -> None:
        path = _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        assert _extract_pattern(path) == "*.py"

    def test_returns_none_without_frontmatter(self, tmp_env: dict[str, str]) -> None:
        path = os.path.join(tmp_env["conv_dir"], "no_front.md")
        with open(path, "w") as f:
            f.write("# No Frontmatter\nContent.\n")
        assert _extract_pattern(path) is None

    def test_returns_none_for_missing_pattern_field(self, tmp_env: dict[str, str]) -> None:
        path = os.path.join(tmp_env["conv_dir"], "no_pattern.md")
        with open(path, "w") as f:
            f.write("---\nname: test\n---\n\n# Content\n")
        assert _extract_pattern(path) is None

    def test_handles_single_quoted_pattern(self, tmp_env: dict[str, str]) -> None:
        path = os.path.join(tmp_env["conv_dir"], "single.md")
        with open(path, "w") as f:
            f.write("---\npattern: '*.py'\n---\n\n# Content\n")
        assert _extract_pattern(path) == "*.py"

    def test_handles_unquoted_pattern(self, tmp_env: dict[str, str]) -> None:
        path = os.path.join(tmp_env["conv_dir"], "unquoted.md")
        with open(path, "w") as f:
            f.write("---\npattern: *.py\n---\n\n# Content\n")
        assert _extract_pattern(path) == "*.py"

    def test_returns_none_for_nonexistent_file(self) -> None:
        assert _extract_pattern("/nonexistent/file.md") is None


class TestSyncPatterns:
    def test_syncs_new_files(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        _write_convention(tmp_env["conv_dir"], "cli.md", "*_cli.*")

        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        names = {os.path.basename(k): v for k, v in patterns.items()}
        assert names == {"python.md": "*.py", "cli.md": "*_cli.*"}

    def test_uses_cache_on_second_call(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        patterns1 = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])
        patterns2 = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        assert patterns1 == patterns2

    def test_removes_stale_cache_entries(self, tmp_env: dict[str, str]) -> None:
        path = _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        os.remove(path)
        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        assert len(patterns) == 0

    def test_updates_changed_files(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        # Overwrite with new pattern
        _write_convention(tmp_env["conv_dir"], "python.md", "*.pyw")
        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])

        names = {os.path.basename(k): v for k, v in patterns.items()}
        assert names["python.md"] == "*.pyw"

    def test_empty_directory(self, tmp_env: dict[str, str]) -> None:
        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])
        assert patterns == {}

    def test_nonexistent_directory(self, tmp_env: dict[str, str]) -> None:
        patterns = sync_patterns(
            tmp_env["db_path"], os.path.join(tmp_env["tmpdir"], "nonexistent")
        )
        assert patterns == {}

    def test_skips_files_without_pattern(self, tmp_env: dict[str, str]) -> None:
        path = os.path.join(tmp_env["conv_dir"], "no_pattern.md")
        with open(path, "w") as f:
            f.write("---\nname: test\n---\n\n# No pattern field\n")

        patterns = sync_patterns(tmp_env["db_path"], tmp_env["conv_dir"])
        assert len(patterns) == 0


class TestMatchConventions:
    def test_matches_by_extension(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.py"]
        )
        assert [os.path.basename(p) for p in matched] == ["python.md"]

    def test_matches_by_filename(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "skill.md", "SKILL.md")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["SKILL.md"]
        )
        assert [os.path.basename(p) for p in matched] == ["skill.md"]

    def test_multiple_patterns_match(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        _write_convention(tmp_env["conv_dir"], "cli.md", "*_cli.*")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo_cli.py"]
        )
        names = [os.path.basename(p) for p in matched]
        assert "python.md" in names
        assert "cli.md" in names

    def test_no_match(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.js"]
        )
        assert matched == []

    def test_multiple_input_files(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")
        _write_convention(tmp_env["conv_dir"], "markdown.md", "*.md")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.py", "bar.md"]
        )
        names = [os.path.basename(p) for p in matched]
        assert "python.md" in names
        assert "markdown.md" in names

    def test_deduplicates_matches(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "python.md", "*.py")

        matched = match_conventions(
            tmp_env["conv_dir"], tmp_env["db_path"], ["foo.py", "bar.py"]
        )
        assert len(matched) == 1

    def test_cli_pattern_matches_any_extension(self, tmp_env: dict[str, str]) -> None:
        _write_convention(tmp_env["conv_dir"], "cli.md", "*_cli.*")

        for filename in ["foo_cli.py", "bar_cli.sh", "baz_cli.rb"]:
            matched = match_conventions(
                tmp_env["conv_dir"], tmp_env["db_path"], [filename]
            )
            assert len(matched) == 1, f"Expected match for {filename}"


class TestGetConventionContent:
    def test_strips_frontmatter(self, tmp_env: dict[str, str]) -> None:
        path = _write_convention(
            tmp_env["conv_dir"], "python.md", "*.py", "# Python\n\nContent here."
        )

        content = get_convention_content([path])
        assert "=== python.md ===" in content
        assert "# Python" in content
        assert "Content here." in content
        assert "pattern:" not in content
        assert "---" not in content

    def test_multiple_conventions(self, tmp_env: dict[str, str]) -> None:
        path1 = _write_convention(tmp_env["conv_dir"], "a.md", "*.py", "# A")
        path2 = _write_convention(tmp_env["conv_dir"], "b.md", "*.md", "# B")

        content = get_convention_content([path1, path2])
        assert "=== a.md ===" in content
        assert "=== b.md ===" in content

    def test_handles_missing_file(self, tmp_env: dict[str, str]) -> None:
        content = get_convention_content(["/nonexistent/file.md"])
        assert "[error: could not read file]" in content
