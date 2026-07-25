# Evidence model

Evidence supports a claim; only **checked** evidence with a declared checker can support a "proved" reading.

## Proof assistant policy

**Lean 4 is the currently supported proof assistant in CI.** Stub adapters exist for Coq, Rocq, and Isabelle (`coq_proof`, `rocq_proof`, `isabelle_proof`); they return `not_checked` until a kernel is configured. The evidence taxonomy is proof-assistant-neutral.

**Permanent policy (F-049):** Rocq and Isabelle adapters remain reserved stubs that
skip / `not_checked` in default CI. They must never gate corpus maturity. Optional
second-kernel work (e.g. Coq) is opt-in only; see GOVERNANCE and
[definition_of_completion.md](definition_of_completion.md) community criterion C3.

## Evidence types (schema enum)

| Type | Role | Typical trust |
|------|------|---------------|
| `lean_proof` | Lean 4 proof | `checked` |
| `smt_certificate` | SMT certificate | `checked` / `independently_checkable` |
| `sat_certificate` | SAT / small-instance certificate | `independently_checkable` |
| `qcec_result` | Circuit equivalence tool | `externally_trusted` |
| `qbricks_result` | External QBricks tool result | `externally_trusted` (fail-closed if tool missing) |
| `zx_certificate` | ZX normal-form certificate | `independently_checkable` |
| `qec_verifier_result` | QEC verifier / JSON validator | `externally_trusted` |
| `qasm_parse` | Syntax parse only | `externally_trusted` (syntax) |
| `matrix_certificate` | Independent matrix-equality certificate (no shared extraction path with the headline bridge) | `independently_checkable` |
| `simulation` | Numeric / sampling | `heuristic` |
| `human_review` | Expert review | `externally_trusted` |
| `ai_draft` | LLM-generated formalization | `untrusted` |
| `other` | Extension point | declare honestly |

`qbricks_result` / `zx_certificate` ship with adapters under `adapters/qbricks/` and
`adapters/zx/` (see historical note in `schema/discovery_evidence_types.json`).
`matrix_certificate` ships with an adapter under `adapters/matrix_certificate/`
(deliberately independent of `qasm_matrix` / `denotate` / `bridge_codegen` so it cannot
rubber-stamp a bridge bug shared by both sides of a headline claim).
**Adapters exist; still not a complete FV standard** — do not sole-ABRC on any of them.

## Checked evidence (Lean 4)

QSpecBench uses **Lean 4** for kernel-checked proofs in CI.

```
lean/
  lakefile.lean
  lean-toolchain
  QSpecBench/          -- proof modules
benchmarks/.../evidence/*.lean   -- evidence anchors
```

CI installs elan, runs `lake build`, then `qspecbench check-evidence`. Proofs containing `sorry` cannot pass.

Example reference: `cnot_self_inverse_cancellation` with `lean_proof` evidence.

## Tool-checked evidence

Specialized tools (QCEC, QEC JSON validator, QASM parser). **QASM parse is syntax only.**

## Heuristic evidence

Simulation and numeric scripts — **not proof**.

## AI-generated evidence

Always `untrusted` until independently checked and semantically reviewed.

## Status values

| Status | Meaning |
|--------|---------|
| `passing` | Checker succeeded |
| `failing` | Checker failed |
| `partial` | Incomplete support |
| `not_checked` | Not run |
| `draft` | Untrusted draft |

```bash
qspecbench check-evidence benchmarks/<track>/<claim_id>/
qspecbench check-evidence benchmarks/
```
