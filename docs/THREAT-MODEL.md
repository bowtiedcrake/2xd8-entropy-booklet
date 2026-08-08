# Threat model

This project separates three questions:

1. Is the printed mapping mathematically correct?
2. Are the physical readings statistically adequate?
3. Does the resulting entropy remain secret?

A success in one category does not imply success in the others.

## Physical dice and rolling

- **Biased dice:** the opposite fold can reduce a small antisymmetric opposite-face component. It does not eliminate arbitrary bias, pair-symmetric bias, or pair-to-pair differences.
- **Changing distributions:** a die whose behavior changes with surface, damage, temperature, or time is outside the fixed-distribution model.
- **Correlation:** repeated throws, paired dice collisions, a dice tower, or a consistent throwing motion can create correlation. The fold does not prove independence.
- **Weak technique:** placing or gently dropping a die can make outcomes predictable. Use a hard rolling area and genuine tumbling.
- **Selective rerolls:** rerolling repetitions or suspicious-looking values introduces human selection. Precommit an invalid-roll rule and apply it only to physical invalidity.
- **Nonstandard numbering:** if `9-x` is not the physical opposite relation on both actual dice, the intended physical model does not apply. Inspect both dice before use.

## Human procedure

- **Swapped die roles:** WHITE and BLACK must remain identifiable and fixed. If roles become uncertain during an incomplete word, discard that word attempt and restart it.
- **Wrong mode/page:** CARD and the full NORMAL/MIRROR mode are the only state carried between pair rolls. Easy pages repeat mode in the header and footer.
- **Transcription errors:** optional printed indices and worksheets support auditing. They do not protect against someone copying the notes.
- **Lost state:** never guess a lost CARD or MODE. Restart that word attempt.
- **Invalid rolls:** if either die in a pair is invalid under the rule chosen before starting, discard the entire pair roll and reroll both dice.

## Printed/software supply chain

- **Tampered booklet:** a malicious PDF can map outcomes nonuniformly or substitute words. Build from source, verify the local word-list hash, run the independent validator, and compare artifact hashes.
- **Wrong BIP39 list:** `src/english.txt` is checked for 2,048 unique entries, exact local SHA-256, and optional online equality with `bitcoin/bips`.
- **Printer scaling/cropping:** hidden row/column labels can cause lookup errors. Print a test sheet and inspect every edge before use.
- **Compromised checksum device:** it may alter entropy, invent missing bits, retain the mnemonic, or expose it. Use a deterministic offline tool/hardware flow that accepts the user's complete entropy.
- **Checksum device contributes entropy:** for 24 words, provide the physical final 3 entropy bits; for 12 words, provide the physical final 7. A device that silently chooses them changes the requested procedure.
- **Checksum helper scope:** the included helper only reconstructs entropy and computes SHA-256 checksum bits. It has no RNG, network call, wallet derivation, private-key derivation, or address derivation.

## Secrecy and records

A statistically sound mnemonic is not secure after disclosure.

- Do not photograph a completed worksheet or seed phrase.
- Do not place it in cloud notes, email, messaging, clipboard synchronization, or an online password manager.
- Treat roll logs, indices, words, and completed worksheets as sensitive; together they can reconstruct entropy.
- Destroy disposable notes securely or store them with seed-level physical protection.
- Be aware of cameras, microphones, windows, printers with retained jobs, and other observers.

The worksheets reduce transcription errors but are never mandatory permanent records.
