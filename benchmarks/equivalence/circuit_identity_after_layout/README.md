# Circuit identity after layout

## Claim

Renaming qubit registers preserves circuit unitary under declared layout map.

## Why this matters

Layout/compiler track sanity check.

## Objects

- source/target QASM

## Specification

Exact equivalence under relabeling.

## Evidence

QASM + QCEC.

## Trust boundary

spec.yaml

## Status

Current maturity: **reference_scaffold**.

## Known gaps

Layout map not formally verified in Lean.

## References

- (add references when promoting beyond usable)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
