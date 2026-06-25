#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf",
# ]
# ///
"""Definitive post-batch check for broken local-file PDF link annotations.

Walks one or more rendered PDFs, extracts every URI link annotation, and reports
any whose target is a local file path (not http(s)/mailto/#anchor) that doesn't
exist relative to the PDF's directory. Companion to `pdf-render.py`, which only
warns per-render (where a sibling render later in the batch may still produce
the missing target).

Usage: uv run pdf-link-check.py <pdf>... [--ignore <pattern>]

Exits 0 if all local links resolve; 1 if any are missing.
"""

import argparse
import fnmatch
import sys
from pathlib import Path

from pypdf import PdfReader


def _extract_uris(pdf_path: Path) -> list[str]:
    """All /URI link annotation values from a PDF, in page order."""
    reader = PdfReader(str(pdf_path))
    uris: list[str] = []
    for page in reader.pages:
        annots = page.get("/Annots")
        if not annots:
            continue
        for annot in annots:
            obj = annot.get_object()
            if obj.get("/Subtype") != "/Link":
                continue
            action = obj.get("/A")
            if not action:
                continue
            uri = action.get("/URI")
            if uri:
                uris.append(str(uri))
    return uris


def _is_local(uri: str) -> bool:
    return not uri.startswith(("http://", "https://", "mailto:", "#"))


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("pdfs", nargs="+", help="PDF files to check")
    ap.add_argument(
        "--ignore", action="append", default=[],
        help="Glob pattern (matched against link target) to ignore. Repeatable.",
    )
    args = ap.parse_args()

    any_missing = False
    for pdf_arg in args.pdfs:
        pdf = Path(pdf_arg)
        if not pdf.exists():
            print(f"error: PDF not found: {pdf}", file=sys.stderr)
            any_missing = True
            continue
        missing: list[str] = []
        for uri in _extract_uris(pdf):
            if not _is_local(uri):
                continue
            if any(fnmatch.fnmatch(uri, pat) for pat in args.ignore):
                continue
            bare = uri.split("#", 1)[0]
            if not bare:
                continue  # in-page #anchor; ignore
            target = Path(bare)
            if not target.is_absolute():
                target = pdf.parent / target
            if not target.exists():
                missing.append(uri)
        if missing:
            any_missing = True
            print(f"{pdf}: {len(missing)} missing local link target(s)")
            for m in missing:
                print(f"  - {m}")
        else:
            print(f"{pdf}: OK")

    return 1 if any_missing else 0


if __name__ == "__main__":
    sys.exit(main())
