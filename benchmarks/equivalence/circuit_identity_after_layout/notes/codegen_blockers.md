# Codegen prep blockers

`circuit_identity_after_layout` has bridge-codegen `ast_sha256` on the source
H+CX trace. Kernel-checked codegen-trace promotion is **blocked**:

- Register rename / layout normalization proof is not wired to `Generated.*.ops`.
- `bridge_circuit_identity_after_layout` remains manifest-checked only.

See `expected/semantic_bridge.json` and `evidence/circuit_identity_after_layout_codegen_ops.lean`.
