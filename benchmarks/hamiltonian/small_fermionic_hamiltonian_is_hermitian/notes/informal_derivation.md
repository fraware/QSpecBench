# Informal derivation: fermionic Hamiltonian Hermiticity

## Claim

The Pauli-decomposed Hamiltonian in `artifacts/hamiltonian.json` represents a Hermitian operator (`H = H†`).

## Argument

Each term is a real coefficient times a tensor product of Pauli matrices. Pauli matrices are Hermitian. Products and sums of Hermitian operators with real coefficients are Hermitian when coefficients are taken from the reals (as declared in the artifact).

The evidence script `evidence/check_hermitian.py` performs a numeric Pauli-matrix expansion and checks `H ≈ H†` within floating tolerance. That check is **heuristic** for this fixed instance; it does not verify the Jordan–Wigner mapping or fermionic semantics.

Kernel-checked Hermiticity for a related small instance appears in the Hamiltonian track reference benchmarks where Lean evidence is wired.
