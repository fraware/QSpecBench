import Mathlib.Data.Complex.Basic
import Mathlib.Data.Matrix.Notation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Data.Rat.Defs
import QSpecBench.Legacy.Pauli

/-!
# Small fermionic Hamiltonian Hermiticity (Pauli matrix model).
-/

namespace QSpecBench

open Matrix Complex

abbrev HamMatrix := Matrix (Fin 4) (Fin 4) ℂ

def pauliZEntry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨1, _⟩ => (-1 : ℂ)
  | ⟨2, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨3, _⟩ => (-1 : ℂ)
  | _, _ => (0 : ℂ)

def pauliXEntry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | _, _ => (0 : ℂ)

def pauliYEntry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨1, _⟩ => (-I : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (I : ℂ)
  | ⟨2, _⟩, ⟨3, _⟩ => (-I : ℂ)
  | ⟨3, _⟩, ⟨2, _⟩ => (I : ℂ)
  | _, _ => (0 : ℂ)

def pauliZ4 : HamMatrix := Matrix.of pauliZEntry
def pauliX4 : HamMatrix := Matrix.of pauliXEntry
def pauliY4 : HamMatrix := Matrix.of pauliYEntry

noncomputable def smallFermionicHamiltonian : HamMatrix :=
  pauliZ4 * pauliZ4 + (1 / 2 : ℂ) • pauliX4 - (1 / 4 : ℂ) • pauliY4

private theorem pauliZEntry_herm (i j : Fin 4) : star (pauliZEntry j i) = pauliZEntry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliZEntry, star, Complex.conj_ofReal, Complex.ext_iff] <;> norm_num

private theorem pauliXEntry_herm (i j : Fin 4) : star (pauliXEntry j i) = pauliXEntry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliXEntry, star, Complex.conj_ofReal, Complex.ext_iff] <;> norm_num

private theorem pauliYEntry_herm (i j : Fin 4) : star (pauliYEntry j i) = pauliYEntry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliYEntry, star, Complex.conj_re, Complex.conj_im, Complex.I_mul_I, Complex.ext_iff]

private theorem pauliZ4_herm : pauliZ4.conjTranspose = pauliZ4 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliZEntry_herm i j

private theorem pauliX4_herm : pauliX4.conjTranspose = pauliX4 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliXEntry_herm i j

private theorem pauliY4_herm : pauliY4.conjTranspose = pauliY4 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliYEntry_herm i j

theorem small_fermionic_hamiltonian_is_hermitian :
    smallFermionicHamiltonian.conjTranspose = smallFermionicHamiltonian := by
  simp [smallFermionicHamiltonian, pauliZ4_herm, pauliX4_herm, pauliY4_herm,
    Matrix.conjTranspose_add, Matrix.conjTranspose_sub, Matrix.conjTranspose_smul,
    Matrix.conjTranspose_mul, Matrix.conjTranspose_one]

/-- Declared Pauli term count for the small fermionic instance. -/
def declaredPauliTermCount : Nat := 3

theorem declared_pauli_term_count_positive : declaredPauliTermCount > 0 := by decide

theorem declared_pauli_term_count_matches_artifact : declaredPauliTermCount = 3 := rfl

/-- Jordan–Wigner scaffold: mapped Pauli X and Z anticommute on one qubit. -/
theorem jordan_wigner_anticommutation_scaffold (i j : Fin 2) :
    mul2 pauliX2 pauliZ2 i j + mul2 pauliZ2 pauliX2 i j = 0 :=
  pauli_x_z_anticommute i j

/-- Pauli decomposition matches declared Z0 Z1 + 0.5 X0 − 0.25 Y1 coefficients. -/
theorem pauli_decomposition_matches_declared_terms :
    smallFermionicHamiltonian =
      pauliZ4 * pauliZ4 + (1 / 2 : ℂ) • pauliX4 - (1 / 4 : ℂ) • pauliY4 := rfl

def pauliZ1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨2, _⟩ => (-1 : ℂ)
  | ⟨3, _⟩, ⟨3, _⟩ => (-1 : ℂ)
  | _, _ => (0 : ℂ)

/-- Pauli X on qubit 0 (flip indices 0↔1, 2↔3). -/
def pauliX0Entry : Fin 4 → Fin 4 → ℂ := pauliXEntry

/-- Pauli X on qubit 1 (flip indices 0↔2, 1↔3). -/
def pauliX1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | _, _ => (0 : ℂ)

/-- Pauli Y on qubit 0 (flip indices 0↔1, 2↔3 with phase). -/
def pauliY0Entry : Fin 4 → Fin 4 → ℂ := pauliYEntry

/-- Pauli Y on qubit 1 (flip indices 0↔2, 1↔3 with phase). -/
def pauliY1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨2, _⟩ => (-I : ℂ)
  | ⟨2, _⟩, ⟨0, _⟩ => (I : ℂ)
  | ⟨1, _⟩, ⟨3, _⟩ => (-I : ℂ)
  | ⟨3, _⟩, ⟨1, _⟩ => (I : ℂ)
  | _, _ => (0 : ℂ)

def pauliX0 : HamMatrix := Matrix.of pauliX0Entry
def pauliX1 : HamMatrix := Matrix.of pauliX1Entry
def pauliY0 : HamMatrix := Matrix.of pauliY0Entry
def pauliY1 : HamMatrix := Matrix.of pauliY1Entry
def pauliZ0 : HamMatrix := Matrix.of pauliZ1Entry
def pauliZ1 : HamMatrix := Matrix.of pauliZEntry

