# Toffoli target decomposition gap (C2)

## Source artifact (kernel-checked)

Native CCX on three qubits is at `kernel_checked_artifact_semantics`:

- `parseQasmSource_toffoli_kernel_eq_generated_ops`
- `bridge_toffoli_codegen_ccx` on codegen trace

## Target artifact (blocked)

Target QASM uses H, T, CX rotations outside the stub codegen gate set. Manifest records `target_ast_sha256: null`.

## Blocker for full equivalence claim

- Extend codegen gate set (H, T, RZ, CX) or independent certified decomposition parser.
- Kernel proof relating source CCX denotation to decomposed target trace.
- QCEC remains external; not sufficient alone for `kernel_checked_artifact_semantics` on the pair.

## Order

Complete source-side artifact semantics (done) before target decomposition codegen (C2), then pair equivalence (research / QCEC + Lean).
