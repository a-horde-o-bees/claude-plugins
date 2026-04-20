"""Unit tests for reference mapping."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from systems.navigator._references import (
    _parse_skill_refs,
    _parse_governance_refs,
    _classify_and_parse,
    references_map,
)


# =========================================================================
# SKILL.md parser
# =========================================================================


class TestParseSkillRefs:
    def test_extracts_backtick_paths(self, tmp_path: Path) -> None:
        """Backtick-wrapped relative paths are extracted."""
        component = tmp_path / "sub" / "_lenses.md"
        component.parent.mkdir(parents=True)
        component.write_text("# Lenses\n")

        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "## Workflow\n\n"
            f"1. Read `sub/_lenses.md`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert len(refs) == 1
        assert refs[0] == str(component.resolve())

    def test_skips_variable_paths(self, tmp_path: Path) -> None:
        """Paths with ${} substitution are CLI scripts, not file refs."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Run `${CLAUDE_PLUGIN_ROOT}/run.py systems.navigator scan`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert refs == []

    def test_skips_code_blocks(self, tmp_path: Path) -> None:
        """Paths inside fenced code blocks are not extracted."""
        component = tmp_path / "sub" / "_example.md"
        component.parent.mkdir(parents=True)
        component.write_text("# Example\n")

        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "```\n"
            "`sub/_example.md`\n"
            "```\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert refs == []

    def test_ignores_nonexistent_paths(self, tmp_path: Path) -> None:
        """References to nonexistent files are silently skipped."""
        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Read `sub/nonexistent.md`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert refs == []

    def test_missing_file(self) -> None:
        """Missing SKILL.md returns empty list."""
        refs = _parse_skill_refs("/nonexistent/SKILL.md")
        assert refs == []

    def test_multiple_refs_on_line(self, tmp_path: Path) -> None:
        """Multiple backtick paths on one line are all extracted."""
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "one.md").write_text("# One\n")
        (tmp_path / "a" / "two.md").write_text("# Two\n")

        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Read `a/one.md` and `a/two.md`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert len(refs) == 2

    def test_parent_relative_not_resolved(self, tmp_path: Path) -> None:
        """Paths to sibling directories (not beside/below) are NOT resolved."""
        skills_dir = tmp_path / "skills"
        skill_dir = skills_dir / "my-skill"
        skill_dir.mkdir(parents=True)
        shared_dir = skills_dir / "shared"
        shared_dir.mkdir()
        (shared_dir / "_common.md").write_text("# Shared\n")

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Read `shared/_common.md`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert refs == []  # not beside or below — requires env var path

    def test_plugin_root_env_var_paths(self, tmp_path: Path, monkeypatch) -> None:
        """${CLAUDE_PLUGIN_ROOT} paths resolve for file references."""
        plugin_root = tmp_path / "plugin"
        plugin_root.mkdir()
        shared = plugin_root / "skills" / "shared"
        shared.mkdir(parents=True)
        (shared / "_common.md").write_text("# Shared\n")

        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(plugin_root))

        skill_dir = plugin_root / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Read `${CLAUDE_PLUGIN_ROOT}/skills/shared/_common.md`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert len(refs) == 1
        assert refs[0] == str((shared / "_common.md").resolve())

    def test_plugin_root_skips_commands(self, tmp_path: Path, monkeypatch) -> None:
        """${CLAUDE_PLUGIN_ROOT} paths that are commands (no file ext) are skipped."""
        monkeypatch.setenv("CLAUDE_PLUGIN_ROOT", str(tmp_path))

        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Run `${CLAUDE_PLUGIN_ROOT}/run.py systems.navigator scan`\n"
        )
        refs = _parse_skill_refs(str(skill_md))
        assert refs == []


# =========================================================================
# Governance parser
# =========================================================================


class TestParseGovernanceRefs:
    def test_extracts_governed_by(self, tmp_path: Path) -> None:
        """Governance governed_by: field is returned as references."""
        gov_file = tmp_path / "rule.md"
        gov_file.write_text(
            "---\n"
            "includes: \"*.md\"\n"
            "governed_by:\n"
            "  - .claude/rules/design.md\n"
            "  - .claude/conventions/ocd/markdown.md\n"
            "---\n\n"
            "# Rule\n"
        )
        refs = _parse_governance_refs(str(gov_file))
        assert refs == [".claude/rules/design.md", ".claude/conventions/ocd/markdown.md"]

    def test_no_governed_by(self, tmp_path: Path) -> None:
        """Governance without governed_by returns empty list."""
        gov_file = tmp_path / "rule.md"
        gov_file.write_text(
            "---\n"
            "includes: \"*\"\n"
            "---\n\n"
            "# Rule\n"
        )
        refs = _parse_governance_refs(str(gov_file))
        assert refs == []

    def test_no_frontmatter(self, tmp_path: Path) -> None:
        """Non-governance file returns empty list."""
        md_file = tmp_path / "plain.md"
        md_file.write_text("# Just markdown\n")
        refs = _parse_governance_refs(str(md_file))
        assert refs == []


# =========================================================================
# Classifier
# =========================================================================


