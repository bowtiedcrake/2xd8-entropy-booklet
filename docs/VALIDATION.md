# Validation design

All release validation runs offline. The optional upstream word-list comparison is the only networked check and runs only when explicitly requested.

## Production implementation

`src/fold_mapping.py` is the canonical, range-checked implementation. `src/test_mapping.py` exhaustively tests:

- opposite involution and absence of fixed faces;
- the exact 8-by-8 selector table;
- selector complement pairs: same card, opposite mode;
- ranges over all 4,096 complete-word tuples;
- all 2,048 indices present with exactly two raw preimages each;
- complete-tuple complement invariance;
- 2,048 unique canonical outputs;
- NORMAL and MIRROR Easy page coordinate mappings;
- final-3 uniform counts and complement invariance;
- final-7 uniform counts and complement invariance over all `8^3 = 512` raw triples;
- local word-list length, uniqueness, digest, index round trips, and worked examples.

The booklet generator runs core invariant checks before it opens an output PDF.

## Independent validator

`src/validate.py` deliberately does not import `fold_mapping.py`. It re-derives canonicalization, selector mapping, full-word indexing, final-3 extraction, and final-7 extraction using separate code.

It then:

- enumerates all 4,096 raw full-word tuples;
- proves every index has exactly two preimages;
- checks every complete complement pair;
- verifies 2,048 unique canonical locations;
- validates all 64 selector cells and mode symmetry;
- checks final-3 has 8 outputs with 8 raw outcomes each;
- checks final-7 has 128 outputs with 4 raw outcomes each;
- verifies the checked-in word-list SHA-256;
- opens both reader PDFs and checks required operational/finalization text;
- checks all selector mode labels;
- locates all 64 printed index and word cells on every card page by PDF coordinates;
- compares Easy NORMAL cells to `(r,c)` and MIRROR cells to `(9-r,9-c)`;
- compares all Compact cells to the canonical grid;
- checks imposed page counts and A4 landscape orientation;
- checks worksheet row counts, final-bit sections, and sensitive-data warning.

PDF text/coordinate validation catches missing or misplaced data, while visual PNG inspection catches clipping, overlap, insufficient contrast, and hierarchy problems that extraction cannot detect.

## Checksum vectors

`tools/test_checksum_only.py` checks the official all-zero 128-bit and 256-bit BIP39 vectors:

- 12 words: eleven `abandon` groups plus physical tail `0000000` produce checksum `0011` and final word `about`.
- 24 words: twenty-three `abandon` groups plus physical tail `000` produce checksum `01100110` and final word `art`.

It also checks word/index parsing and rejects missing or nonbinary entropy tails.

## Commands

```bash
source .venv/bin/activate
cd src
python -m unittest test_mapping.py
python -m unittest discover -s ../tools -p 'test_*.py'
python validate.py
```

Optional network comparison:

```bash
python validate.py --online-wordlist
```

## Known local word-list digest

The digest includes the file's final newline:

```text
SHA-256  2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda
```
