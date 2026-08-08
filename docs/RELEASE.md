# Opposite-complement-fold edition release notes

This edition is based on upstream commit `34168e757ea1eba2a8eab2ac2187da593deb9c84` and replaces the upstream 5+6-bit discard mapping with a global physical-opposite complement fold.

## Procedure changes

- The actual first WHITE+BLACK roll selects both a card and explicit NORMAL/MIRROR mode from an 8-by-8 table.
- The primary Easy booklet has separate NORMAL and MIRROR pages for all 32 cards. Actual second-roll values are always used directly.
- Every raw four-reading tuple maps identically to its complete physical opposite, giving exactly two raw preimages per BIP39 word under the fair independent model.
- 24-word finalization now generates the missing 3 entropy bits physically before the 8-bit checksum.
- 12-word finalization now generates the missing 7 entropy bits physically before the 4-bit checksum.
- A deterministic checksum-only CLI, optional sensitive-data worksheets, independent validator, and Compact edition are included.

This changed procedure is not represented as endorsed by the upstream author.

## Reproducible artifact hashes

Two consecutive builds in the pinned local dependency environment produced identical SHA-256 values:

```text
bae7de0e756708a87b3010ff7611dc49088fa09906e34e2749d548806e4f36e4  2XD8_Entropy_Booklet_OppositeFold_Easy.pdf
fb0a3a7df4c0bec60a67b164cc77d489cf39ea87fdcb1e20c1daceae86c95e69  2XD8_Entropy_Booklet_OppositeFold_Easy_Print-at-Home.pdf
afb749f9a1e4a5ce881ec762e0828a9a3b96722fe75aa0a70374ecadb03774b1  2XD8_Entropy_Booklet_OppositeFold_Compact.pdf
dfef8533f5cdf996bc82bf34e72089d6ae102e529276e089a6bf7d680fbec2ac  2XD8_Entropy_Booklet_OppositeFold_Compact_Print-at-Home.pdf
9bddcbda92682b14ff68f7a76bae8b4f959e3b7310c4a524b17d297654736943  2XD8_Entropy_Worksheet_24.pdf
fe9f1640aadd4a42d61e3be44a8488d08f2657b6abdde0a0f332888e17a4f2d0  2XD8_Entropy_Worksheet_12.pdf
```

The dependency versions used are pinned in `src/requirements.txt`.
