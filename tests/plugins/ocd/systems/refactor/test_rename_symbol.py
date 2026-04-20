"""Unit tests for the rename_symbol codemod.

Exercises the AST-aware rename on synthetic Python source and verifies
that identifiers in code are rewritten while string literals, comments,
and unrelated tokens are preserved. These tests catch the exact
false-positive class that burned a live rename session — a regex-based
rename converting `plugin.json` (a filename literal) into
`framework.json` — so a future regression is surfaced immediately.
"""

from pathlib import Path

import pytest

from refactor._rename_symbol import rename_symbol_in_file, rename_symbol_in_scope


@pytest.fixture
def scratch(tmp_path: Path) -> Path:
    return tmp_path


class TestRenameImport:
    def test_bare_import(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("import plugin\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert result.rewritten
        assert f.read_text() == "import framework\n"

    def test_import_with_alias(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("import plugin as p\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert result.rewritten
        assert f.read_text() == "import framework as p\n"

    def test_from_import(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("from plugin import get_project_dir\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert result.rewritten
        assert f.read_text() == "from framework import get_project_dir\n"

    def test_from_submodule_import(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("from plugin.sub import thing\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert result.rewritten
        assert f.read_text() == "from framework.sub import thing\n"


class TestRenameAttributeAccess:
    def test_dot_access(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("import plugin\nx = plugin.get_project_dir()\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert result.rewritten
        assert "framework.get_project_dir()" in f.read_text()

    def test_nested_attribute(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("import plugin\ny = plugin.NotReadyError('msg')\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert result.rewritten
        assert "framework.NotReadyError('msg')" in f.read_text()


class TestFalsePositivesNotTouched:
    def test_string_literal_filename_unchanged(self, scratch: Path) -> None:
        """`plugin.json` inside a string must not become `framework.json`."""
        f = scratch / "mod.py"
        f.write_text('path = ".claude-plugin/plugin.json"\n')
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert not result.rewritten
        assert f.read_text() == 'path = ".claude-plugin/plugin.json"\n'

    def test_comment_unchanged(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("x = 1  # uses the plugin\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert not result.rewritten
        assert f.read_text() == "x = 1  # uses the plugin\n"

    def test_unrelated_name_unchanged(self, scratch: Path) -> None:
        f = scratch / "mod.py"
        f.write_text("plugins = []\nprint(plugins)\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert not result.rewritten


class TestScopeWalk:
    def test_rewrites_all_py_files(self, scratch: Path) -> None:
        (scratch / "a.py").write_text("import plugin\n")
        (scratch / "b.py").write_text("import plugin\n")
        (scratch / "c.md").write_text("import plugin\n")  # non-py, skipped
        results = rename_symbol_in_scope("plugin", "framework", scratch)
        rewritten = [r for r in results if r.rewritten]
        assert len(rewritten) == 2
        assert (scratch / "a.py").read_text() == "import framework\n"
        assert (scratch / "b.py").read_text() == "import framework\n"
        assert (scratch / "c.md").read_text() == "import plugin\n"

    def test_skips_pycache(self, scratch: Path) -> None:
        (scratch / "__pycache__").mkdir()
        (scratch / "__pycache__" / "a.cpython-312.pyc").write_bytes(b"compiled")
        (scratch / "a.py").write_text("import plugin\n")
        results = rename_symbol_in_scope("plugin", "framework", scratch)
        assert len(results) == 1
        assert results[0].file == scratch / "a.py"


class TestParseErrorNonFatal:
    def test_parse_error_reported_not_raised(self, scratch: Path) -> None:
        f = scratch / "bad.py"
        f.write_text("def not valid python\n")
        result = rename_symbol_in_file(f, "plugin", "framework")
        assert not result.rewritten
        assert result.error is not None
        assert "parse error" in result.error
