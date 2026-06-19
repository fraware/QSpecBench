import QSpecBench.Legacy.Matrix
import Mathlib.Tactic.FinCases

namespace QSpecBench

open QSpecBench (Matrix4 mul4 id4)

/-- CNOT with control qubit 0 and target qubit 1 in lexicographic basis |00⟩,|01⟩,|10⟩,|11⟩. -/
def cnot4 (i j : Fin 4) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => 1
  | ⟨2, _⟩, ⟨3, _⟩ => 1
  | ⟨3, _⟩, ⟨2, _⟩ => 1
  | _, _ => 0

theorem cnot_mul_self (i j : Fin 4) : mul4 cnot4 cnot4 i j = id4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench
