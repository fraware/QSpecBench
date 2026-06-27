# Phase estimation recovers eigenphase (small instance)

## Claim

Phase estimation on a declared small unitary eigenstate reports the correct eigenphase bits in ideal semantics.

## Why this matters

Frontier-difficulty algorithm benchmark for eigenphase reasoning.

## Objects

- `artifacts/circuit.qasm`

## Specification

Fixed-size exact claim on measured phase bits.

## Evidence

- QASM syntax parse (passing)
- Lean 4 kernel: `phase_estimation_z_eigenvalue_on_one` (Z eigenvalue −1 on |1⟩)

## Trust boundary

**Checked:** QASM syntax; Z eigenvalue scaffold on computational |1⟩.

**Not checked:** full phase-estimation unitary; eigenphase bit recovery from circuit.

Semantic bridge: `documented_not_proved` — see `expected/semantic_bridge.json`.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Kernel-checked eigenphase relation on declared eigenstate
- Semantic bridge from QASM phase-estimation circuit to measured bits

## References

- Standard phase estimation presentation
