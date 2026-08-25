# Native CCX artifact denotes Toffoli unitary

## Claim

The declared native CCX artifact denotes the standard three-qubit Toffoli unitary under the declared finite matrix semantics.

## Why this matters

Establishes the kernel-checked native CCX denotation anchor before any source/target decomposition equivalence claim.

## Objects

- `artifacts/source.qasm` — native CCX on three qubits (SHA256-bound; LF bytes)

## Specification

The declared native CCX artifact denotes the standard three-qubit Toffoli unitary under the declared finite matrix semantics.

## Evidence

- QASM syntax check (passing; syntax only)
- Lean 4 kernel proof `QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccx` (passing)
- Artifact parse chain: `parseQasmSourceToOps toffoliKernelArtifactSource = some Generated.ToffoliDecompositionEquivalence.ops`
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| Source QASM bytes | `artifact_sha256` | provenance + Lean `toffoliKernelArtifactSource` |
| Canonical AST | `lean_ast_sha256` (`ast_authority: lean_mirror`) | Lean-mirror parse on source |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Kernel claim | `theorem_elaborator_hash` (primary) | BridgeMetadata pins |

Honest limits: native CCX source artifact only; H/T/CX decomposition equivalence is a separate scaffold benchmark.

## Status

Current maturity: **experimental_closed** (`kernel_checked_artifact_semantics`).

## Known gaps

- Full OpenQASM 3 / hardware semantics
- Decomposition pair equivalence (tracked under `toffoli_decomposition_equivalence`)

## References

- Standard Toffoli / CCX gate semantics
