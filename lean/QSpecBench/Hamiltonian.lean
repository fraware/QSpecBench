import Mathlib.Data.Complex.Basic
import Mathlib.Data.Matrix.Notation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum

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

end QSpecBench
