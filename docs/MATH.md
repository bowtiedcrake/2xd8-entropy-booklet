# Mathematical specification

## Full-word partition proof

Let a raw complete-word outcome be:

```text
T = (W1, B1, W2, B2), each coordinate in {1,...,8}.
```

For a standard d8, define `o(x) = 9-x`, corresponding to the physical opposite face. Define the complete complement:

```text
C(T) = (o(W1), o(B1), o(W2), o(B2)).
```

`o(o(x)) = x`, so `C(C(T)) = T`. There is no integer die face satisfying `x = 9-x`, so `C(T) != T`. Thus `C` partitions all `8^4 = 4096` tuples into `4096/2 = 2048` unordered pairs.

Canonicalization chooses exactly one member from each pair: retain a tuple when `W1 <= 4`; otherwise replace all four coordinates by their opposites. A canonical tuple therefore lies in:

```text
W1c in 1..4
B1c in 1..8
W2c in 1..8
B2c in 1..8
```

There are `4 x 8 x 8 x 8 = 2048` canonical tuples. Map one bijectively to a printed location:

```text
card   = (W1c - 1) * 8 + B1c
row    = W2c
column = B2c
index  = card + 32 * ((row - 1) * 8 + column - 1)
```

This is a bijection from canonical tuples to `32 x 8 x 8 = 2048` locations and one-based BIP39 indices. Every output has precisely the two raw preimages `T` and `C(T)`. With independent fair dice:

```text
P(output) = 2 / 4096 = 1 / 2048.
```

There is no modulo reduction and no rejection boundary.

## Printed NORMAL and MIRROR pages

The first-roll selector uses actual values. If actual `W1 <= 4`, it reports NORMAL. Otherwise it reports MIRROR and selects the card corresponding to `(9-W1,9-B1)`.

On a NORMAL page, actual second-roll cell `(r,c)` prints the canonical location `(r,c)`. On a MIRROR page, actual cell `(r,c)` prints canonical location `(9-r,9-c)`. This is a 180-degree rotation of the canonical grid while the displayed die labels remain actual values 1 through 8.

The user performs no complement arithmetic.

## Folded final 3 bits

For one actual WHITE+BLACK pair, canonicalize the first roll as above and compute its card 1 through 32. The output is:

```text
value3 = floor((card - 1) / 4)
```

The 64 pair outcomes fold into 32 complementary pairs. Each of 8 values receives four canonical cards, hence 8 raw pair outcomes. Complementary raw pairs produce the same value.

## Folded final 7 bits

The complete raw sample space is `(W1,B1,W2) in {1,...,8}^3`, where `W2` is a WHITE-only second roll. The BLACK die is not rolled on the second step and no second BLACK result is used.

First canonicalize `(W1,B1)` to a card and mode. Let canonical second WHITE be `W2` in NORMAL or `9-W2` in MIRROR. Then:

```text
card5    = card - 1
rowPair2 = floor((canonicalW2 - 1) / 2)
value7   = (card5 << 2) | rowPair2
```

There are 512 raw triples. The complement on all three readings is fixed-point-free and invariant under the extractor. Each of 128 outputs has four raw preimages. Under the fair independent model every seven-bit value has probability `4/512 = 1/128`.

## Opposite-antisymmetric bias model

Let WHITE and BLACK face probabilities be `pW` and `pB`. A canonical output represented by `(a,b,c,d)` has probability:

```text
pW(a)pB(b)pW(c)pB(d)
+ pW(a')pB(b')pW(c')pB(d')
```

where each primed face is its physical opposite.

For a small antisymmetric opposite-face perturbation, write schematically:

```text
p(i)  = 1/8 + e_i
p(i') = 1/8 - e_i.
```

Expanding the two products shows their linear terms have opposite signs and cancel. Terms of second and higher order can remain.

This statement is deliberately limited. If both faces in an opposite pair become more likely together, that pair-symmetric deviation does not reverse sign and need not cancel. Pair-to-pair probability differences, roll correlation, nonstationarity, and technique-dependent outcomes can remain.

## No universal extractor claim

This fold is not a theorem that arbitrary biased dice become uniform. Generalized von Neumann, Elias, or Peres extraction is a different class of method with different assumptions and typically more variable roll counts and operational complexity. This edition chooses a direct-lookup, low-state physical procedure with exact fair-dice combinatorics and limited mitigation under the stated opposite-antisymmetric model.
