import QSpecBench.Legacy.Matrix
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import QSpecBench.Legacy.QFT2
import QSpecBench.Teleportation
import Mathlib.Tactic.FinCases

/-!
# Fixed-instance algorithm scaffolds (Bell pair, QFT, oracle distinction).
-/

namespace QSpecBench

open QSpecBench (Matrix2 Matrix4 mul2 mul4 id2 id4 scale2 scale4 kron2I hadamard2 pauliX2 pauliZ2
  cnot4 qft2 invqft2 bellPrep)

/-- Superdense-coding Bell-pair preparation matches teleportation Bell prep. -/
def superdenseBellPrep := bellPrep

theorem superdense_bell_pair_entangled (j : Fin 4) :
    superdenseBellPrep 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  simpa [superdenseBellPrep] using bell_prep_from_00 j

theorem superdense_bell_pair_nontrivial : ∃ i j : Fin 4, superdenseBellPrep i j ≠ 0 :=
  teleportation_preserves_state

/-- Deutsch–Jozsa constant-oracle scaffold: H² = 2I on the query qubit. -/
theorem dj_constant_oracle_hadamard_square (i j : Fin 2) :
    mul2 hadamard2 hadamard2 i j = scale2 2 id2 i j :=
  hadamard_mul_self i j

/-- Grover single-iteration diffuser scaffold H X H on the marked qubit. -/
def groverDiffuser (i j : Fin 2) : Int :=
  mul2 hadamard2 (mul2 pauliX2 hadamard2) i j

theorem grover_diffuser_nontrivial : ∃ i j : Fin 2, groverDiffuser i j ≠ 0 := ⟨0, 0, by
  simp [groverDiffuser, mul2, hadamard2, pauliX2]⟩

/-- QFT then inverse QFT equals 4•I on the two-qubit scaffold (unnormalized convention). -/
theorem qft_then_inverse_qft_identity (i j : Fin 4) :
    mul4 qft2 invqft2 i j = scale4 4 id4 i j :=
  qft2_mul_invqft2 i j

/-- Phase-estimation scaffold: Z has eigenvalue −1 on |1⟩. -/
theorem phase_estimation_z_eigenvalue_on_one :
    mul2 pauliZ2 (show Fin 2 from 1) (show Fin 2 from 1) = (-1 : Int) := by
  simp [mul2, pauliZ2]

end QSpecBench
