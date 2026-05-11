"""Tests for the pdf system — generate_pdf facade + __main__ CLI dispatch.

Tests exercise real WeasyPrint rendering and real argparse dispatch.
WeasyPrint and markdown are installed into the plugin venv by
`install_deps.sh`; CI bootstraps the same venv before running pytest,
so no skip guard is needed.
"""

from pathlib import Path

import pytest

from systems.pdf import generate_pdf
from systems.pdf.__main__ import main


class TestGeneratePdf:
    def test_produces_pdf_file(self, tmp_path: Path):
        src = tmp_path / "doc.md"
        src.write_text("# Title\n\nBody paragraph.\n")
        dest = tmp_path / "doc.pdf"

        generate_pdf(src, dest)

        assert dest.exists()
        assert dest.read_bytes().startswith(b"%PDF-")

    def test_creates_missing_parent_directory(self, tmp_path: Path):
        """Destination parent is created so callers don't have to pre-mkdir."""
        src = tmp_path / "doc.md"
        src.write_text("# Title\n")
        dest = tmp_path / "nested" / "sub" / "doc.pdf"

        generate_pdf(src, dest)

        assert dest.exists()

    def test_applies_css_when_provided(self, tmp_path: Path):
        src = tmp_path / "doc.md"
        src.write_text("# Styled\n")
        css = tmp_path / "style.css"
        css.write_text("body { color: red; }\n")
        dest = tmp_path / "doc.pdf"

        generate_pdf(src, dest, css)

        assert dest.exists()
        assert dest.read_bytes().startswith(b"%PDF-")


class TestCliDispatch:
    def test_exits_1_when_source_missing(self, tmp_path: Path, capsys):
        exit_code = main(["--src", str(tmp_path / "nope.md")])

        assert exit_code == 1
        assert "not found" in capsys.readouterr().err

    def test_exits_1_when_css_missing(self, tmp_path: Path, capsys):
        src = tmp_path / "doc.md"
        src.write_text("# Title\n")

        exit_code = main([
            "--src", str(src),
            "--css", str(tmp_path / "missing.css"),
        ])

        assert exit_code == 1
        assert "not found" in capsys.readouterr().err

    def test_defaults_dest_to_source_with_pdf_suffix(self, tmp_path: Path):
        src = tmp_path / "doc.md"
        src.write_text("# Title\n")

        exit_code = main(["--src", str(src)])

        assert exit_code == 0
        assert (tmp_path / "doc.pdf").exists()

    def test_respects_explicit_dest(self, tmp_path: Path):
        src = tmp_path / "doc.md"
        src.write_text("# Title\n")
        dest = tmp_path / "out" / "custom.pdf"

        exit_code = main(["--src", str(src), "--dest", str(dest)])

        assert exit_code == 0
        assert dest.exists()

    def test_requires_src_argument(self):
        """argparse rejects invocations without --src."""
        with pytest.raises(SystemExit):
            main([])
