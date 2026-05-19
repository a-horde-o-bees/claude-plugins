#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "reportlab",
# ]
# ///
"""Markdown to PDF via reportlab with selectable style presets.

A style module under `../styles/<name>.py` declares only the visual constants
it wants to override. Anything it doesn't declare falls through to reportlab's
library defaults. The shipped `compact` preset declares a full opinionated style;
custom presets can be as minimal as a single constant.

Usage: uv run pdf-render.py --src file.md --dest file.pdf [--style compact]
"""

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
)


# Loaded style module and resolved paragraph styles. Populated in load_style().
STYLE_MOD: ModuleType | None = None
STYLES: dict[str, ParagraphStyle] = {}


def _s(attr: str, default: Any = None) -> Any:
    """Read a style attribute from the loaded module; fall back to `default`.

    Using None as the default and conditionally passing kwargs lets reportlab's
    library defaults apply when a style is silent.
    """
    return getattr(STYLE_MOD, attr, default)


def _generic_make_styles() -> dict[str, ParagraphStyle]:
    """Minimum-sufficient paragraph styles when a style module doesn't provide
    `make_styles()`. Sizes only — no font or color opinions; reportlab's defaults
    apply (Times-Roman). Heading hierarchy is preserved by size alone.
    """
    return {
        "h1": ParagraphStyle(name="h1", fontSize=18, leading=22, spaceAfter=4),
        "h2": ParagraphStyle(name="h2", fontSize=14, leading=18, spaceBefore=10, spaceAfter=4),
        "h3": ParagraphStyle(name="h3", fontSize=12, leading=15, spaceBefore=8, spaceAfter=3),
        "h4": ParagraphStyle(name="h4", fontSize=11, leading=14, spaceBefore=6, spaceAfter=2),
        "body": ParagraphStyle(name="body", fontSize=10, leading=13, spaceAfter=6),
        "bullet_text": ParagraphStyle(name="bullet_text", fontSize=10, leading=13, spaceAfter=3),
    }


def load_style(name: str) -> None:
    """Load style preset from ../styles/<name>.py."""
    global STYLE_MOD, STYLES

    styles_dir = Path(__file__).parent.parent / "styles"
    style_file = styles_dir / f"{name}.py"
    if not style_file.exists():
        available = sorted(
            p.stem for p in styles_dir.glob("*.py")
            if not p.stem.startswith("_")
        )
        print(f"Error: style '{name}' not found at {style_file}", file=sys.stderr)
        print(
            f"Available styles: {', '.join(available) if available else '(none)'}",
            file=sys.stderr,
        )
        sys.exit(2)

    spec = importlib.util.spec_from_file_location(f"_pdfstyle_{name}", style_file)
    assert spec is not None and spec.loader is not None, f"failed to load {style_file}"
    STYLE_MOD = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(STYLE_MOD)

    if hasattr(STYLE_MOD, "make_styles"):
        STYLES = STYLE_MOD.make_styles()
    else:
        STYLES = _generic_make_styles()


def escape_xml(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def inline_format(text: str) -> str:
    """Convert inline markdown to reportlab paragraph XML.

    Order matters — links first (so URLs containing _ or * aren't mangled),
    then bold (**) before italic (*), then code spans.
    """
    text = escape_xml(text)

    # Links — apply color attribute only if LINK_COLOR is set
    link_color = _s("LINK_COLOR")
    if link_color:
        link_repl = rf'<link href="\2" color="{link_color}"><u>\1</u></link>'
    else:
        link_repl = r'<link href="\2"><u>\1</u></link>'
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_repl, text)

    # Bold **
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    # Italic *
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<i>\1</i>', text)

    # Inline code — reportlab has no native concept, so the renderer must
    # choose a font. Style overrides via CODE_FONT_NAME / CODE_FONT_SIZE; the
    # minimal fallback is Courier 9pt (conventional monospace).
    code_font = _s("CODE_FONT_NAME", "Courier")
    code_size = _s("CODE_FONT_SIZE", 9)
    text = re.sub(
        r'`([^`]+)`',
        rf'<font face="{code_font}" size="{code_size}">\1</font>',
        text,
    )
    return text


