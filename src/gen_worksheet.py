#!/usr/bin/env python3
"""Generate optional, consumable 12- and 24-word audit worksheets."""
import os

from reportlab.lib.colors import HexColor, black
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import vintage as V

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WARNING = "SENSITIVE: A COMPLETED WORKSHEET CAN RECONSTRUCT THE MNEMONIC ENTROPY. PROTECT OR DESTROY IT LIKE THE SEED PHRASE."


def wrap(text, c, font, size, width):
    words, lines, current = text.split(), [], ""
    for word in words:
        trial = (current + " " + word).strip()
        if not current or c.stringWidth(trial, font, size) <= width:
            current = trial
        else:
            lines.append(current); current = word
    if current:
        lines.append(current)
    return lines


def generate(path, mnemonic_words):
    page_size = landscape(A4)
    page_w, page_h = page_size
    c = canvas.Canvas(path, pagesize=page_size, invariant=1, pageCompression=1)
    c.setTitle(f"2XD8 Opposite-Fold {mnemonic_words}-Word Worksheet")
    c.setAuthor("2XD8 Entropy Booklet opposite-fold contributors")
    left, right = 10 * mm, page_w - 10 * mm
    top, bottom = page_h - 9 * mm, 9 * mm

    c.setFont("MonoB", 16); c.drawString(left, top, f"2XD8 OPPOSITE-FOLD WORKSHEET - {mnemonic_words} WORDS")
    c.setFont("Mono", 7.5); c.drawRightString(right, top, "WHITE/BLACK ARE FIXED ROLES - ACTUAL VALUES ONLY")
    y = top - 7 * mm
    c.setFillColor(HexColor("#E5E5E5")); c.rect(left, y - 10 * mm, right - left, 10 * mm, stroke=1, fill=1)
    c.setFillColor(black); c.setFont("MonoB", 7.3)
    c.drawCentredString((left + right) / 2, y - 6.2 * mm, WARNING)
    y -= 14 * mm

    headers = ["#", "W1", "B1", "CARD", "MODE", "W2", "B2", "WORD", "BIP39 INDEX"]
    widths = [9, 13, 13, 20, 28, 13, 13, 74, 31]
    widths = [value * mm for value in widths]
    scale = (right - left) / sum(widths)
    widths = [value * scale for value in widths]
    xs = [left]
    for width in widths:
        xs.append(xs[-1] + width)
    full_words = 23 if mnemonic_words == 24 else 11
    reserved = 34 * mm if mnemonic_words == 24 else 43 * mm
    row_h = min(6.0 * mm, (y - bottom - reserved) / (full_words + 1))
    table_top = y
    c.setFillColor(HexColor("#D7D7D7")); c.rect(left, y - row_h, right - left, row_h, stroke=0, fill=1)
    for col, header in enumerate(headers):
        c.setFillColor(black); c.setFont("MonoB", 7)
        c.drawCentredString((xs[col] + xs[col + 1]) / 2, y - row_h + 2.1 * mm, header)
    for row in range(1, full_words + 1):
        y0 = table_top - (row + 1) * row_h
        if row % 2 == 0:
            c.setFillColor(HexColor("#F1F1F1")); c.rect(left, y0, right - left, row_h, stroke=0, fill=1)
        c.setFillColor(black); c.setFont("Mono", 7)
        c.drawCentredString((xs[0] + xs[1]) / 2, y0 + 2.0 * mm, str(row))
    table_bottom = table_top - (full_words + 1) * row_h
    c.setStrokeColor(black)
    for row in range(full_words + 2):
        yy = table_top - row * row_h
        c.setLineWidth(.8 if row in (0, 1, full_words + 1) else .25)
        c.line(left, yy, right, yy)
    for xx in xs:
        c.setLineWidth(.6); c.line(xx, table_bottom, xx, table_top)

    y = table_bottom - 6 * mm
    c.setFont("MonoB", 9)
    if mnemonic_words == 24:
        c.drawString(left, y, "FINAL 3 ENTROPY BITS (one WHITE+BLACK pair roll; use FINAL 3 BITS table)")
        y -= 7 * mm
        c.setFont("Mono", 9)
        c.drawString(left, y, "WHITE = ______    BLACK = ______    BITS = ___")
        c.drawString(left + 120 * mm, y, "CHECKSUM BITS = ________    FINAL WORD = ____________________")
    else:
        c.drawString(left, y, "FINAL 7 ENTROPY BITS (CARD SELECT pair, then WHITE alone; no second BLACK roll)")
        y -= 7 * mm
        c.setFont("Mono", 8.5)
        c.drawString(left, y, "W1 = ____  B1 = ____  CARD = ____  MODE = __________  SECOND WHITE = ____  BITS = _______")
        y -= 7 * mm
        c.drawString(left, y, "CHECKSUM BITS = ____    FINAL 11-BIT GROUP = ___________    FINAL WORD = ____________________")
    c.setFont("MonoI", 6.8)
    c.drawRightString(right, bottom, "The worksheet is optional. Do not photograph, sync, or retain it carelessly.")
    c.save()
    print("OK worksheet ->", os.path.relpath(path, HERE))


def main():
    V.register_fonts()
    generate(os.path.join(ROOT, "2XD8_Entropy_Worksheet_24.pdf"), 24)
    generate(os.path.join(ROOT, "2XD8_Entropy_Worksheet_12.pdf"), 12)


if __name__ == "__main__":
    main()
