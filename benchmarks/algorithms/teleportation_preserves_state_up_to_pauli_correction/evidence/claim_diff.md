# Claim diff: teleportation_preserves_state_up_to_pauli_correction

<!-- scope_fingerprint: a2ef0d7446f7227cb88a11b4219d3db796801d2afe04dde98106a9cbf4366499 -->

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
The teleportation circuit transfers an arbitrary one-qubit state to the receiver after applying the Pauli correction determined by the two classical measurement bits.

## Declared headline (claim_scope)
The declared teleportation QASM unitary prefix (Bell prep + entangling gates before measurement) matches the Lean/OpenQASM3 denotation; measurement and Pauli correction lines use projective POVM stub skips (not kernel-checked).

## Required obligations
- unitary_fragment_matches_ordering

## Checked obligations
- [x] unitary_fragment_matches_ordering

## Unproved / open obligations
- [ ] arbitrary_state_relational_transfer
- [ ] measurement_conditioned_pauli_correction
- [ ] arbitrary_state_relational_transfer_after_measur
- [ ] idealized_measurement_semantics
- [ ] classical_feed_forward_control_semantics_in_qasm

## Gap
- Headline not marked checked despite obligation coverage; review maturity label.
