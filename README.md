# 2XD8 Entropy Booklet - Opposite-Complement Fold

This is a fork of [`bowtiedcrake/2xd8-entropy-booklet`](https://github.com/bowtiedcrake/2xd8-entropy-booklet), based on upstream commit `34168e757ea1eba2a8eab2ac2187da593deb9c84`.

It still uses two distinguishable d8 dice and a printed booklet, but it changes the 4,096-to-2,048 mapping. Each four-reading sequence is paired with the sequence obtained by replacing every face with its physical opposite: `1<->8`, `2<->7`, `3<->6`, `4<->5`.

The Easy edition encodes the entire transformation in printed NORMAL/MIRROR pages. Ordinary word generation requires no subtraction, binary arithmetic, modulo operation, rejection, or face conversion:

```text
ROLL
LOOK UP CARD + MODE
TURN TO THAT PAGE
ROLL
LOOK UP WORD
```

> Before use, physically inspect both dice. Their opposite faces must be `1<->8`, `2<->7`, `3<->6`, and `4<->5`. If either die differs, do not use this edition.

This fork changes the entropy mapping and is not the same procedure as the upstream booklet. It is not presented as endorsed by the upstream author.

## Artifacts

- `2XD8_Entropy_Booklet_OppositeFold_Easy.pdf` - primary A5 reader edition, with separate NORMAL and MIRROR pages for every card.
- `2XD8_Entropy_Booklet_OppositeFold_Easy_Print-at-Home.pdf` - Easy edition imposed two-up on A4 landscape.
- `2XD8_Entropy_Booklet_OppositeFold_Compact.pdf` - secondary/advanced A5 edition with dual coordinate labels.
- `2XD8_Entropy_Booklet_OppositeFold_Compact_Print-at-Home.pdf` - Compact edition imposed two-up on A4 landscape.
- `2XD8_Entropy_Worksheet_24.pdf` and `2XD8_Entropy_Worksheet_12.pdf` - optional consumable audit worksheets. A completed worksheet is as sensitive as the mnemonic entropy.
- `tools/checksum_only.py` - optional deterministic checksum-only helper. It contains no RNG and performs no network, wallet, key, or address operations.

The Easy edition is recommended. The Compact edition saves pages but asks the user to choose the coordinate labels for the recorded mode.

## Generate one complete 11-bit word

Use two visually distinguishable d8 dice with fixed roles: WHITE and BLACK.

1. Roll WHITE and BLACK together.
2. Cross the actual readings on CARD SELECT.
3. Record both the CARD and the full mode, NORMAL or MIRROR.
4. Turn to exactly that CARD/MODE page.
5. Roll WHITE and BLACK together again.
6. Use the actual WHITE result as row and actual BLACK result as column.
7. Record the word, and optionally its printed one-based BIP39 index.

On a MIRROR page the actual values are still used directly. The page data implements the complement; the user never calculates `9-x`.

If CARD/MODE or die roles are lost before a word is complete, discard that word attempt and restart it from the first pair roll.

## Correct BIP39 finalization

A final BIP39 word is not entirely checksum.

- A 24-word mnemonic has 256 entropy bits plus 8 checksum bits. The first 23 complete word indices contain 253 entropy bits. Generate the missing 3 entropy bits physically with the booklet's folded FINAL 3 BITS table, then calculate the checksum.
- A 12-word mnemonic has 128 entropy bits plus 4 checksum bits. The first 11 complete word indices contain 121 entropy bits. Generate the missing 7 entropy bits physically with the booklet's folded FINAL 7 BITS procedure, then calculate the checksum.

The checksum device/tool may hash completed entropy; it must not invent the remaining entropy bits or call an RNG.

> The checksum tool is allowed to calculate; it is not allowed to contribute randomness.

Example helper calls, using either one-based indices or BIP39 words:

```bash
python tools/checksum_only.py --length 12 --prefix \
  abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon \
  --final-bits 0000000

python tools/checksum_only.py --length 24 --prefix \
  1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 \
  --final-bits 000
```

## Why the full-word mapping is exactly uniform for fair dice

For raw readings `T = (W1,B1,W2,B2)`, define:

```text
C(T) = (9-W1, 9-B1, 9-W2, 9-B2)
```

`C` is an involution with no fixed points. It partitions the 4,096 raw tuples into 2,048 two-element classes. Canonicalization chooses the member whose first WHITE value is 1 through 4, then maps the resulting `4 x 8 x 8 x 8` canonical space bijectively to 32 cards by 8 rows by 8 columns. Every BIP39 index therefore has exactly two raw preimages, giving `2/4096 = 1/2048` under fair independent rolls.

This is an exact combinatorial proof of no modulo/rejection bias. It is distinct from the physical bias claim.

## What the fold can and cannot mitigate

If a small physical imbalance is approximately antisymmetric across opposite faces, its first-order contribution cancels when the probabilities of a tuple and its full physical opposite are added.

This is not a universal randomness extractor. It does not guarantee perfect output from arbitrary biased dice. Bias shared by the two faces in an opposite pair, pair-to-pair differences, correlations, changing distributions, deterministic or weak throwing technique, and malicious dice can remain. Exact `1/2048` probabilities require the fair, independent-roll model. See [docs/MATH.md](docs/MATH.md) and [docs/THREAT-MODEL.md](docs/THREAT-MODEL.md).

## Roll-quality and invalid-roll rule

- Use a hard, flat rolling surface or dice tray and ensure genuine tumbling.
- Decide the invalid-roll rule before starting.
- Recommended rule: if either die in a pair roll leaves the accepted area, is cocked, wedged, unreadable, or otherwise invalid, discard that entire pair roll and reroll both dice.
- Do not selectively reroll repetitions or patterns. Repeated values are valid.
- Do not restart because generated words look unusual.

## Reproducible offline build and validation

Python 3.11 or newer is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/requirements.txt

cd src
python gen_booklet.py
python gen_worksheet.py
python impose_booklet.py
python -m unittest test_mapping.py
python -m unittest discover -s ../tools -p 'test_*.py'
python validate.py
```

Offline validation checks the local word-list digest, all mathematical invariants, both final-bit extractors, every card grid in both PDFs, the imposed page geometry, and both worksheets. It does not need the internet. An explicitly optional comparison is available with `python validate.py --online-wordlist`.

The checked-in `src/english.txt` has SHA-256:

```text
2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda
```

See [docs/VALIDATION.md](docs/VALIDATION.md) for the independence boundary and exact checks.

## Printing and binding

Reader PDFs contain A5 portrait pages in reading order. The print-at-home PDFs impose them two-up on A4 landscape in single-signature saddle-stitch order.

- Duplex: print two-sided, flip on the short edge.
- Single-sided: print odd PDF pages; flip the whole stack left-to-right without rotating it; reload it the same way up; print even PDF pages.
- Fold the full stack in half and staple through the spine.
- Test one sheet first. Printer drivers vary, and scaling/cropping can hide critical labels.

The imposition pads each edition to a multiple of four A5 pages. In the Easy reader, CARD NORMAL pages start on even/left pages and their matching MIRROR pages follow on odd/right pages.

## Security

Statistical quality and secrecy are different. Do not photograph, cloud-sync, retain carelessly, or expose completed worksheets/notes. Use checksum hardware/software offline and verify that it accepts all user-generated entropy rather than silently replacing missing bits. See [docs/THREAT-MODEL.md](docs/THREAT-MODEL.md).

## Attribution and license

Forked from `bowtiedcrake/2xd8-entropy-booklet`, baseline commit `34168e757ea1eba2a8eab2ac2187da593deb9c84`, itself derived from the Seed Jar Method. Original repository history and attribution are preserved in Git.

Released under CC0 1.0; see `LICENSE`. Bundled Ubuntu Mono fonts retain their SIL Open Font License; see `src/fonts/LICENSE.md`.

Not financial advice. Use at your own risk.
