# Equivalence Track

## Purpose

Encode source-target equivalence claims for circuits, compiler passes, and transformations.

## Accepted claim types

Unitary equivalence, phase equivalence, distribution equivalence, approximate equivalence under a metric.

## Accepted artifacts

At minimum two artifacts per claim: `source` and `target` QASM (or formal objects).

## Accepted evidence

QASM parse (syntax only), QCEC results, SAT-style certificates, kernel-checked semantic bridges.

## Good first claims

- `cnot_self_inverse_cancellation` (introductory, experimental_closed; former ABRC demoted for v1; checkable certificate retained)
- `rx_gate_equivalence_small_instance` (introductory, reference_scaffold)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| circuit_identity_after_layout | introductory | reference_scaffold | Auto-synced from spec.yaml |
| clifford_simplification_preserves_unitary | advanced | experimental_closed | Auto-synced from spec.yaml |
| cnot_self_inverse_cancellation | introductory | experimental_closed | Auto-synced from spec.yaml |
| hadamard_conjugates_x_to_z | intermediate | experimental_closed | Auto-synced from spec.yaml |
| native_ccx_artifact_denotes_toffoli_unitary | intermediate | experimental_closed | Auto-synced from spec.yaml |
| phase_polynomial_equivalence_small_instance | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| qft_inverse_qft_small_instance | intermediate | experimental_closed | Auto-synced from spec.yaml |
| qft_then_inverse_qft_identity_up_to_ordering | intermediate | experimental_closed | Auto-synced from spec.yaml |
| qiskit_optimize_1q_gates_hxx_identity | intermediate | experimental_closed | Auto-synced from spec.yaml |
| rx_gate_equivalence_small_instance | introductory | reference_scaffold | Auto-synced from spec.yaml |
| single_qubit_gate_cancellation | introductory | experimental_closed | Auto-synced from spec.yaml |
| source_optimized_qasm_equivalence_small_instance | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| toffoli_decomposition_equivalence | intermediate | experimental_closed | Auto-synced from spec.yaml |

## Known limitations

QASM parsing does not establish semantic equivalence. Reference benchmark certificates apply only to the declared fixed instance.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md). Gold/`reference_claim` /
ABRC promotion is frozen for v1 (live inventory 0). Usable benchmarks without Lean kernel
proof and semantic bridge (e.g. `circuit_identity_after_layout`) require that stack before any
future promotion. Toffoli decompositions with T gates rely on QCEC externally; Lean S/T gates
are identity stubs — see [docs/semantic_bridge.md](../../docs/semantic_bridge.md).
