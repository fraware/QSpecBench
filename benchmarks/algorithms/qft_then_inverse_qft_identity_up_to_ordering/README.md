# QFT then inverse QFT is identity up to ordering

## Claim

Applying QFT followed by inverse QFT yields the identity on the declared register up to bit-ordering conventions.

## Why this matters

Tests algorithm identity claims with ordering conventions explicit.

## Objects

- `artifacts/circuit.qasm`

## Specification

Exact algorithm identity; ordering conventions must be read from assumptions.

## Evidence

- QASM syntax parse (passing)
- Lean 4 kernel: `qft_then_inverse_qft_identity` (QFT·IQFT = 4I on 2-qubit scaffold)
- verify-bridge (`kernel_checked`) matrix match on declared circuit

## Trust boundary

**Checked:** QASM syntax; QFT identity theorem; OpenQASM3 denotation bridge on artifact.

**Not checked:** bit-ordering conventions beyond declared scaffold normalization.

Semantic bridge: `kernel_checked` — see `expected/semantic_bridge.json`.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- General n-qubit QFT ordering conventions beyond fixed 2-qubit instance

## References

- Standard QFT presentation
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
