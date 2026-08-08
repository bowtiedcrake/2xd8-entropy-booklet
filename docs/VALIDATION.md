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

## Comparative bias analysis (upstream vs opposite fold)

Independent exact-enumeration analysis contributed by Kimi K3 (AI assistant, model `opencode-go/kimi-k3`), 2026-08-08. The comparison target is the upstream baseline recorded in `docs/UPSTREAM-BASELINE.md`. The analysis scripts are ad-hoc and external to this repository; the method and results are recorded here so the comparison is reproducible.

### Method

- Both mappings were re-implemented independently and enumerated over all 4,096 raw tuples. No sampling; distributions are exact.
- The fork re-implementation was checked against `src/fold_mapping.py` (`index_for_rolls`) on every tuple. The upstream re-implementation reproduces the upstream worked example (WHITE 3, BLACK 6 selects card 11).
- Bias models apply per-face probability deviations to each die. Rolls are independent and identically distributed; dice are independent of each other.
- Metrics: total variation distance (TVD) from uniform over the 2,048 words, worst-word probability ratio, and per-word min-entropy loss in bits. Seed figures scale the per-word figure by 23 complete words.

### Findings

Per-word min-entropy loss. Deviation `e` is an absolute probability; `e = 0.01` is about +/-8% relative per face. "Heavy face" means one face at `1/8 - e` and its physical opposite at `1/8 + e` (opposite-antisymmetric density model).

| Bias model | Upstream | Opposite fold |
|---|---|---|
| Heavy face, `e = 0.01` | 0.222 bits (~5.1 bits/seed) | 0.009 bits (~0.21 bits/seed) |
| Heavy face, `e = 0.04` | 0.801 bits (~18.4 bits/seed) | 0.141 bits (~3.2 bits/seed) |
| Heavy face on both dice, different faces, `e = 0.01` | 0.390 bits | 0.054 bits |
| Brick die (one opposite pair favored), `e = 0.01` | 0.222 bits | 0.222 bits (identical; no gain) |
| Heavy face with deficit spread over all 7 faces, `e = 0.01` | 0.033 bits worst case | identical worst case; ~27% lower TVD |
| Mixed heavy + brick, `e = 0.01` | 0.327 bits | 0.122 bits |
| Random bias on both dice, 3,000 draws, max deviation 0.01 | mean 0.330 bits | mean 0.207 bits; better at median and p95; worse in ~2% of draws |

Under the pure opposite-antisymmetric model the fold's residual is exactly quadratic (x4.00 per doubling of `e`), confirming exact cancellation of all odd-order terms. The folded FINAL 3 BITS table is exactly unbiased (TVD 0) under that model because its output classes are complement-closed per coordinate; FINAL 7 BITS retains the same quadratic residual as the full-word mapping.

### Interpretation

- The fold removes the bias component that is antisymmetric across physical opposite faces (the density/loading model) at first order and at every odd order. The leading residual is second order.
- Pair-symmetric (geometric) bias is untouched: results identical to upstream.
- Generic random bias is reduced on average, not in every draw.
- The cancellation requires the standard opposite-face numbering on both dice, fixed distributions, and independent rolls.
- This analysis compares statistical robustness only. It changes no validation invariant above, and neither scheme extracts randomness from arbitrarily biased dice.
