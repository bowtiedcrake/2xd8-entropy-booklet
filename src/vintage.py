"""Shared drawing toolkit (pure black & white), monospace/technical style."""
import os
from reportlab.lib.units import mm
from reportlab.lib.colors import black, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

INK = black
HERE = os.path.dirname(os.path.abspath(__file__))

def register_fonts(font_dir=None):
    font_dir = font_dir or os.path.join(HERE, "fonts")
    F = {
        "Mono": "UbuntuMono-R.ttf",
        "MonoB": "UbuntuMono-B.ttf",
        "MonoI": "UbuntuMono-RI.ttf",
        "MonoBI": "UbuntuMono-BI.ttf",
    }
    for k, v in F.items():
        pdfmetrics.registerFont(TTFont(k, os.path.join(font_dir, v)))

def spaced(c, x, y, text, font, size, tracking, center=True, color=INK):
    c.setFont(font, size); c.setFillColor(color)
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    cx = x - total / 2 if center else x
    for ch, w in zip(text, widths):
        c.drawString(cx, y, ch); cx += w + tracking
    return total

def double_rule(c, x1, x2, y, thick=1.4, thin=0.4, gap=1.1):
    c.setStrokeColor(INK)
    c.setLineWidth(thick); c.line(x1, y, x2, y)
    c.setLineWidth(thin);  c.line(x1, y - gap, x2, y - gap)
