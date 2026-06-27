# Deutsch–Jozsa distinguishes constant from balanced oracles

## Claim

The Deutsch–Jozsa circuit accepts constant oracles and rejects balanced ones for the declared small instance.

## Why this matters

Oracle-based algorithm benchmark with explicit oracle semantics.

## Objects

- `artifacts/circuit.qasm` — DJ circuit with oracle placeholder

## Specification

Oracle-based, fixed-size exact decision claim on measurement outcome. Oracle is a placeholder in the scaffold circuit.

## Evidence

- QASM syntax parse (passing)
- Lean 4 kernel: `dj_constant_oracle_hadamard_square` (Hadamard-square scaffold on query qubit)

## Trust boundary

**Checked:** QASM syntax; Hadamard-layer scaffold (`H² = 2I` on query qubit).

**Not checked:** constant vs balanced oracle distinction; oracle placeholder semantics.

Semantic bridge: `documented_not_proved` — see `expected/semantic_bridge.json`.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Kernel-checked oracle distinction for constant vs balanced functions
- Semantic bridge from QASM circuit to DJ decision claim

## References

- Standard Deutsch–Jozsa presentation
