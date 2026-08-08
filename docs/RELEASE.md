# Opposite-complement-fold edition release notes

This edition is based on upstream commit `34168e757ea1eba2a8eab2ac2187da593deb9c84` and replaces the upstream 5+6-bit discard mapping with a global physical-opposite complement fold.

## Procedure changes

- The actual first pair roll of WHITE and BLACK together selects both a card and explicit NORMAL/MIRROR mode from an 8-by-8 table.
- The primary Easy booklet has separate NORMAL and MIRROR pages for all 32 cards. Actual second-roll values are always used directly.
- Every raw four-reading tuple maps identically to its complete physical opposite, giving exactly two raw preimages per BIP39 word under the fair independent model.
- 24-word finalization now generates the missing 3 entropy bits physically before the 8-bit checksum.
- 12-word finalization now generates the missing 7 entropy bits physically before the 4-bit checksum.
- A deterministic checksum-only CLI, optional sensitive-data worksheets, independent validator, and Compact edition are included.

This changed procedure is not represented as endorsed by the upstream author.

## Reproducible artifact hashes

Two consecutive builds in the pinned local dependency environment produced identical SHA-256 values:

```text
adb7c9e0f20d6311cd2f5a75f743749f572985b7372be287e7b30805a3907f22  2XD8_Entropy_Booklet_OppositeFold_Easy.pdf
79acf6c89fdafaf23ec6bf8656875c7a19702f077160c5aa620a97f414fde852  2XD8_Entropy_Booklet_OppositeFold_Easy_Print-at-Home.pdf
36208903008f2dc8bf6954d8a9488f9435b0220e52817e34e6d0b0125d857857  2XD8_Entropy_Booklet_OppositeFold_Compact.pdf
a432faacea1478f65b549cda33a7b60c48a724b5853714729698ad6ad0071aae  2XD8_Entropy_Booklet_OppositeFold_Compact_Print-at-Home.pdf
a333a37e4cc547b7e5982f954f2b20d43d5fd8b3f881adff86ae9ebf9ab4704c  2XD8_Entropy_Worksheet_24.pdf
fe9f1640aadd4a42d61e3be44a8488d08f2657b6abdde0a0f332888e17a4f2d0  2XD8_Entropy_Worksheet_12.pdf
```

The dependency versions used are pinned in `src/requirements.txt`.
