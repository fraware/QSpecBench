import Mathlib.Data.Matrix.Basic
import Mathlib.Data.Complex.Basic
import QSpecBench.Legacy.Matrix

/-!
# Quantum basic types (Mathlib-backed scaffold).
-/


namespace QSpecBench.Quantum

variable {nq : ℕ}

abbrev QubitRegister (nq : ℕ) := Fin (2 ^ nq)
abbrev StateVec (nq : ℕ) := QubitRegister nq → ℂ
abbrev Unitary (nq : ℕ) := Matrix (QubitRegister nq) (QubitRegister nq) ℂ

end QSpecBench.Quantum
