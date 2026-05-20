#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "reportlab",
#     "markdown-it-py",
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

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter as _DEFAULT_PAGE_SIZE
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable, ListFlowable, ListItem, Paragraph, SimpleDocTemplate,
    Table, TableStyle,
)


# Loaded style module and resolved paragraph styles. Populated in load_style().
STYLE_MOD: ModuleType | None = None
STYLES: dict[str, ParagraphStyle] = {}

# CLI-controlled rendering options.
STRIP_LOCAL_LINKS: bool = False
REWRITE_MD_LINKS: bool = True

# Targets of `[label](*.md)` → `[label](*.pdf)` rewrites, accumulated during
# inline_format(). Checked at end of render to warn about missing companion PDFs.
REWRITTEN_PDF_TARGETS: set[str] = set()


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

    _register_style_fonts(styles_dir.parent)


def _register_style_fonts(skill_base: Path) -> None:
    """Register TTF fonts the style declares. Currently only inline code:
    `CODE_FONT_FILE` (path; relative to skill base if not absolute) is
    registered under `CODE_FONT_NAME`. Missing file aborts with a clear error
    rather than silently falling back, so a typo doesn't render a broken PDF.
    """
    code_file = _s("CODE_FONT_FILE")
    code_name = _s("CODE_FONT_NAME")
    if not code_file or not code_name:
        return
    font_path = Path(code_file)
    if not font_path.is_absolute():
        font_path = skill_base / font_path
    if not font_path.exists():
        print(
            f"Error: CODE_FONT_FILE points to missing file: {font_path}",
            file=sys.stderr,
        )
        sys.exit(2)
    pdfmetrics.registerFont(TTFont(code_name, str(font_path)))


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

    # Local-link handling — strip and rewrite are mutually exclusive. Strip
    # takes precedence: if the user asked to drop all local links, there's no
    # point rewriting any of them first (and doing so would emit false-positive
    # missing-target warnings).
    if STRIP_LOCAL_LINKS:
        text = re.sub(
            r'\[([^\]]+)\]\((?!https?://|mailto:|#)[^)]+\)',
            r'\1',
            text,
        )
    elif REWRITE_MD_LINKS:
        # [label](X.md) → [label](X.pdf), anchors preserved. If the label text
        # itself names the .md filename (e.g. `[`foo.md`](./foo.md)`), rewrite
        # the basename in the label too so the visible text matches the target.
        # Targets accumulate for the post-render existence check.
        def _md_to_pdf(m: re.Match) -> str:
            label, target, anchor = m.group(1), m.group(2), m.group(3) or ""
            pdf_target = target[:-3] + ".pdf"
            REWRITTEN_PDF_TARGETS.add(pdf_target)
            target_basename = target.rsplit("/", 1)[-1]  # e.g. "foo.md"
            pdf_basename = target_basename[:-3] + ".pdf"
            new_label = label.replace(target_basename, pdf_basename)
            return f"[{new_label}]({pdf_target}{anchor})"
        text = re.sub(
            r'\[([^\]]+)\]\((?!https?://|mailto:|#)([^)#]+\.md)(#[^)]*)?\)',
            _md_to_pdf,
            text,
        )

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
    # choose a font. Style overrides via CODE_* constants; minimal fallback is
    # Courier 9pt (conventional monospace), no color override, no background.
    code_font = _s("CODE_FONT_NAME", "Courier")
    code_size = _s("CODE_FONT_SIZE", 9)
    code_attrs = f'face="{code_font}" size="{code_size}"'
    code_color = _s("CODE_TEXT_COLOR")
    if code_color:
        code_attrs += f' color="{code_color}"'
    code_bg = _s("CODE_BG_COLOR")
    if code_bg:
        code_attrs += f' backColor="{code_bg}"'
    text = re.sub(
        r'`([^`]+)`',
        rf'<font {code_attrs}>\1</font>',
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


def _strip_markdown_for_measure(text: str) -> str:
    """Strip markdown markers that don't render as glyphs in the PDF, so column-
    width measurement reflects what the reader actually sees. URLs in
    `[label](url)` are the dominant source of inflation (a 60-char URL is
    invisible in the output but would otherwise dominate the desired width).
    Bold/italic/code markers contribute a few chars per occurrence — stripped
    too for consistency.
    """
    # Links — URL is invisible, only label renders. Strip first so URLs
    # containing `*` or `_` don't mis-trigger the bold/italic patterns below.
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    return text


def _compute_column_widths(
    rows: list[list[str]], available_width: float,
    font_name: str, font_size: float, pad: float,
) -> list[float]:
    """Two-pass measure-then-budget column sizing.

    Measure each column's natural width via `stringWidth`; then either grow
    proportionally if the total fits, or freeze narrow columns at their desired
    width and let wide columns wrap inside their `Paragraph` cells when total
    desired width exceeds available width. Canonical reportlab community
    pattern — see reportlab-users threads on Paragraph-cell width sizing.
    """
    ncols = len(rows[0])
    desired = [0.0] * ncols
    for row in rows:
        for i in range(ncols):
            cell = row[i] if i < len(row) else ""
            stripped = _strip_markdown_for_measure(cell)
            for line in stripped.splitlines() or [""]:
                w = pdfmetrics.stringWidth(line, font_name, font_size) + 2 * pad
                if w > desired[i]:
                    desired[i] = w
    total = sum(desired)
    if total <= available_width:
        # Natural width fits — leave at desired sizes. Caller sets hAlign=LEFT
        # so the narrower table sits against the left margin rather than the
        # default centered placement.
        return list(desired)
    # Overflow — use the full available width via the freeze-narrow /
    # wrap-wide algorithm below.
    narrow_cap = available_width / ncols * 0.6
    narrow_idx = [i for i, w in enumerate(desired) if w <= narrow_cap]
    wide_idx = [i for i in range(ncols) if i not in narrow_idx]
    narrow_total = sum(desired[i] for i in narrow_idx)
    remaining = available_width - narrow_total
    wide_total = sum(desired[i] for i in wide_idx) or 1.0
    out = list(desired)
    for i in wide_idx:
        out[i] = remaining * desired[i] / wide_total
    return out


def _table_cell_style(name: str, alignment: str, bold: bool) -> ParagraphStyle:
    """ParagraphStyle for a table cell. `alignment` is LEFT|CENTER|RIGHT."""
    font = _s("BOLD_FONT") if bold else _s("BODY_FONT")
    size = _s("TABLE_FONT_SIZE", 9)
    align_map = {"LEFT": 0, "CENTER": 1, "RIGHT": 2}
    kwargs: dict[str, Any] = {
        "name": name,
        "fontSize": size,
        "leading": size * 1.3,
        "alignment": align_map.get(alignment, 0),
    }
    if font is not None:
        kwargs["fontName"] = font
    return ParagraphStyle(**kwargs)


def _parse_table_block(
    lines: list[str], start: int
) -> tuple[list[list[str]], list[str], int] | None:
    """Parse a GFM table starting at `lines[start]` using markdown-it-py.

    Returns (rows, alignments, next_index) on success — rows[0] is the header,
    alignments is per-column LEFT|CENTER|RIGHT — or None if no table here.

    Detection: lines[start] contains '|' and lines[start+1] is a separator row
    (e.g. `|---|---|`, with optional `:` for alignment).
    """
    if start + 1 >= len(lines):
        return None
    first = lines[start].rstrip()
    second = lines[start + 1].rstrip()
    if "|" not in first:
        return None
    if not re.match(
        r'^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$',
        second,
    ):
        return None

    # Collect until blank line or a line without a pipe.
    block_lines = [first, second]
    j = start + 2
    while j < len(lines):
        nxt = lines[j].rstrip()
        if not nxt or "|" not in nxt:
            break
        block_lines.append(nxt)
        j += 1

    from markdown_it import MarkdownIt
    md_parser = MarkdownIt("commonmark").enable("table")
    tokens = md_parser.parse("\n".join(block_lines))

    rows: list[list[str]] = []
    alignments: list[str] = []
    current_row: list[str] = []
    in_header = False
    capturing = False
    cell_content = ""

    for tok in tokens:
        t = tok.type
        if t == "thead_open":
            in_header = True
        elif t == "thead_close":
            in_header = False
        elif t == "tr_open":
            current_row = []
        elif t == "tr_close":
            rows.append(current_row)
        elif t in ("th_open", "td_open"):
            capturing = True
            cell_content = ""
            if in_header:
                style_attr = str(tok.attrGet("style") or "")
                if "center" in style_attr:
                    alignments.append("CENTER")
                elif "right" in style_attr:
                    alignments.append("RIGHT")
                else:
                    alignments.append("LEFT")
        elif t in ("th_close", "td_close"):
            current_row.append(cell_content)
            capturing = False
        elif t == "inline" and capturing:
            cell_content = tok.content

    if not rows:
        return None
    return rows, alignments, j


def _build_table_flowable(rows: list[list[str]], alignments: list[str]) -> Table:
    """Reportlab Table from parsed markdown table data. rows[0] is the header.

    Column widths are equal-distributed across the available page width so wide
    tables wrap inside cells rather than overflowing the page. Style commands
    are minimal — GRID + header BACKGROUND if declared, padding, top-valign.
    """
    ncols = len(rows[0])
    data = []
    for ridx, row in enumerate(rows):
        cells = []
        for cidx in range(ncols):
            cell_text = row[cidx] if cidx < len(row) else ""
            align = alignments[cidx] if cidx < len(alignments) else "LEFT"
            style = _table_cell_style(
                name=f"_tcell_{ridx}_{cidx}",
                alignment=align,
                bold=(ridx == 0),
            )
            cells.append(Paragraph(inline_format(cell_text), style))
        data.append(cells)

    page_size = _s("PAGE_SIZE", _DEFAULT_PAGE_SIZE)
    margin = _s("PAGE_MARGIN", 36)
    avail = page_size[0] - 2 * margin

    padding = _s("TABLE_PADDING", 4)
    grid_color = _s("TABLE_GRID_COLOR", _s("RULE_COLOR", colors.grey))
    header_bg = _s("TABLE_HEADER_BG_COLOR")

    # Cell horizontal padding matches the LEFTPADDING/RIGHTPADDING in the table
    # style below; pass it into the measurement so desired widths account for it.
    cell_h_pad = padding + 2
    body_font = _s("BODY_FONT", "Helvetica")
    table_font_size = _s("TABLE_FONT_SIZE", 9)
    col_widths = _compute_column_widths(
        rows, avail, body_font, table_font_size, cell_h_pad,
    )

    cmds: list[tuple] = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), padding + 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), padding + 2),
        ("TOPPADDING", (0, 0), (-1, -1), padding),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padding),
        ("GRID", (0, 0), (-1, -1), 0.25, grid_color),
    ]
    if header_bg is not None:
        cmds.append(("BACKGROUND", (0, 0), (-1, 0), header_bg))

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(cmds))
    table.hAlign = "LEFT"  # reportlab Table defaults to CENTER; we want left
    table.spaceBefore = 6
    table.spaceAfter = 6
    return table


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

        # GFM table — must precede paragraph absorption so cells aren't eaten.
        table_result = _parse_table_block(lines, i)
        if table_result is not None:
            rows, alignments, j = table_result
            flowables.append(_build_table_flowable(rows, alignments))
            i = j
            continue

        # Plain paragraph — consume continuation lines until blank or block element
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if not nxt or re.match(r'^(#|---+\s*$|- |\|)', nxt):
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
    ap.add_argument(
        "--no-rewrite-md-links", action="store_true",
        help="Disable the default rewrite of [label](*.md) link targets to "
             "[label](*.pdf). Use when rendering markdown that should keep its "
             "original .md link targets in the PDF (rare).",
    )
    ap.add_argument(
        "--strip-local-links", action="store_true",
        help="Strip links whose target is a local file (not http(s)/mailto/#anchor) "
             "down to plain label text. Escape hatch for cases where the recipient "
             "won't have any companion files — runs AFTER md→pdf rewrite, so it "
             "also catches rewritten targets.",
    )
    args = ap.parse_args()

    global STRIP_LOCAL_LINKS, REWRITE_MD_LINKS
    STRIP_LOCAL_LINKS = args.strip_local_links
    REWRITE_MD_LINKS = not args.no_rewrite_md_links

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

    _warn_missing_pdf_targets(Path(args.dest))


def _warn_missing_pdf_targets(dest_pdf: Path) -> None:
    """For each [label](*.md) → [label](*.pdf) rewrite, check whether the
    target PDF actually exists at the location a viewer would resolve. Missing
    targets emit a stderr warning — informational only, since a sibling render
    later in the same batch may produce them. Definitive check is the separate
    pdf-link-check.py script run post-batch.
    """
    if not REWRITTEN_PDF_TARGETS:
        return
    dest_dir = dest_pdf.parent
    missing = []
    for target in sorted(REWRITTEN_PDF_TARGETS):
        # Strip any anchor (already not in the captured target, but be safe).
        bare = target.split("#", 1)[0]
        path = Path(bare)
        if not path.is_absolute():
            path = dest_dir / path
        if not path.exists():
            missing.append(target)
    if missing:
        print(
            f"Warning: {dest_pdf.name} links to local PDFs not (yet) present:",
            file=sys.stderr,
        )
        for t in missing:
            print(f"  - {t}", file=sys.stderr)


if __name__ == "__main__":
    main()
