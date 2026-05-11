"""PDF subsystem — markdown to PDF via WeasyPrint.

Public surface:
    generate_pdf(src, dest, css) — one-shot conversion
"""

from ._generate import generate_pdf

__all__ = ["generate_pdf"]
