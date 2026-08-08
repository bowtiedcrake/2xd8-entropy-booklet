#!/usr/bin/env python3
"""Known BIP39-vector and validation tests for checksum_only.py."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import checksum_only


class ChecksumOnlyTests(unittest.TestCase):
    def test_official_all_zero_128_bit_vector(self):
        result = checksum_only.finish([1] * 11, "0000000", 12)
        self.assertEqual(result.entropy_hex, "00" * 16)
        self.assertEqual(result.checksum_bits, "0011")
        self.assertEqual((result.final_index, result.final_word), (4, "about"))

    def test_official_all_zero_256_bit_vector(self):
        result = checksum_only.finish([1] * 23, "000", 24)
        self.assertEqual(result.entropy_hex, "00" * 32)
        self.assertEqual(result.checksum_bits, "01100110")
        self.assertEqual((result.final_index, result.final_word), (103, "art"))

    def test_words_and_indices_parse_identically(self):
        self.assertEqual(checksum_only.parse_prefix(["abandon"] * 11, 11), [1] * 11)
        self.assertEqual(checksum_only.parse_prefix(["1"] * 11, 11), [1] * 11)

    def test_rejects_missing_or_nonbinary_entropy(self):
        for value in ("", "000", "0000002", "00000000"):
            with self.assertRaises(ValueError):
                checksum_only.finish([1] * 11, value, 12)


if __name__ == "__main__":
    unittest.main()
