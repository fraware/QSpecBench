# Flagship specification: operator-level Hamiltonian product-formula bound

Status: **machine-closed experimental package** (`experimental_closed`), **narrowed**. Not independently reviewed. Not a gold/reference claim.

Mathlib 4.14 does not close a fully general operator-norm first-order Lie-Trotter bound for arbitrary finite-dimensional Hermitian `A,B`. The completed instance is [`xz_product_formula_frobenius_majorant_at_pi4`](../benchmarks/hamiltonian/xz_product_formula_frobenius_majorant_at_pi4/) plus [`lean/QSpecBench/Research/HamiltonianFlagship.lean`](../lean/QSpecBench/Research/HamiltonianFlagship.lean).

The sibling [`single_trotter_step_declares_error_contract`](../benchmarks/hamiltonian/single_trotter_step_declares_error_contract/) remains the entry-modulus contract package. It is not this flagship and is not relabeled as operator-norm closure.

## Proposition (this instance)

For Pauli `X,Z` on `C^2` at `t = pi/4`, the product-formula error has positive entry modulus dominated by the Frobenius mass of the difference.

This is **not** `||exp(-i t (A+B)) - (exp(-i t A/r) exp(-i t B/r))^r||_op <= C(A,B) * t^2 / r` for arbitrary Hermitian `A,B`.

## Closed obligations

1. `frobenius_majorant_instance`

## Residual

General operator-norm Lie-Trotter, unbounded step count, and independent review remain out of scope.
