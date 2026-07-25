# Compiler equivalence gap (Clifford simplification) - closed

## Checked (kernel)

- [x] Source trace `clifford_hhs` matches QASM gate list (`source_trace_is_hhs`).
- [x] Target trace `clifford_s_single` matches simplified QASM (`target_trace_is_single_s`).
- [x] Complex denotation of each trace (`source_codegen_denotes_*`, `target_codegen_denotes_*`).
- [x] Artifact parse bounds for both artifacts
      (`parseQasmSource_clifford_kernel_eq_generated_ops`,
      `parseQasmSource_clifford_target_kernel_eq_generated_ops`).
- [x] Exact matrix equality under the normalized (physical-unitary) complex model
      (`bridge_clifford_source_target_normalized_exact`; `H . H = I` normalized).
- [x] Global-phase policy (`clifford_normalized_global_phase_policy_exact`,
      `EquivUpToGlobalPhase1` with phi = 0).
- [x] Wire-order policy (`clifford_normalized_pair_wire_order_trivial`; single-qubit register,
      no permutation ambiguity).
- [x] Dual-manifest `verify-bridge` on the source artifact under the normalized gate model
      (`kernel_checked_artifact_semantics`).

## Closed gap

The prior gap — exact matrix equality was **false** under the unnormalized integer model
(scale factor 2 from `H . H = 2 . I`) — is closed by declaring the headline under the
**normalized** (physical-unitary) denotation `denotateOps1C_normalized`, where `H . H = I`
holds exactly (`hadamardC_normalized_mul_self`). See `notes/normalized_unitary_policy.md` for
the full model comparison and promotion rationale.

The unnormalized scaled relation `bridge_clifford_source_target_scaled` remains kernel-checked
as a secondary, non-headline fact and is listed under `not_checked_under` /
`assumptions_not_checked` for the normalized headline.

## External evidence

- QCEC equivalence on source/target QASM pair (see spec `qcec_equivalence`).
- Physical unitary equivalence; kernel chain now closes exact equality under the normalized
  model matching QCEC's physical Hadamard convention.
