"""Unit tests for conventions module."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from skills.conventions.scripts.conventions import (
    load_manifest,
    load_settings,
    list_patterns,
    list_matching,
    topological_order,
    validate_manifest,
)


@pytest.fixture
def tmp_env() -> Generator[dict[str, Path], None, None]:
    """Create temp directory with conventions dir, rules dir, and manifest path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        conv_dir = root / ".claude" / "ocd" / "conventions"
        conv_dir.mkdir(parents=True)
        rules_dir = root / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        manifest_path = conv_dir / "manifest.yaml"
        yield {
            "root": root,
            "conv_dir": conv_dir,
            "rules_dir": rules_dir,
            "manifest": manifest_path,
        }


def _write_manifest(
    manifest_path: Path,
    conventions: dict[str, dict],
    settings: dict[str, int | str] | None = None,
) -> None:
    """Write a manifest.yaml file with optional settings section."""
    lines = []
    if settings:
        lines.append("settings:")
        for key, value in settings.items():
            lines.append(f"  {key}: {value}")
        lines.append("")
    lines.append("conventions:")
    for path, entry in conventions.items():
        lines.append(f"  {path}:")
        lines.append(f'    pattern: "{entry.get("pattern", "*")}"')
        deps = entry.get("dependencies", [])
        deps_str = ", ".join(deps)
        lines.append(f"    dependencies: [{deps_str}]")
    manifest_path.write_text("\n".join(lines) + "\n")


def _write_file(root: Path, rel_path: str, content: str = "# Content") -> Path:
    """Write a file at a relative path under root."""
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{content}\n")
    return path


# =========================================================================
# Settings loading
# =========================================================================


class TestLoadSettings:
    def test_loads_settings(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(
            tmp_env["manifest"],
            {".claude/rules/ocd-auth.md": {"pattern": "*"}},
            settings={"lines_warn_threshold": 500, "lines_fail_threshold": 2000},
        )
        result = load_settings(tmp_env["manifest"])
        assert result["lines_warn_threshold"] == 500
        assert result["lines_fail_threshold"] == 2000

    def test_missing_settings_section(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*"},
        })
        result = load_settings(tmp_env["manifest"])
        assert result == {}

    def test_missing_manifest_file(self, tmp_env: dict[str, Path]) -> None:
        result = load_settings(tmp_env["manifest"])
        assert result == {}

    def test_settings_do_not_affect_conventions(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(
            tmp_env["manifest"],
            {".claude/rules/ocd-auth.md": {"pattern": "*", "dependencies": []}},
            settings={"lines_warn_threshold": 500},
        )
        conventions_result = load_manifest(tmp_env["manifest"])
        assert len(conventions_result) == 1
        assert conventions_result[".claude/rules/ocd-auth.md"]["pattern"] == "*"


# =========================================================================
# Manifest loading
# =========================================================================


class TestLoadManifest:
    def test_loads_manifest(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*", "dependencies": []},
            ".claude/ocd/conventions/python.md": {"pattern": "*.py", "dependencies": [".claude/rules/ocd-auth.md"]},
        })
        result = load_manifest(tmp_env["manifest"])
        assert len(result) == 2
        assert result[".claude/rules/ocd-auth.md"]["pattern"] == "*"
        assert result[".claude/ocd/conventions/python.md"]["dependencies"] == [".claude/rules/ocd-auth.md"]

    def test_missing_manifest(self, tmp_env: dict[str, Path]) -> None:
        with pytest.raises(FileNotFoundError):
            load_manifest(tmp_env["manifest"])

    def test_empty_manifest(self, tmp_env: dict[str, Path]) -> None:
        tmp_env["manifest"].write_text("conventions:\n")
        result = load_manifest(tmp_env["manifest"])
        assert result == {}


# =========================================================================
# Pattern listing
# =========================================================================


class TestListPatterns:
    def test_lists_all(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*"},
            ".claude/ocd/conventions/python.md": {"pattern": "*.py"},
        })
        result = list_patterns(tmp_env["manifest"])
        assert len(result) == 2
        assert result[0] == (".claude/ocd/conventions/python.md", "*.py")
        assert result[1] == (".claude/rules/ocd-auth.md", "*")

    def test_empty(self, tmp_env: dict[str, Path]) -> None:
        tmp_env["manifest"].write_text("conventions:\n")
        assert list_patterns(tmp_env["manifest"]) == []


# =========================================================================
# File matching
# =========================================================================


class TestListMatching:
    def test_matches_by_extension(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/ocd/conventions/python.md": {"pattern": "*.py"},
        })
        result = list_matching(tmp_env["manifest"], ["foo.py"])
        assert "foo.py" in result
        assert ".claude/ocd/conventions/python.md" in result["foo.py"]

    def test_matches_by_filename(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/ocd/conventions/skill.md": {"pattern": "SKILL.md"},
        })
        result = list_matching(tmp_env["manifest"], ["SKILL.md"])
        assert "SKILL.md" in result

    def test_multiple_conventions_match(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/ocd/conventions/python.md": {"pattern": "*.py"},
            ".claude/ocd/conventions/cli.md": {"pattern": "*_cli.*"},
        })
        result = list_matching(tmp_env["manifest"], ["foo_cli.py"])
        assert len(result["foo_cli.py"]) == 2

    def test_no_match(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/ocd/conventions/python.md": {"pattern": "*.py"},
        })
        result = list_matching(tmp_env["manifest"], ["foo.js"])
        assert result == {}

    def test_wildcard_matches_everything(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*"},
        })
        result = list_matching(tmp_env["manifest"], ["anything.txt"])
        assert "anything.txt" in result

    def test_multiple_files(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/ocd/conventions/python.md": {"pattern": "*.py"},
            ".claude/ocd/conventions/markdown.md": {"pattern": "*.md"},
        })
        result = list_matching(tmp_env["manifest"], ["foo.py", "bar.md"])
        assert len(result) == 2


