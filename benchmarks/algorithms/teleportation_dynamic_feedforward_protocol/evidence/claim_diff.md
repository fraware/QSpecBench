# Claim diff: teleportation_dynamic_feedforward_protocol

<!-- scope_fingerprint: e00dea073039f40a818db59d526d5977c620e259c22af33caad8c83b18130310 -->

**Maturity:** experimental_closed
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
- arbitrary_pure_state_instrument

## Checked obligations
- [x] dynamic_ast_fail_closed_mirror
- [x] dynamic_denotation_bridge_metadata
- [x] lean_dynamic_denotation_protocol
- [x] dynamic_denotation_bridge_verify
- [x] arbitrary_pure_state_instrument
- [x] hardware_abstraction_isa_layer

## Unproved / open obligations

## Gap
- None among declared required obligations.
