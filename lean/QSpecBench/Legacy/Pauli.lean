import QSpecBench.Legacy.Matrix
import Mathlib.Tactic.FinCases

/-!
# Single-qubit Pauli/Hadamard matrix lemmas (legacy Mathlib-free layer).
-/


namespace QSpecBench

open QSpecBench (Matrix2 mul2 id2 scale2)

/-- Unnormalized Hadamard matrix. -/
def hadamard2 (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨0, _⟩, ⟨1, _⟩ => 1
  | ⟨1, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => -1

theorem hadamard_mul_self (i j : Fin 2) : mul2 hadamard2 hadamard2 i j = scale2 2 id2 i j := by
  fin_cases i <;> fin_cases j <;> rfl

def pauliX2 (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨1, _⟩ => 1
  | ⟨1, _⟩, ⟨0, _⟩ => 1
  | _, _ => 0

def pauliZ2 (i j : Fin 2) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => -1
  | _, _ => 0

/-- Unnormalized model: H X H = 2 • Z (OpenQASM H carries 1/√2 scaling per gate). -/
theorem hadamard_conjugates_x (i j : Fin 2) :
    mul2 (mul2 hadamard2 pauliX2) hadamard2 i j = scale2 2 pauliZ2 i j := by
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench
