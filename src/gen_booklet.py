#!/usr/bin/env python3
"""2XD8 Entropy Booklet — dice-only fork of the Seed Jar Method.

One combined A5-portrait booklet, vintage letterpress, pure B&W:
cover -> short guide -> card-select table -> 32 word-grid cards.

No tickets, no jar. The same two distinguishable d8 (White / Black) are
rolled twice per word: once to pick a card (1-32), once to pick a cell
on that card (row/column, 1-8 each).
"""
import os
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader
import vintage as V

HERE = os.path.dirname(os.path.abspath(__file__))
V.register_fonts()

WORDS = open(os.path.join(HERE, "english.txt")).read().split()
assert len(WORDS) == 2048 and len(set(WORDS)) == 2048, "wordlist must be 2048 unique words"

# Card n, cell k (row-major, 8 cols) holds BIP39 index n + 32*k, k = 0..63.
cards = {n: [n + 32 * k for k in range(64)] for n in range(1, 33)}
allidx = [i for v in cards.values() for i in v]
assert len(cards) == 32, "must be 32 cards"
assert all(len(v) == 64 for v in cards.values()), "each card must have 64 cells"
assert sorted(allidx) == list(range(1, 2049)), "indices 1..2048 must each appear exactly once"
assert cards[1][:2] == [1, 33] and cards[9][0] == 9, "mapping sanity check failed"
assert cards[1][8] == 257, "row-major mapping check failed (row 2 of card 001 should start at 257)"

# Card-select table: card = (white-1)*4 + black_bucket, black_bucket = ceil(black/2).
# White's full 8 values (3 bits) x Black collapsed into 4 equal-size pairs (2 bits) = 5 bits = 1-of-32.
def card_for(white, black_pair_idx):
    return (white - 1) * 4 + black_pair_idx

selector = {(w, b): card_for(w, b) for w in range(1, 9) for b in range(1, 5)}
assert sorted(selector.values()) == list(range(1, 33)), "selector table must cover 1..32 exactly once"

PAGE_W, PAGE_H = A5  # 148 x 210mm, portrait
GRAY = HexColor("#555555")
BAND = HexColor("#E8E8E8")

MARGIN_TOP = 6 * mm
MARGIN_SIDE = 6 * mm
MARGIN_BOTTOM = 11 * mm

ROWS = COLS = 8

def fit(text, font, maxsize, maxw):
    s = maxsize
    while s > 4 and stringWidth(text, font, s) > maxw:
        s -= 0.25
    return s

def wrap(text, font, size, maxw):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if stringWidth(trial, font, size) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# ---------------------------------------------------------------- frame ----

def frame_bounds():
    """Inner content bounds (il, ir, it, ib) for any page -- pure geometry,
    same numbers page_frame() draws into. Kept separate so guide pagination
    can measure content against the real frame without drawing anything."""
    x, y = MARGIN_SIDE, MARGIN_BOTTOM
    w, h = PAGE_W - 2 * MARGIN_SIDE, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM
    pad = 2.0 * mm
    il = x + pad + 1.4 * mm; ir = x + w - pad - 1.4 * mm
    it = y + h - pad - 1.4 * mm; ib = y + pad + 1.4 * mm
    return il, ir, it, ib

def page_frame(c, footer_text=""):
    """Content bounds (il, ir, it, ib) + footer, shared by every page.
    No border box, no corner ornament -- margins only."""
    il, ir, it, ib = frame_bounds()

    if footer_text:
        c.setFillColor(GRAY)
        V.spaced(c, PAGE_W / 2, MARGIN_BOTTOM - 5.5 * mm, footer_text, "Mono", 6.4, 0.7)
    return il, ir, it, ib

# ------------------------------------------------------------- cover page --

COVER_ART = os.path.join(HERE, "cover.png")

