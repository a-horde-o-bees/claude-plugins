"""Generate PDF from markdown using WeasyPrint.

Standalone script — no framework dependencies. Reads markdown, converts to
HTML, applies CSS, writes PDF. Replaces the Puppeteer/Chromium pipeline with
a purpose-built CSS-to-PDF engine that produces correct text layers.

Usage:
    python3 generate.py --src file.md [--css style.css] [--dest output.pdf]

If --dest is omitted, writes PDF next to the source file (same name, .pdf extension).
If --css is omitted, uses no custom styling (browser-default rendering).
"""

import argparse
import sys
from pathlib import Path

try:
    import markdown
    from weasyprint import HTML, CSS
except ImportError:
    print(
        "Missing dependencies: weasyprint and markdown.\n"
        "Install with: uv pip install weasyprint markdown",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate PDF from markdown using WeasyPrint",
    )
    parser.add_argument("--src", required=True, type=Path, help="Markdown source file")
    parser.add_argument("--css", type=Path, help="CSS stylesheet")
    parser.add_argument("--dest", type=Path, help="Output PDF path (default: next to source)")

    args = parser.parse_args(argv)

    if not args.src.exists():
        print(f"Source file not found: {args.src}", file=sys.stderr)
        return 1

    if args.css and not args.css.exists():
        print(f"CSS file not found: {args.css}", file=sys.stderr)
        return 1

    dest = args.dest or args.src.with_suffix(".pdf")

    generate_pdf(args.src, dest, args.css)
    print(f"Generated: {dest}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
