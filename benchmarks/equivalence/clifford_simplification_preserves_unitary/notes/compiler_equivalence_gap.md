# Compiler equivalence gap (Clifford simplification)

## Checked (kernel)

- [x] Source trace `clifford_hhs` matches QASM gate list (`source_trace_is_hhs`).
- [x] Target trace `clifford_s_single` matches simplified QASM (`target_trace_is_single_s`).
- [x] Complex denotation of each trace (`source_codegen_denotes_*`, `target_codegen_denotes_*`).
- [x] Scaled compiler identity `denotateOps1C clifford_hhs = 2 · denotateOps1C clifford_s_single`
      (`clifford_source_target_denotation_scaled`; unnormalized H·H = 2·I).

## Remaining gap (blocks `kernel_checked_codegen_trace` promotion)

- [ ] Exact matrix equality under declared normalization / global-phase policy.
- [ ] Dual-manifest hash chain treating source and target as one kernel bridge.
- [ ] Lean theorem `denotateOps1C clifford_hhs = denotateOps1C clifford_s_single` (false in complex model).

## External evidence

- QCEC equivalence on source/target QASM pair (see spec `qcec_equivalence`).
- `claimed_link` remains `manifest_checked_theorem_binding` until normalized-unitary policy closes the scale gap.
