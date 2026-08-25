import QSpecBench.Hamiltonian

/-!
# Hamiltonian product-formula flagship (honest scope)

Mathlib 4.14 does not currently close a fully general operator-norm first-order
Lie–Trotter bound for arbitrary finite-dimensional Hermitian `A,B`. This module
packages the strongest kernel-checked instance in this repository:

* concrete Pauli `X,Z` on `ℂ²`;
* explicit time `t = π/4`;
* the product-formula error has positive entry modulus, dominated by the
  Frobenius mass of the difference.

That is a matrix-norm bound on a concrete instance. It is **not** a general
operator-norm `O(t²/n)` theorem with universal constants, and it is not an
entrywise-only certificate being relabeled as operator-norm closure.
-/

namespace QSpecBench.Research.HamiltonianFlagship

open QSpecBench

/-- Concrete instance: product-formula error at `t = π/4` for `X,Z` is nonzero
and Frobenius-dominated. -/
theorem xz_product_formula_frobenius_majorant_at_pi4 :
    (0 : ℝ) <
        entryModulus
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) 0 1 ∧
      entryModulus
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) 0 1 ≤
        frobeniusNorm
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) ∧
      (0 : ℝ) <
        frobeniusNorm
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) :=
  product_formula_operator_norm_sandwich_at_pi4

end QSpecBench.Research.HamiltonianFlagship