def draw_cover(c):
    img = ImageReader(COVER_ART)
    iw, ih = img.getSize()
    # Full-bleed width, aspect-correct height, centered vertically -- the
    # art's own aspect ratio is a touch wider than A5 portrait, so it can't
    # fill the whole page without either cropping or a tiny top/bottom gap;
    # a gap preserves the whole illustration instead of cutting into it.
    # No byline footer here -- the art already carries its own title
    # treatment, and there's no clear space left to put one without
    # overlapping it.
    draw_w = PAGE_W
    draw_h = draw_w * ih / iw
    y = (PAGE_H - draw_h) / 2
    c.drawImage(img, 0, y, width=draw_w, height=draw_h, preserveAspectRatio=True, mask="auto")
    c.showPage()

# ------------------------------------------------------------- guide pages -

GUIDE = [
    ("h1", "INTRODUCTION"),
    ("p", "For secure self-custody, bitcoiners must create seed phrases by generating "
          "entropy offline rather than trusting computer/hardware random number "
          "generators."),
    ("p", "With a pair of d8 dice and this booklet, sufficient offline entropy can be "
          "generated quickly and easily."),
    ("p", "Eleven words for a 12-word seed, twenty-three for a 24-word seed. The final word "
          "is always a checksum computed by your hardware wallet, never drawn by hand — "
          "see The Checksum Step."),

    ("h1", "WHAT YOU NEED"),
    ("li", "This booklet"),
    ("li", "Some pen and paper"),
    ("li", "A pair of distinguishable d8 (eight-sided) dice — one always White, one "
           "always Black, never swapped mid-process"),
    ("li", "A checksum-capable hardware wallet or offline BIP39 tool"),

    ("h1", "HOW IT WORKS"),
    ("num", "Turn to the CARD SELECT table on page 1."),
    ("num", "Roll both dice. Read White openly, 1–8. Read Black only as a pair: 1/2, "
            "3/4, 5/6, or 7/8."),
    ("num", "Cross White against the Black-pair on the table to get a card number, 1–32. "
            "Turn to that card. For example, if you rolled White 3 and Black 6, you land on "
            "card 11, so you turn to that page."),
    ("num", "Roll both dice again. White gives the row, 1–8; Black gives the column, 1–8."),
    ("num", "Read the word at that row/column and write it down. For example, on Card 1, "
            "White 6 and Black 6 give you row 6, column 6 — the word there is REDUCE."),
    ("num", "Repeat from step 2. Do this 11 times for a 12-word seed, or 23 times for a "
            "24-word seed."),
    ("num", "Feed your drawn words into your hardware wallet (or an offline BIP39 tool) "
            "to get the valid final checksum word. Never hand-pick, guess, or re-roll it "
            "yourself. Do this air-gapped, on a device that has never touched the internet "
            "with this seed."),
    ("num", "Enjoy your new seed."),

    ("h1", "THE CHECKSUM STEP"),
    ("p", "These pages give you raw entropy only, never a finished mnemonic. In BIP39 the "
          "final word encodes a checksum over every word before it — draw all 12 (or 24) "
          "words independently and the phrase is only valid about 1 time in 16 (1 in 256 for "
          "24 words). So: draw 11 or 23 words with this booklet, then let your hardware "
          "wallet or an offline tool compute the valid final word. Never hand-pick, guess, or "
          "re-roll it yourself."),
    ("small", "Released under CC0 1.0 — print, fork, adapt, share freely. Fonts under "
              "SIL OFL. Not financial advice. Use at your own risk."),

    ("h1", "WHY THE BLACK AND WHITE ARE NOT INTERCHANGEABLE VALUES"),
    ("p", "White and Black each roll twice per word, but they mean two different things each "
          "time — a card number on the first roll, a row/column on the second. Keep their "
          "identity fixed."),
    ("p", "Repeat, you must NEVER swap which die is White and which is Black mid-process. "
          "If you do, you collapse two distinct outcomes into one, which breaks the uniform "
          "1-in-2048 odds and non-linearly COMPROMISES your entropy, making your final "
          "outputs insecure and unusable."),
    ("p", "The bit math: two d8 give 6 bits — 64 outcomes, one shy of 2048. So each word "
          "costs two rolls of the same pair. Roll one narrows 2048 words to 1 of 32 cards, "
          "using White's full 8 values (3 bits) and Black collapsed into 4 pairs (2 bits) "
          "— 5 bits. Roll two picks the exact cell on that card, using White as row and "
          "Black as column, full 8×8 — 6 bits. 5 + 6 = 11 bits = 1-in-2048, exactly "
          "uniform, no modulo bias — the same two dice doing double duty instead of "
          "needing a jar, tickets, or a third randomness source."),

    ("h1", "WHY 32 CARDS WITH 64 WORDS EACH"),
    ("p", "There are 2048 words in the BIP39 list used to generate every English seed "
          "phrase. 32 cards of 64 words each is the cleanest way to cover all 2048 with a "
          "booklet you can actually print and flip through — not so many pages it's a "
          "chore, not so few words per page that you'd still need a stack of loose pieces."),
    ("p", "There are pre-existing products that sell 1024 or 2048 pieces which work fine, "
          "but it's impractical to handcraft or mark that many individual pieces yourself."),
    ("p", "A pair of d8 dice already gives you 64 unique outputs on a grid, so this booklet "
          "only needed 32 pages to cover the same 2048 words. And because it's bound as a "
          "booklet instead of loose tickets or tablets, there's nothing to lose track of at "
          "all — just this book and two d8 dice."),
]

