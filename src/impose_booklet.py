#!/usr/bin/env python3
"""Booklet imposition for home/office printing.

Takes the normal reader PDF (one A5 page per page, in reading order) and
reshuffles + pairs it onto A4-landscape sheets, two A5 pages per side, in
the standard single-signature saddle-stitch order: fold the whole printed
stack in half once, staple through the spine, and the pages read 1..N in
order.

How to print it:
  - Duplex printer: turn on two-sided printing, flip on the SHORT edge,
    print the whole file once.
  - Single-sided printer: print ODD pages only, flip the entire printed
    stack over left-to-right (like turning a page -- don't rotate it),
    reload it the same way up, then print EVEN pages only.
Then fold every sheet in half together as one stack and staple the spine.

Page count is padded to a multiple of 4 with blank A5 pages (required for
a single-signature saddle-stitch fold) -- they land at the very end of the
reading order, after the last card.
"""
import os
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf._page import PageObject
from reportlab.lib.pagesizes import A5, A4, landscape

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "2XD8_Entropy_Booklet.pdf")
OUT = os.path.join(HERE, "..", "2XD8_Entropy_Booklet_Print-at-Home.pdf")

A5_W, A5_H = A5
A4_W, A4_H = landscape(A4)
# ISO 216 rounds A4 and A5 independently (297mm vs 2x148mm), so two A5
# pages fall ~1mm short of A4's width -- harmless, just centered below.
assert abs(A4_W - 2 * A5_W) < 3, "two A5-portrait pages should roughly tile one A4-landscape sheet"
assert abs(A4_H - A5_H) < 0.5
X_OFFSET = (A4_W - 2 * A5_W) / 2

reader = PdfReader(SRC)
pages = list(reader.pages)
P = len(pages)
total = P + ((-P) % 4)  # pad up to a multiple of 4
blanks_added = total - P
S = total // 4  # sheets

def get_page(n):
    """1-indexed reader-PDF page, or None for the padding blanks."""
    return pages[n - 1] if 1 <= n <= P else None

def make_side(left_n, right_n):
    side = PageObject.create_blank_page(width=A4_W, height=A4_H)
    left = get_page(left_n)
    right = get_page(right_n)
    if left is not None:
        side.merge_transformed_page(left, Transformation().translate(X_OFFSET, 0))
    if right is not None:
        side.merge_transformed_page(right, Transformation().translate(X_OFFSET + A5_W, 0))
    return side

writer = PdfWriter()
for s in range(1, S + 1):
    front_left, front_right = total + 2 - 2 * s, 2 * s - 1
    back_left, back_right = 2 * s, total + 1 - 2 * s
    writer.add_page(make_side(front_left, front_right))
    writer.add_page(make_side(back_left, back_right))

with open(OUT, "wb") as f:
    writer.write(f)

print(f"OK imposed booklet: {P} reader pages (+{blanks_added} blank) -> "
      f"{S} sheets / {2*S} printed sides -> {os.path.relpath(OUT)}")
