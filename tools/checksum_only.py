#!/usr/bin/env python3
"""Deterministically finish a BIP39 checksum from already-generated entropy.

This program contains no RNG and makes no network or wallet calls. It accepts
11/23 complete BIP39 groups plus the user's physical final 7/3 entropy bits.
"""
import argparse
import hashlib
import os
from dataclasses import dataclass

HERE = os.path.dirname(os.path.abspath(__file__))
WORDLIST_PATH = os.path.join(os.path.dirname(HERE), "src", "english.txt")
WORDS = open(WORDLIST_PATH, encoding="utf-8").read().split()
WORD_TO_INDEX = {word: index for index, word in enumerate(WORDS, 1)}


@dataclass(frozen=True)
class Result:
    entropy_bits: str
    entropy_hex: str
    checksum_bits: str
    final_group: str
    final_index: int
    final_word: str


def parse_prefix(values, expected_count):
    if len(values) != expected_count:
        raise ValueError(f"expected exactly {expected_count} prefix words/indices, got {len(values)}")
    indices = []
    for value in values:
        if value.isdigit():
            index = int(value)
            if not 1 <= index <= 2048:
                raise ValueError(f"BIP39 index out of range: {value}")
        else:
            try:
                index = WORD_TO_INDEX[value.lower()]
            except KeyError as exc:
                raise ValueError(f"not an English BIP39 word: {value}") from exc
        indices.append(index)
    return indices


def finish(prefix_indices, final_entropy_bits, mnemonic_length):
    if mnemonic_length not in (12, 24):
        raise ValueError("mnemonic length must be 12 or 24")
    expected_prefix = 11 if mnemonic_length == 12 else 23
    expected_tail = 7 if mnemonic_length == 12 else 3
    checksum_length = 4 if mnemonic_length == 12 else 8
    if len(prefix_indices) != expected_prefix:
        raise ValueError(f"expected {expected_prefix} prefix indices")
    if len(final_entropy_bits) != expected_tail or set(final_entropy_bits) - {"0", "1"}:
        raise ValueError(f"final entropy must be exactly {expected_tail} binary digits")
    if any(isinstance(index, bool) or not isinstance(index, int) or not 1 <= index <= 2048 for index in prefix_indices):
        raise ValueError("each prefix index must be an integer from 1 through 2048")

    prefix_bits = "".join(f"{index - 1:011b}" for index in prefix_indices)
    entropy_bits = prefix_bits + final_entropy_bits
    expected_entropy_length = 128 if mnemonic_length == 12 else 256
    assert len(entropy_bits) == expected_entropy_length
    entropy_bytes = int(entropy_bits, 2).to_bytes(expected_entropy_length // 8, "big")
    digest_bits = f"{int.from_bytes(hashlib.sha256(entropy_bytes).digest(), 'big'):0256b}"
    checksum_bits = digest_bits[:checksum_length]
    final_group = final_entropy_bits + checksum_bits
    final_index = int(final_group, 2) + 1
    return Result(
        entropy_bits=entropy_bits,
        entropy_hex=entropy_bytes.hex(),
        checksum_bits=checksum_bits,
        final_group=final_group,
        final_index=final_index,
        final_word=WORDS[final_index - 1],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--length", type=int, choices=(12, 24), required=True, help="final mnemonic length")
    parser.add_argument("--prefix", nargs="+", required=True, help="11/23 one-based indices or English BIP39 words")
    parser.add_argument("--final-bits", required=True, help="physical final 7 bits (12 words) or 3 bits (24 words)")
    args = parser.parse_args()
    expected = 11 if args.length == 12 else 23
    try:
        prefix = parse_prefix(args.prefix, expected)
        result = finish(prefix, args.final_bits, args.length)
    except ValueError as error:
        parser.error(str(error))
    print("Entropy bits:", result.entropy_bits)
    print("Entropy hex: ", result.entropy_hex)
    print("Checksum:    ", result.checksum_bits)
    print("Final group: ", result.final_group)
    print("Final index: ", result.final_index)
    print("Final word:  ", result.final_word)


if __name__ == "__main__":
    main()