LINE_H = 4.6 * mm
SMALL_LINE_H = 3.8 * mm
TITLE_SIZE = 11.5
TITLE_LINE_H = 5.5 * mm
_GIL, _GIR, _, _ = frame_bounds()  # guide content width is the same on every page
CONTENT_W = _GIR - _GIL

def block_height(kind, text):
    if kind == "p":
        return len(wrap(text, "Mono", 9.0, CONTENT_W)) * LINE_H + 2.6 * mm
    if kind == "li":
        return len(wrap(text, "Mono", 9.0, CONTENT_W - 5 * mm)) * LINE_H + 1.5 * mm
    if kind == "num":
        return len(wrap(text, "Mono", 9.0, CONTENT_W - 7 * mm)) * LINE_H + 1.5 * mm
    if kind == "small":
        return len(wrap(text, "MonoI", 7.3, CONTENT_W)) * SMALL_LINE_H
    raise ValueError(kind)

def header_height(text, at_top):
    title_lines = len(wrap(text, "MonoB", TITLE_SIZE, CONTENT_W))
    return (0 if at_top else 4 * mm) + (title_lines - 1) * TITLE_LINE_H + 2.4 * mm + 6.5 * mm

def group_sections(items):
    """[(h1, [blocks...]), ...] -- pagination breaks between sections, never inside one,
    unless a single section is too tall for an empty page (falls back to a mid-section break)."""
    sections = []
    for kind, text in items:
        if kind == "h1":
            sections.append((text, []))
        else:
            sections[-1][1].append((kind, text))
    return sections

