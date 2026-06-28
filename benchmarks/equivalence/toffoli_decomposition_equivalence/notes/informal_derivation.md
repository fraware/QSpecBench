# Informal derivation

Native CCX on three qubits (`artifacts/source.qasm`) is kernel-checked via
`bridge_ccx_single` / `bridge_toffoli_codegen_ccx` on the codegen gate trace.

The decomposed circuit pair (`source` vs `target`) is checked by QCEC external
equivalence only. Promoting decomposition equivalence to a kernel-checked
codegen-trace bridge on the full H/T/CX target circuit is **blocked**:

- Target circuit gate trace includes parameterized rotations not in the five kernel
  bridge QASM subset.
- Layout-identity and phase-polynomial bridges remain manifest-checked only.

See `expected/semantic_bridge.json` for hash-linked source CCX codegen (`ast_sha256`).
