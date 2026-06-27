# Teleportation preserves an unknown qubit up to Pauli correction

## Claim

The teleportation protocol transfers an arbitrary one-qubit pure state from Alice to Bob using one Bell pair and two classical bits that determine a Pauli correction on Bob's qubit.

## Why this matters

This is the canonical **relational** algorithm benchmark: correctness is a relation between input state, measurement outcomes, and corrected output — not merely a unitary factorization.

## Objects

- `artifacts/teleportation.qasm` — three-qubit teleportation circuit (q[0] input, q[1]/q[2] Bell pair)
- `artifacts/bell_prep_scaffold.qasm` — two-qubit Bell-pair fragment for semantic bridge verification

## Specification

Fixed-size, exact, relational claim on pure states. Qubit ordering is explicit in preconditions. Resource contract: 3 qubits, 2 measurements, no T gates. Postconditions distinguish kernel-checked unitary fragment from documented (unchecked) relational transfer.

## Evidence

- QASM syntax check on full circuit (passing)
- Lean 4 kernel: `teleportation_unitary_fragment_checked` and documented correction table (`evidence/teleportation.lean`)
- verify-bridge on Bell-prep scaffold (`kernel_checked` against OpenQASM3 denotation)
- Informal derivation in `notes/informal_derivation.md` (partial human review)

## Trust boundary

**Checked:** Bell-pair preparation denotation matches OpenQASM3; Alice entangling unitary fragment is nontrivial on declared ordering.

**Not checked:** arbitrary-state transfer after measurement; Pauli correction correctness; classical feed-forward in QASM; full relational protocol.

See `spec.yaml` `trust_boundary` and `proof_obligations` (`relational_protocol: partial`).

## Status

Current maturity: **reference_scaffold**.

## Known gaps

- Kernel-checked proof of full relational transfer for arbitrary `|ψ⟩`
- Fully expanded classically controlled Pauli corrections in QASM
- Three-qubit semantic bridge for the complete pre-measurement unitary

## References

- Standard teleportation presentation (Nielsen & Chuang)
## Claim diff

See evidence/claim_diff.md for declared vs checked obligation gap (Section C).