def draw_guide(c):
    il = ir = it = ib = None
    y = 0
    num_counter = 0

    def start_page():
        nonlocal il, ir, it, ib, y
        il, ir, it, ib = page_frame(c, "2XD8 ENTROPY BOOKLET  ·  GUIDE")
        y = it - 3 * mm

    def at_top():
        return y >= it - 3 * mm - 0.01

    def ensure(space):
        nonlocal y
        if y - space < ib + 4 * mm:
            c.showPage(); start_page()

    def draw_header(text):
        nonlocal y
        top = at_top()
        if not top:
            y -= 4 * mm
        lines = wrap(text, "MonoB", TITLE_SIZE, ir - il)
        c.setFillColor(black); c.setFont("MonoB", TITLE_SIZE)
        for i, ln in enumerate(lines):
            c.drawString(il, y, ln)
            if i < len(lines) - 1:
                y -= TITLE_LINE_H
        y -= 2.4 * mm
        V.double_rule(c, il, ir, y, thick=0.9, thin=0.32, gap=0.8)
        y -= 6.5 * mm

    def draw_block(kind, text):
        nonlocal y, num_counter
        if kind == "p":
            lines = wrap(text, "Mono", 9.0, ir - il)
            ensure(len(lines) * LINE_H + 2 * mm)
            c.setFont("Mono", 9.0); c.setFillColor(black)
            for ln in lines:
                c.drawString(il, y, ln); y -= LINE_H
            y -= 2.6 * mm
        elif kind == "li":
            lines = wrap(text, "Mono", 9.0, ir - il - 5 * mm)
            ensure(len(lines) * LINE_H + 1.5 * mm)
            c.setFont("Mono", 9.0); c.setFillColor(black)
            c.drawString(il, y, "•")
            for ln in lines:
                c.drawString(il + 5 * mm, y, ln); y -= LINE_H
            y -= 1.5 * mm
        elif kind == "num":
            num_counter += 1
            lines = wrap(text, "Mono", 9.0, ir - il - 7 * mm)
            ensure(len(lines) * LINE_H + 1.5 * mm)
            c.setFont("MonoB", 9.0); c.setFillColor(black)
            c.drawString(il, y, f"{num_counter}.")
            c.setFont("Mono", 9.0)
            for ln in lines:
                c.drawString(il + 7 * mm, y, ln); y -= LINE_H
            y -= 1.5 * mm
        elif kind == "small":
            lines = wrap(text, "MonoI", 7.3, ir - il)
            ensure(len(lines) * SMALL_LINE_H)
            c.setFont("MonoI", 7.3); c.setFillColor(GRAY)
            for ln in lines:
                c.drawString(il, y, ln); y -= SMALL_LINE_H

    start_page()
    page_h = it - ib
    for header, blocks in group_sections(GUIDE):
        num_counter = 0
        blocks_h = sum(block_height(k, t) for k, t in blocks)
        total_mid = header_height(header, at_top=False) + blocks_h
        total_top = header_height(header, at_top=True) + blocks_h
        # Keep a section whole on one page unless it can't possibly fit an
        # empty page either -- then fall back to letting it break mid-section
        # (per-block `ensure` calls below still guarantee no overlap with the
        # frame) rather than orphaning a header or a trailing line alone.
        if not at_top() and y - total_mid < ib + 4 * mm and total_top <= page_h:
            c.showPage(); start_page()
        draw_header(header)
        for kind, text in blocks:
            draw_block(kind, text)
    c.showPage()

# ----------------------------------------------------------- selector page -

