# Superdense coding decodes two classical bits

## Claim

A shared Bell pair and one qubit transmission let Bob decode two classical bits after a Bell measurement and Pauli correction.

## Why this matters

Introductory protocol linking entanglement, dense coding, and measurement semantics.

## Objects

- `artifacts/circuit.qasm` — superdense coding circuit scaffold

## Specification

Exact relational claim on decoded classical bits; fixed 2+1 qubit profile.

## Evidence

- QASM syntax parse (passing)
- Lean 4 kernel Bell-pair preparation scaffold (`superdense_bell_pair_entangled`)

## Trust boundary

**Checked:** QASM syntax; Bell-pair preparation matches teleportation Bell prep scaffold.

**Not checked:** two-bit decoding relation; measurement and Pauli frame.

Semantic bridge: `documented_not_proved` — see `expected/semantic_bridge.json`.

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Kernel-checked decoding relation (two classical bits → Bob's qubit state)
- Measurement semantics and correction frame

## References

- Standard superdense coding presentation
