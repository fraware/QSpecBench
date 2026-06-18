# Hamiltonian track

## Purpose

Scientific quantum simulation claims: Hermiticity, mappings, Trotter error, resource contracts.

## Accepted artifacts

Hamiltonian JSON, mapping specifications, compilation artifacts.

## Accepted evidence

Python numeric checks (heuristic), SMT, proof assistant formalizations.

## Rules

Declare source/target representation, mappings, approximation metric and bound when applicable, Trotter order for product formulas.

## Examples

- `small_fermionic_hamiltonian_is_hermitian`
- `single_trotter_step_declares_error_contract` — approximate mode

## Limitations

Numeric Hermiticity checks are not formal proofs.