class TestClassifyAndParse:
    def test_component_is_leaf(self, tmp_path: Path) -> None:
        """Component _*.md files return no references."""
        component = tmp_path / "_lenses.md"
        component.write_text("# Lenses\n\nSome content with `path/to.md`\n")
        refs = _classify_and_parse(str(component))
        assert refs == []

    def test_skill_md_dispatches(self, tmp_path: Path) -> None:
        """SKILL.md files dispatch to skill parser."""
        (tmp_path / "ref").mkdir()
        (tmp_path / "ref" / "file.md").write_text("# Ref\n")

        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Read `ref/file.md`\n"
        )
        refs = _classify_and_parse(str(skill_md))
        assert len(refs) == 1

    def test_governance_dispatches(self, tmp_path: Path) -> None:
        """Files in .claude/rules/ dispatch to governance parser."""
        rules_dir = tmp_path / ".claude" / "rules"
        rules_dir.mkdir(parents=True)
        rule = rules_dir / "test-rule.md"
        rule.write_text(
            "---\n"
            "includes: \"*\"\n"
            "governed_by:\n"
            "  - .claude/rules/parent.md\n"
            "---\n\n"
            "# Rule\n"
        )
        refs = _classify_and_parse(str(rule))
        assert refs == [".claude/rules/parent.md"]

    def test_unknown_file_type(self, tmp_path: Path) -> None:
        """Unrecognized file types return no references."""
        other = tmp_path / "readme.md"
        other.write_text("# README\n")
        refs = _classify_and_parse(str(other))
        assert refs == []


# =========================================================================
# DAG builder
# =========================================================================


class TestMapReferences:
    def test_single_file_no_refs(self, tmp_path: Path) -> None:
        """Single file with no references returns just that file."""
        leaf = tmp_path / "_leaf.md"
        leaf.write_text("# Leaf\n")
        result = references_map([str(leaf)])
        assert result["total_files"] == 1
        assert result["files"][0]["references"] == []
        assert result["files"][0]["depth"] == 0

    def test_skill_with_components(self, tmp_path: Path) -> None:
        """SKILL.md referencing components builds a 2-level DAG."""
        (tmp_path / "sub").mkdir()
        lenses = tmp_path / "sub" / "_lenses.md"
        lenses.write_text("# Lenses\n")
        triage = tmp_path / "sub" / "_triage.md"
        triage.write_text("# Triage\n")

        skill_md = tmp_path / "SKILL.md"
        skill_md.write_text(
            "---\nname: test\n---\n\n"
            "1. Read `sub/_lenses.md`\n"
            "2. Read `sub/_triage.md`\n"
        )

        result = references_map([str(skill_md)])
        assert result["total_files"] == 3
        # Root is at depth 0
        root_entry = next(f for f in result["files"] if f["depth"] == 0)
        assert len(root_entry["references"]) == 2
        # Components are at depth 1
        depth_1 = [f for f in result["files"] if f["depth"] == 1]
        assert len(depth_1) == 2

    def test_dedup_across_roots(self, tmp_path: Path) -> None:
        """Multiple roots referencing the same file don't duplicate."""
        shared = tmp_path / "shared" / "_common.md"
        shared.parent.mkdir()
        shared.write_text("# Shared\n")

        skill_a = tmp_path / "a" / "SKILL.md"
        skill_a.parent.mkdir()
        skill_a.write_text(
            "---\nname: a\n---\n\n"
            "1. Read `../shared/_common.md`\n"
        )
        skill_b = tmp_path / "b" / "SKILL.md"
        skill_b.parent.mkdir()
        skill_b.write_text(
            "---\nname: b\n---\n\n"
            "1. Read `../shared/_common.md`\n"
        )

        result = references_map([str(skill_a), str(skill_b)])
        # 2 skills + 1 shared = 3 total, not 4
        assert result["total_files"] == 3

    def test_max_depth_respected(self, tmp_path: Path) -> None:
        """Traversal stops at max_depth."""
        # Create a chain: SKILL.md -> sub/SKILL.md -> sub/sub/SKILL.md
        # With max_depth=1, only the first level of references is followed
        (tmp_path / "sub").mkdir()
        (tmp_path / "sub" / "inner").mkdir()
        inner_ref = tmp_path / "sub" / "inner" / "_deep.md"
        inner_ref.write_text("# Deep\n")

        mid = tmp_path / "sub" / "SKILL.md"
        mid.write_text(
            "---\nname: mid\n---\n\n"
            "1. Read `inner/_deep.md`\n"
        )

        root = tmp_path / "SKILL.md"
        root.write_text(
            "---\nname: root\n---\n\n"
            f"1. Read `sub/SKILL.md`\n"
        )

        # max_depth=1 means root (depth 0) follows refs to depth 1, but depth 1 doesn't follow further
        result = references_map([str(root)], max_depth=1)
        assert result["total_files"] == 2  # root + sub/SKILL.md, not sub/inner/_deep.md

    def test_roots_preserved(self, tmp_path: Path) -> None:
        """The roots field reflects the input paths."""
        leaf = tmp_path / "_leaf.md"
        leaf.write_text("# Leaf\n")
        result = references_map([str(leaf)])
        assert result["roots"] == [str(leaf)]
