"""PDF subsystem CLI.

Presentation layer: argument parsing and dispatch. Business logic
lives in _generate.py and is exposed via the package facade.

Usage:
    ocd-run subsystems.pdf --src file.md [--css style.css] [--dest output.pdf]
"""

import argparse
import sys
from pathlib import Path

from . import generate_pdf


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
