# Hamiltonian Track

## Purpose

Scientific Hamiltonian simulation claims: Hermiticity, mappings, Trotter error, Pauli decompositions, resource contracts.

## Accepted artifacts

Hamiltonian JSON, mapping metadata, compilation artifacts.

## Accepted evidence

Python heuristic checks, SMT, proof assistants. Simulation is heuristic, not proof.

## Good first claims

- `small_fermionic_hamiltonian_is_hermitian` (introductory, reference_claim)
- `single_trotter_step_declares_error_contract` (intermediate, reference_claim)

## Examples

| ID | Difficulty | Maturity | Notes |
|----|------------|----------|-------|
| bravyi_kitaev_small_instance | intermediate | usable | Auto-synced from spec.yaml |
| heisenberg_model_hermiticity_small_instance | introductory | reference_scaffold | Auto-synced from spec.yaml |
| jordan_wigner_preserves_anticommutation_small_instance | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| pauli_decomposition_matches_source_hamiltonian_small_instance | advanced | reference_scaffold | Auto-synced from spec.yaml |
| resource_contract_for_small_hamiltonian_simulation | intermediate | reference_scaffold | Auto-synced from spec.yaml |
| single_trotter_step_declares_error_contract | intermediate | reference_claim | Auto-synced from spec.yaml |
| small_fermionic_hamiltonian_is_hermitian | introductory | reference_claim | Auto-synced from spec.yaml |
| trotter_second_order_bound_contract | intermediate | reference_contract | Auto-synced from spec.yaml |

## Known limitations

Numeric checks do not replace formal proofs. Fermionic mapping conventions must be explicit in artifacts.

## Reference promotion

See [docs/reference_benchmarks.md](../../docs/reference_benchmarks.md). Hamiltonian reference maturity requires Lean `Hermitian` or matrix equality on the declared Pauli model. `single_trotter_step_declares_error_contract` is **`reference_claim`** under the entry-modulus headline (historical fidelity 1e-6 at Δt=0.1 permanently not_applicable; revised Taylor-proxy fidelity at Δt=1/100 checked). Side obligations `multi_step_trotter_composition` (declared N=5, entry-modulus triangle proxy) and `haar_monte_carlo_integral` (hashed numerical certificate vs Nielsen closed form) are checked under declared scope — neither is an operator-norm/unbounded-N Trotter result nor a measure-theoretic Haar-integral proof. `trotter_second_order_bound_contract` remains **usable** until a checked bound proof or simulation with honest trust boundary is wired.