# =========================================================================
# Topological ordering
# =========================================================================


class TestTopologicalOrder:
    def test_single_root(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*", "dependencies": []},
        })
        levels = topological_order(tmp_env["manifest"])
        assert len(levels) == 1
        assert levels[0] == [".claude/rules/ocd-auth.md"]

    def test_two_independent_roots(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-a.md": {"pattern": "*", "dependencies": []},
            ".claude/rules/ocd-b.md": {"pattern": "*", "dependencies": []},
        })
        levels = topological_order(tmp_env["manifest"])
        assert len(levels) == 1
        assert len(levels[0]) == 2

    def test_linear_chain(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-a.md": {"pattern": "*", "dependencies": []},
            ".claude/ocd/conventions/b.md": {"pattern": "*.b", "dependencies": [".claude/rules/ocd-a.md"]},
            ".claude/ocd/conventions/c.md": {"pattern": "*.c", "dependencies": [".claude/ocd/conventions/b.md"]},
        })
        levels = topological_order(tmp_env["manifest"])
        assert len(levels) == 3
        assert levels[0] == [".claude/rules/ocd-a.md"]
        assert levels[1] == [".claude/ocd/conventions/b.md"]
        assert levels[2] == [".claude/ocd/conventions/c.md"]

    def test_diamond_dependency(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-a.md": {"pattern": "*", "dependencies": []},
            ".claude/ocd/conventions/b.md": {"pattern": "*.b", "dependencies": [".claude/rules/ocd-a.md"]},
            ".claude/ocd/conventions/c.md": {"pattern": "*.c", "dependencies": [".claude/rules/ocd-a.md"]},
            ".claude/ocd/conventions/d.md": {"pattern": "*.d", "dependencies": [".claude/ocd/conventions/b.md", ".claude/ocd/conventions/c.md"]},
        })
        levels = topological_order(tmp_env["manifest"])
        assert len(levels) == 3
        assert levels[0] == [".claude/rules/ocd-a.md"]
        assert sorted(levels[1]) == [".claude/ocd/conventions/b.md", ".claude/ocd/conventions/c.md"]
        assert levels[2] == [".claude/ocd/conventions/d.md"]

    def test_detects_cycle(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/ocd/conventions/a.md": {"pattern": "*.a", "dependencies": [".claude/ocd/conventions/b.md"]},
            ".claude/ocd/conventions/b.md": {"pattern": "*.b", "dependencies": [".claude/ocd/conventions/a.md"]},
        })
        with pytest.raises(ValueError, match="cycle"):
            topological_order(tmp_env["manifest"])

    def test_missing_dependency(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-a.md": {"pattern": "*", "dependencies": [".claude/rules/nonexistent.md"]},
        })
        with pytest.raises(ValueError, match="nonexistent"):
            topological_order(tmp_env["manifest"])

    def test_empty_manifest(self, tmp_env: dict[str, Path]) -> None:
        tmp_env["manifest"].write_text("conventions:\n")
        assert topological_order(tmp_env["manifest"]) == []

    def test_deterministic_ordering(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-z.md": {"pattern": "*", "dependencies": []},
            ".claude/rules/ocd-a.md": {"pattern": "*", "dependencies": []},
            ".claude/rules/ocd-m.md": {"pattern": "*", "dependencies": []},
        })
        levels = topological_order(tmp_env["manifest"])
        assert levels[0] == sorted(levels[0])


# =========================================================================
# Manifest validation
# =========================================================================


class TestValidateManifest:
    def test_all_present(self, tmp_env: dict[str, Path]) -> None:
        _write_file(tmp_env["root"], ".claude/rules/ocd-auth.md")
        _write_file(tmp_env["root"], ".claude/ocd/conventions/python.md")
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*"},
            ".claude/ocd/conventions/python.md": {"pattern": "*.py"},
        })
        result = validate_manifest(tmp_env["manifest"])
        assert result["missing"] == []
        assert result["untracked"] == []

    def test_missing_file(self, tmp_env: dict[str, Path]) -> None:
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*"},
        })
        result = validate_manifest(tmp_env["manifest"])
        assert ".claude/rules/ocd-auth.md" in result["missing"]

    def test_untracked_file(self, tmp_env: dict[str, Path]) -> None:
        _write_file(tmp_env["root"], ".claude/ocd/conventions/extra.md")
        _write_manifest(tmp_env["manifest"], {
            ".claude/rules/ocd-auth.md": {"pattern": "*"},
        })
        result = validate_manifest(tmp_env["manifest"])
        assert ".claude/ocd/conventions/extra.md" in result["untracked"]

    def test_manifest_itself_not_untracked(self, tmp_env: dict[str, Path]) -> None:
        """manifest.yaml should not appear as untracked (it's not .md)."""
        _write_manifest(tmp_env["manifest"], {})
        result = validate_manifest(tmp_env["manifest"])
        assert result["untracked"] == []
