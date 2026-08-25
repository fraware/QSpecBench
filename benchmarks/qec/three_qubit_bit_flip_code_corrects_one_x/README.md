# Three-qubit bit-flip code corrects one X error

## Claim

Under the declared single-X Pauli bit-flip error model, the standard lookup-table decoder corrects each single X error with logical preservation verified by Lean 4 kernel proof and brute-force validation.

## Why this matters

Separates code definition, decoder assumption, and correction claim.

## Objects

- `artifacts/code.json` stabilizer specification

## Specification

Algebraic/circuit-level QEC claim with explicit error model.

## Evidence

- QEC JSON validator (structure + syndrome/correction tables)
- Lean lookup-table decoder under single-X model
- Prefer-round1, three-round majority, and five-round majority matching FT fragments

## Trust boundary

Lookup-table decoder kernel-checked in Lean (`bit_flip_lookup_decoder_correct`); brute-force
validator checks logical preservation. OpenQASM ancilla syndrome denotation ≡ lookup is
kernel-checked under `DeclaredBitFlipNoiseModel` (ideal Z;
`syndrome_extraction_circuit_semantics`). Prefer-round1 covers
`{none, measFlipRound0S0, measFlipRound0S1}`; three-round majority covers all single
round-i S0/S1 flips; five-round majority matching covers declared dual same-bit flips
(three-round outside class). General decoder algorithm and full MWPM not claimed.

## Status

Current maturity: **experimental_closed** (lookup-table scope under single-X model).

## Known gaps

General decoder beyond declared lookup tables. Noisy measurement / gate-fault syndrome
extraction. Faults outside declared FT models (`full_mwpm_multi_round_ft` and related
outside-fault labels). Unbounded all-codes MWPM permanently not applicable.

## References

- (none yet)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
