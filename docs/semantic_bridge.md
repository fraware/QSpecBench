# Semantic bridge (QASM ↔ Lean)

QSpecBench benchmarks that pair **OpenQASM artifacts** with **Lean 4 kernel proofs** declare an explicit semantic bridge so reviewers can inspect the artifact–proof link without inferring it from prose alone.

> **Honesty note.** `qspecbench verify-bridge` performs a **Python-level denotation-consistency
> check**: it confirms that the Python matrix extracted from the QASM artifact equals the matrix
> produced by the Python OpenQASM3 denotation model. It does **not** invoke the Lean kernel to tie the
> artifact to the named theorem. The corresponding `claimed_link` is therefore
> `python_consistency_checked`, **not** `kernel_checked`. There are currently **no** kernel-checked
> artifact-to-theorem bridges; `kernel_checked` is reserved for a future real kernel bridge.

## Files

| File | Role |
|------|------|
| `expected/semantic_bridge.json` | Machine-readable bridge declaration |
| `notes/semantic_bridge.md` | Human-readable explanation and normalization notes |

Both are optional but recommended whenever a benchmark has parallel QASM and Lean evidence.

## JSON format

```json
{
  "artifact_gate_model": "openqasm3_complex_unitary",
  "lean_module": "QSpecBench.Quantum.OpenQASM3",
  "lean_theorem": "bridge_cnot_self_inverse",
  "normalization": {
    "hadamard": "unnormalized_int_model",
    "qasm_factor": "1/sqrt(2) per gate"
  },
  "claimed_link": "python_consistency_checked"
}
```

### Fields

- **artifact_gate_model** — gate set / semantics assumed for QASM parsing or matrix extraction.
- **lean_module** — Lean namespace module containing the matrix model.
- **lean_theorem** — theorem name the bridge documents (anchoring, not kernel-checked by verify-bridge).
- **normalization** — free-form map documenting scaling conventions (especially for `H`).
- **claimed_link** — one of:
  - `documented_not_proved` (default): link explained in prose only.
  - `python_consistency_checked`: `qspecbench verify-bridge` confirms the Python QASM matrix equals the Python denotation model.
  - `kernel_checked`: reserved for a real Lean-kernel artifact-to-theorem bridge (not yet implemented; unused).

## Honesty rule

`claimed_link: documented_not_proved` remains appropriate when the Lean theorem is a scaffold that does not cover the full informal claim. Passing QCEC or SAT matrix certificates narrows the **practical** gap but does not alone upgrade the link. `python_consistency_checked` asserts only Python-side matrix consistency; it is **not** a kernel-checked proof that the artifact satisfies the named theorem.

## Complex unitary model (authoritative for phase gates)

The Python extractor (`tools/qspecbench/qasm_matrix.py`) and Lean module `QSpecBench.Quantum.ComplexGate` use a **complex unitary model** with exact rational entries where possible:

- Clifford gates (`H`, `X`, `Y`, `Z`, indexed `CX`, `SWAP`, `CCX`) match the integer scaffold on real parts.
- `S`, `T`, `Sdg`, `Tdg` use diagonal complex phases.
- `RX(θ)` uses standard `exp(-i θ/2 X)`; `θ = π/2` aligns with unnormalized `H` in the bridge tooling.

The legacy integer layer in `QSpecBench.Quantum.OpenQASM3.denotateGate` keeps `S`/`T` as identity stubs for backward-compatible Clifford-only proofs (e.g. `bridge_clifford_hhs`). **verify-bridge** uses the complex Python denotation path.

Implications:

- Set `claimed_link: python_consistency_checked` only when `qspecbench verify-bridge` passes on the declared QASM artifact.
- Document normalization in `expected/semantic_bridge.json` when decompositions include phase gates checked externally via QCEC.
- Use `documented_not_proved` when the Lean theorem scope is intentionally narrower than the README claim.

## Tooling

```bash
qspecbench verify-bridge benchmarks/equivalence/cnot_self_inverse_cancellation/
qspecbench extract-matrix artifacts/source.qasm --out expected/matrix.json
```

See [`tools/qspecbench/qasm_matrix.py`](../tools/qspecbench/qasm_matrix.py).

## Related

- [Trust boundaries](trust_boundaries.md)
- [Evidence model](evidence_model.md)
- [Equivalence track](equivalence_track.md)
