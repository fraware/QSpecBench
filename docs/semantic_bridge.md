# Semantic bridge

A **semantic bridge** ties a QASM artifact to a Lean theorem name. It does **not** by itself
prove that the artifact satisfies the theorem — it documents what link is claimed and what
evidence supports it.

> **Current corpus (v0.1.0):** eleven bridges use `manifest_checked_theorem_binding`
> (manifest + theorem reference + hash anchors, **not** full artifact semantics).
> Three bridges use `python_denotation_consistency` (Python matrix vs denotation model only).
> `kernel_checked_artifact_semantics` is reserved; **none qualify yet**.

## Bridge taxonomy

| `claimed_link` | Meaning |
|---|---|
| `documented_not_proved` | Lean theorem is named; no automated matrix/manifest check |
| `python_denotation_consistency` | `qspecbench verify-bridge` confirms Python QASM matrix equals Python denotation |
| `manifest_checked_theorem_binding` | Manifest allowlist + SHA256 anchors + structured Lean `#check` evidence |
| `kernel_checked_artifact_semantics` | Reserved: real Lean-kernel proof that artifact semantics satisfy theorem |

`manifest_checked_theorem_binding` is **not** a kernel-checked proof that the QASM artifact
satisfies the named theorem end-to-end. It checks manifest membership, hash stability, and an
exact Lean evidence anchor — not full OpenQASM3 or hardware semantics.

## Example (`expected/semantic_bridge.json`)

```json
{
  "artifact_gate_model": "openqasm3_1q2q_clifford",
  "gate_model": "qspecbench.openqasm3.int_scaffold.v0",
  "lean_module": "QSpecBench.Quantum.OpenQASM3",
  "lean_theorem": "bridge_cnot_self_inverse",
  "normalization": { "cnot": "standard_01_control_target" },
  "claimed_link": "manifest_checked_theorem_binding",
  "qasm_artifact": "artifacts/source.qasm",
  "artifact_sha256": "...",
  "gate_trace_sha256": "..."
}
```

## Lean evidence anchor (required for manifest bridges)

Passing `lean_proof` evidence for a manifest bridge must include:

```lean
/- QSpecBench evidence:
benchmark_id = "cnot_self_inverse_cancellation"
obligation_id = "semantic_bridge"
theorem = "QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse"
artifact_sha256 = "..."
gate_trace_sha256 = "..."
-/

#check QSpecBench.Quantum.OpenQASM3.bridge_cnot_self_inverse
```

The validator requires **exact** anchor field matches and an **exact** `#check` line.

## When to use each link

- `documented_not_proved`: scaffold theorem; QCEC/SAT may narrow practical gap but do not upgrade the link.
- `python_denotation_consistency`: Python-side matrix consistency only; set when `verify-bridge` passes.
- `manifest_checked_theorem_binding`: manifest entry + hashes + anchor; still not full semantic proof.
- `kernel_checked_artifact_semantics`: unused until a real artifact-semantics kernel bridge exists.
