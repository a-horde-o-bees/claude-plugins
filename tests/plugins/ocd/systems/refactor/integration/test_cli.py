"""Integration tests for the refactor CLI verb dispatch.

Exercises `ocd-run refactor rename-symbol` argparse + dispatch wiring
through the real bin wrapper. The AST-aware rewriter is covered in
depth by test_rename_symbol.py; this suite locks the CLI surface so
flag marshaling and exit-code contract cannot regress silently.
"""

import subprocess
from pathlib import Path


def _run(
    ocd_run: Path, *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(ocd_run), "refactor", *args],
        capture_output=True, text=True,
    )


class TestRenameSymbolVerb:
    def test_rewrites_module_references_in_scope(
        self, ocd_run: Path, tmp_path: Path,
    ):
        """rename-symbol handles import-style renames — `import X`, `from X
        import ...`, and `X.attr` access. Function definitions are out of
        scope (scope-analysis deliberately omitted)."""
        src = tmp_path / "caller.py"
        src.write_text(
            "import old_mod\n"
            "from old_mod import helper\n"
            "print(old_mod.value)\n",
        )

        result = _run(
            ocd_run,
            "rename-symbol",
            "--from", "old_mod",
            "--to", "new_mod",
            "--scope", str(tmp_path),
        )

        assert result.returncode == 0, result.stderr
        content = src.read_text()
        assert "new_mod" in content
        assert "old_mod" not in content
        assert "1 file(s) rewritten" in result.stdout

    def test_no_matches_reports_zero_rewritten(
        self, ocd_run: Path, tmp_path: Path,
    ):
        (tmp_path / "mod.py").write_text("def unrelated():\n    return 1\n")

        result = _run(
            ocd_run,
            "rename-symbol",
            "--from", "no_such_name",
            "--to", "replacement",
            "--scope", str(tmp_path),
        )

        assert result.returncode == 0, result.stderr
        assert "0 file(s) rewritten" in result.stdout

    def test_missing_from_exits_nonzero(self, ocd_run: Path, tmp_path: Path):
        result = _run(
            ocd_run,
            "rename-symbol",
            "--to", "new_name",
            "--scope", str(tmp_path),
        )
        assert result.returncode != 0

    def test_missing_to_exits_nonzero(self, ocd_run: Path, tmp_path: Path):
        result = _run(
            ocd_run,
            "rename-symbol",
            "--from", "old_name",
            "--scope", str(tmp_path),
        )
        assert result.returncode != 0

    def test_invalid_scope_exits_1(self, ocd_run: Path, tmp_path: Path):
        result = _run(
            ocd_run,
            "rename-symbol",
            "--from", "old_name",
            "--to", "new_name",
            "--scope", str(tmp_path / "does_not_exist"),
        )
        assert result.returncode == 1
        assert "not a directory" in result.stderr

    def test_missing_verb_exits_nonzero(self, ocd_run: Path):
        result = subprocess.run(
            [str(ocd_run), "refactor"],
            capture_output=True, text=True,
        )
        assert result.returncode != 0
