# Operational dynamic semantics

QSpecBench separates three layers for circuits with measurement or classical control:

| Layer | Tooling | Kernel-checked? |
|-------|---------|-----------------|
| Unitary prefix (int scaffold) | `extract_matrix` + Lean `OpenQASM3` | Partial (manifest / kernel bridges on gate traces) |
| Unitary prefix (complex model) | Python complex matrices | Python bridge checks only |
| Measurement + feed-forward | `dynamic_simulator.py` | **No** — Python operational simulator |

## Wire indexing (important)

OpenQASM labels `q[i]` refer to bit `i` in the Python state index (`idx = Σ bit_q · 2^q`).
`dynamic_simulator.py` applies single-qubit gates and CNOT on the **same** wire indices.

The verify-bridge matrix extractor (`qasm_matrix._apply_single`) uses a legacy Kronecker order
aligned with Lean `kron2I` / `kronI2` for kernel-checked gate traces. Concretely:

| Model | Kronecker fold for 3 qubits, H on `q[0]` |
|-------|------------------------------------------|
| Operational (`dynamic_simulator._tensor_product_on_qubit`) | `kron(H, kron(I, I))` — wire 0 is **most significant** bit in the index |
| Int scaffold (`qasm_matrix._apply_single`) | `kron(kron(H, I), I)` — wire 0 is **least significant** bit |

CNOT and multi-qubit gates in verify-bridge use the same legacy convention as Lean
`denotateCX` / `applySingle2`. Branch-enumeration checks use the operational model;
manifest bridges remain on the int scaffold.

`tests/test_phase5.py::test_int_scaffold_vs_operational_h_on_q0_three_qubits` asserts the
H-on-`q[0]` matrices differ on a 3-qubit register (teleportation wire count). This is
**expected** and does not invalidate operational teleportation checks or kernel-checked
2-qubit bridges where both models agree.

## Teleportation benchmark

The artifact `teleportation.qasm` includes measurement but omits classically controlled Pauli
corrections (feed-forward is documented in `notes/informal_derivation.md`). A supplementary
artifact `teleportation_with_feedforward.qasm` (spec `role: witness`, supplementary feedforward) expands X/Z
corrections on `q[2]` and is wired for optional dynamic simulation:

```bash
qspecbench dynamic-simulate benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction \
  --teleport-basis-check \
  --feedforward \
  --out evidence/dynamic_simulation_feedforward.json
```

This path is **not** promoted to `reference_claim`; basis checks still apply documented
corrections in Python rather than parsing `if (c) x q[i];` from QASM.

`qspecbench dynamic-simulate --teleport-basis-check` runs a **branch-enumeration check** on
computational basis inputs `|0⟩` and `|1⟩` with the documented correction table:

| c[0] | c[1] | Correction on q[2] |
|------|------|---------------------|
| 0 | 0 | I |
| 0 | 1 | X |
| 1 | 0 | Z |
| 1 | 1 | Z, then X |

The primary check uses a **complex-normalized** unitary prefix (H scaled by `1/sqrt(2)` per gate)
under the OpenQASM-consistent wire model above.

### Current calibration

As of Phase 6, **`all_ok` is `true`** for basis inputs under
`gate_model: complex_normalized_unitary_prefix`. The int-scaffold diagnostic
(`int_scaffold_diagnostic`, mirroring verify-bridge) may still fail — that reflects the
legacy Kronecker convention, not a failure of the documented correction table under the
operational model.

Lean scope (`QSpecBench.Teleportation.teleportation_unitary_fragment_checked`) proves only that
the Alice entangling fragment is nontrivial on the declared wire ordering — not relational state
transfer after measurement. Projective-measurement scaffold: `QSpecBench.Quantum.Measurement`.

Evidence JSON includes `report_fingerprint`; `qspecbench validate` fails if the file is stale
vs regenerated simulation output.

## CLI

```bash
qspecbench dynamic-simulate benchmarks/algorithms/teleportation_preserves_state_up_to_pauli_correction \
  --teleport-basis-check \
  --out evidence/dynamic_simulation_basis_check.json
```

## Operational qubit limit

`dynamic_simulator.py` supports at most **4 qubits** (`MAX_OPERATIONAL_QUBITS`). Larger
registers raise `ValueError` at simulation time. `qspecbench validate` emits a **warning**
(not a hard failure) when a `semantics_base=dynamic_circuit` benchmark declares a QASM
artifact with more than four qubits.

## Fail-closed validation

`qasm_extraction.mode=full_dynamic_semantics` is accepted only as a legacy alias for
`dynamic_fragment_recording` when `semantics_base=dynamic_circuit` and explicit
`allowed_to_skip` includes measurement. Default remains `unitary_fragment` (fail-closed).
