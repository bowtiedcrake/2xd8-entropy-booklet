#!/usr/bin/env python3
"""Auditable opposite-complement mapping for the 2XD8 booklet.

Public indices are one-based, matching the numbering printed beside BIP39
words. Die faces are always the actual readings, in the range 1..8.
"""
from collections import Counter
from typing import Tuple

NORMAL = "NORMAL"
MIRROR = "MIRROR"
MODES = (NORMAL, MIRROR)


def _face(value: int, name: str = "face") -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 8:
        raise ValueError(f"{name} must be an integer from 1 through 8")
    return value


def _card(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 32:
        raise ValueError("card must be an integer from 1 through 32")
    return value


def _mode(value: str) -> str:
    if value not in MODES:
        raise ValueError(f"mode must be {NORMAL!r} or {MIRROR!r}")
    return value


def opposite(face: int) -> int:
    """Return the standard-d8 physical opposite of an actual face reading."""
    return 9 - _face(face)


def mode_for_first_white(w1: int) -> str:
    return NORMAL if _face(w1, "w1") <= 4 else MIRROR


def canonical_first_roll(w1: int, b1: int) -> Tuple[str, int, int]:
    """Return (mode, canonical white, canonical black) for the first pair."""
    w1 = _face(w1, "w1")
    b1 = _face(b1, "b1")
    mode = mode_for_first_white(w1)
    if mode == NORMAL:
        return mode, w1, b1
    return mode, opposite(w1), opposite(b1)


def canonicalize_word_rolls(w1: int, b1: int, w2: int, b2: int) -> Tuple[str, int, int, int, int]:
    """Fold a complete four-reading outcome into the W1<=4 half-space."""
    w1 = _face(w1, "w1")
    b1 = _face(b1, "b1")
    w2 = _face(w2, "w2")
    b2 = _face(b2, "b2")
    mode = mode_for_first_white(w1)
    if mode == NORMAL:
        return mode, w1, b1, w2, b2
    return mode, opposite(w1), opposite(b1), opposite(w2), opposite(b2)


def card_for_canonical_first(w1c: int, b1c: int) -> int:
    w1c = _face(w1c, "canonical w1")
    b1c = _face(b1c, "canonical b1")
    if w1c > 4:
        raise ValueError("canonical w1 must be from 1 through 4")
    return (w1c - 1) * 8 + b1c


def canonical_to_location(w1c: int, b1c: int, w2c: int, b2c: int) -> Tuple[int, int, int]:
    card = card_for_canonical_first(w1c, b1c)
    return card, _face(w2c, "canonical w2"), _face(b2c, "canonical b2")


def bip39_index(card: int, row: int, column: int) -> int:
    card = _card(card)
    row = _face(row, "row")
    column = _face(column, "column")
    offset = (row - 1) * 8 + (column - 1)
    return card + 32 * offset


def location_for_rolls(w1: int, b1: int, w2: int, b2: int) -> Tuple[int, int, int]:
    _, w1c, b1c, w2c, b2c = canonicalize_word_rolls(w1, b1, w2, b2)
    return canonical_to_location(w1c, b1c, w2c, b2c)


def index_for_rolls(w1: int, b1: int, w2: int, b2: int) -> int:
    return bip39_index(*location_for_rolls(w1, b1, w2, b2))


def selector_cell(w1: int, b1: int) -> Tuple[int, str]:
    mode, w1c, b1c = canonical_first_roll(w1, b1)
    return card_for_canonical_first(w1c, b1c), mode


def easy_page_index(card: int, mode: str, raw_w2: int, raw_b2: int) -> int:
    """Index printed at actual raw coordinates on an Easy card page."""
    card = _card(card)
    mode = _mode(mode)
    raw_w2 = _face(raw_w2, "raw w2")
    raw_b2 = _face(raw_b2, "raw b2")
    if mode == NORMAL:
        return bip39_index(card, raw_w2, raw_b2)
    return bip39_index(card, opposite(raw_w2), opposite(raw_b2))


def canonical_card_indices(card: int) -> Tuple[int, ...]:
    card = _card(card)
    return tuple(card + 32 * offset for offset in range(64))


def page_indices(card: int, mode: str) -> Tuple[int, ...]:
    return tuple(
        easy_page_index(card, mode, row, column)
        for row in range(1, 9)
        for column in range(1, 9)
    )


def final3_for_pair(white: int, black: int) -> str:
    """Fold one pair roll into one of eight three-bit strings."""
    card, _ = selector_cell(white, black)
    return f"{(card - 1) // 4:03b}"


def final7_parts(w1: int, b1: int, raw_w2: int) -> Tuple[int, str, str, str]:
    """Return (card, mode, row-pair bits, seven entropy bits)."""
    card, mode = selector_cell(w1, b1)
    raw_w2 = _face(raw_w2, "raw w2")
    canonical_w2 = raw_w2 if mode == NORMAL else opposite(raw_w2)
    row_pair_value = (canonical_w2 - 1) // 2
    bits2 = f"{row_pair_value:02b}"
    return card, mode, bits2, f"{card - 1:05b}{bits2}"


def final7_for_rolls(w1: int, b1: int, raw_w2: int) -> str:
    return final7_parts(w1, b1, raw_w2)[3]


def assert_core_invariants() -> None:
    """Fast exhaustive self-check used before any PDF is emitted."""
    counts = Counter()
    canonical = set()
    for w1 in range(1, 9):
        for b1 in range(1, 9):
            for w2 in range(1, 9):
                for b2 in range(1, 9):
                    folded = canonicalize_word_rolls(w1, b1, w2, b2)
                    mode, *values = folded
                    assert mode in MODES
                    canonical_tuple = tuple(values)
                    canonical.add(canonical_tuple)
                    index = index_for_rolls(w1, b1, w2, b2)
                    counts[index] += 1
                    assert index == index_for_rolls(
                        opposite(w1), opposite(b1), opposite(w2), opposite(b2)
                    )
    assert canonical == {
        (w1, b1, w2, b2)
        for w1 in range(1, 5)
        for b1 in range(1, 9)
        for w2 in range(1, 9)
        for b2 in range(1, 9)
    }
    assert set(counts) == set(range(1, 2049))
    assert set(counts.values()) == {2}

    counts3 = Counter(final3_for_pair(w, b) for w in range(1, 9) for b in range(1, 9))
    assert set(counts3.values()) == {8} and len(counts3) == 8

    counts7 = Counter(
        final7_for_rolls(w1, b1, w2)
        for w1 in range(1, 9)
        for b1 in range(1, 9)
        for w2 in range(1, 9)
    )
    assert set(counts7.values()) == {4} and len(counts7) == 128


assert_core_invariants()
