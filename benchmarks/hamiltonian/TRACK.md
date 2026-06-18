# Hamiltonian Track

## Purpose

Scientific Hamiltonian simulation claims: Hermiticity, mappings, Trotter error, Pauli decompositions, resource contracts.

## Accepted artifacts

Hamiltonian JSON, mapping metadata, compilation artifacts.

## Accepted evidence

Python heuristic checks, SMT, proof assistants. Simulation is heuristic, not proof.

## Good first claims

- `small_fermionic_hamiltonian_is_hermitian` (introductory, usable)
- `single_trotter_step_declares_error_contract` (intermediate, approximate)

## Examples

| ID | Difficulty | Notes |
|----|------------|-------|
| small_fermionic_hamiltonian_is_hermitian | introductory | Hermiticity numeric check |
| single_trotter_step_declares_error_contract | intermediate | Approximate error contract |
| resource_contract_for_small_hamiltonian_simulation | intermediate | Resource fields in spec |

## Known limitations

Numeric checks do not replace formal proofs. Fermionic mapping conventions must be explicit in artifacts.
