#!/usr/bin/env python3
"""Exhaustive tests for the opposite-complement edition."""
from collections import Counter
import hashlib
import itertools
import os
import unittest

import fold_mapping as mapping

HERE = os.path.dirname(os.path.abspath(__file__))
WORDS = open(os.path.join(HERE, "english.txt"), encoding="utf-8").read().split()


class MappingTests(unittest.TestCase):
    def all_word_rolls(self):
        return itertools.product(range(1, 9), repeat=4)

    def test_opposite_is_involution(self):
        for face in range(1, 9):
            self.assertEqual(mapping.opposite(mapping.opposite(face)), face)

    def test_opposite_has_no_fixed_points(self):
        for face in range(1, 9):
            self.assertNotEqual(mapping.opposite(face), face)

    def test_input_ranges_are_checked(self):
        for invalid in (0, 9, -1, 1.5, True, "1"):
            with self.assertRaises(ValueError):
                mapping.opposite(invalid)
        with self.assertRaises(ValueError):
            mapping.bip39_index(33, 1, 1)
        with self.assertRaises(ValueError):
            mapping.easy_page_index(1, "NORMAL-ish", 1, 1)

    def test_canonical_first_white_is_1_to_4(self):
        for w, b in itertools.product(range(1, 9), repeat=2):
            _, wc, bc = mapping.canonical_first_roll(w, b)
            self.assertIn(wc, range(1, 5))
            self.assertIn(bc, range(1, 9))

    def test_selector_exact_table(self):
        expected_cards = [
            [1, 2, 3, 4, 5, 6, 7, 8],
            [9, 10, 11, 12, 13, 14, 15, 16],
            [17, 18, 19, 20, 21, 22, 23, 24],
            [25, 26, 27, 28, 29, 30, 31, 32],
            [32, 31, 30, 29, 28, 27, 26, 25],
            [24, 23, 22, 21, 20, 19, 18, 17],
            [16, 15, 14, 13, 12, 11, 10, 9],
            [8, 7, 6, 5, 4, 3, 2, 1],
        ]
        for w, row in enumerate(expected_cards, 1):
            expected_mode = mapping.NORMAL if w <= 4 else mapping.MIRROR
            self.assertEqual(
                [mapping.selector_cell(w, b)[0] for b in range(1, 9)], row
            )
            self.assertEqual(
                [mapping.selector_cell(w, b)[1] for b in range(1, 9)],
                [expected_mode] * 8,
            )

    def test_selector_complement_pairs_same_card(self):
        for w, b in itertools.product(range(1, 9), repeat=2):
            card, _ = mapping.selector_cell(w, b)
            opposite_card, _ = mapping.selector_cell(mapping.opposite(w), mapping.opposite(b))
            self.assertEqual(card, opposite_card)

    def test_selector_complement_pairs_opposite_mode(self):
        for w, b in itertools.product(range(1, 9), repeat=2):
            _, mode = mapping.selector_cell(w, b)
            _, opposite_mode = mapping.selector_cell(mapping.opposite(w), mapping.opposite(b))
            self.assertNotEqual(mode, opposite_mode)

    def test_all_4096_outputs_in_range(self):
        for rolls in self.all_word_rolls():
            card, row, column = mapping.location_for_rolls(*rolls)
            index = mapping.index_for_rolls(*rolls)
            self.assertIn(card, range(1, 33))
            self.assertIn(row, range(1, 9))
            self.assertIn(column, range(1, 9))
            self.assertIn(index, range(1, 2049))

    def test_all_2048_indices_present(self):
        indices = {mapping.index_for_rolls(*rolls) for rolls in self.all_word_rolls()}
        self.assertEqual(indices, set(range(1, 2049)))

    def test_exactly_two_preimages_per_index(self):
        counts = Counter(mapping.index_for_rolls(*rolls) for rolls in self.all_word_rolls())
        self.assertEqual(set(counts), set(range(1, 2049)))
        self.assertEqual(set(counts.values()), {2})

    def test_complete_tuple_complement_invariance(self):
        for rolls in self.all_word_rolls():
            complemented = tuple(mapping.opposite(face) for face in rolls)
            self.assertEqual(mapping.index_for_rolls(*rolls), mapping.index_for_rolls(*complemented))

    def test_canonical_space_has_2048_unique_outputs(self):
        outputs = {
            mapping.bip39_index(mapping.card_for_canonical_first(w1, b1), w2, b2)
            for w1 in range(1, 5)
            for b1 in range(1, 9)
            for w2 in range(1, 9)
            for b2 in range(1, 9)
        }
        self.assertEqual(outputs, set(range(1, 2049)))

    def test_card_decomposition_is_complete(self):
        indices = [
            index
            for card in range(1, 33)
            for index in mapping.canonical_card_indices(card)
        ]
        self.assertEqual(sorted(indices), list(range(1, 2049)))

    def test_easy_normal_page_mapping(self):
        for card, row, column in itertools.product(range(1, 33), range(1, 9), range(1, 9)):
            self.assertEqual(
                mapping.easy_page_index(card, mapping.NORMAL, row, column),
                mapping.bip39_index(card, row, column),
            )

    def test_easy_mirror_page_mapping(self):
        for card, row, column in itertools.product(range(1, 33), range(1, 9), range(1, 9)):
            self.assertEqual(
                mapping.easy_page_index(card, mapping.MIRROR, row, column),
                mapping.bip39_index(card, 9 - row, 9 - column),
            )

    def test_final3_uniform_counts(self):
        counts = Counter(mapping.final3_for_pair(w, b) for w, b in itertools.product(range(1, 9), repeat=2))
        self.assertEqual(set(counts), {f"{value:03b}" for value in range(8)})
        self.assertEqual(set(counts.values()), {8})

    def test_final3_complement_invariance(self):
        for w, b in itertools.product(range(1, 9), repeat=2):
            self.assertEqual(
                mapping.final3_for_pair(w, b),
                mapping.final3_for_pair(mapping.opposite(w), mapping.opposite(b)),
            )

    def test_final7_uniform_counts(self):
        # Complete sample space: first White + Black pair, then White alone = 8^3 outcomes.
        counts = Counter(
            mapping.final7_for_rolls(w1, b1, w2)
            for w1, b1, w2 in itertools.product(range(1, 9), repeat=3)
        )
        self.assertEqual(set(counts), {f"{value:07b}" for value in range(128)})
        self.assertEqual(set(counts.values()), {4})

    def test_final7_complement_invariance(self):
        for rolls in itertools.product(range(1, 9), repeat=3):
            complemented = tuple(mapping.opposite(face) for face in rolls)
            self.assertEqual(mapping.final7_for_rolls(*rolls), mapping.final7_for_rolls(*complemented))

    def test_wordlist_has_2048_unique_words(self):
        self.assertEqual(len(WORDS), 2048)
        self.assertEqual(len(set(WORDS)), 2048)
        digest = hashlib.sha256(("\n".join(WORDS) + "\n").encode()).hexdigest()
        self.assertEqual(digest, "2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda")

    def test_index_to_word_roundtrip(self):
        for index in range(1, 2049):
            word = WORDS[index - 1]
            self.assertEqual(WORDS.index(word) + 1, index)

    def test_worked_examples(self):
        self.assertEqual(mapping.selector_cell(2, 7), (15, mapping.NORMAL))
        self.assertEqual(mapping.index_for_rolls(2, 7, 6, 3), 1359)
        self.assertEqual(WORDS[1358], "prefer")
        self.assertEqual(mapping.selector_cell(7, 2), (15, mapping.MIRROR))
        self.assertEqual(mapping.index_for_rolls(7, 2, 3, 8), 1295)
        self.assertEqual(WORDS[1294], "peace")


if __name__ == "__main__":
    unittest.main()
