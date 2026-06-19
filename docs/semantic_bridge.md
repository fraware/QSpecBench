# Semantic bridge (QASM ↔ Lean)

QSpecBench benchmarks that pair **OpenQASM artifacts** with **Lean 4 kernel proofs** declare an explicit semantic bridge so reviewers can inspect the artifact–proof link without inferring it from prose alone.

## Files

| File | Role |
|------|------|
| `expected/semantic_bridge.json` | Machine-readable bridge declaration |
| `notes/semantic_bridge.md` | Human-readable explanation and normalization notes |

Both are optional but recommended whenever a benchmark has parallel QASM and Lean evidence.

## JSON format

```json
{
  "artifact_gate_model": "openqasm3_1q2q_clifford",
  "lean_module": "QSpecBench.Pauli",
  "lean_theorem": "hadamard_conjugates_x",
  "normalization": {
    "hadamard": "unnormalized_int_model",
    "qasm_factor": "1/sqrt(2) per gate"
  },
  "claimed_link": "documented_not_proved"
}
```

### Fields

- **artifact_gate_model** — gate set / semantics assumed for QASM parsing or matrix extraction.
- **lean_module** — Lean namespace module containing the matrix model.
- **lean_theorem** — theorem name anchoring the kernel-checked claim.
- **normalization** — free-form map documenting scaling conventions (especially for `H`).
- **claimed_link** — one of `documented_not_proved` (default) or `kernel_checked` when a formal QASM semantics proof exists.

## Honesty rule

`claimed_link: documented_not_proved` remains the default until a real OpenQASM semantics formalization exists in Lean. Passing QCEC or SAT matrix certificates narrows the **practical** gap but does not upgrade the link to `kernel_checked`.

## Integer scaffold limitations (S/T gates)

The Lean module `QSpecBench.Quantum.OpenQASM3` uses an **integer matrix scaffold** for kernel-checked composition proofs. Clifford gates (`H`, `X`, `Y`, `Z`, `CX`, `SWAP`, `CCX`) denotate to the expected integer models on fixed small instances.

**S, T, Sdg, and Tdg are identity stubs** in Lean (`denotateGate .S => id2`, etc.). Phase on \(|1\rangle\) is not represented in the integer model. The Python matrix extractor uses complex arithmetic and matches OpenQASM semantics for phase gates; Lean bridge theorems that include S/T therefore prove **Clifford-only equivalence** (e.g. `H·H·S` equals `H·H` in the scaffold), not full phase-correct unitary equality.

Implications:

- Do not set `claimed_link: kernel_checked` on benchmarks whose QASM artifacts rely on non-trivial S/T phase unless the bridge theorem and verify step are scoped to the stub model.
- Document normalization in `expected/semantic_bridge.json` when Toffoli or other decompositions include T gates checked only via QCEC externally.
- Prefer QCEC or SAT certificates for phase-sensitive equivalence; use Lean bridges for Clifford subsets or instances where S/T are absent or provably cancel.

## Tooling

Use matrix extraction to compare QASM artifacts with Lean integer models:

```bash
qspecbench extract-matrix artifacts/source.qasm --out expected/matrix.json
```

See [`tools/qspecbench/qasm_matrix.py`](../tools/qspecbench/qasm_matrix.py).

## Related

- [Trust boundaries](trust_boundaries.md)
- [Evidence model](evidence_model.md)
- [Equivalence track](equivalence_track.md)
