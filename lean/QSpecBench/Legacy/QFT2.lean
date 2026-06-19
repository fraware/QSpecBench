import QSpecBench.Legacy.Matrix
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import Mathlib.Tactic.FinCases

/-!
# Two-qubit QFT scaffold (legacy layer).
-/


namespace QSpecBench

open QSpecBench (Matrix4 mul4 id4 scale4 kron2I)

def qft2 (i j : Fin 4) : Int :=
  mul4 (kron2I hadamard2) (mul4 cnot4 (kron2I hadamard2)) i j

def invqft2 := qft2

theorem qft2_mul_invqft2 (i j : Fin 4) : mul4 qft2 invqft2 i j = scale4 4 id4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench
