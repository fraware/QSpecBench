# Hamiltonian Track

## Purpose

Scientific Hamiltonian simulation claims: Hermiticity, mappings, Trotter error, Pauli decompositions, resource contracts.

## Accepted artifacts

Hamiltonian JSON, mapping metadata, compilation artifacts.

## Accepted evidence

Python heuristic checks, SMT, proof assistants. Simulation is heuristic, not proof.

## Good first claims

- `small_fermionic_hamiltonian_is_hermitian` (introductory, reference)
- `single_trotter_step_declares_error_contract` (intermediate, usable)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| bravyi_kitaev_small_instance | intermediate | usable | Auto-synced from spec.yaml |
| heisenberg_model_hermiticity_small_instance | introductory | reference | Auto-synced from spec.yaml |
| jordan_wigner_preserves_anticommutation_small_instance | intermediate | reference | Auto-synced from spec.yaml |
| pauli_decomposition_matches_source_hamiltonian_small_instance | advanced | reference | Auto-synced from spec.yaml |
| resource_contract_for_small_hamiltonian_simulation | intermediate | reference | Auto-synced from spec.yaml |
| single_trotter_step_declares_error_contract | intermediate | usable | Auto-synced from spec.yaml |
| small_fermionic_hamiltonian_is_hermitian | introductory | reference | Auto-synced from spec.yaml |
| trotter_second_order_bound_contract | intermediate | usable | Auto-synced from spec.yaml |

## Known limitations

Numeric checks do not replace formal proofs. Fermionic mapping conventions must be explicit in artifacts.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md). Hamiltonian reference maturity requires Lean `Hermitian` or matrix equality on the declared Pauli model. Contract-only Trotter benchmarks (`single_trotter_step_declares_error_contract`, `trotter_second_order_bound_contract`) remain **usable** until a checked bound proof or simulation with honest trust boundary is wired.
