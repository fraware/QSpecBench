import QSpecBench.Legacy.Matrix
import Mathlib.Tactic.FinCases

namespace QSpecBench

open QSpecBench (Matrix4 mul4 id4)

/-- CNOT with control qubit 0 and target qubit 1 in lexicographic basis |00⟩,|01⟩,|10⟩,|11⟩. -/
private def cnot4_01 (i j : Fin 4) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨3, _⟩ => 1
  | ⟨2, _⟩, ⟨2, _⟩ => 1
  | ⟨3, _⟩, ⟨1, _⟩ => 1
  | _, _ => 0

/-- CNOT with control qubit 1 and target qubit 0 in lexicographic basis |00⟩,|01⟩,|10⟩,|11⟩. -/
private def cnot4_10 (i j : Fin 4) : Int :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => 1
  | ⟨2, _⟩, ⟨3, _⟩ => 1
  | ⟨3, _⟩, ⟨2, _⟩ => 1
  | _, _ => 0

/-- Indexed two-qubit CNOT matching OpenQASM `cx q[ctrl], q[tgt]` (qubit 0 = LSB). -/
def cnot4_ctrl_tgt (ctrl tgt : Fin 2) (i j : Fin 4) : Int :=
  match ctrl, tgt with
  | ⟨0, _⟩, ⟨1, _⟩ => cnot4_01 i j
  | ⟨1, _⟩, ⟨0, _⟩ => cnot4_10 i j
  | _, _ => id4 i j

/-- Standard CNOT: control qubit 0, target qubit 1. -/
def cnot4 (i j : Fin 4) : Int := cnot4_ctrl_tgt 0 1 i j

theorem cnot4_ctrl_tgt_mul_self (ctrl tgt : Fin 2) (i j : Fin 4) :
    mul4 (cnot4_ctrl_tgt ctrl tgt) (cnot4_ctrl_tgt ctrl tgt) i j = id4 i j := by
  fin_cases ctrl <;> fin_cases tgt <;> fin_cases i <;> fin_cases j <;> rfl

theorem cnot_mul_self (i j : Fin 4) : mul4 cnot4 cnot4 i j = id4 i j :=
  cnot4_ctrl_tgt_mul_self 0 1 i j

end QSpecBench
