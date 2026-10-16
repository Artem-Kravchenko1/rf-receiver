"""Build template.docx (DSTU 3008-like styles) from pandoc's default reference.docx."""

import sys

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

src, dst = sys.argv[1], sys.argv[2]
doc = Document(src)

FONT = "Times New Roman"
BLACK = RGBColor(0, 0, 0)


def set_font(style, size, bold=None, italic=None):
    style.font.name = FONT
    style.font.size = Pt(size)
    style.font.color.rgb = BLACK
    if bold is not None:
        style.font.bold = bold
    if italic is not None:
        style.font.italic = italic
    rpr = style.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = rpr.makeelement(qn("w:rFonts"), {})
        rpr.append(fonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), FONT)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        fonts.attrib.pop(qn(attr), None)


def set_paragraph(style, *, align=None, indent=None, spacing=1.5, before=0, after=0):
    fmt = style.paragraph_format
    fmt.line_spacing = spacing
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    if indent is not None:
        fmt.first_line_indent = Cm(indent)
    if align is not None:
        fmt.alignment = align


styles = doc.styles


def style(name, kind=WD_STYLE_TYPE.PARAGRAPH):
    try:
        return styles[name]
    except KeyError:
        return styles.add_style(name, kind)


# page: A4, margins left 30, right 10, top/bottom 20 mm
for section in doc.sections:
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.left_margin, section.right_margin = Cm(3), Cm(1)
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)

# body text
for name in ("Normal", "Body Text", "First Paragraph"):
    s = style(name)
    set_font(s, 14)
    set_paragraph(s, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=1.25)

# headings: bold, black, with paragraph indent
for level, size in ((1, 14), (2, 14), (3, 14)):
    s = style(f"Heading {level}")
    set_font(s, size, bold=True, italic=False)
    set_paragraph(s, align=WD_ALIGN_PARAGRAPH.LEFT, indent=1.25, before=12, after=6)

# title page
for name in ("Title", "Subtitle", "Author", "Date"):
    s = style(name)
    set_font(s, 14, bold=(name == "Title"), italic=False)
    set_paragraph(s, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)

# captions: centered, no indent
for name in ("Caption", "Image Caption", "Table Caption"):
    s = style(name)
    set_font(s, 14, italic=False)
    set_paragraph(
        s, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, spacing=1.0, before=6, after=6
    )

# figures and table cells
s = style("Figure")
set_paragraph(s, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, spacing=1.0)
s = style("Captioned Figure")
set_paragraph(s, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0, spacing=1.0)
# "Compact" is used both for list items and table cells (cells get explicit alignment)
s = style("Compact")
set_font(s, 14)
set_paragraph(s, align=WD_ALIGN_PARAGRAPH.LEFT, indent=0, spacing=1.0, after=3)

# table of contents
s = style("TOC Heading")
set_font(s, 14, bold=True)
set_paragraph(s, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)

# centered helper style for the custom title page
s = style("Centered")
set_font(s, 14)
set_paragraph(s, align=WD_ALIGN_PARAGRAPH.CENTER, indent=0)

doc.save(dst)
print("saved", dst)
