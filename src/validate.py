#!/usr/bin/env python3
"""Independent post-generation check: confirm the booklet PDF contains the full data set."""
import os, re, sys, urllib.request, urllib.error
HERE = os.path.dirname(os.path.abspath(__file__))
try:
    import pdfplumber
except ImportError:
    sys.exit("pip install pdfplumber to run validation")

CARD_COUNT = 32
UPSTREAM_WORDLIST_URL = "https://raw.githubusercontent.com/bitcoin/bips/master/bip-0039/english.txt"

words = set(open(os.path.join(HERE, "english.txt")).read().split())
assert len(words) == 2048

def check_booklet(path):
    fi, fw = set(), set()
    selector_nums = set()
    card_pages = 0
    saw_selector = False
    with pdfplumber.open(path) as pdf:
        assert len(pdf.pages) >= 1 + CARD_COUNT + 1, "booklet is missing guide/selector/card pages"
        for pg in pdf.pages:
            t = pg.extract_text() or ""
            if "CARD SELECT" in t:
                saw_selector = True
                for m in re.finditer(r'\b(\d{1,2})\b', t):
                    v = int(m.group(1))
                    if 1 <= v <= CARD_COUNT:
                        selector_nums.add(v)
            if re.search(r'CARD \d{3} OF 032', t):
                card_pages += 1
                for m in re.finditer(r'\b(\d{4})\b', t):
                    v = int(m.group(1))
                    if 1 <= v <= 2048: fi.add(v)
                for tok in re.findall(r'[a-z]+', t):
                    if tok in words: fw.add(tok)
    assert saw_selector, "card-select table page not found"
    assert card_pages == CARD_COUNT, f"expected {CARD_COUNT} word-grid card pages, found {card_pages}"
    assert len(fi) == 2048, f"cards: expected 2048 indices, found {len(fi)}"
    assert len(fw) == 2048, f"cards: expected 2048 words, found {len(fw)}"
    # The selector table's own row/pair numbers (1-8) alias with card numbers 1-8, so a plain
    # digit scan can't isolate exactly the 32 card values -- this is a presence floor, not a
    # substitute for the generator's own selector-table assertion (see gen_booklet.py).
    assert selector_nums == set(range(1, CARD_COUNT + 1)), \
        f"card-select table: expected values 1..{CARD_COUNT} to appear, found {sorted(selector_nums)}"
    print(f"BOOKLET OK: card-select table present, all {CARD_COUNT} word-grid cards present, "
          f"all 2048 words + indices found")

def check_wordlist_matches_upstream():
    local = open(os.path.join(HERE, "english.txt")).read().split()
    try:
        with urllib.request.urlopen(UPSTREAM_WORDLIST_URL, timeout=10) as resp:
            upstream = resp.read().decode("utf-8").split()
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"WORDLIST CHECK SKIPPED: could not reach upstream ({e})")
        return
    if local == upstream:
        print("WORDLIST OK: src/english.txt matches upstream bitcoin/bips english.txt (order included)")
    else:
        diffs = [(i, a, b) for i, (a, b) in enumerate(zip(local, upstream), 1) if a != b]
        assert local == upstream, (
            f"src/english.txt diverges from upstream: {len(local)} vs {len(upstream)} words, "
            f"first mismatch at index {diffs[0] if diffs else 'length mismatch'}"
        )

check_booklet(os.path.join(HERE, "..", "2XD8_Entropy_Booklet.pdf"))
check_wordlist_matches_upstream()
print("ALL VALIDATION PASSED")
