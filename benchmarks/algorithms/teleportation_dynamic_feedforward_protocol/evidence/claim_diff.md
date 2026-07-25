# Claim diff: teleportation_dynamic_feedforward_protocol

<!-- scope_fingerprint: 5a6a97a5b2c7edd1e49c588e6cea1a2e2e35b869e5091cf4e924dd1798223ead -->

**Maturity:** artifact_bound_reference_claim
**Headline status:** checked

## Informal claim (README/spec)
The on-disk teleportation-with-feedforward QASM CanonicalAst measure and if AST nodes (gates, measurements, and classical controls) are bound to the Lean Measurement.writeZOutcome / ClassicalReg feed-forward denotation under kernel-checked dynamic denotation semantics.

## Declared headline (claim_scope)
The on-disk teleportation-with-feedforward QASM CanonicalAst measure and if AST nodes (gates, measurements, and classical controls) are bound to the Lean Measurement.writeZOutcome / ClassicalReg feed-forward denotation under kernel-checked dynamic denotation semantics.

## Required obligations
- dynamic_ast_fail_closed_mirror
- dynamic_denotation_bridge_metadata
- lean_dynamic_denotation_protocol
- dynamic_denotation_bridge_verify

## Checked obligations
- [x] dynamic_ast_fail_closed_mirror
- [x] dynamic_denotation_bridge_metadata
- [x] lean_dynamic_denotation_protocol
- [x] dynamic_denotation_bridge_verify
- [x] hardware_abstraction_isa_layer

## Unproved / open obligations

## Gap
- None among declared required obligations.
