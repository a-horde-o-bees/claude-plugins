"""Markdown-to-PDF conversion via WeasyPrint.

Business logic only. Reads markdown, renders HTML, applies CSS, writes
PDF. CLI dispatch lives in __main__.py; facade re-exports in __init__.py.
"""

import sys
from pathlib import Path

try:
    import markdown
    from weasyprint import HTML, CSS
except ImportError:
    print(
        "Missing dependencies: weasyprint and markdown.\n"
        "Declared in plugins/ocd/requirements.txt; install_deps.sh installs\n"
        "them into the plugin venv on SessionStart. Invoke via `ocd-run subsystems.pdf`,\n"
        "not system python3 directly.",
        file=sys.stderr,
    )
    sys.exit(1)


def generate_pdf(src: Path, dest: Path, css: Path | None = None) -> None:
    """Convert a markdown file to PDF.

    Args:
        src: Path to the .md source file.
        dest: Path for the output .pdf file.
        css: Optional path to a CSS stylesheet.
    """
    md_content = src.read_text(encoding="utf-8")

    html_body = markdown.markdown(md_content, extensions=["extra"])

    html_doc = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head><meta charset="utf-8"></head>\n'
        f'<body class="markdown-body">{html_body}</body>\n'
        '</html>'
    )

    stylesheets = [CSS(filename=str(css))] if css else []

    dest.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc).write_pdf(str(dest), stylesheets=stylesheets)
