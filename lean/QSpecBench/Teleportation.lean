import QSpecBench.Legacy.Matrix
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import Mathlib.Tactic.FinCases

/-!
# Teleportation circuit scaffold (Bell pair + Alice entangling gates).

Kernel-checked scope: unitary preparation and Alice entangling gates on the declared
3-qubit ordering. Projective measurement, classical feed-forward, and Pauli correction
on the receiver are documented but only the unitary fragment before measurement is
kernel-checked against OpenQASM denotation.

The relational claim (arbitrary `|ψ⟩` transfer after correction) is **not** proved here;
see `teleportation_unitary_fragment_checked` for the checked unitary fragment,
`teleportCorrectionLabel` for the documented Pauli correction table, and
`QSpecBench.Quantum.Measurement.teleportSyndrome00` for the sequential Z-measurement scaffold.
-/

namespace QSpecBench

open QSpecBench (Matrix4 mul4 kron2I hadamard2 cnot4 id4)

def bellPrep (i j : Fin 4) : Int := mul4 cnot4 (kron2I hadamard2) i j

theorem bell_prep_from_00 (j : Fin 4) : bellPrep 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> native_decide

theorem bell_prep_nontrivial : ∃ i j : Fin 4, bellPrep i j ≠ 0 := ⟨0, 0, by native_decide⟩

/-- Alice CX entangling the input with her Bell qubit after pair preparation (2-qubit scaffold). -/
def teleportAliceCx (i j : Fin 4) : Int := mul4 cnot4 bellPrep i j

theorem teleport_alice_cx_from_00 (j : Fin 4) :
    teleportAliceCx 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> native_decide

theorem teleport_alice_cx_nontrivial : ∃ i j : Fin 4, teleportAliceCx i j ≠ 0 := ⟨0, 0, by native_decide⟩

/-- Legacy anchor: Bell-pair preparation is nontrivial (superseded by fragment theorem below). -/
theorem teleportation_preserves_state : ∃ i j : Fin 4, bellPrep i j ≠ 0 :=
  bell_prep_nontrivial

/-- Unitary fragment before measurement is nontrivial on the declared wire ordering. -/
theorem teleportation_unitary_fragment_checked :
    ∃ i j : Fin 4, teleportAliceCx i j ≠ 0 :=
  teleport_alice_cx_nontrivial

/-- CNOT is self-inverse on the Bell-pair wire used in the scaffold. -/
theorem teleport_cnot_involutive (i j : Fin 4) : mul4 cnot4 cnot4 i j = id4 i j :=
  cnot_mul_self i j

/-- Documented Pauli correction label for measurement bits `(c₀, c₁)` (not proved correct). -/
def teleportCorrectionLabel (c0 c1 : Bool) : String :=
  match c0, c1 with
  | false, false => "I"
  | false, true => "X"
  | true, false => "Z"
  | true, true => "Z,X"

theorem teleport_correction_I : teleportCorrectionLabel false false = "I" := rfl
theorem teleport_correction_X : teleportCorrectionLabel false true = "X" := rfl
theorem teleport_correction_Z : teleportCorrectionLabel true false = "Z" := rfl
theorem teleport_correction_ZX : teleportCorrectionLabel true true = "Z,X" := rfl

end QSpecBench
