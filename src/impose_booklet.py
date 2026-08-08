#!/usr/bin/env python3
"""Impose both reader editions two-up on A4 for saddle-stitch printing."""
import os

from pypdf import PdfReader, PdfWriter, Transformation
from pypdf._page import PageObject
from reportlab.lib.pagesizes import A4, A5, landscape

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A5_W, A5_H = A5
A4_W, A4_H = landscape(A4)
X_OFFSET = (A4_W - 2 * A5_W) / 2


def impose(source, output):
    pages = list(PdfReader(source).pages)
    page_count = len(pages)
    total = page_count + (-page_count % 4)

    def get_page(number):
        return pages[number - 1] if 1 <= number <= page_count else None

    def side(left_number, right_number):
        page = PageObject.create_blank_page(width=A4_W, height=A4_H)
        left = get_page(left_number)
        right = get_page(right_number)
        if left is not None:
            page.merge_transformed_page(left, Transformation().translate(X_OFFSET, 0))
        if right is not None:
            page.merge_transformed_page(right, Transformation().translate(X_OFFSET + A5_W, 0))
        return page

    writer = PdfWriter()
    for sheet in range(1, total // 4 + 1):
        writer.add_page(side(total + 2 - 2 * sheet, 2 * sheet - 1))
        writer.add_page(side(2 * sheet, total + 1 - 2 * sheet))
    writer.add_metadata({"/Title": os.path.basename(output), "/Producer": "pypdf deterministic imposition"})
    with open(output, "wb") as stream:
        writer.write(stream)
    print(f"OK imposed {page_count} reader pages (+{total - page_count} blank) -> {os.path.relpath(output, HERE)}")


def main():
    for edition in ("Easy", "Compact"):
        source = os.path.join(ROOT, f"2XD8_Entropy_Booklet_OppositeFold_{edition}.pdf")
        output = os.path.join(ROOT, f"2XD8_Entropy_Booklet_OppositeFold_{edition}_Print-at-Home.pdf")
        impose(source, output)


if __name__ == "__main__":
    main()
