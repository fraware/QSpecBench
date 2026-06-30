# Toffoli target decomposition gap (C2)

## Source artifact (kernel-checked)

Native CCX on three qubits is at `kernel_checked_artifact_semantics`:

- `parseQasmSource_toffoli_kernel_eq_generated_ops`
- `bridge_toffoli_codegen_ccx` on codegen trace

## Target artifact (partial)

Target QASM parse/codegen bound via `parseQasmSource_toffoli_target_kernel_eq_generated_ops`.
Complex denotation scaffold: `denotateOps3C` on target trace (H/T/CX).

## Blocker for full equivalence claim

- Lean pair theorem relating source CCX to decomposed target trace (exact or documented global phase).
- QCEC remains external; not sufficient alone for closed kernel pair chain.

## Order

Source-side artifact semantics (done) → target codegen parse (done) → pair equivalence (open; QCEC + partial Lean).
