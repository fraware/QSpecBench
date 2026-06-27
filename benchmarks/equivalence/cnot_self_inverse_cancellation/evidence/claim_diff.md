# Claim diff: cnot_self_inverse_cancellation

<!-- scope_fingerprint: 1d301c6ee53e9fc398e9e72bae3502f45006d6b1dc242f60bb80d427c2a0a351 -->

**Maturity:** reference_claim
**Headline status:** checked

## Informal claim (README/spec)
Two consecutive CNOT gates on the same control-target pair implement the identity on the declared two-qubit register.

## Declared headline (claim_scope)
Two consecutive CNOT gates on the same control-target pair implement the identity on the declared two-qubit register.

## Required obligations
- lean_kernel_proof
- semantic_bridge

## Checked obligations
- [x] lean_kernel_proof
- [x] semantic_bridge

## Unproved / open obligations
- [ ] matrix_model_matches_qasm_semantics_for_all_inst
- [ ] general_n_qubit_extension_of_cancellation_rule

## Gap
- None among declared required obligations.