def _hr_kwargs(style_space_before: float, style_space_after: float) -> dict[str, Any]:
    """Build HRFlowable kwargs from style. spaceBefore/spaceAfter are caller-
    provided defaults specific to the rule's role; thickness/color fall through
    to reportlab when not set in the style.
    """
    kwargs: dict[str, Any] = {
        "width": "100%",
        "spaceBefore": style_space_before,
        "spaceAfter": style_space_after,
    }
    thickness = _s("HR_THICKNESS")
    if thickness is not None:
        kwargs["thickness"] = thickness
    color = _s("RULE_COLOR")
    if color is not None:
        kwargs["color"] = color
    return kwargs


def parse_markdown(md_text: str):
    """Parse markdown into a list of reportlab Flowables."""
    flowables = []
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        if not line:
            i += 1
            continue

        # H1
        m = re.match(r'^# (.+)', line)
        if m:
            flowables.append(Paragraph(inline_format(m.group(1)), STYLES["h1"]))
            i += 1
            continue

        # H2 — uppercase + hairline rule below
        m = re.match(r'^## (.+)', line)
        if m:
            flowables.append(Paragraph(inline_format(m.group(1).upper()), STYLES["h2"]))
            flowables.append(HRFlowable(**_hr_kwargs(
                style_space_before=0,
                style_space_after=_s("H2_RULE_SPACE_AFTER", 0),
            )))
            i += 1
            continue

        # H3
        m = re.match(r'^### (.+)', line)
        if m:
            flowables.append(Paragraph(inline_format(m.group(1)), STYLES["h3"]))
            i += 1
            continue

        # H4
        m = re.match(r'^#### (.+)', line)
        if m:
            flowables.append(Paragraph(inline_format(m.group(1)), STYLES["h4"]))
            i += 1
            continue

        # Bulleted list
        if re.match(r'^- ', line):
            items = []
            while i < len(lines) and re.match(r'^- ', lines[i].rstrip()):
                item_text = re.sub(r'^- ', '', lines[i].rstrip())
                j = i + 1
                while j < len(lines) and lines[j].startswith("  "):
                    item_text += " " + lines[j].strip()
                    j += 1
                items.append(ListItem(
                    Paragraph(inline_format(item_text), STYLES["bullet_text"]),
                ))
                i = j

            list_kwargs: dict[str, Any] = {"bulletType": "bullet"}
            bullet_char = _s("BULLET_CHAR")
            if bullet_char is not None:
                list_kwargs["start"] = bullet_char
            bullet_indent = _s("BULLET_INDENT")
            if bullet_indent is not None:
                list_kwargs["leftIndent"] = bullet_indent
            body_font = _s("BODY_FONT")
            if body_font is not None:
                list_kwargs["bulletFontName"] = body_font
            bullet_font_size = _s("BULLET_FONT_SIZE")
            if bullet_font_size is not None:
                list_kwargs["bulletFontSize"] = bullet_font_size
            flowables.append(ListFlowable(items, **list_kwargs))
            continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line):
            flowables.append(HRFlowable(**_hr_kwargs(
                style_space_before=_s("BREAK_RULE_SPACE_BEFORE", 0),
                style_space_after=_s("BREAK_RULE_SPACE_AFTER", 0),
            )))
            i += 1
            continue

        # Plain paragraph — consume continuation lines until blank or block element
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt or re.match(r'^(#|---+\s*$|- )', nxt):
                break
            para_lines.append(nxt)
            i += 1
        para_text = " ".join(para_lines)
        flowables.append(Paragraph(inline_format(para_text), STYLES["body"]))

    return flowables


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dest", required=True)
    ap.add_argument(
        "--style", default="compact",
        help="Style preset name from styles/<name>.py (default: compact)",
    )
    args = ap.parse_args()

    load_style(args.style)

    md_text = Path(args.src).read_text()
    flowables = parse_markdown(md_text)

    # SimpleDocTemplate kwargs — pass-through style; reportlab defaults apply when silent.
    doc_kwargs: dict[str, Any] = {"title": Path(args.src).stem}
    page_size = _s("PAGE_SIZE")
    if page_size is not None:
        doc_kwargs["pagesize"] = page_size
    page_margin = _s("PAGE_MARGIN")
    if page_margin is not None:
        doc_kwargs["leftMargin"] = page_margin
        doc_kwargs["rightMargin"] = page_margin
        doc_kwargs["topMargin"] = page_margin
        doc_kwargs["bottomMargin"] = page_margin

    doc = SimpleDocTemplate(args.dest, **doc_kwargs)
    doc.build(flowables)
    print(f"Generated: {args.dest}")


if __name__ == "__main__":
    main()
