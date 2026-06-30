# Compiler equivalence gap (Clifford simplification)

## Checked (kernel)

- [x] Source trace `clifford_hhs` matches QASM gate list (`source_trace_is_hhs`).
- [x] Target trace `clifford_s_single` matches simplified QASM (`target_trace_is_single_s`).
- [x] Complex denotation of each trace (`source_codegen_denotes_*`, `target_codegen_denotes_*`).
- [x] Scaled compiler identity `denotateOps1C clifford_hhs = 2 · denotateOps1C clifford_s_single`
      (`bridge_clifford_source_target_scaled`; unnormalized H·H = 2·I).
- [x] Normalized-unitary / global-phase policy documented (`notes/normalized_unitary_policy.md`).

## Remaining gap (blocks `kernel_checked_codegen_trace` promotion)

- [ ] Exact matrix equality under unnormalized complex model (false; scale factor 2 instead).
- [ ] Dual-manifest verify-bridge on both artifacts under single normalized gate model.
- [ ] Headline promotion beyond `manifest_checked_theorem_binding`.

## External evidence

- QCEC equivalence on source/target QASM pair (see spec `qcec_equivalence`).
- Physical unitary equivalence; kernel chain closes scaled relation only.
