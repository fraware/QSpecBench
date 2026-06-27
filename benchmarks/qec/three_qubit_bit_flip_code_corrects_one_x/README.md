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

Decoder lookup tables checked by brute-force validator; general decoder algorithm not kernel-checked.

## Status

Current maturity: **reference_claim**.

## Known gaps

Syndrome extraction circuit; decoder proof.

## References

- (none yet)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
