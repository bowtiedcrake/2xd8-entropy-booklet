# 2XD8 Entropy Booklet

*Offline BIP39 Entropy*

A fork of the [Seed Jar Method](https://github.com/bowtiedcrake/seed-jar-method-d8) that drops the jar and the printed
tickets entirely. One A5 booklet, one pair of distinguishable d8 dice. No
cutting, no jar, no printer run beyond the one that made this booklet.

> ⚠️ **Read the whole booklet before using this for real funds.** Same as the
> jar method: these pages produce *raw entropy only* — the valid final
> (checksum) word must be computed by a hardware wallet or an offline tool.

---

## How it's different from the Seed Jar Method

The jar method spends one blind ticket-draw (5 bits) plus one d8 double-roll
(6 bits) per word. This fork has no tickets to draw, so the same two dice do
that job too: **roll the pair twice per word instead of once.**

1. **Roll 1 — card select.** White die read openly (1–8, 3 bits); Black die
   read only as a pair — 1/2, 3/4, 5/6, or 7/8 (2 bits). Cross them on the
   CARD SELECT page to get a card, 1–32.
2. **Roll 2 — word select.** White = row, Black = column, full 8×8 on that
   card (6 bits).

5 + 6 = 11 bits = 1-of-2048, same uniform math as the jar method — just
sourced from four die reads instead of a draw plus two die reads.

**The honest tradeoff:** this roughly doubles the number of physical die
rolls per word (4 rolls vs. 2 rolls + 1 draw) in exchange for removing every
piece of jar/ticket hardware and the caveats that came with it (ticket
tells, shake quality, sourcing an opaque container). Pick whichever fork
suits you — this one is for "I don't want to print, cut, or carry a jar,"
not for "fewest possible dice rolls." That one's still the jar method.

---

## Contents

- `2XD8_Entropy_Booklet.pdf` — the whole product: cover, short guide,
  card-select table, and all 32 word-grid cards, one A5-portrait page each.
- `src/` — the generator (`gen_booklet.py`), the wordlist, fonts, and an
  independent validator, forked from the jar method's `src/`.

There is no tickets generator in this fork — there's nothing to cut.

---

## The math (why it's uniform)

- Card select: White's full 8 values (3 bits) × Black collapsed into 4 equal
  pairs (2 bits) = 5 bits → 1-of-32 cards.
- Word select: White × Black, full 8×8 on that card = 6 bits → 1-of-64 cells.
- 5 + 6 = **11 bits = 1-of-2048**, exactly uniform, no modulo bias.

Card *n* holds BIP39 indices `n + 32·k` for `k = 0…63`, same mapping as the
jar method, so all 2048 words appear exactly once across the 32 cards.

Why White and Black must stay fixed roles across **both** rolls: if they
were swapped mid-process, or indistinguishable, outcomes that should be
distinct would collapse together and break uniformity — same argument as
the jar method's row/column dice, just now applying to two rolls instead
of one.

---

## What you need

- This booklet, printed and bound (see [Printing & binding](#printing--binding)).
- **Two distinguishable eight-sided dice (d8)** — one always White, one
  always Black, never swapped.
- A compatible **hardware wallet** with a "generate from dice / enter your
  own entropy" feature (e.g. Blockstream Jade, BitBox02), **or** an offline
  BIP39 tool for the final checksum word.
- A pen and paper.

---

## Step-by-step: generating a seed

Decide your length first: a **12-word** seed needs **11** drawn words; a
**24-word** seed needs **23**.

For **each** word:

1. Turn to the **CARD SELECT** page.
2. Roll both dice. Read White openly, 1–8. Read Black only as a pair:
   1/2, 3/4, 5/6, or 7/8.
3. Cross White against the Black-pair on the table to get a card number,
   1–32. Turn to that card.
4. Roll both dice again. White gives the row (1–8); Black gives the column
   (1–8).
5. Read the word at that row/column and write it down.
6. Repeat from step 2.

> Roll hard — from a cup or against a wall. Dice barely tumble on a soft
> surface, so a weak roll is weak randomness.

---

## The checksum step

Same as the jar method, unchanged: **the cards produce raw entropy only —
never the finished mnemonic.** Draw the first 11 (or 23) words with the
booklet, then let a hardware wallet or offline BIP39 tool compute the valid
final checksum word. **Never** hand-pick, guess, or re-roll only the last
word — that silently destroys uniformity. Do this step air-gapped.

---

## Verify it yourself (don't trust, verify)

```bash
cd src
pip install -r requirements.txt        # reportlab (+ pdfplumber for validation)
python gen_booklet.py                  # -> ../2XD8_Entropy_Booklet.pdf
python validate.py                     # independent check of the finished PDF
```

The generator refuses to output unless: exactly 32 cards, 64 cells each,
every index 1–2048 present exactly once, and the card-select table covers
1–32 exactly once. `validate.py` re-opens the finished PDF and confirms all
2048 words/indices and the full card-select table actually rendered, and
diffs `src/english.txt` word-for-word against the upstream `bitcoin/bips`
wordlist.

---

## Printing & binding

Every page is a single A5-portrait (148×210mm) sheet — cover, guide, the
card-select table, and each of the 32 cards. Print single-sided on
cardstock or heavy paper and bind however you like (saddle-stitch, comb, a
binder ring through the left edge) — nothing about the layout assumes a
particular binding method.

### Printing it as an actual folded booklet

`2XD8_Entropy_Booklet_Print-at-Home.pdf` is a second, separate PDF (never
overwrites the reader PDF) built by `src/impose_booklet.py`: it reorders and
pairs the reader pages two-up onto A4-landscape sheets in standard
saddle-stitch order, padding to a multiple of 4 with blank A5 pages at the
end. Fold the whole printed stack in half at once and staple through the
spine — the pages come out in order.

```bash
cd src
python impose_booklet.py               # -> ../2XD8_Entropy_Booklet_Print-at-Home.pdf
```

How to print it:
- **Duplex printer:** turn on two-sided printing, flip on the **short**
  edge, print the whole file once.
- **Single-sided printer:** print **odd** pages only, flip the entire
  printed stack over left-to-right (like turning a page — don't rotate
  it), reload it the same way up, then print **even** pages only.

Do a single test sheet before running a full batch of copies to confirm
your printer's flip convention matches.

---

## Caveats & honest limitations

- **d8 quality.** Cheap dice have some bias. Roll hard; for larger sums,
  casino-grade dice are marginally better.
- **More rolls than the jar method.** See
  [How it's different](#how-its-different-from-the-seed-jar-method) — this
  fork trades roll-count for zero jar/ticket hardware, not the other way
  around.
- **Same-dice, two-meanings discipline.** White and Black mean different
  things on the card-select roll vs. the word-select roll. Don't mix up
  which roll you're on mid-word.
- **This is a hobbyist tool.** Not a certified RNG. Understand each step
  before securing meaningful value.

---

## Credits

The 1–32 card-select table — the White/Black-pair → card-number mapping
used on the CARD SELECT page — was created by
[@FieldNas](https://x.com/FieldNas) on X. Used here with thanks.

---

## License

Released under **CC0 1.0** (public domain dedication) — see `LICENSE`.
Print, fork, adapt, and share freely. Bundled fonts are under the SIL Open
Font License; see `src/fonts/` for details.

*Not financial advice. Use at your own risk.*
