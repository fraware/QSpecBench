# Three-qubit bit-flip code corrects one X error

## Claim

Single X error correction under explicit Pauli bit-flip model.

## Why this matters

Separates code definition, decoder assumption, and correction claim.

## Objects

- `artifacts/code.json` stabilizer specification

## Specification

Algebraic/circuit-level QEC claim with explicit error model.

## Evidence

- QEC JSON validator (structure only)

## Trust boundary

Lookup-table decoder kernel-checked in Lean (`bit_flip_lookup_decoder_correct`); brute-force
validator checks logical preservation. General decoder algorithm and syndrome-extraction circuits
not claimed.

## Status

Current maturity: **reference_claim** (lookup-table scope under single-X model).

## Known gaps

Syndrome extraction circuit semantics; general decoder beyond declared lookup tables.

## References

- (none yet)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
