# Claim diff: teleportation_preserves_state_up_to_pauli_correction

<!-- scope_fingerprint: e63cb10c568013d3f4108698c25e37b747fa0e16454821a0be526cfdef9d2543 -->

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
The teleportation circuit transfers an arbitrary one-qubit state to the receiver after applying the Pauli correction determined by the two classical measurement bits.

## Declared headline (claim_scope)
The declared teleportation QASM unitary fragment matches the Lean/OpenQASM3 denotation on the Bell-prep wire ordering (measurement and Pauli correction semantics not checked).

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
