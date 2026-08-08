#!/usr/bin/env python3
"""Generate the Easy and Compact opposite-complement-fold booklets."""
import os
from collections import Counter

from reportlab.lib.colors import HexColor, black, white
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

import fold_mapping as F
import vintage as V

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORDS = open(os.path.join(HERE, "english.txt"), encoding="utf-8").read().split()

EASY_OUT = os.path.join(ROOT, "2XD8_Entropy_Booklet_OppositeFold_Easy.pdf")
COMPACT_OUT = os.path.join(ROOT, "2XD8_Entropy_Booklet_OppositeFold_Compact.pdf")

PAGE_W, PAGE_H = A5
GRAY = HexColor("#4A4A4A")
LIGHT = HexColor("#E7E7E7")
MID = HexColor("#C9C9C9")
MARGIN_X = 7 * mm
MARGIN_TOP = 7 * mm
MARGIN_BOTTOM = 10 * mm


def fit(text, font, max_size, max_width, minimum=4.0):
    size = max_size
    while size > minimum and stringWidth(text, font, size) > max_width:
        size -= 0.25
    return size


def wrap(text, font, size, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if not current or stringWidth(trial, font, size) <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def frame(c, footer=""):
    left, right = MARGIN_X, PAGE_W - MARGIN_X
    top, bottom = PAGE_H - MARGIN_TOP, MARGIN_BOTTOM
    if footer:
        c.setFillColor(GRAY)
        c.setFont("Mono", 6.3)
        c.drawCentredString(PAGE_W / 2, 4.5 * mm, footer)
    return left, right, top, bottom


def title(c, text, subtitle=None):
    left, right, top, _ = frame(c)
    c.setFillColor(black)
    c.setFont("MonoB", 15)
    c.drawString(left, top - 7 * mm, text)
    y = top - 11 * mm
    if subtitle:
        c.setFont("MonoI", 8)
        c.setFillColor(GRAY)
        c.drawString(left, y, subtitle)
        y -= 3 * mm
    V.double_rule(c, left, right, y, thick=1.0, thin=0.35, gap=0.9)
    return y - 7 * mm


def paragraph(c, text, x, y, width, size=8.7, leading=4.25 * mm, font="Mono"):
    c.setFont(font, size)
    c.setFillColor(black)
    for line in wrap(text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y - 2 * mm


def bullet(c, marker, text, x, y, width, size=8.5):
    c.setFont("MonoB", size)
    c.drawString(x, y, marker)
    return paragraph(c, text, x + 7 * mm, y, width - 7 * mm, size=size)


def section(c, heading, items, footer="OPPOSITE-FOLD EASY GUIDE"):
    left, right, _, bottom = frame(c, footer)
    y = title(c, heading)
    for kind, text in items:
        if kind == "h":
            y -= 1.5 * mm
            c.setFillColor(black)
            c.setFont("MonoB", 10.5)
            c.drawString(left, y, text)
            y -= 5.5 * mm
        elif kind == "p":
            y = paragraph(c, text, left, y, right - left)
        elif kind == "warn":
            lines = wrap(text, "MonoB", 8.5, right - left - 7 * mm)
            height = (len(lines) * 4.2 + 6) * mm
            c.setFillColor(LIGHT)
            c.rect(left, y - height + 2 * mm, right - left, height, stroke=1, fill=1)
            c.setFillColor(black)
            c.setFont("MonoB", 8.5)
            yy = y - 2.5 * mm
            for line in lines:
                c.drawString(left + 3.5 * mm, yy, line)
                yy -= 4.2 * mm
            y -= height + 2 * mm
        elif kind == "li":
            y = bullet(c, "-", text, left, y, right - left)
        elif kind == "num":
            number, body = text.split("|", 1)
            y = bullet(c, number + ".", body, left, y, right - left)
        if y < bottom + 3 * mm:
            raise RuntimeError(f"guide page overflow: {heading}")
    c.showPage()


def draw_cover(c, edition):
    c.setFillColor(black)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    c.setFillColor(white)
    c.setFont("MonoB", 22)
    c.drawCentredString(PAGE_W / 2, 153 * mm, "2XD8 ENTROPY")
    c.drawCentredString(PAGE_W / 2, 142 * mm, "BOOKLET")
    c.setLineWidth(1.1)
    c.line(22 * mm, 134 * mm, PAGE_W - 22 * mm, 134 * mm)
    c.setFont("MonoB", 14)
    c.drawCentredString(PAGE_W / 2, 117 * mm, "OPPOSITE-COMPLEMENT FOLD")
    c.setFont("Mono", 10)
    c.drawCentredString(PAGE_W / 2, 106 * mm, edition)
    c.setFont("Mono", 8)
    c.drawCentredString(PAGE_W / 2, 75 * mm, "TWO DISTINGUISHABLE STANDARD D8 DICE")
    c.drawCentredString(PAGE_W / 2, 68 * mm, "PHYSICAL ENTROPY - OFFLINE CHECKSUM")
    c.setFont("MonoB", 8.5)
    c.drawCentredString(PAGE_W / 2, 41 * mm, "VERIFY BOTH DICE BEFORE USE")
    c.setFont("Mono", 7.5)
    c.drawCentredString(PAGE_W / 2, 34 * mm, "OPPOSITES: 1<->8  2<->7  3<->6  4<->5")
    c.setFont("Mono", 6.5)
    c.drawCentredString(PAGE_W / 2, 12 * mm, "CC0 1.0 - FOR AUDITABLE OFFLINE USE")
    c.showPage()


def draw_guide_pages(c):
    section(c, "BEFORE YOU START", [
        ("warn", "INSPECT BOTH ACTUAL DICE. Verify that opposite faces are 1<->8, 2<->7, 3<->6, and 4<->5. If either die differs, do not use this edition."),
        ("li", "Use two visually distinguishable d8 dice. Assign one permanently as WHITE and one as BLACK."),
        ("li", "Use a hard, flat rolling area or dice tray and ensure genuine tumbling."),
        ("li", "Precommit this invalid-roll rule: if either die is off-table, cocked, wedged, or unreadable, discard that entire pair roll and reroll both dice."),
        ("li", "Repeated values and apparent patterns are valid. Never selectively reroll a result because it looks suspicious."),
        ("warn", "If you lose CARD or MODE before the second roll, discard that incomplete word attempt and restart from the first pair roll."),
    ])
    section(c, "GENERATE ONE FULL WORD", [
        ("num", "1|Roll WHITE and BLACK together."),
        ("num", "2|Use the CARD SELECT table with the actual readings."),
        ("num", "3|Record both the CARD number and the full word NORMAL or MIRROR."),
        ("num", "4|Turn to exactly that CARD / MODE page."),
        ("num", "5|Roll WHITE and BLACK together again."),
        ("num", "6|Use the actual WHITE result as the row and actual BLACK result as the column."),
        ("num", "7|Read and record the printed word. The small number is its one-based BIP39 index for auditing."),
        ("warn", "There is no subtraction, binary arithmetic, modulo, or die-face conversion in this ordinary workflow."),
    ])
    section(c, "FINAL ENTROPY + CHECKSUM", [
        ("h", "24 WORDS"),
        ("p", "Generate 23 full word indices: 253 entropy bits. Then use the FINAL 3 BITS table for one additional physical WHITE+BLACK pair roll. Those 3 bits complete the 256-bit entropy."),
        ("h", "12 WORDS"),
        ("p", "Generate 11 full word indices: 121 entropy bits. Then use the FINAL 7 BITS procedure: one CARD SELECT pair roll plus one additional WHITE-only roll. Those 7 bits complete the 128-bit entropy."),
        ("h", "CHECKSUM"),
        ("p", "A deterministic offline checksum tool hashes the completed 128- or 256-bit entropy, takes the first 4 or 8 hash bits, and combines them with the final physical entropy bits to select the last word."),
        ("warn", "The checksum tool is allowed to calculate; it is not allowed to contribute randomness."),
    ])
    section(c, "WORKED EXAMPLES", [
        ("h", "NORMAL"),
        ("p", "First roll WHITE 2, BLACK 7 gives CARD 15 - NORMAL. Second roll WHITE 6, BLACK 3: turn to CARD 015 NORMAL, use actual row 6 and column 3, and read PREFER (BIP39 index 1359)."),
        ("h", "MIRROR"),
        ("p", "First roll WHITE 7, BLACK 2 gives CARD 15 - MIRROR. Second roll WHITE 3, BLACK 8: turn to CARD 015 MIRROR, use actual row 3 and column 8, and read PEACE (BIP39 index 1295)."),
        ("warn", "On a MIRROR page, actual die values are still used directly. The printed page already performs the fold."),
        ("p", "Keep WHITE and BLACK roles fixed so the mapping remains deterministic and auditable. If their identities become uncertain during a word, restart that word attempt."),
    ])
    section(c, "WHAT THE FOLD PROVES", [
        ("h", "EXACT FAIR-DICE RESULT"),
        ("p", "Every four-reading tuple is paired with the tuple obtained by replacing every face with its physical opposite. There are no fixed points. The 4,096 raw tuples therefore form 2,048 pairs, and each pair maps to one BIP39 index: exactly 2/4,096 = 1/2,048 under fair independent rolls. This proves no modulo or rejection bias."),
        ("h", "LIMITED BIAS MITIGATION"),
        ("p", "If a small imbalance is approximately antisymmetric across physical opposite faces, first-order terms from that component cancel when paired tuple probabilities are added."),
        ("p", "This does not make arbitrary biased dice perfect. Pair-symmetric bias, pair-to-pair differences, changing distributions, correlation, deterministic throwing, and weak technique can remain. Dice quality still matters. This is not a general-purpose randomness extractor."),
        ("warn", "Exact 1/2,048 output probabilities require the fair, independent-roll model."),
    ])


def selector_data():
    return [[F.selector_cell(w, b) for b in range(1, 9)] for w in range(1, 9)]


def draw_selector(c):
    left, right, top, bottom = frame(c, "ACTUAL FIRST ROLL - READ CARD AND FULL MODE")
    y = title(c, "CARD SELECT", "Rows = actual WHITE; columns = actual BLACK")
    label_w = 8 * mm
    grid_left = left + label_w
    grid_right = right
    grid_top = y - 7 * mm
    header_h = 8 * mm
    grid_bottom = bottom + 12 * mm
    row_h = (grid_top - header_h - grid_bottom) / 8
    col_w = (grid_right - grid_left) / 8

    c.setFillColor(LIGHT)
    c.rect(grid_left, grid_top - header_h, grid_right - grid_left, header_h, stroke=0, fill=1)
    for column in range(8):
        c.setFont("MonoB", 8)
        c.setFillColor(black)
        c.drawCentredString(grid_left + (column + .5) * col_w, grid_top - 5.2 * mm, str(column + 1))
    c.setFont("MonoB", 7)
    c.drawCentredString((grid_left + grid_right) / 2, grid_top + 2 * mm, "ACTUAL BLACK")

    data = selector_data()
    body_top = grid_top - header_h
    for row in range(8):
        y0 = body_top - (row + 1) * row_h
        c.setFillColor(LIGHT if row >= 4 else white)
        c.rect(grid_left, y0, grid_right - grid_left, row_h, stroke=0, fill=1)
        c.setFillColor(black)
        c.setFont("MonoB", 8)
        c.drawCentredString(left + label_w / 2, y0 + row_h / 2 - 2, str(row + 1))
        for column in range(8):
            card, mode = data[row][column]
            x = grid_left + (column + .5) * col_w
            c.setFont("MonoB", 7.2)
            c.drawCentredString(x, y0 + row_h / 2 + 1.2, f"{card:02d}")
            c.setFont("MonoB" if mode == F.MIRROR else "Mono", 5.8)
            c.drawCentredString(x, y0 + row_h / 2 - 5.2, mode)
            if mode == F.MIRROR:
                c.setLineWidth(.35)
                for hatch in range(3):
                    hx = grid_left + column * col_w + 1.5 + hatch * 3.5
                    c.line(hx, y0 + 1.2, min(hx + 3, grid_left + (column + 1) * col_w - 1), y0 + 4.2)

    c.setStrokeColor(black)
    for row in range(9):
        yy = body_top - row * row_h
        c.setLineWidth(1 if row in (0, 4, 8) else .3)
        c.line(grid_left, yy, grid_right, yy)
    for column in range(9):
        xx = grid_left + column * col_w
        c.setLineWidth(1 if column in (0, 8) else .3)
        c.line(xx, grid_bottom, xx, grid_top)
    c.setLineWidth(1.2)
    c.rect(grid_left, grid_bottom, grid_right - grid_left, grid_top - grid_bottom)
    c.saveState()
    c.translate(left + 2.5 * mm, (body_top + grid_bottom) / 2)
    c.rotate(90)
    c.setFont("MonoB", 7)
    c.drawCentredString(0, 0, "ACTUAL WHITE")
    c.restoreState()
    c.showPage()


def draw_final3(c):
    left, right, top, bottom = frame(c, "24 WORDS - PHYSICAL FINAL 3 ENTROPY BITS")
    y = title(c, "FINAL 3 BITS", "After 23 full words, roll WHITE + BLACK once")
    y = paragraph(c, "Use the actual WHITE row and actual BLACK column. Record the printed three bits. This completes all 256 entropy bits before checksum calculation.", left, y, right - left, size=8.2)
    label_w = 8 * mm
    grid_left, grid_right = left + label_w, right
    grid_top, grid_bottom = y - 6 * mm, bottom + 13 * mm
    header_h = 7 * mm
    body_top = grid_top - header_h
    row_h = (body_top - grid_bottom) / 8
    col_w = (grid_right - grid_left) / 8
    c.setFillColor(LIGHT)
    c.rect(grid_left, body_top, grid_right - grid_left, header_h, stroke=0, fill=1)
    for b in range(1, 9):
        c.setFont("MonoB", 8)
        c.setFillColor(black)
        c.drawCentredString(grid_left + (b - .5) * col_w, body_top + 2.2 * mm, str(b))
    for w in range(1, 9):
        y0 = body_top - w * row_h
        c.setFillColor(LIGHT if w > 4 else white)
        c.rect(grid_left, y0, grid_right - grid_left, row_h, stroke=0, fill=1)
        c.setFillColor(black)
        c.setFont("MonoB", 8)
        c.drawCentredString(left + label_w / 2, y0 + row_h / 2 - 2, str(w))
        for b in range(1, 9):
            c.setFont("MonoB", 8.2)
            c.drawCentredString(grid_left + (b - .5) * col_w, y0 + row_h / 2 - 2, F.final3_for_pair(w, b))
    c.setStrokeColor(black)
    for i in range(9):
        yy = body_top - i * row_h
        c.setLineWidth(1 if i in (0, 4, 8) else .3)
        c.line(grid_left, yy, grid_right, yy)
    for j in range(9):
        xx = grid_left + j * col_w
        c.setLineWidth(1 if j in (0, 8) else .3)
        c.line(xx, grid_bottom, xx, grid_top)
    c.setLineWidth(1.2)
    c.rect(grid_left, grid_bottom, grid_right - grid_left, grid_top - grid_bottom)
    c.setFont("MonoB", 6.5)
    c.drawCentredString((grid_left + grid_right) / 2, grid_top + 2 * mm, "ACTUAL BLACK")
    c.saveState(); c.translate(left + 2.5 * mm, (body_top + grid_bottom) / 2); c.rotate(90)
    c.drawCentredString(0, 0, "ACTUAL WHITE"); c.restoreState()
    c.showPage()


def draw_final7_page(c, first_card, last_card, instructions):
    left, right, top, bottom = frame(c, "12 WORDS - PHYSICAL FINAL 7 ENTROPY BITS")
    y = title(c, "FINAL 7 BITS", f"Direct lookup - cards {first_card:02d} through {last_card:02d}")
    y = paragraph(c, instructions, left, y, right - left, size=7.8, leading=3.7 * mm)
    c.setFont("MonoB", 7.5)
    c.drawString(left, y, "ACTUAL WHITE:     1/2      3/4      5/6      7/8")
    y -= 4.5 * mm
    c.setFont("Mono", 7.5)
    c.drawString(left, y, "NORMAL ->         00       01       10       11")
    y -= 4 * mm
    c.setFont("MonoB", 7.5)
    c.drawString(left, y, "MIRROR ->         11       10       01       00")
    y -= 6 * mm
    table_top = y
    table_bottom = bottom + 4 * mm
    card_count = last_card - first_card + 1
    row_h = (table_top - table_bottom) / (card_count + 1)
    widths = [13 * mm, 17 * mm] + [(right - left - 30 * mm) / 4] * 4
    xs = [left]
    for width in widths:
        xs.append(xs[-1] + width)
    c.setFillColor(LIGHT); c.rect(left, table_top - row_h, right - left, row_h, stroke=0, fill=1)
    headers = ["CARD", "FIRST 5", "00", "01", "10", "11"]
    for col, header in enumerate(headers):
        c.setFillColor(black); c.setFont("MonoB", 7.2)
        c.drawCentredString((xs[col] + xs[col + 1]) / 2, table_top - row_h + row_h / 2 - 2, header)
    for position, card in enumerate(range(first_card, last_card + 1), 1):
        y0 = table_top - (position + 1) * row_h
        if card % 2 == 0:
            c.setFillColor(HexColor("#F2F2F2")); c.rect(left, y0, right - left, row_h, stroke=0, fill=1)
        values = [f"{card:02d}", f"{card - 1:05b}"] + [f"{((card - 1) << 2) | pair:07b}" for pair in range(4)]
        for col, value in enumerate(values):
            c.setFillColor(black); c.setFont("MonoB" if col >= 2 else "Mono", 7.2)
            c.drawCentredString((xs[col] + xs[col + 1]) / 2, y0 + row_h / 2 - 2, value)
    c.setStrokeColor(black)
    for row in range(card_count + 2):
        yy = table_top - row * row_h
        c.setLineWidth(.8 if row in (0, 1, card_count + 1) else .2)
        c.line(left, yy, right, yy)
    for xx in xs:
        c.setLineWidth(.7); c.line(xx, table_bottom, xx, table_top)
    c.showPage()


def draw_final7(c):
    draw_final7_page(
        c, 1, 16,
        "After 11 full words: 1. Roll WHITE+BLACK and use CARD SELECT; keep CARD and MODE. 2. Roll WHITE only; BLACK is not rolled and no second Black result is used. 3. Use the mode row to choose a 2-bit column. 4. Cross CARD and that column; record the direct 7-bit result.",
    )
    draw_final7_page(
        c, 17, 32,
        "Continue here when CARD SELECT returned card 17 through 32. Use the recorded NORMAL/MIRROR mode and the actual WHITE-only second result. Do not concatenate or convert values: the bold seven-bit cell is the final physical entropy output.",
    )


def draw_blank(c, text="CARD SECTION STARTS ON THE NEXT PAGE"):
    c.setFont("MonoI", 7)
    c.setFillColor(GRAY)
    c.drawCentredString(PAGE_W / 2, PAGE_H / 2, text)
    c.showPage()


def grid_geometry(left, right, top, bottom, compact=False):
    zone_top = top - (29 if compact else 31) * mm
    zone_bottom = bottom + 11 * mm
    label = 7 * mm if compact else 6 * mm
    grid_left, grid_right = left + label, right - label
    grid_top, grid_bottom = zone_top - label, zone_bottom + label
    return grid_left, grid_right, grid_top, grid_bottom, label


def draw_word_grid(c, card, indices, compact=False):
    left, right, top, bottom = frame(c)
    grid_left, grid_right, grid_top, grid_bottom, label = grid_geometry(left, right, top, bottom, compact)
    cell_w = (grid_right - grid_left) / 8
    cell_h = (grid_top - grid_bottom) / 8
    c.setFillColor(LIGHT)
    for row in range(8):
        if row % 2:
            c.rect(grid_left, grid_top - (row + 1) * cell_h, grid_right - grid_left, cell_h, stroke=0, fill=1)
    c.setStrokeColor(black)
    for row in range(9):
        yy = grid_top - row * cell_h
        c.setLineWidth(1.1 if row in (0, 4, 8) else .3)
        c.line(grid_left, yy, grid_right, yy)
    for col in range(9):
        xx = grid_left + col * cell_w
        c.setLineWidth(1.1 if col in (0, 4, 8) else .3)
        c.line(xx, grid_bottom, xx, grid_top)
    for offset, index in enumerate(indices):
        row, col = divmod(offset, 8)
        x = grid_left + (col + .5) * cell_w
        y = grid_top - (row + .5) * cell_h
        word = WORDS[index - 1]
        c.setFillColor(black); c.setFont("MonoB", fit(word, "MonoB", 9.1, cell_w - 1.2 * mm))
        c.drawCentredString(x, y + 1.1 * mm, word)
        c.setFillColor(GRAY); c.setFont("Mono", 5.1)
        c.drawCentredString(x, y - 3.0 * mm, f"{index:04d}")
    return grid_left, grid_right, grid_top, grid_bottom, cell_w, cell_h


def draw_easy_card(c, card, mode):
    left, right, top, bottom = frame(c, f"CARD {card:03d} - {mode} - WHITE = ROW - BLACK = COLUMN")
    c.setFillColor(LIGHT if mode == F.MIRROR else white)
    c.rect(left, top - 25 * mm, right - left, 23 * mm, stroke=1, fill=1)
    c.setFillColor(black); c.setFont("MonoB", 18)
    c.drawString(left + 4 * mm, top - 10 * mm, f"CARD {card:03d}")
    c.setFont("MonoB", 16)
    c.drawRightString(right - 4 * mm, top - 10 * mm, mode)
    c.setFont("MonoB", 7.3)
    c.drawCentredString((left + right) / 2, top - 17 * mm, "SECOND ROLL: ACTUAL WHITE = ROW / ACTUAL BLACK = COLUMN")
    c.setFont("MonoB" if mode == F.MIRROR else "Mono", 6.8)
    c.drawCentredString((left + right) / 2, top - 22 * mm, f"USE THIS PAGE ONLY IF SELECTOR SAID {mode}")
    indices = F.page_indices(card, mode)
    gl, gr, gt, gb, cw, ch = draw_word_grid(c, card, indices)
    for col in range(8):
        x = gl + (col + .5) * cw
        c.setFillColor(black); c.setFont("MonoB", 7.5)
        c.drawCentredString(x, gt + 2.3 * mm, str(col + 1))
    for row in range(8):
        y = gt - (row + .5) * ch - 2
        c.setFillColor(black); c.setFont("MonoB", 7.5)
        c.drawCentredString(gl - 3.2 * mm, y, str(row + 1))
        c.drawCentredString(gr + 3.2 * mm, y, str(row + 1))
    c.setFont("MonoB", 6.2); c.drawCentredString((gl + gr) / 2, gt + 6.4 * mm, "ACTUAL BLACK")
    c.saveState(); c.translate(gl - 6.3 * mm, (gt + gb) / 2); c.rotate(90)
    c.drawCentredString(0, 0, "ACTUAL WHITE"); c.restoreState()
    c.showPage()


def draw_compact_card(c, card):
    left, right, top, bottom = frame(c, f"CARD {card:03d} - COMPACT DUAL COORDINATES")
    c.setFillColor(black); c.setFont("MonoB", 17)
    c.drawString(left, top - 9 * mm, f"CARD {card:03d}")
    c.setFont("MonoB", 8.2); c.drawRightString(right, top - 7 * mm, "COMPACT / ADVANCED")
    c.setFont("Mono", 6.7)
    c.drawRightString(right, top - 12 * mm, "NORMAL: LEFT row + TOP column")
    c.setFont("MonoB", 6.7)
    c.drawRightString(right, top - 17 * mm, "MIRROR: RIGHT row + BOTTOM column")
    c.setFont("Mono", 6.3)
    c.drawString(left, top - 22 * mm, "Use actual second-roll values; choose only the labels for your mode.")
    indices = F.canonical_card_indices(card)
    gl, gr, gt, gb, cw, ch = draw_word_grid(c, card, indices, compact=True)
    for col in range(8):
        x = gl + (col + .5) * cw
        c.setFont("Mono", 7.2); c.setFillColor(black)
        c.drawCentredString(x, gt + 2.1 * mm, str(col + 1))
        c.setFont("MonoB", 7.2)
        c.drawCentredString(x, gb - 4.4 * mm, str(8 - col))
    for row in range(8):
        y = gt - (row + .5) * ch - 2
        c.setFont("Mono", 7.2); c.drawCentredString(gl - 3.6 * mm, y, str(row + 1))
        c.setFont("MonoB", 7.2); c.drawCentredString(gr + 3.6 * mm, y, str(8 - row))
    c.setFont("Mono", 5.8); c.drawCentredString((gl + gr) / 2, gt + 6.1 * mm, "NORMAL TOP - ACTUAL BLACK")
    c.setFont("MonoB", 5.8); c.drawCentredString((gl + gr) / 2, gb - 8.4 * mm, "MIRROR BOTTOM - ACTUAL BLACK")
    c.showPage()


def build_easy_pages():
    return [(card, mode, F.page_indices(card, mode)) for card in range(1, 33) for mode in F.MODES]


def build_compact_pages():
    return [(card, F.canonical_card_indices(card)) for card in range(1, 33)]


def self_check():
    assert len(WORDS) == 2048 and len(set(WORDS)) == 2048
    F.assert_core_invariants()
    easy = build_easy_pages()
    assert len(easy) == 64
    assert {(card, mode) for card, mode, _ in easy} == {(card, mode) for card in range(1, 33) for mode in F.MODES}
    assert all(len(indices) == 64 for _, _, indices in easy)
    compact = build_compact_pages()
    assert len(compact) == 32 and all(len(indices) == 64 for _, indices in compact)
    assert sorted(index for _, indices in compact for index in indices) == list(range(1, 2049))
    selector = selector_data()
    assert len(selector) == 8 and all(len(row) == 8 for row in selector)
    assert Counter(card for row in selector[:4] for card, mode in row) == Counter(range(1, 33))
    assert Counter(card for row in selector[4:] for card, mode in row) == Counter(range(1, 33))


def make_canvas(path, title_text):
    c = canvas.Canvas(path, pagesize=A5, invariant=1, pageCompression=1)
    c.setTitle(title_text)
    c.setAuthor("2XD8 Entropy Booklet opposite-fold contributors")
    c.setSubject("Offline physical BIP39 entropy with opposite-complement folding")
    return c


def generate_easy(path=EASY_OUT):
    c = make_canvas(path, "2XD8 Entropy Booklet - Opposite Fold Easy")
    draw_cover(c, "EASY / RECOMMENDED EDITION")
    draw_guide_pages(c)
    draw_selector(c)
    draw_final3(c)
    draw_final7(c)
    # Ten content pages plus this deliberate spacer put each NORMAL page on
    # an even/left page and its matching MIRROR page on the following right page.
    draw_blank(c)
    for card, mode, _ in build_easy_pages():
        draw_easy_card(c, card, mode)
    c.save()
    return path


def generate_compact(path=COMPACT_OUT):
    c = make_canvas(path, "2XD8 Entropy Booklet - Opposite Fold Compact")
    draw_cover(c, "COMPACT / ADVANCED EDITION")
    draw_guide_pages(c)
    draw_selector(c)
    draw_final3(c)
    draw_final7(c)
    draw_blank(c)
    for card, _ in build_compact_pages():
        draw_compact_card(c, card)
    c.save()
    return path


def main():
    V.register_fonts()
    self_check()
    easy = generate_easy()
    compact = generate_compact()
    print("OK Easy booklet ->", os.path.relpath(easy, HERE))
    print("OK Compact booklet ->", os.path.relpath(compact, HERE))


if __name__ == "__main__":
    main()
