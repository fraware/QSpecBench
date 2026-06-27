# Grover single-iteration amplitude amplification

## Claim

One Grover iteration increases the measurement probability of a marked basis state for a declared small instance.

## Why this matters

Amplitude amplification benchmark for probabilistic algorithmic claims.

## Objects

- `artifacts/circuit.qasm`

## Specification

Probabilistic exact claim on measurement distribution after one iteration.

## Evidence

- QASM syntax parse (passing)
- Lean 4 kernel: `grover_diffuser_nontrivial` (diffuser scaffold `H·X·H` is nontrivial)

## Trust boundary

**Checked:** QASM syntax; Grover diffuser matrix scaffold is nontrivial.

**Not checked:** probability lift on marked state; oracle and measurement semantics.

Semantic bridge: `documented_not_proved` — see `expected/semantic_bridge.json`.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Kernel-checked amplitude amplification on declared marked basis state
- Oracle and measurement semantics linked to QASM artifact

## References

- Standard Grover search presentation
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
