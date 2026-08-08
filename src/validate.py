#!/usr/bin/env python3
"""Independent offline validation of math, word list, and generated PDFs.

The fold below is deliberately re-derived here and does not import the
production fold_mapping module.
"""
import argparse
from collections import Counter
import hashlib
import itertools
import os
import re
import urllib.error
import urllib.request

import pdfplumber
from pypdf import PdfReader

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORDLIST_PATH = os.path.join(HERE, "english.txt")
WORDLIST_SHA256 = "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda"
UPSTREAM_URL = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt"

WORDS = open(WORDLIST_PATH, encoding="utf-8").read().split()


def complement(value):
    if not 1 <= value <= 8:
        raise ValueError(value)
    return 9 - value


def independent_fold(w1, b1, w2, b2):
    if w1 < 5:
        mode, values = "NORMAL", (w1, b1, w2, b2)
    else:
        mode, values = "MIRROR", tuple(9 - value for value in (w1, b1, w2, b2))
    wc1, bc1, wc2, bc2 = values
    card = (wc1 - 1) * 8 + bc1
    index = card + 32 * ((wc2 - 1) * 8 + bc2 - 1)
    return mode, card, wc2, bc2, index


def independent_selector(w, b):
    mode = "NORMAL" if w <= 4 else "MIRROR"
    wc, bc = (w, b) if mode == "NORMAL" else (9 - w, 9 - b)
    return (wc - 1) * 8 + bc, mode


def independent_final3(w, b):
    card, _ = independent_selector(w, b)
    return f"{(card - 1) // 4:03b}"


def independent_final7(w1, b1, w2):
    card, mode = independent_selector(w1, b1)
    wc2 = w2 if mode == "NORMAL" else 9 - w2
    pair = (wc2 - 1) // 2
    return f"{((card - 1) << 2) | pair:07b}"


def validate_math():
    counts = Counter()
    canonical = set()
    for raw in itertools.product(range(1, 9), repeat=4):
        mode, card, row, column, index = independent_fold(*raw)
        assert mode in ("NORMAL", "MIRROR")
        assert 1 <= card <= 32 and 1 <= row <= 8 and 1 <= column <= 8 and 1 <= index <= 2048
        counts[index] += 1
        canonical.add((card, row, column))
        opposite_raw = tuple(9 - value for value in raw)
        assert index == independent_fold(*opposite_raw)[4]
    assert set(counts) == set(range(1, 2049))
    assert set(counts.values()) == {2}
    assert len(canonical) == 2048

    normal = Counter(); mirror = Counter()
    for w, b in itertools.product(range(1, 9), repeat=2):
        card, mode = independent_selector(w, b)
        (normal if mode == "NORMAL" else mirror)[card] += 1
        opposite_card, opposite_mode = independent_selector(9 - w, 9 - b)
        assert card == opposite_card and mode != opposite_mode
    assert normal == Counter(range(1, 33))
    assert mirror == Counter(range(1, 33))
    assert independent_selector(2, 7) == (15, "NORMAL")
    assert independent_selector(7, 2) == (15, "MIRROR")

    counts3 = Counter(independent_final3(w, b) for w, b in itertools.product(range(1, 9), repeat=2))
    assert len(counts3) == 8 and set(counts3.values()) == {8}
    for w, b in itertools.product(range(1, 9), repeat=2):
        assert independent_final3(w, b) == independent_final3(9 - w, 9 - b)

    counts7 = Counter(independent_final7(*raw) for raw in itertools.product(range(1, 9), repeat=3))
    assert len(counts7) == 128 and set(counts7.values()) == {4}
    for raw in itertools.product(range(1, 9), repeat=3):
        assert independent_final7(*raw) == independent_final7(*(9 - value for value in raw))
    print("MAPPING OK: 4096 raw tuples; 2048 outputs; exactly 2/output; complements invariant; 2048 canonical locations unique")
    print("FINAL BITS OK: final-3 has 8 outcomes x 8 preimages; final-7 has 128 outcomes x 4 preimages; complements invariant")


def validate_wordlist():
    raw = open(WORDLIST_PATH, "rb").read()
    assert len(WORDS) == 2048 and len(set(WORDS)) == 2048
    assert hashlib.sha256(raw).hexdigest() == WORDLIST_SHA256
    print(f"WORDLIST OK: 2048 unique words in official order; SHA-256 {WORDLIST_SHA256}")


def ordered_tokens(page, pattern, min_top=0):
    tokens = [
        word for word in page.extract_words()
        if word["top"] >= min_top and re.fullmatch(pattern, word["text"])
    ]
    return [word["text"] for word in sorted(tokens, key=lambda item: (round(item["top"] / 2) * 2, item["x0"]))]


def expected_easy(card, mode):
    values = []
    for raw_row in range(1, 9):
        for raw_col in range(1, 9):
            row = raw_row if mode == "NORMAL" else 9 - raw_row
            col = raw_col if mode == "NORMAL" else 9 - raw_col
            values.append(card + 32 * ((row - 1) * 8 + col - 1))
    return values