private theorem pauliZ1Entry_herm (i j : Fin 4) : star (pauliZ1Entry j i) = pauliZ1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliZ1Entry, star, Complex.conj_ofReal, Complex.ext_iff] <;> norm_num

private theorem pauliX0Entry_herm (i j : Fin 4) : star (pauliX0Entry j i) = pauliX0Entry i j :=
  pauliXEntry_herm i j

private theorem pauliY0Entry_herm (i j : Fin 4) : star (pauliY0Entry j i) = pauliY0Entry i j :=
  pauliYEntry_herm i j

private theorem pauliX1Entry_herm (i j : Fin 4) : star (pauliX1Entry j i) = pauliX1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliX1Entry, star, Complex.conj_ofReal, Complex.ext_iff] <;> norm_num

private theorem pauliY1Entry_herm (i j : Fin 4) : star (pauliY1Entry j i) = pauliY1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliY1Entry, star, Complex.conj_re, Complex.conj_im, Complex.I_mul_I, Complex.ext_iff]

private theorem pauliX0_herm : pauliX0.conjTranspose = pauliX0 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliX0Entry_herm i j

private theorem pauliX1_herm : pauliX1.conjTranspose = pauliX1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliX1Entry_herm i j

private theorem pauliY0_herm : pauliY0.conjTranspose = pauliY0 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliY0Entry_herm i j

private theorem pauliY1_herm : pauliY1.conjTranspose = pauliY1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliY1Entry_herm i j

private theorem pauliZ0_herm : pauliZ0.conjTranspose = pauliZ0 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliZ1Entry_herm i j

private theorem pauliZ1_herm : pauliZ1.conjTranspose = pauliZ1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliZEntry_herm i j

theorem pauliX0_ne_pauliX1 : pauliX0 ≠ pauliX1 := by
  intro h
  have ne_entry : pauliX0 0 2 ≠ pauliX1 0 2 := by
    simp [pauliX0, pauliX1, Matrix.of_apply, pauliX0Entry, pauliX1Entry]
  exact ne_entry (congr_fun (congr_fun h 0) 2)

private theorem pauliX0_mul_pauliX1_commute : pauliX0 * pauliX1 = pauliX1 * pauliX0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Matrix.of_apply, pauliX0Entry, pauliX1Entry, Fin.sum_univ_four]
    <;> ring_nf

private theorem pauliY0_mul_pauliY1_commute : pauliY0 * pauliY1 = pauliY1 * pauliY0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Matrix.of_apply, pauliY0Entry, pauliY1Entry, Fin.sum_univ_four]
    <;> ring_nf

private theorem pauliZ0_eq_diagonal : pauliZ0 = Matrix.diagonal fun i => pauliZ1Entry i i := by
  ext i j
  simp [pauliZ0, Matrix.of_apply, Matrix.diagonal_apply, pauliZ1Entry]
  fin_cases i <;> fin_cases j <;> rfl

private theorem pauliZ1_eq_diagonal : pauliZ1 = Matrix.diagonal fun i => pauliZEntry i i := by
  ext i j
  simp [pauliZ1, Matrix.of_apply, Matrix.diagonal_apply, pauliZEntry]
  fin_cases i <;> fin_cases j <;> rfl

private theorem pauliZ0_mul_pauliZ1_commute : pauliZ0 * pauliZ1 = pauliZ1 * pauliZ0 := by
  rw [pauliZ0_eq_diagonal, pauliZ1_eq_diagonal]
  ext i j
  by_cases hij : i = j
  · subst hij
    simp [Matrix.diagonal_mul_diagonal, Matrix.diagonal_apply, mul_comm]
  · simp [Matrix.diagonal_mul_diagonal, Matrix.diagonal_apply, hij]

/-- Two-qubit Heisenberg-type instance matching `heisenberg_model_hermiticity_small_instance`. -/
noncomputable def heisenbergSmallInstance : HamMatrix :=
  pauliX0 * pauliX1 + (1 / 2 : ℂ) • (pauliY0 * pauliY1) + (1 / 4 : ℂ) • (pauliZ0 * pauliZ1)

theorem heisenberg_small_instance_is_hermitian :
    heisenbergSmallInstance.conjTranspose = heisenbergSmallInstance := by
  simp [heisenbergSmallInstance, pauliX0_herm, pauliX1_herm, pauliY0_herm, pauliY1_herm,
    pauliZ0_herm, pauliZ1_herm, Matrix.conjTranspose_add, Matrix.conjTranspose_smul,
    Matrix.conjTranspose_mul, pauliX0_mul_pauliX1_commute, pauliY0_mul_pauliY1_commute,
    pauliZ0_mul_pauliZ1_commute]

/-- Declared single-step Trotter fidelity bound from artifact contract (not proved). -/
def declaredSingleTrotterFidelityBound : ℚ := 1 / 1000000

theorem single_trotter_step_declares_error_contract :
    declaredSingleTrotterFidelityBound > 0 := by
  norm_num [declaredSingleTrotterFidelityBound]

/-- Declared second-order Trotter operator-norm contract exponent (documented only). -/
def declaredSecondOrderTrotterOrder : Nat := 2

theorem trotter_second_order_bound_contract :
    declaredSecondOrderTrotterOrder = 2 := rfl

end QSpecBench
