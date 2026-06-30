# CNOT self-inverse cancellation

## Claim

Two consecutive CNOT gates on the same control-target pair implement the identity on the declared two-qubit register.

## Why this matters

Minimal **equivalence** benchmark for compiler peephole optimization with an independently checkable certificate on a fixed instance.

## Objects

- `artifacts/source.qasm` — CX.CX circuit (SHA256-bound; LF bytes)
- `artifacts/target.qasm` — empty circuit (identity)
- `evidence/unitary_equality.certificate.json` — checkable certificate

## Specification

Exact unitary equality; no ancillae, garbage, measurements, or parameterized gates. Qubit ordering: `q[0]` control, `q[1]` target.

## Evidence

- QASM syntax checks (passing; syntax only)
- **Lean 4 kernel proof** `QSpecBench.Quantum.OpenQASM3.bridge_cnot_codegen_self_inverse` (passing; checked via `lake build`)
- **Artifact parse chain**: `parseQasmSourceToOps cnotKernelArtifactSource = some Generated.CnotSelfInverse.ops` (Lean kernel)
- **Wire-order lemma**: `cnot_wire_order_models_agree_on_two_qubits` (2-qubit register only)
- Independently checkable unitary certificate (supplementary)
- `qspecbench bridge-codegen verify` + `qspecbench bridge-metadata verify` (CI)

## Trust boundary / checker chain

| Stage | Anchor | Checked by |
|-------|--------|------------|
| QASM bytes | `artifact_sha256` | provenance + Lean `cnotKernelArtifactSource` byte match |
| Gate trace | `gate_trace_sha256` | Python extractor |
| Canonical AST | `ast_sha256` | codegen verify |
| Generated ops | `generated_lean_sha256` | lake build + manifest |
| Parse → ops | `artifact_parse_theorem` | Lean `OpenQASM3Parser` |
| Kernel claim | `theorem_source_statement_hash`, `theorem_elaborator_hash` | BridgeMetadata pins |

Honest limits: int-scaffold matrix model only; not full OpenQASM 3; not general n-qubit rule.

## Status

Current maturity: **artifact_bound_reference_claim** (`kernel_checked_artifact_semantics` bridge label).

## Known gaps

- General n-qubit proof in a proof assistant
- QCEC integration in CI for larger instances
- Global wire-order equivalence beyond 2-qubit CNOT (3-qubit H-on-q0 counterexample documented)

## References

- Standard self-inverse property of CNOT
