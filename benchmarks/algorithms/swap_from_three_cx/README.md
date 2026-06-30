# SWAP from three CNOT gates

## Claim

Three CNOT gates in standard order implement SWAP on two qubits.

## Why this matters

Standard circuit identity for routing and compilation tracks.

## Objects

- `artifacts/source.qasm` — three CX gates (SHA256-bound; LF bytes)
- `artifacts/target.qasm` — SWAP

## Specification

Exact unitary equivalence on two qubits under the declared gate subset.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.Quantum.OpenQASM3.bridge_swap_from_three_cx_codegen` (passing)
- **Artifact parse chain**: `parseQasmSourceToOps swapKernelArtifactSource = some Generated.SwapFromThreeCx.ops`
- QCEC external equivalence (supplementary)
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| QASM bytes | `artifact_sha256` | provenance + Lean embedded source |
| Canonical AST | `lean_ast_sha256` (`ast_authority: lean_mirror`) | Lean-mirror parse |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Kernel claim | `theorem_elaborator_hash` (primary) | BridgeMetadata pins |

Honest limits: declared gate subset only; not general n-qubit or full OpenQASM 3.

## Status

Current maturity: **artifact_bound_reference_claim** (`kernel_checked_artifact_semantics`).

## Known gaps

- Unitary equivalence beyond declared gate subset
- Full OpenQASM 3 / hardware semantics

## References

- Standard three-CX SWAP construction
