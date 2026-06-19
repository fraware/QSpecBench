import QSpecBench.Legacy.Matrix
import QSpecBench.Quantum.Gate
import QSpecBench.Quantum.CNOT
import Mathlib.Tactic.FinCases

/-!
# Circuit composition utilities.
-/


namespace QSpecBench.Quantum

open QSpecBench (Matrix2 Matrix4 mul2 mul4)

def compose2 (A B : Matrix2) : Matrix2 := fun i j => mul2 A B i j
def compose4 (A B : Matrix4) : Matrix4 := fun i j => mul4 A B i j

theorem compose2_assoc (A B C : Matrix2) (i j : Fin 2) :
    mul2 (mul2 A B) C i j = mul2 A (mul2 B C) i j := by
  fin_cases i <;> fin_cases j <;> simp [mul2]

end QSpecBench.Quantum