def draw_select_grid(c, tab_left, tab_right, zone_top, zone_bot, scale=1.0, side_labels=True):
    """The White/Black -> card lookup grid. `scale` shrinks every tuned
    dimension and font size uniformly from the CARD SELECT page's own
    numbers, so a reduced copy (e.g. on the cover) is a faithful miniature
    rather than a separately re-tuned approximation. Returns grid_bot."""
    tab_w = tab_right - tab_left
    col_w = tab_w / 4  # 4 black-pair columns
    header_h = 9 * mm * scale
    max_row_h = 15 * mm * scale

    avail_h = zone_top - zone_bot
    grid_h = min(avail_h - header_h, max_row_h * 8)
    row_h = grid_h / 8
    top_pad = (avail_h - header_h - grid_h) / 2

    header_y = zone_top - top_pad - header_h  # bottom edge of the header band
    grid_top = header_y
    grid_bot = grid_top - grid_h

    label_size = 8.5 * scale
    pair_size = 9 * scale
    num_size = 13 * scale

    if side_labels:
        c.setFont("MonoB", label_size); c.setFillColor(black)
        c.drawCentredString((tab_left + tab_right) / 2, header_y + header_h + 3 * mm * scale,
                             "BLACK D8")
        c.saveState()
        c.translate(tab_left - 10 * mm * scale, (grid_top + grid_bot) / 2)
        c.rotate(90)
        c.setFont("MonoB", label_size)
        c.drawCentredString(0, 0, "WHITE D8")
        c.restoreState()

    # header band (black-pair labels)
    c.setFillColor(BAND)
    c.rect(tab_left, header_y, tab_w, header_h, stroke=0, fill=1)
    pair_labels = ["1 / 2", "3 / 4", "5 / 6", "7 / 8"]
    for j, lbl in enumerate(pair_labels):
        cxx = tab_left + (j + 0.5) * col_w
        c.setFont("MonoB", pair_size); c.setFillColor(black)
        c.drawCentredString(cxx, header_y + header_h / 2 - 1.4 * mm * scale, lbl)
        if j > 0:
            c.setStrokeColor(black); c.setLineWidth(0.5)
            c.line(tab_left + j * col_w, header_y, tab_left + j * col_w, header_y + header_h)

    # row banding, alternating white rows shaded light grey
    c.setFillColor(BAND)
    for i in range(8):
        if (i + 1) % 2 == 0:
            c.rect(tab_left, grid_top - (i + 1) * row_h, tab_w, row_h, stroke=0, fill=1)

    # grid lines
    c.setStrokeColor(black)
    for i in range(9):
        yy = grid_top - i * row_h
        c.setLineWidth(1.2 if i in (0, 8) else 0.35)
        c.line(tab_left, yy, tab_right, yy)
    for j in range(5):
        xx = tab_left + j * col_w
        c.setLineWidth(1.2 if j in (0, 4) else 0.35)
        c.line(xx, grid_top, xx, grid_bot)

    # outer frame around header + grid together
    c.setLineWidth(1.6)
    c.rect(tab_left, grid_bot, tab_w, header_y + header_h - grid_bot)

    # row labels + card numbers
    for i in range(8):
        white = i + 1
        ry = grid_top - (i + 0.5) * row_h
        if side_labels:
            c.setFont("MonoB", pair_size); c.setFillColor(black)
            c.drawCentredString(tab_left - 5 * mm * scale, ry - 1.3 * scale, str(white))
        for j in range(4):
            card_n = selector[(white, j + 1)]
            cxx = tab_left + (j + 0.5) * col_w
            c.setFont("MonoB", num_size); c.setFillColor(black)
            c.drawCentredString(cxx, ry - 1.6 * scale, f"{card_n}")

    return grid_bot

def draw_selector(c):
    il, ir, it, ib = page_frame(
        c, "CARD SELECT  ·  WHITE = ROW OF TABLE  ·  BLACK = COLUMN PAIR")
    cx = (il + ir) / 2

    V.spaced(c, cx, it - 9 * mm, "CARD SELECT", "MonoB", 12.5, 2.0)
    V.double_rule(c, il + 8 * mm, ir - 8 * mm, it - 13.5 * mm, thick=1.0, thin=0.35, gap=0.9)

    tab_left = il + 15 * mm  # 10mm label width + 5mm gap, room for the rotated WHITE D8 label
    tab_right = ir - 5 * mm
    zone_top = it - 24 * mm
    zone_bot = ib + 15 * mm

    grid_bot = draw_select_grid(c, tab_left, tab_right, zone_top, zone_bot)

    c.setFont("MonoI", 7.5); c.setFillColor(GRAY)
    c.drawCentredString(cx, grid_bot - 8 * mm,
                         "Example: White 3, Black 6 -> row 3, pair 5/6 -> card 11.")
    c.drawCentredString(cx, grid_bot - 12 * mm,
                         "Card-select table by @FieldNas on X.")
    c.showPage()

# ------------------------------------------------------------ card pages ---

