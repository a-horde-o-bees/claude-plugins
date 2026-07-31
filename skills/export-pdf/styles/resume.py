"""Resume style preset for pdf-render.py.

Derived from compact; differs only in h3, restyled as a resume entry
heading (company + date-range line): roman base font at 11pt so inline
**bold** / *italic* markers control weight and slant — `### **Company** -
*dates*` renders bold company, light oblique dates. All-bold h3 headings
should use compact instead.
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
            name="h3", fontName=BODY_FONT, fontSize=11, leading=14,
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
