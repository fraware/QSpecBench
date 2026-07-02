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

- `cnot_self_inverse_cancellation` (introductory, **reference** with checkable certificate)
- `rx_gate_equivalence_small_instance` (introductory, usable)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| circuit_identity_after_layout | introductory | reference_scaffold | Auto-synced from spec.yaml |
| clifford_simplification_preserves_unitary | advanced | reference_scaffold | Auto-synced from spec.yaml |
| cnot_self_inverse_cancellation | introductory | artifact_bound_reference_claim | Auto-synced from spec.yaml |
| hadamard_conjugates_x_to_z | intermediate | artifact_bound_reference_claim | Auto-synced from spec.yaml |
| phase_polynomial_equivalence_small_instance | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| qft_inverse_qft_small_instance | intermediate | reference_claim | Auto-synced from spec.yaml |
| rx_gate_equivalence_small_instance | introductory | reference_scaffold | Auto-synced from spec.yaml |
| single_qubit_gate_cancellation | introductory | artifact_bound_reference_claim | Auto-synced from spec.yaml |
| source_optimized_qasm_equivalence_small_instance | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| toffoli_decomposition_equivalence | intermediate | artifact_bound_reference_claim | Auto-synced from spec.yaml |

## Known limitations

QASM parsing does not establish semantic equivalence. Reference benchmark certificates apply only to the declared fixed instance.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md). Usable benchmarks without Lean kernel proof and semantic bridge (e.g. `circuit_identity_after_layout`, `toffoli_decomposition_equivalence`) require that stack before promotion. Toffoli decompositions with T gates rely on QCEC externally; Lean S/T gates are identity stubs — see [docs/semantic_bridge.md](../../docs/semantic_bridge.md).