def draw_card(c, n):
    il, ir, it, ib = page_frame(c, f"WHITE = ROW  ·  BLACK = COLUMN  ·  CARD {n:03d} OF 032")
    cx = (il + ir) / 2

    V.spaced(c, cx, it - 6.6 * mm, "CARD", "MonoB", 9.5, 1.8)
    V.spaced(c, cx - 9.5 * mm, it - 12.4 * mm, "Nº", "MonoI", 9, 0)
    c.setFont("MonoB", 17); c.setFillColor(black)
    c.drawString(cx - 3.5 * mm, it - 13.7 * mm, f"{n:03d}")
    V.double_rule(c, il + 3 * mm, ir - 3 * mm, it - 15.8 * mm, thick=1.0, thin=0.35, gap=0.9)

    zone_top = it - 19.0 * mm
    zone_bot = ib + 9.0 * mm
    top_labels_h = 5.2 * mm
    bot_labels_h = 5.2 * mm
    left_labels_w = 6.5 * mm
    right_labels_w = 6.5 * mm

    avail_h = (zone_top - top_labels_h) - (zone_bot + bot_labels_h)
    MAX_ROW_H = 14.5 * mm
    gh = min(avail_h, MAX_ROW_H * 8)
    gtop = zone_top - top_labels_h - (avail_h - gh) / 2
    gbot = gtop - gh

    gx = il + left_labels_w
    grx = ir - right_labels_w
    gw = grx - gx
    cw, ch = gw / COLS, gh / ROWS

    c.setFillColor(BAND)
    for i in range(ROWS):
        if (i + 1) % 2 == 0:
            c.rect(gx, gtop - (i + 1) * ch, gw, ch, stroke=0, fill=1)

    c.setStrokeColor(black)
    for i in range(ROWS + 1):
        yy = gtop - i * ch
        c.setLineWidth(1.4 if i % 4 == 0 else 0.35)
        c.line(gx, yy, gx + gw, yy)
    for j in range(COLS + 1):
        xx = gx + j * cw
        c.setLineWidth(1.4 if j % 4 == 0 else 0.35)
        c.line(xx, gtop, xx, gtop - gh)

    for j in range(COLS):
        num = str(j + 1)
        cxx = gx + (j + 0.5) * cw
        V.spaced(c, cxx, gtop + 1.1 * mm, num, "MonoI", 7.5, 0, color=GRAY)
        V.spaced(c, cxx, gbot - 4.0 * mm, num, "MonoI", 7.5, 0, color=GRAY)
    for i in range(ROWS):
        num = str(i + 1)
        cyy = gtop - (i + 0.5) * ch - 1.3
        V.spaced(c, gx - 3.6 * mm, cyy, num, "MonoI", 7.5, 0, color=GRAY)
        V.spaced(c, grx + 3.6 * mm, cyy, num, "MonoI", 7.5, 0, color=GRAY)

    for k, idx in enumerate(cards[n]):
        i, j = divmod(k, COLS)
        wx = gx + (j + 0.5) * cw; wy = gtop - (i + 0.5) * ch
        word = WORDS[idx - 1]
        fs = fit(word, "MonoB", 10.0, cw - 2.0 * mm)
        c.setFillColor(black); c.setFont("MonoB", fs)
        c.drawCentredString(wx, wy + 0.6 * mm, word)
        c.setFillColor(GRAY); c.setFont("Mono", 5.4)
        c.drawCentredString(wx, wy - 4.0 * mm, f"{idx:04d}")

    V.spaced(c, cx, ib + 1.6 * mm, "OFFICIAL BIP39 ENGLISH LIST", "Mono", 5.0, 0.6, color=GRAY)
    c.showPage()

# --------------------------------------------------------------- assemble --

OUT = os.path.join(HERE, "..", "2XD8_Entropy_Booklet.pdf")
c = canvas.Canvas(OUT, pagesize=A5)
c.setTitle("2XD8 Entropy Booklet")
c.setSubject("Offline BIP39 Entropy — Two Dice, Thirty-Two Cards, Nothing Else")

draw_cover(c)
draw_selector(c)
draw_guide(c)
for n in range(1, 33):
    draw_card(c, n)

c.save()
print("OK booklet ->", os.path.relpath(OUT))
