# Claim diff: teleportation_preserves_state_up_to_pauli_correction

<!-- scope_fingerprint: 34a61be02bf60260f8be508e994e583f8cd4460ceb78920305286e4fb3ac7980 -->

**Maturity:** artifact_bound_reference_claim
**Headline status:** checked

## Informal claim (README/spec)
Under the Lean 4 kernel OpenQASM3 denotation, the measure-free artifact teleport-unitary-prefix.qasm parses to Generated.TeleportationUnitaryPrefix.ops and matches the declared unitary-prefix gate list (bridge-teleport-unitary-prefix-codegen).

## Declared headline (claim_scope)
Under the Lean 4 kernel OpenQASM3 denotation, the measure-free artifact teleport-unitary-prefix.qasm parses to Generated.TeleportationUnitaryPrefix.ops and matches the declared unitary-prefix gate list (bridge-teleport-unitary-prefix-codegen).

## Required obligations
- unitary_fragment_matches_ordering
- semantic_bridge

## Checked obligations
- [x] unitary_fragment_matches_ordering
- [x] semantic_bridge
- [x] openqasm_measure_assignment_denotation
- [x] arbitrary_complex_state_transfer_normalized_h
- [x] alice_normed_povm_quarter
- [x] declared_dynamic_fragment_protocol
- [x] dynamic_feedforward_artifact_canonical_ast
- [x] dynamic_feedforward_artifact_protocol_linked
- [x] dynamic_ast_fail_closed_mirror
- [x] dynamic_ast_bridge_metadata

## Unproved / open obligations

## Gap
- None among declared required obligations.
