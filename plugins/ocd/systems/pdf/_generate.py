"""Markdown-to-PDF conversion via WeasyPrint.

Business logic only. Reads markdown, renders HTML, applies CSS, writes
PDF. CLI dispatch lives in __main__.py; facade re-exports in __init__.py.
"""

import re
import sys
from pathlib import Path

try:
    import markdown
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print(
        "Missing dependencies: weasyprint and markdown.\n"
        "Declared in plugins/ocd/pyproject.toml; install_deps.sh installs\n"
        "them into the plugin venv on SessionStart. Invoke via `ocd-run pdf`,\n"
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

    # `sane_lists` preserves explicit ordered-list starting numbers when a
    # list is split by an intervening block (e.g. a blockquote). Without it,
    # `1.…`, `2.`, `<blockquote>`, `3.`, `4.` renders as two separate lists
    # both starting at 1 — breaking numbering continuity across blockquote
    # interrupts common in PFN-style workflow docs.
    html_body = markdown.markdown(md_content, extensions=["extra", "sane_lists"])

    # WeasyPrint honors CSS `counter-reset` but not HTML `<ol start="N">`.
    # python-markdown's sane_lists extension emits the HTML attribute; we
    # translate it into an inline CSS counter-reset so the rendered PDF
    # shows the correct starting number. `list-item` is the built-in CSS
    # counter used by `list-style-type: decimal`; reset to N-1 so the
    # first li increments to N.
    html_body = re.sub(
        r'<ol start="(\d+)"',
        lambda m: f'<ol start="{m.group(1)}" style="counter-reset: list-item {int(m.group(1)) - 1}"',
        html_body,
    )

    html_doc = (
        '<!DOCTYPE html>\n'
        '<html>\n'
        '<head><meta charset="utf-8"></head>\n'
        f'<body class="markdown-body">{html_body}</body>\n'
        '</html>'
    )

    # FontConfiguration must be passed to both CSS() and write_pdf() for
    # @font-face declarations in the stylesheet to be honored. Without it,
    # WeasyPrint silently drops @font-face rules and falls back to system
    # fonts — custom fonts bundled alongside a stylesheet never load.
    font_config = FontConfiguration()
    stylesheets = (
        [CSS(filename=str(css), font_config=font_config)] if css else []
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html_doc).write_pdf(
        str(dest), stylesheets=stylesheets, font_config=font_config
    )
