# RX gate equivalence

## Claim

Rx(pi/2) equals H up to global phase on one qubit for the declared instance.

## Why this matters

Parameterized gate equivalence instance.

## Objects

- source/target QASM

## Specification

Phase-aware equivalence declared.

## Evidence

QASM + QCEC.

## Trust boundary

spec.yaml

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Lean proof uses H scaffold; QASM trace is RX — **not eligible for kernel_checked** until traces align.
- Global phase between RX(π/2) and H is not checked.
- General Rx parameterization beyond π/2 instance is not covered.

## References

- (add references when promoting beyond usable)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
