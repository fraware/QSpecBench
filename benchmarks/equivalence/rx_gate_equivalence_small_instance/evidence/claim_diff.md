# Claim diff: rx_gate_equivalence_small_instance

<!-- scope_fingerprint: 42c274ec45f77f6c49af0e2009e17b89b235bb5bbc7839c19792c917b14e499c -->

**Maturity:** reference_scaffold
**Headline status:** partially_checked

## Informal claim (README/spec)
Rx(pi/2) equals H up to global phase on one qubit for the declared instance.

## Declared headline (claim_scope)
Rx(pi/2) complex denotation matches the declared OpenQASM rotation matrix; equivalence to H is int-scaffold only (global phase not checked).

## Required obligations
- lean_kernel_proof
- semantic_bridge

## Checked obligations
- [x] lean_kernel_proof
- [x] semantic_bridge

## Unproved / open obligations
- [ ] openqasm_rx_parameter_semantics_beyond_pi_2_inst
- [ ] global_phase_between_rx_and_h

## Gap
- Headline not marked checked despite obligation coverage; review maturity label.
