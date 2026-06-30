# Single-qubit gate cancellation

## Claim

Consecutive inverse single-qubit gates on the same wire cancel to identity.

## Why this matters

Minimal equivalence pattern for compiler peephole rules.

## Objects

- `artifacts/source.qasm` — H H circuit (SHA256-bound; LF bytes)
- `artifacts/target.qasm` — identity

## Specification

Exact unitary equality on one qubit under the int-scaffold model.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.Quantum.OpenQASM3.bridge_hadamard_codegen_cancel` (passing)
- **Artifact parse chain**: `parseQasmSourceToOps hhKernelArtifactSource = some Generated.SingleQubitGateCancellation.ops`
- QCEC external equivalence (supplementary)
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| QASM bytes | `artifact_sha256` | provenance + Lean embedded source |
| Canonical AST | `lean_ast_sha256` (`ast_authority: lean_mirror`) | Lean-mirror parse |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Kernel claim | `theorem_elaborator_hash` (primary) | BridgeMetadata pins |

Honest limits: int-scaffold H-H cancellation; OpenQASM H normalization factor not checked under this headline.

## Status

Current maturity: **artifact_bound_reference_claim** (`kernel_checked_artifact_semantics`).

## Known gaps

- OpenQASM H normalization factor links integer matrix model to gate semantics
- Full OpenQASM 3 / hardware semantics

## References

- Standard inverse-gate cancellation
