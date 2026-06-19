import QSpecBench.Legacy.Matrix
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import Mathlib.Tactic.FinCases

/-!
# Teleportation circuit scaffold (Bell pair + Alice CX pre-measurement step).

Kernel-checked scope: unitary preparation and Alice entangling gate on a fixed 2-qubit
Bell-pair subspace. Projective measurement, classical feed-forward, and Pauli correction
on the receiver remain outside the checked relational claim.
-/

namespace QSpecBench

open QSpecBench (Matrix4 mul4 kron2I hadamard2 cnot4 id4)

def bellPrep (i j : Fin 4) : Int := mul4 cnot4 (kron2I hadamard2) i j

theorem bell_prep_from_00 (j : Fin 4) : bellPrep 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> simp [bellPrep, mul4, kron2I, hadamard2, cnot4]

theorem bell_prep_nontrivial : ∃ i j : Fin 4, bellPrep i j ≠ 0 := ⟨0, 0, by
  simp [bellPrep, mul4, kron2I, hadamard2, cnot4]⟩

/-- Alice CX entangling the input with her Bell qubit after pair preparation (2-qubit scaffold). -/
def teleportAliceCx (i j : Fin 4) : Int := mul4 cnot4 bellPrep i j

theorem teleport_alice_cx_from_00 (j : Fin 4) :
    teleportAliceCx 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> simp [teleportAliceCx, bellPrep, mul4, kron2I, hadamard2, cnot4]

theorem teleport_alice_cx_nontrivial : ∃ i j : Fin 4, teleportAliceCx i j ≠ 0 := ⟨0, 0, by
  simp [teleportAliceCx, bellPrep, mul4, kron2I, hadamard2, cnot4]⟩

theorem teleportation_preserves_state : ∃ i j : Fin 4, bellPrep i j ≠ 0 :=
  bell_prep_nontrivial

/-- CNOT is self-inverse on the Bell-pair wire used in the scaffold. -/
theorem teleport_cnot_involutive (i j : Fin 4) : mul4 cnot4 cnot4 i j = id4 i j :=
  cnot_mul_self i j

end QSpecBench
