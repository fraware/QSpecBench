# Claim diff: teleportation_preserves_state_up_to_pauli_correction

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
The teleportation circuit transfers an arbitrary one-qubit state to the receiver after applying the Pauli correction determined by the two classical measurement bits.

## Declared headline (claim_scope)
The teleportation circuit transfers an arbitrary one-qubit state to the receiver after applying the Pauli correction determined by the two classical measurement bits.

## Required obligations
- unitary_fragment_matches_ordering
- arbitrary_state_relational_transfer
- measurement_conditioned_pauli_correction

## Checked obligations
- [x] unitary_fragment_matches_ordering

## Unproved / open obligations
- [ ] arbitrary_state_relational_transfer
- [ ] measurement_conditioned_pauli_correction
- [ ] arbitrary_state_relational_transfer_after_measur
- [ ] idealized_measurement_semantics
- [ ] classical_feed_forward_control_semantics_in_qasm

## Gap (required but not checked)
- arbitrary_state_relational_transfer
- measurement_conditioned_pauli_correction

## Conflict
- Obligations appear in both required and unproved lists.