def validate_reader_pdf(path, edition):
    expected_pages = 75 if edition == "Easy" else 43
    expected_cards = 64 if edition == "Easy" else 32
    with pdfplumber.open(path) as pdf:
        assert len(pdf.pages) == expected_pages, f"{edition}: expected {expected_pages} pages, got {len(pdf.pages)}"
        front_text = "\n".join((page.extract_text() or "") for page in pdf.pages[:11])
        required = [
            "CARD SELECT", "FINAL 3 BITS", "FINAL 7 BITS", "253 entropy bits",
            "121 entropy bits", "1<->8", "checksum tool is allowed to calculate",
            "PREFER", "PEACE", "Exact 1/2,048",
        ]
        lowered = front_text.lower()
        for phrase in required:
            assert phrase.lower() in lowered, f"{edition}: missing front-matter phrase {phrase!r}"
        selector_page = pdf.pages[6].extract_text() or ""
        assert selector_page.count("NORMAL") == 32 and selector_page.count("MIRROR") == 32

        card_pages = pdf.pages[11:]
        assert len(card_pages) == expected_cards
        for offset, page in enumerate(card_pages):
            text = page.extract_text() or ""
            if edition == "Easy":
                card = offset // 2 + 1
                mode = "NORMAL" if offset % 2 == 0 else "MIRROR"
                assert f"CARD {card:03d}" in text and mode in text
                expected_indices = expected_easy(card, mode)
            else:
                card = offset + 1
                assert f"CARD {card:03d}" in text and "COMPACT" in text
                expected_indices = [card + 32 * k for k in range(64)]
            actual_indices = [int(value) for value in ordered_tokens(page, r"\d{4}")]
            assert actual_indices == expected_indices, f"{edition} card {card} coordinate/index sequence mismatch"
            actual_words = ordered_tokens(page, r"[a-z]+", min_top=100)
            expected_words = [WORDS[index - 1] for index in expected_indices]
            assert actual_words == expected_words, f"{edition} card {card} coordinate/word sequence mismatch"
    print(f"{edition.upper()} PDF OK: {expected_pages} pages; selector/finalization present; {expected_cards} card grids coordinate-checked")


def validate_imposed(path, reader_pages):
    padded = reader_pages + (-reader_pages % 4)
    expected_sides = padded // 2
    reader = PdfReader(path)
    assert len(reader.pages) == expected_sides
    for page in reader.pages:
        width = float(page.mediabox.width); height = float(page.mediabox.height)
        assert width > height, "imposed output must be A4 landscape"
    print(f"IMPOSITION OK: {os.path.basename(path)} has {expected_sides} A4-landscape sides")


def validate_worksheet(path, rows, final_phrase):
    with pdfplumber.open(path) as pdf:
        assert len(pdf.pages) == 1
        text = pdf.pages[0].extract_text() or ""
        assert WARNING_FRAGMENT in text
        assert final_phrase in text
        for row in range(1, rows + 1):
            assert re.search(rf"\b{row}\b", text)
    print(f"WORKSHEET OK: {os.path.basename(path)} has {rows} audit rows and sensitive-data warning")


WARNING_FRAGMENT = "SENSITIVE: A COMPLETED WORKSHEET CAN RECONSTRUCT"


def optional_online_wordlist_check():
    with urllib.request.urlopen(UPSTREAM_URL, timeout=10) as response:
        upstream = response.read().decode("utf-8").split()
    assert upstream == WORDS
    print("ONLINE WORDLIST OK: local order matches bitcoin/bips")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online-wordlist", action="store_true", help="also compare against bitcoin/bips (network required)")
    args = parser.parse_args()
    validate_math()
    validate_wordlist()
    validate_reader_pdf(os.path.join(ROOT, "2XD8_Entropy_Booklet_OppositeFold_Easy.pdf"), "Easy")
    validate_reader_pdf(os.path.join(ROOT, "2XD8_Entropy_Booklet_OppositeFold_Compact.pdf"), "Compact")
    validate_imposed(os.path.join(ROOT, "2XD8_Entropy_Booklet_OppositeFold_Easy_Print-at-Home.pdf"), 75)
    validate_imposed(os.path.join(ROOT, "2XD8_Entropy_Booklet_OppositeFold_Compact_Print-at-Home.pdf"), 43)
    validate_worksheet(os.path.join(ROOT, "2XD8_Entropy_Worksheet_24.pdf"), 23, "FINAL 3 ENTROPY BITS")
    validate_worksheet(os.path.join(ROOT, "2XD8_Entropy_Worksheet_12.pdf"), 11, "FINAL 7 ENTROPY BITS")
    if args.online_wordlist:
        try:
            optional_online_wordlist_check()
        except (urllib.error.URLError, TimeoutError) as error:
            raise SystemExit(f"online word-list check failed: {error}")
    print("ALL OFFLINE VALIDATION PASSED")


if __name__ == "__main__":
    main()
