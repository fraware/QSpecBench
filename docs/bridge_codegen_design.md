# OpenQASM-to-Lean bridge codegen design

Full **kernel_checked_artifact_semantics** (`kernel_checked_artifact_semantics`) requires Lean proofs
that the OpenQASM artifact denotes the same operator as the formal gate semantics — not merely a
manifest-listed theorem on a fixed gate trace.

## Current state (2026-06-27)

- **manifest_checked_theorem_binding**: allowlisted gate trace + Lean theorem name + SHA256 hashes
- **python_denotation_consistency**: Python matrix extractor matches Lean `denotateOps*` on trace
- **Codegen pilot (cnot_self_inverse_cancellation)**: canonical AST + `ast_sha256` +
  `generated_lean_sha256` wired in `bridge_theorem_manifest.json`; generated Lean stub at
  `evidence/cnot_self_inverse_cancellation_codegen_ops.lean`. `claimed_link` remains
  `manifest_checked_theorem_binding` — **not** upgraded to `kernel_checked_artifact_semantics`.
- **RX(π/2)**: `QasmOp.rx` + `ComplexGate.rxGate` wired; `bridge_rx_pi2_eq_h` proves complex
  denotation equals `hadamardC`. Global-phase equivalence to H and manifest binding remain blocked;
  `rx_gate_equivalence_small_instance` stays `reference_scaffold`.

## Target architecture

```mermaid
flowchart LR
  QASM["artifacts/*.qasm"] --> AST["QASM AST + ast_sha256"]
  AST --> Trace["Normalized gate trace"]
  Trace --> LeanGen["Generated Lean snippet"]
  LeanGen --> Proof["Kernel proof: trace denotation = artifact matrix"]
  Proof --> Bridge["semantic_bridge.claimed_link = kernel_checked_artifact_semantics"]
```

## Planned steps

1. **AST canonicalization** — stable JSON AST, `ast_sha256` in `bridge_theorem_manifest.json` (pilot done for CNOT)
2. **Codegen** — emit Lean `def <benchmark>_ops` from trace (parameterized gates: RX(θ), RZ(θ), U)
3. **Proof templates** — `denotateOpsN <benchmark>_ops = <matrix>` by `fin_cases` or tactic macro
4. **Hash pipeline** — `generated_lean_sha256`, CI drift check via `qspecbench bridge-codegen verify`
5. **Obligation wiring** — `obligation_ids` in manifest maps theorems to `claim_scope` entries
6. **First candidate** — `cnot_self_inverse_cancellation` retrofitted as codegen golden test (hashes wired; kernel proof gap documented)
7. **Second candidate** — parameterized RX(π/2) using `ComplexGate.rxGate` (Lean denotation done; manifest blocked on global phase)

## Gap to kernel_checked_artifact_semantics

The pilot proves nothing new in Lean: the hand-written `bridge_cnot_self_inverse` theorem on
`cnot_cx_cx` remains the checked link. Codegen validates that the QASM artifact parses to a stable
AST and emits a matching `QasmOp` list; a future kernel bridge must prove
`denotateOps2 <benchmark>_codegen_ops = <artifact_matrix>` without relying on a parallel hand-named op list.

## Out of scope for first kernel bridge

- Dynamic circuits (measurement, classical control)
- Full OpenQASM3 language
- Hardware calibration semantics

## RX(θ) blocker (rx_gate_equivalence_small_instance)

`bridge_rx_pi2_eq_h` shows `denotateOps1C rx_pi2_ops = hadamardC` entry-wise. Promoting to
`manifest_checked_theorem_binding` still requires:

1. Manifest entry with real RX gate trace + evidence anchor (not H-plumbing)
2. Closing `global_phase_between_rx_and_h` if headline claims phase equivalence

Until then, the benchmark stays `reference_scaffold` with `python_denotation_consistency` only.

## CI implications

- Run `qspecbench bridge-codegen verify` on entries with non-null codegen hashes
- Keeps separate from manifest binding job to avoid conflating trust levels

See [roadmap.md](roadmap.md) P1/P2 milestones.
