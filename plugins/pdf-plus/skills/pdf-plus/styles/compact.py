"""Compact style preset for pdf-render.py.

Tight single-page document style — resumes, cover letters, recommendation
letters. Helvetica family, tight margins, uppercase H2 with hairline rule,
dash bullets, blue links.

Serves as the canonical example for authoring custom styles — declares every
overridable constant explicitly. A custom style module can omit any subset of
these; the renderer falls back to its built-in defaults (which match the
values below).
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm


# Fonts
BODY_FONT = "Helvetica"
BOLD_FONT = "Helvetica-Bold"
ITALIC_FONT = "Helvetica-Oblique"

# Colors
LINK_COLOR = "#0550ae"
RULE_COLOR = colors.HexColor("#d0d7de")
MUTED_COLOR = colors.HexColor("#59636e")

# Page
PAGE_SIZE = letter
PAGE_MARGIN = 1.3 * cm

# Horizontal rules
HR_THICKNESS = 0.5
H2_RULE_SPACE_AFTER = 4
BREAK_RULE_SPACE_BEFORE = 6
BREAK_RULE_SPACE_AFTER = 6

# Bullets
BULLET_CHAR = "•"
BULLET_INDENT = 14
BULLET_FONT_SIZE = 10

# Inline code — JetBrains Mono Regular (bundled under fonts/, OFL-1.1).
# JBM has a noticeably taller x-height than Courier, so 9pt visually matches
# 10pt Helvetica body. Text color intentionally unset so inline code inside a
# link inherits the link color rather than overriding it.
CODE_FONT_FILE = "fonts/JetBrainsMono-Regular.ttf"
CODE_FONT_NAME = "JetBrainsMono"
CODE_FONT_SIZE = 9
CODE_BG_COLOR = colors.HexColor("#d8dde2")

# Tables
TABLE_HEADER_BG_COLOR = colors.HexColor("#f6f8fa")
TABLE_GRID_COLOR = colors.HexColor("#d0d7de")
TABLE_FONT_SIZE = 8
TABLE_PADDING = 3


def make_styles():
    return {
        "h1": ParagraphStyle(
            name="h1", fontName=BOLD_FONT, fontSize=18, leading=22,
            spaceBefore=0, spaceAfter=4,
        ),
        "h2": ParagraphStyle(
            name="h2", fontName=BOLD_FONT, fontSize=11.5, leading=14,
            spaceBefore=12, spaceAfter=2,
        ),
        "h3": ParagraphStyle(
            name="h3", fontName=BOLD_FONT, fontSize=11.5, leading=14,
            spaceBefore=10, spaceAfter=2,
        ),
        "h4": ParagraphStyle(
            name="h4", fontName=BOLD_FONT, fontSize=10, leading=13,
            spaceBefore=8, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            name="body", fontName=BODY_FONT, fontSize=10, leading=14,
            spaceBefore=8, spaceAfter=8,
        ),
        "bullet_text": ParagraphStyle(
            name="bullet_text", fontName=BODY_FONT, fontSize=10, leading=14,
            spaceBefore=4, spaceAfter=4,
        ),
    }
