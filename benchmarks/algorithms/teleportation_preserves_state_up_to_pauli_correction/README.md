# Teleportation preserves an unknown qubit up to Pauli correction

## Claim

The teleportation protocol transfers an arbitrary one-qubit pure state from Alice to Bob using one Bell pair and two classical bits that determine a Pauli correction on Bob's qubit.

## Why this matters

This is the canonical **relational** algorithm benchmark: correctness is a relation between input state, measurement outcomes, and corrected output — not merely a unitary factorization.

## Objects

- `artifacts/teleportation.qasm` — three-qubit teleportation circuit (q[0] input, q[1]/q[2] Bell pair)

## Specification

Fixed-size, exact, relational claim on pure states. Qubit ordering is explicit in preconditions. Resource contract: 3 qubits, 2 measurements, no T gates.

## Evidence

- QASM syntax check (passing; syntax only)
- Informal derivation in `notes/informal_derivation.md` (partial human review)
- Acceptable future evidence: Lean 4 kernel proof

## Trust boundary

QASM parsing is checked. Informal derivation and classical feed-forward semantics are **not** kernel-checked. This benchmark is **not** marked proved.

## Status

Current maturity: **usable**.

## Known gaps

- Kernel-checked proof in a proof assistant
- Fully expanded classically controlled Pauli corrections in QASM
- Semantic validation linking QASM to the relational specification

## References

- Standard teleportation presentation (Nielsen & Chuang)
