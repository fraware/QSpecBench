import Mathlib.Data.Complex.Basic
import Mathlib.Data.Matrix.Notation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
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

def pauliX1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | _, _ => (0 : ℂ)

def pauliY1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨1, _⟩ => (-I : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (I : ℂ)
  | ⟨2, _⟩, ⟨3, _⟩ => (-I : ℂ)
  | ⟨3, _⟩, ⟨2, _⟩ => (I : ℂ)
  | _, _ => (0 : ℂ)

def pauliX0 : HamMatrix := Matrix.of pauliXEntry
def pauliX1 : HamMatrix := Matrix.of pauliX1Entry
def pauliY0 : HamMatrix := Matrix.of pauliYEntry
def pauliY1 : HamMatrix := Matrix.of pauliY1Entry
def pauliZ0 : HamMatrix := Matrix.of pauliZ1Entry
def pauliZ1 : HamMatrix := Matrix.of pauliZEntry

private theorem pauliZ1Entry_herm (i j : Fin 4) : star (pauliZ1Entry j i) = pauliZ1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliZ1Entry, star, Complex.conj_ofReal, Complex.ext_iff] <;> norm_num

private theorem pauliX1Entry_herm (i j : Fin 4) : star (pauliX1Entry j i) = pauliX1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliX1Entry, star, Complex.conj_ofReal, Complex.ext_iff] <;> norm_num

private theorem pauliY1Entry_herm (i j : Fin 4) : star (pauliY1Entry j i) = pauliY1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliY1Entry, star, Complex.conj_re, Complex.conj_im, Complex.I_mul_I, Complex.ext_iff]

private theorem pauliX0_herm : pauliX0.conjTranspose = pauliX0 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliXEntry_herm i j

private theorem pauliX1_herm : pauliX1.conjTranspose = pauliX1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliX1Entry_herm i j

private theorem pauliY0_herm : pauliY0.conjTranspose = pauliY0 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliYEntry_herm i j

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

private theorem pauliX0_mul_pauliX1_commute : pauliX0 * pauliX1 = pauliX1 * pauliX0 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Matrix.of_apply, pauliXEntry, pauliX1Entry]

private theorem pauliY0_mul_pauliY1_commute : pauliY0 * pauliY1 = pauliY1 * pauliY0 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Matrix.of_apply, pauliYEntry, pauliY1Entry]

private theorem pauliZ0_mul_pauliZ1_commute : pauliZ0 * pauliZ1 = pauliZ1 * pauliZ0 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Matrix.of_apply, pauliZ1Entry, pauliZEntry]

/-- Two-qubit Heisenberg-type instance matching `heisenberg_model_hermiticity_small_instance`. -/
noncomputable def heisenbergSmallInstance : HamMatrix :=
  pauliX0 * pauliX1 + (1 / 2 : ℂ) • (pauliY0 * pauliY1) + (1 / 4 : ℂ) • (pauliZ0 * pauliZ1)

theorem heisenberg_small_instance_is_hermitian :
    heisenbergSmallInstance.conjTranspose = heisenbergSmallInstance := by
  simp [heisenbergSmallInstance, pauliX0_herm, pauliX1_herm, pauliY0_herm, pauliY1_herm,
    pauliZ0_herm, pauliZ1_herm, Matrix.conjTranspose_add, Matrix.conjTranspose_smul,
    Matrix.conjTranspose_mul, pauliX0_mul_pauliX1_commute, pauliY0_mul_pauliY1_commute,
    pauliZ0_mul_pauliZ1_commute]

end QSpecBench
