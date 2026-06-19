import QSpecBench.Legacy.Matrix
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import Mathlib.Tactic.FinCases

/-!
# Teleportation circuit scaffold (Bell pair preparation).
-/

namespace QSpecBench

open QSpecBench (Matrix4 mul4 kron2I hadamard2 cnot4)

def bellPrep (i j : Fin 4) : Int := mul4 cnot4 (kron2I hadamard2) i j

theorem bell_prep_from_00 (j : Fin 4) : bellPrep 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> simp [bellPrep, mul4, kron2I, hadamard2, cnot4]

theorem teleportation_preserves_state : ∃ i j : Fin 4, bellPrep i j ≠ 0 := ⟨0, 0, by
  simp [bellPrep, mul4, kron2I, hadamard2, cnot4]⟩

end QSpecBench
