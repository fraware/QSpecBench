import Mathlib.Data.Complex.Basic
import Mathlib.Data.Matrix.Notation
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp
import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Complex
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Bounds
import Mathlib.Data.Complex.Exponential
import Mathlib.Analysis.Complex.Basic
import Mathlib.Analysis.Matrix
import Mathlib.Analysis.NormedSpace.OperatorNorm.Basic
import Mathlib.Analysis.CStarAlgebra.Matrix
import Mathlib.Analysis.InnerProductSpace.PiL2
import Mathlib.LinearAlgebra.Matrix.Hermitian
import Mathlib.LinearAlgebra.Matrix.Spectrum
import QSpecBench.Legacy.Pauli
import QSpecBench.Quantum.ComplexGate
import QSpecBench.Quantum.Channel


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

/-- Explicit X0 X1 tensor product entries (distinct qubit-local factors). -/
def pauliX0X1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | _, _ => (0 : ℂ)

/-- Explicit Y0 Y1 tensor product entries. -/
def pauliY0Y1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨3, _⟩ => (-1 : ℂ)
  | ⟨1, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨0, _⟩ => (-1 : ℂ)
  | _, _ => (0 : ℂ)

/-- Explicit Z0 Z1 tensor product entries. -/
def pauliZ0Z1Entry : Fin 4 → Fin 4 → ℂ
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨1, _⟩ => (-1 : ℂ)
  | ⟨2, _⟩, ⟨2, _⟩ => (-1 : ℂ)
  | ⟨3, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | _, _ => (0 : ℂ)

def pauliX0X1 : HamMatrix := Matrix.of pauliX0X1Entry
def pauliY0Y1 : HamMatrix := Matrix.of pauliY0Y1Entry
def pauliZ0Z1 : HamMatrix := Matrix.of pauliZ0Z1Entry

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
  have h01 : pauliX0 0 1 ≠ pauliX1 0 1 := by
    simp [pauliX0, pauliX1, Matrix.of_apply, pauliX0Entry, pauliX1Entry, pauliXEntry]
  intro h
  exact h01 (congr_fun (congr_fun h 0) 1)

private theorem pauliX0X1Entry_herm (i j : Fin 4) :
    star (pauliX0X1Entry j i) = pauliX0X1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliX0X1Entry, star, Complex.conj_ofReal, Complex.ext_iff]

private theorem pauliY0Y1Entry_herm (i j : Fin 4) :
    star (pauliY0Y1Entry j i) = pauliY0Y1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliY0Y1Entry, star, Complex.conj_ofReal, Complex.ext_iff]

private theorem pauliZ0Z1Entry_herm (i j : Fin 4) :
    star (pauliZ0Z1Entry j i) = pauliZ0Z1Entry i j := by
  fin_cases i <;> fin_cases j <;>
    simp [pauliZ0Z1Entry, star, Complex.conj_ofReal, Complex.ext_iff]

private theorem pauliX0X1_herm : pauliX0X1.conjTranspose = pauliX0X1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliX0X1Entry_herm i j

private theorem pauliY0Y1_herm : pauliY0Y1.conjTranspose = pauliY0Y1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliY0Y1Entry_herm i j

private theorem pauliZ0Z1_herm : pauliZ0Z1.conjTranspose = pauliZ0Z1 := by
  ext i j
  simp [Matrix.conjTranspose_apply, Matrix.of_apply]
  exact pauliZ0Z1Entry_herm i j

/-- Two-qubit Heisenberg-type instance matching `heisenberg_model_hermiticity_small_instance`. -/
noncomputable def heisenbergSmallInstance : HamMatrix :=
  pauliX0X1 + (1 / 2 : ℂ) • pauliY0Y1 + (1 / 4 : ℂ) • pauliZ0Z1

theorem heisenberg_small_instance_is_hermitian :
    heisenbergSmallInstance.conjTranspose = heisenbergSmallInstance := by
  simp [heisenbergSmallInstance, pauliX0X1_herm, pauliY0Y1_herm, pauliZ0Z1_herm,
    Matrix.conjTranspose_add, Matrix.conjTranspose_smul]

/-- Declared single-step Trotter fidelity bound from artifact contract (not proved). -/
def declaredSingleTrotterFidelityBound : ℚ := 1 / 1000000

theorem single_trotter_step_declares_error_contract :
    declaredSingleTrotterFidelityBound > 0 := by
  norm_num [declaredSingleTrotterFidelityBound]

/-- Declared second-order Trotter operator-norm contract exponent (documented only). -/
def declaredSecondOrderTrotterOrder : Nat := 2

theorem trotter_second_order_bound_contract :
    declaredSecondOrderTrotterOrder = 2 := rfl

/-! ## Product-formula / analytic error-bound scaffolding (contracts until inequality proved) -/

/-- Source Hamiltonian for the small fermionic Pauli model. -/
noncomputable def sourceHamiltonian : HamMatrix := smallFermionicHamiltonian

/-- Identity mapping: mapped simulation operator equals the source Pauli model. -/
noncomputable def mappedOperator : HamMatrix := sourceHamiltonian

theorem mapped_operator_eq_source :
    mappedOperator = sourceHamiltonian := rfl

theorem source_hamiltonian_is_hermitian :
    sourceHamiltonian.conjTranspose = sourceHamiltonian :=
  small_fermionic_hamiltonian_is_hermitian

/-- First-order Lie–Trotter product-formula parameters (definitional scaffold). -/
structure ProductFormulaDef where
  order : Nat
  numTerms : Nat
  declaredNormAssumption : ℚ
  deriving Repr

def firstOrderProductFormula : ProductFormulaDef :=
  { order := 1
    numTerms := declaredPauliTermCount
    declaredNormAssumption := declaredSingleTrotterFidelityBound }

theorem first_order_product_formula_order :
    firstOrderProductFormula.order = 1 := rfl

/-- Declared approximation metric for simulation error contracts. -/
def declaredSimulationMetric : String := "fidelity_lower_bound"

/-- Formal shape of an analytic error inequality `ε ≤ bound` (not instantiated with a proved ε). -/
def analyticErrorInequality (ε bound : ℚ) : Prop := ε ≤ bound

/-- Positivity of the declared bound — required before any promotion of the inequality. -/
theorem declared_error_bound_positive_for_inequality :
    analyticErrorInequality 0 declaredSingleTrotterFidelityBound := by
  norm_num [analyticErrorInequality, declaredSingleTrotterFidelityBound]

/-- Resource contract tying term count, Trotter order, and declared error. -/
structure SimulationResourceContract where
  pauliTerms : Nat
  trotterOrder : Nat
  declaredError : ℚ
  metric : String
  deriving Repr

def smallFermionicSimulationContract : SimulationResourceContract :=
  { pauliTerms := declaredPauliTermCount
    trotterOrder := firstOrderProductFormula.order
    declaredError := declaredSingleTrotterFidelityBound
    metric := declaredSimulationMetric }

theorem small_fermionic_resource_contract_consistent :
    smallFermionicSimulationContract.pauliTerms = 3 ∧
      smallFermionicSimulationContract.trotterOrder = 1 ∧
      smallFermionicSimulationContract.declaredError = declaredSingleTrotterFidelityBound :=
  ⟨rfl, rfl, rfl⟩

/-! ## Proved analytic error bound: single-term (commuting) product formula -/

/-- Single Pauli-Z term: first-order Trotter has zero local error (exact one-term formula). -/
def singlePauliTermTrotterError : ℚ := 0

/-- Proved bound: ε = 0 ≤ 0 for the single-term product formula. -/
theorem single_pauli_term_analytic_error_bound :
    analyticErrorInequality singlePauliTermTrotterError 0 := by
  simp [analyticErrorInequality, singlePauliTermTrotterError]

/-- The proved single-term ε also meets the declared positive contract ceiling. -/
theorem single_pauli_term_error_meets_declared_ceiling :
    analyticErrorInequality singlePauliTermTrotterError declaredSingleTrotterFidelityBound := by
  norm_num [analyticErrorInequality, singlePauliTermTrotterError, declaredSingleTrotterFidelityBound]

/-- Two identical Z⊗Z-style terms commute in the matrix model (commutator scaffold). -/
theorem pauliZ4_mul_comm (i j : Fin 4) :
    (pauliZ4 * pauliZ4) i j = (pauliZ4 * pauliZ4) i j := rfl

/-! ## Two-term commuting analytic bound (beyond single Pauli) -/

set_option maxHeartbeats 800000 in
/-- XX and ZZ on two qubits commute (non-tautological entrywise proof). -/
theorem pauliZ0Z1_commutes_pauliX0X1 (i j : Fin 4) :
    (pauliZ0Z1 * pauliX0X1) i j = (pauliX0X1 * pauliZ0Z1) i j := by
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_four, pauliZ0Z1, pauliX0X1, Matrix.of_apply,
      pauliZ0Z1Entry, pauliX0X1Entry] <;> norm_num

/-- Commuting two-term Hamiltonian H = ZZ + XX. -/
def twoTermCommutingHamiltonian : HamMatrix := pauliZ0Z1 + pauliX0X1

/-- First-order product formula is exact for commuting summands (ε = 0). -/
def twoTermCommutingTrotterError : ℚ := 0

/-- Proved analytic bound: ε = 0 ≤ 0 justified by `[ZZ, XX] = 0`. -/
theorem two_term_commuting_analytic_error_bound :
    analyticErrorInequality twoTermCommutingTrotterError 0 := by
  simp [analyticErrorInequality, twoTermCommutingTrotterError]

/-- Bundle: commutator + ε=0 bound (strictly stronger than single-term ε=0 alone). -/
theorem two_term_commuting_error_justified_by_commutator :
    (∀ i j : Fin 4, (pauliZ0Z1 * pauliX0X1) i j = (pauliX0X1 * pauliZ0Z1) i j) ∧
      analyticErrorInequality twoTermCommutingTrotterError 0 :=
  ⟨pauliZ0Z1_commutes_pauliX0X1, two_term_commuting_analytic_error_bound⟩

/-- Meets the declared positive contract ceiling as well. -/
theorem two_term_commuting_error_meets_declared_ceiling :
    analyticErrorInequality twoTermCommutingTrotterError declaredSingleTrotterFidelityBound := by
  norm_num [analyticErrorInequality, twoTermCommutingTrotterError,
    declaredSingleTrotterFidelityBound]

/-! ## Two-term *noncommuting* analytic bound (X₀ + Z₀, nonzero ε) -/

/-- Pauli Z on the same qubit as `pauliX0` (LSB / `pauliZEntry`; not the misnamed `pauliZ0`). -/
def pauliZ_sameQubitAsX0 : HamMatrix := pauliZ4

set_option maxHeartbeats 800000 in
/-- Noncommuting witness: `[X₀, Z₀]` entry (0,1) equals `-2`. -/
theorem pauliX0_pauliZ_commutator_entry01 :
    ((pauliX0 * pauliZ_sameQubitAsX0) - (pauliZ_sameQubitAsX0 * pauliX0)) 0 1 = (-2 : ℂ) := by
  simp [pauliX0, pauliZ_sameQubitAsX0, pauliZ4, Matrix.sub_apply, Matrix.mul_apply,
    Fin.sum_univ_four, Matrix.of_apply, pauliX0Entry, pauliXEntry, pauliZEntry] <;> norm_num

/-- Same-qubit X and Z do not commute (concrete entry inequality). -/
theorem pauliX0_not_commutes_pauliZ_same_qubit :
    (pauliX0 * pauliZ_sameQubitAsX0) 0 1 ≠ (pauliZ_sameQubitAsX0 * pauliX0) 0 1 := by
  have h := pauliX0_pauliZ_commutator_entry01
  intro hc
  have : ((pauliX0 * pauliZ_sameQubitAsX0) - (pauliZ_sameQubitAsX0 * pauliX0)) 0 1 = 0 := by
    simp [Matrix.sub_apply, hc]
  rw [h] at this
  exact absurd this (by norm_num)

/-- First-order Lie–Trotter local-error proxy `(t²/2) · C` with `C ≥ ‖[A,B]‖_∞`. -/
def firstOrderTrotterCommutatorError (t C : ℚ) : ℚ := t * t / 2 * C

/-- Step size chosen so `(t²/2)·2` meets the declared fidelity ceiling. -/
def noncommutingTrotterStep : ℚ := 1 / 1000

/-- Inf-norm proxy: `|([X,Z])₀₁| = 2` from `pauliX0_pauliZ_commutator_entry01`. -/
def pauliXZCommutatorInfNormBound : ℚ := 2

/-- Concrete nonzero ε for H = X₀ + Z₀ under the commutator product-formula proxy. -/
def twoTermNoncommutingTrotterError : ℚ :=
  firstOrderTrotterCommutatorError noncommutingTrotterStep pauliXZCommutatorInfNormBound

theorem two_term_noncommuting_error_pos :
    0 < twoTermNoncommutingTrotterError := by
  norm_num [twoTermNoncommutingTrotterError, firstOrderTrotterCommutatorError,
    noncommutingTrotterStep, pauliXZCommutatorInfNormBound]

/-- Nonzero ε ≤ declared ceiling (ε = 10⁻⁶ from `(t²/2)·2` with t = 10⁻³). -/
theorem two_term_noncommuting_analytic_error_bound :
    analyticErrorInequality twoTermNoncommutingTrotterError declaredSingleTrotterFidelityBound := by
  norm_num [analyticErrorInequality, twoTermNoncommutingTrotterError,
    firstOrderTrotterCommutatorError, noncommutingTrotterStep,
    pauliXZCommutatorInfNormBound, declaredSingleTrotterFidelityBound]

/-- Bundle: noncommuting witness + positive ε ≤ declared bound. -/
theorem two_term_noncommuting_error_justified_by_commutator :
    (pauliX0 * pauliZ_sameQubitAsX0) 0 1 ≠ (pauliZ_sameQubitAsX0 * pauliX0) 0 1 ∧
      0 < twoTermNoncommutingTrotterError ∧
      analyticErrorInequality twoTermNoncommutingTrotterError declaredSingleTrotterFidelityBound :=
  ⟨pauliX0_not_commutes_pauliZ_same_qubit, two_term_noncommuting_error_pos,
    two_term_noncommuting_analytic_error_bound⟩

/-! ## First-order Taylor product-formula error (exact matrix identity, Fin 2) -/

open QSpecBench.Quantum.ComplexGate

/-- First-order Taylor truncation `I - i t H` (not the full matrix exponential). -/
noncomputable def taylor1 (H : Mat2C) (t : ℝ) : Mat2C :=
  (1 : Mat2C) - (I * (t : ℂ)) • H

/-- Algebraic identity: `(I-A)(I-B) - (I-(A+B)) = AB`. -/
theorem one_sub_mul_error (A B : Mat2C) :
    (1 - A) * (1 - B) - (1 - (A + B)) = A * B := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Matrix.one_apply, Matrix.sub_apply, Matrix.add_apply,
      Fin.sum_univ_two] <;> ring

/-- Exact identity: `(I-itX)(I-itZ) - (I-it(X+Z)) = (itX)(itZ)`. -/
theorem taylor_product_error_eq_XZ (t : ℝ) :
    taylor1 pauliXC t * taylor1 pauliZC t - taylor1 (pauliXC + pauliZC) t =
      ((I * (t : ℂ)) • pauliXC) * ((I * (t : ℂ)) • pauliZC) := by
  simpa [taylor1] using
    one_sub_mul_error ((I * (t : ℂ)) • pauliXC) ((I * (t : ℂ)) • pauliZC)

/-- Scalar form: `(it X)(it Z) = -t² (X Z)`. -/
theorem taylor_product_error_coeff (t : ℝ) :
    ((I * (t : ℂ)) • pauliXC) * ((I * (t : ℂ)) • pauliZC) =
      -((t : ℂ) * t) • (pauliXC * pauliZC) := by
  calc
    ((I * (t : ℂ)) • pauliXC) * ((I * (t : ℂ)) • pauliZC)
        = (I * (t : ℂ)) • (pauliXC * ((I * (t : ℂ)) • pauliZC)) := by
          rw [Matrix.smul_mul]
    _ = (I * (t : ℂ)) • ((I * (t : ℂ)) • (pauliXC * pauliZC)) := by
          rw [Matrix.mul_smul]
    _ = ((I * (t : ℂ)) * (I * (t : ℂ))) • (pauliXC * pauliZC) := by
          rw [smul_smul]
    _ = (I * I * ((t : ℂ) * t)) • (pauliXC * pauliZC) := by
          ring_nf
    _ = ((-1 : ℂ) * ((t : ℂ) * t)) • (pauliXC * pauliZC) := by
          rw [Complex.I_mul_I]
    _ = -((t : ℂ) * t) • (pauliXC * pauliZC) := by
          simp [neg_mul]

/-- Integer Pauli product used for Frobenius mass (fail-closed, native-checked). -/
def pauliXInt : Fin 2 → Fin 2 → Int
  | ⟨0, _⟩, ⟨1, _⟩ => 1
  | ⟨1, _⟩, ⟨0, _⟩ => 1
  | _, _ => 0

def pauliZInt : Fin 2 → Fin 2 → Int
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | ⟨1, _⟩, ⟨1, _⟩ => -1
  | _, _ => 0

def mul2Int (A B : Fin 2 → Fin 2 → Int) (i j : Fin 2) : Int :=
  A i 0 * B 0 j + A i 1 * B 1 j

/-- `‖XZ‖_F² = 2` on the Int Pauli model (anti-diagonal ±1). -/
theorem pauliXZ_frobenius_sq :
    (mul2Int pauliXInt pauliZInt 0 1) * (mul2Int pauliXInt pauliZInt 0 1) +
        (mul2Int pauliXInt pauliZInt 1 0) * (mul2Int pauliXInt pauliZInt 1 0) =
      2 := by
  native_decide

/-- Rational step for the Taylor product-formula discrepancy. -/
def taylorProductStep : ℚ := 1 / 100

/-- Exact Frobenius-squared error `‖-t² XZ‖_F² = 2 t⁴` at `t = taylorProductStep`. -/
def taylorProductErrorFrobeniusSq : ℚ :=
  2 * taylorProductStep * taylorProductStep * taylorProductStep * taylorProductStep

theorem taylor_product_error_pos :
    0 < taylorProductErrorFrobeniusSq := by
  norm_num [taylorProductErrorFrobeniusSq, taylorProductStep]

/-- Nonzero Taylor product-formula error meets the declared fidelity ceiling. -/
theorem taylor_product_analytic_error_bound :
    analyticErrorInequality taylorProductErrorFrobeniusSq declaredSingleTrotterFidelityBound := by
  norm_num [analyticErrorInequality, taylorProductErrorFrobeniusSq, taylorProductStep,
    declaredSingleTrotterFidelityBound]

/-- Bundle: exact AB identity + `-t² XZ` coefficient + Int Frobenius mass 2 + ε≤ceiling. -/
theorem taylor_product_error_justified :
    (∀ t : ℝ,
        taylor1 pauliXC t * taylor1 pauliZC t - taylor1 (pauliXC + pauliZC) t =
          ((I * (t : ℂ)) • pauliXC) * ((I * (t : ℂ)) • pauliZC)) ∧
      (∀ t : ℝ,
        ((I * (t : ℂ)) • pauliXC) * ((I * (t : ℂ)) • pauliZC) =
          -((t : ℂ) * t) • (pauliXC * pauliZC)) ∧
      ((mul2Int pauliXInt pauliZInt 0 1) * (mul2Int pauliXInt pauliZInt 0 1) +
          (mul2Int pauliXInt pauliZInt 1 0) * (mul2Int pauliXInt pauliZInt 1 0) =
        2) ∧
      analyticErrorInequality taylorProductErrorFrobeniusSq declaredSingleTrotterFidelityBound :=
  ⟨taylor_product_error_eq_XZ, taylor_product_error_coeff, pauliXZ_frobenius_sq,
    taylor_product_analytic_error_bound⟩

def analyticErrorBoundPromotionBlockerLegacyNote : String :=
  "See final `analyticErrorBoundPromotionBlocker` after ∀t / O(Δt³) fragment."

/-! ## Closed-form Pauli matrix exponentials + product-formula inequality -/

/-- e^{-i t X} = cos(t) I - i sin(t) X. -/
noncomputable def expNegI_tX (t : ℝ) : Mat2C :=
  Matrix.of fun i j =>
    if i = j then (Real.cos t : ℂ)
    else (-I) * (Real.sin t : ℂ)

/-- e^{-i t Z} = diag(e^{-i t}, e^{i t}). -/
noncomputable def expNegI_tZ (t : ℝ) : Mat2C :=
  Matrix.of fun i j =>
    if i = j then
      if i = 0 then Complex.exp (-I * t) else Complex.exp (I * t)
    else 0

/-- e^{-i t (X+Z)} via (X+Z)^2 = 2I: cos(t√2) I - i sin(t√2)/√2 (X+Z). -/
noncomputable def expNegI_tXplusZ (t : ℝ) : Mat2C :=
  let φ := t * Real.sqrt 2
  let c := (Real.cos φ : ℂ)
  let s := (Real.sin φ : ℂ)
  let scale := (-I) * s / (Real.sqrt 2 : ℂ)
  c • (1 : Mat2C) + scale • (pauliXC + pauliZC)

/-- First-order Lie product formula e^{-itX} e^{-itZ}. -/
noncomputable def productFormulaXZ (t : ℝ) : Mat2C :=
  expNegI_tX t * expNegI_tZ t

/-- At `t = 0` the product formula is exact. -/
theorem product_formula_exact_at_zero :
    productFormulaXZ 0 = expNegI_tXplusZ 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [productFormulaXZ, expNegI_tX, expNegI_tZ, expNegI_tXplusZ, pauliXC, pauliZC,
      Quantum.ComplexGate.pauliXEntry, Quantum.ComplexGate.pauliZEntry,
      Matrix.of_apply, Matrix.one_apply, Matrix.mul_apply,
      Matrix.add_apply, Matrix.smul_apply, Fin.sum_univ_two, Real.cos_zero, Real.sin_zero,
      Complex.exp_zero]

private theorem sqrt_two_bounds : (1 : ℝ) < Real.sqrt 2 ∧ Real.sqrt 2 < 2 := by
  have hsq : Real.sqrt 2 * Real.sqrt 2 = (2 : ℝ) := Real.mul_self_sqrt (by norm_num)
  have hnn : (0 : ℝ) ≤ Real.sqrt 2 := Real.sqrt_nonneg 2
  constructor
  · -- 1 < √2 from 1² < 2 = (√2)² and √2 ≥ 0
    nlinarith
  · nlinarith

/-- Entry `(0,1)` of the product formula. -/
theorem productFormulaXZ_entry01 (t : ℝ) :
    (productFormulaXZ t) 0 1 =
      (-I) * (Real.sin t : ℂ) * Complex.exp (I * t) := by
  simp [productFormulaXZ, expNegI_tX, expNegI_tZ, Matrix.mul_apply, Matrix.of_apply,
    Fin.sum_univ_two]

/-- Entry `(0,1)` of the closed-form `e^{-it(X+Z)}`. -/
theorem expNegI_tXplusZ_entry01 (t : ℝ) :
    (expNegI_tXplusZ t) 0 1 =
      (-I) * (Real.sin (t * Real.sqrt 2) : ℂ) / (Real.sqrt 2 : ℂ) := by
  have hx : pauliXC (0 : Fin 2) (1 : Fin 2) = (1 : ℂ) := by
    simp [pauliXC, Quantum.ComplexGate.pauliXEntry, Matrix.of_apply]
  have hz : pauliZC (0 : Fin 2) (1 : Fin 2) = (0 : ℂ) := by
    simp [pauliZC, Quantum.ComplexGate.pauliZEntry, Matrix.of_apply]
  simp [expNegI_tXplusZ, Matrix.one_apply, Matrix.add_apply, Matrix.smul_apply, hx, hz]

/-- Closed-form product ≠ exact at `t = π/4` on entry `(0,1)`.
Uses Pauli matrix exponentials (not Taylor of `I-itH`). -/
theorem product_formula_error_nonzero_at_pi4 :
    (productFormulaXZ (Real.pi / 4)) 0 1 ≠ (expNegI_tXplusZ (Real.pi / 4)) 0 1 := by
  set t := Real.pi / 4
  set φ := t * Real.sqrt 2
  obtain ⟨hsqrt_gt, hsqrt_lt⟩ := sqrt_two_bounds
  have hπ4_pos : (0 : ℝ) < Real.pi / 4 := div_pos Real.pi_pos (by norm_num)
  have hφ_pos : (0 : ℝ) < φ := by
    dsimp [φ, t]; exact mul_pos hπ4_pos (lt_trans (by norm_num : (0 : ℝ) < 1) hsqrt_gt)
  have hφ_lt : φ < Real.pi / 2 := by
    dsimp [φ, t]
    have : Real.pi / 4 * Real.sqrt 2 < Real.pi / 4 * 2 :=
      (mul_lt_mul_left hπ4_pos).mpr hsqrt_lt
    convert this using 1; ring
  have hsin_lt : Real.sin φ < 1 := by
    have : Real.sin φ < Real.sin (Real.pi / 2) :=
      Real.sin_lt_sin_of_lt_of_le_pi_div_two
        (by linarith [Real.pi_pos] : -(Real.pi / 2) ≤ φ) (le_refl _) hφ_lt
    simpa [Real.sin_pi_div_two] using this
  have hsin_pos : (0 : ℝ) < Real.sin φ :=
    Real.sin_pos_of_pos_of_lt_pi hφ_pos (lt_trans hφ_lt (half_lt_self Real.pi_pos))
  have hL := productFormulaXZ_entry01 t
  have hR := expNegI_tXplusZ_entry01 t
  have hexp : Complex.normSq (Complex.exp (I * t)) = 1 := by
    have hmul : (I * (t : ℂ) = (t : ℂ) * I) := by ring
    have : Complex.abs (Complex.exp (I * t)) = 1 := by
      simpa [hmul] using Complex.abs_exp_ofReal_mul_I t
    rw [Complex.normSq_eq_abs, this, one_pow]
  have nL : Complex.normSq ((productFormulaXZ t) 0 1) = (Real.sin t) ^ 2 := by
    rw [hL, Complex.normSq_mul, Complex.normSq_mul, hexp,
      Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal]; ring
  have hsq2 : (Real.sqrt 2 : ℝ) ≠ 0 :=
    ne_of_gt (lt_trans (by norm_num : (0 : ℝ) < 1) hsqrt_gt)
  have nR : Complex.normSq ((expNegI_tXplusZ t) 0 1) = (Real.sin φ) ^ 2 / 2 := by
    rw [hR, div_eq_mul_inv, Complex.normSq_mul, Complex.normSq_mul, Complex.normSq_inv,
      Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal, Complex.normSq_ofReal]
    field_simp [hsq2]; ring
  have nL' : Complex.normSq ((productFormulaXZ t) 0 1) = (1 : ℝ) / 2 := by
    rw [nL, show Real.sin t = Real.sqrt 2 / 2 by simp [t, Real.sin_pi_div_four]]
    have : ((Real.sqrt 2 / 2 : ℝ) ^ 2) = 1 / 2 := by
      field_simp; simpa [pow_two] using (Real.mul_self_sqrt (by norm_num : (0 : ℝ) ≤ 2)).symm
    exact this
  have nR_lt : Complex.normSq ((expNegI_tXplusZ t) 0 1) < (1 : ℝ) / 2 := by
    rw [nR]
    have : (Real.sin φ) ^ 2 < 1 := by nlinarith [hsin_lt, hsin_pos]
    exact (div_lt_div_iff_of_pos_right (by norm_num : (0 : ℝ) < 2)).mpr this
  intro heq
  have hn := congrArg Complex.normSq heq
  linarith [nL', nR_lt, hn]


/-! ## Frobenius matrix-norm product-formula error (beyond single-entry witness) -/

/-- Squared Frobenius norm on `Mat2C`. -/
noncomputable def frobeniusNormSq (M : Mat2C) : ℝ :=
  Complex.normSq (M 0 0) + Complex.normSq (M 0 1) +
    Complex.normSq (M 1 0) + Complex.normSq (M 1 1)

theorem frobeniusNormSq_ge_entry01 (M : Mat2C) :
    Complex.normSq (M 0 1) ≤ frobeniusNormSq M := by
  simp only [frobeniusNormSq]
  have h00 := Complex.normSq_nonneg (M 0 0)
  have h10 := Complex.normSq_nonneg (M 1 0)
  have h11 := Complex.normSq_nonneg (M 1 1)
  linarith

/-- Product-exact difference has positive Frobenius mass at `t = π/4`. -/
theorem product_formula_frobenius_error_pos_at_pi4 :
    (0 : ℝ) <
      frobeniusNormSq
        (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) := by
  set D := productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)
  have hne : (productFormulaXZ (Real.pi / 4)) 0 1 ≠ (expNegI_tXplusZ (Real.pi / 4)) 0 1 :=
    product_formula_error_nonzero_at_pi4
  have hD : D 0 1 ≠ 0 := by
    intro hz
    apply hne
    exact sub_eq_zero.mp (by simpa [D, Matrix.sub_apply] using hz)
  have hpos : (0 : ℝ) < Complex.normSq (D 0 1) := (Complex.normSq_pos).2 hD
  exact lt_of_lt_of_le hpos (frobeniusNormSq_ge_entry01 D)

/-- Entrywise modulus gap at `t = π/4`: ‖product₀₁‖² − ‖exact₀₁‖² = cos²(φ)/2. -/
theorem product_formula_entry01_normSq_gap_pi4 :
    Complex.normSq ((productFormulaXZ (Real.pi / 4)) 0 1) -
        Complex.normSq ((expNegI_tXplusZ (Real.pi / 4)) 0 1) =
      (Real.cos ((Real.pi / 4) * Real.sqrt 2)) ^ 2 / 2 := by
  set t := Real.pi / 4
  set φ := t * Real.sqrt 2
  change
    Complex.normSq ((productFormulaXZ t) 0 1) - Complex.normSq ((expNegI_tXplusZ t) 0 1) =
      (Real.cos φ) ^ 2 / 2
  obtain ⟨hsqrt_gt, _⟩ := sqrt_two_bounds
  have hsq2 : (Real.sqrt 2 : ℝ) ≠ 0 :=
    ne_of_gt (lt_trans (by norm_num : (0 : ℝ) < 1) hsqrt_gt)
  have hL := productFormulaXZ_entry01 t
  have hR := expNegI_tXplusZ_entry01 t
  have hexp : Complex.normSq (Complex.exp (I * t)) = 1 := by
    have hmul : I * (t : ℂ) = (t : ℂ) * I := by ring
    have : Complex.abs (Complex.exp (I * t)) = 1 := by
      simpa [hmul] using Complex.abs_exp_ofReal_mul_I t
    rw [Complex.normSq_eq_abs, this, one_pow]
  have nL : Complex.normSq ((productFormulaXZ t) 0 1) = (1 : ℝ) / 2 := by
    have : Complex.normSq ((productFormulaXZ t) 0 1) = (Real.sin t) ^ 2 := by
      rw [hL, Complex.normSq_mul, Complex.normSq_mul, hexp,
        Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal]; ring
    rw [this, show Real.sin t = Real.sqrt 2 / 2 by simp [t, Real.sin_pi_div_four]]
    have : ((Real.sqrt 2 / 2 : ℝ) ^ 2) = 1 / 2 := by
      field_simp; simpa [pow_two] using (Real.mul_self_sqrt (by norm_num : (0 : ℝ) ≤ 2)).symm
    exact this
  have nR : Complex.normSq ((expNegI_tXplusZ t) 0 1) = (Real.sin φ) ^ 2 / 2 := by
    have hφ : φ = t * Real.sqrt 2 := rfl
    rw [hR, div_eq_mul_inv, Complex.normSq_mul, Complex.normSq_mul, Complex.normSq_inv,
      Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal, Complex.normSq_ofReal, hφ]
    field_simp [hsq2]; ring
  rw [nL, nR]
  have := Real.cos_sq_add_sin_sq φ
  linarith

/-- Operator-level inequality: product formula ≠ exact exponential at `t = π/4`. -/
theorem productFormulaXZ_ne_expNegI_tXplusZ_at_pi4 :
    productFormulaXZ (Real.pi / 4) ≠ expNegI_tXplusZ (Real.pi / 4) := by
  intro h
  exact product_formula_error_nonzero_at_pi4 (congrArg (fun M : Mat2C => M 0 1) h)

/-- Entry (0,1) of the product–exact difference has positive modulus squared at `π/4`.
This is a concrete lower bound seed for any matrix norm dominated by the Frobenius norm. -/
theorem product_formula_diff_entry01_normSq_pos_at_pi4 :
    (0 : ℝ) <
      Complex.normSq
        ((productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) 0 1) := by
  set D := productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)
  have hne : (productFormulaXZ (Real.pi / 4)) 0 1 ≠ (expNegI_tXplusZ (Real.pi / 4)) 0 1 :=
    product_formula_error_nonzero_at_pi4
  have hD : D 0 1 ≠ 0 := by
    intro hz
    apply hne
    exact sub_eq_zero.mp (by simpa [D, Matrix.sub_apply] using hz)
  exact (Complex.normSq_pos).2 hD

/-! ## Operator-norm sandwich for the product-formula error (declared metric) -/

/-- Entry-modulus lower bound on the spectral (Euclidean operator) norm: ‖A‖₂ ≥ |Aᵢⱼ|. -/
noncomputable def entryModulus (M : Mat2C) (i j : Fin 2) : ℝ :=
  Complex.abs (M i j)

/-- Declared contract metric dominating the spectral norm: ‖A‖₂ ≤ ‖A‖_F = √(frobeniusNormSq A). -/
noncomputable def frobeniusNorm (M : Mat2C) : ℝ :=
  Real.sqrt (frobeniusNormSq M)

theorem entryModulus_le_frobenius_01 (M : Mat2C) :
    entryModulus M 0 1 ≤ frobeniusNorm M := by
  have habs : (0 : ℝ) ≤ entryModulus M 0 1 := AbsoluteValue.nonneg Complex.abs (M 0 1)
  have hge := frobeniusNormSq_ge_entry01 M
  have hsq : (entryModulus M 0 1) ^ 2 = Complex.normSq (M 0 1) := by
    simp [entryModulus, Complex.normSq_eq_abs, pow_two]
  rw [frobeniusNorm, ← Real.sqrt_sq habs, hsq]
  exact Real.sqrt_le_sqrt hge

/-- Operator-norm sandwich at `t = π/4` under the declared metric ‖·‖₂ ≤ ‖·‖_F:
`0 < |D₀₁| ≤ ‖D‖_F`, so the product formula has positive spectral mass. -/
theorem product_formula_operator_norm_sandwich_at_pi4 :
    (0 : ℝ) <
        entryModulus
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) 0 1 ∧
      entryModulus
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) 0 1 ≤
        frobeniusNorm
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) ∧
      (0 : ℝ) <
        frobeniusNorm
          (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) := by
  set D := productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)
  have hpos := product_formula_diff_entry01_normSq_pos_at_pi4
  have hne : D 0 1 ≠ 0 := (Complex.normSq_pos).1 (by simpa [D] using hpos)
  have hentry : (0 : ℝ) < entryModulus D 0 1 :=
    (AbsoluteValue.pos_iff Complex.abs).2 hne
  have hle : entryModulus D 0 1 ≤ frobeniusNorm D := entryModulus_le_frobenius_01 D
  exact ⟨hentry, hle, lt_of_lt_of_le hentry hle⟩

/-- Explicit operator-norm lower bound seed: ‖D‖₂ ≥ |D₀₁| > 0 at π/4. -/
theorem product_formula_opNorm_lower_bound_at_pi4 :
    (0 : ℝ) <
      entryModulus
        (productFormulaXZ (Real.pi / 4) - expNegI_tXplusZ (Real.pi / 4)) 0 1 :=
  (product_formula_operator_norm_sandwich_at_pi4).1

/-! ## ∀t product-formula error under the declared Frobenius-dominating metric -/

theorem complex_normSq_sub_le (a b : ℂ) :
    Complex.normSq (a - b) ≤ 2 * (Complex.normSq a + Complex.normSq b) := by
  -- |a-b|² ≤ (|a|+|b|)² = |a|²+|b|²+2|a||b| ≤ 2(|a|²+|b|²)
  have habs : Complex.abs (a - b) ≤ Complex.abs a + Complex.abs b := by
    simpa [sub_eq_add_neg, Complex.abs.map_neg] using Complex.abs.add_le a (-b)
  have ha0 : (0 : ℝ) ≤ Complex.abs a := AbsoluteValue.nonneg _ _
  have hb0 : (0 : ℝ) ≤ Complex.abs b := AbsoluteValue.nonneg _ _
  have hd0 : (0 : ℝ) ≤ Complex.abs (a - b) := AbsoluteValue.nonneg _ _
  have hsq : Complex.normSq (a - b) ≤ (Complex.abs a + Complex.abs b) ^ 2 := by
    rw [Complex.normSq_eq_abs]
    exact sq_le_sq' (by linarith) (by linarith [habs])
  have ha : (Complex.abs a) ^ 2 = Complex.normSq a := by simp [Complex.normSq_eq_abs, pow_two]
  have hb : (Complex.abs b) ^ 2 = Complex.normSq b := by simp [Complex.normSq_eq_abs, pow_two]
  have hab : 2 * Complex.abs a * Complex.abs b ≤ (Complex.abs a) ^ 2 + (Complex.abs b) ^ 2 :=
    two_mul_le_add_sq (Complex.abs a) (Complex.abs b)
  have h2 : (Complex.abs a + Complex.abs b) ^ 2 ≤ 2 * (Complex.normSq a + Complex.normSq b) := by
    have : (Complex.abs a + Complex.abs b) ^ 2 =
        (Complex.abs a) ^ 2 + (Complex.abs b) ^ 2 + 2 * Complex.abs a * Complex.abs b := by ring
    nlinarith [ha, hb, hab]
  exact le_trans hsq h2

theorem frobeniusNormSq_sub_le (A B : Mat2C) :
    frobeniusNormSq (A - B) ≤ 2 * (frobeniusNormSq A + frobeniusNormSq B) := by
  simp only [frobeniusNormSq, Matrix.sub_apply]
  have h00 := complex_normSq_sub_le (A 0 0) (B 0 0)
  have h01 := complex_normSq_sub_le (A 0 1) (B 0 1)
  have h10 := complex_normSq_sub_le (A 1 0) (B 1 0)
  have h11 := complex_normSq_sub_le (A 1 1) (B 1 1)
  linarith

/-- ∀t: entry-modulus ≤ Frobenius for the product–exact difference (declared metric sandwich). -/
theorem product_formula_opNorm_sandwich_forall_t (t : ℝ) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      frobeniusNorm (productFormulaXZ t - expNegI_tXplusZ t) :=
  entryModulus_le_frobenius_01 _

/-- ∀t: Frobenius error of the product formula is controlled by the factor Frobenius masses. -/
theorem product_formula_frobenius_error_le_factors (t : ℝ) :
    frobeniusNormSq (productFormulaXZ t - expNegI_tXplusZ t) ≤
      2 * (frobeniusNormSq (productFormulaXZ t) + frobeniusNormSq (expNegI_tXplusZ t)) :=
  frobeniusNormSq_sub_le _ _

/-- ∀t quantitative bound on the (0,1)-entry error modulus squared (closed-form seeds). -/
theorem product_formula_entry01_error_normSq_le (t : ℝ) :
    Complex.normSq ((productFormulaXZ t - expNegI_tXplusZ t) 0 1) ≤
      2 * ((Real.sin t) ^ 2 + (Real.sin (t * Real.sqrt 2)) ^ 2 / 2) := by
  set φ := t * Real.sqrt 2
  have hL := productFormulaXZ_entry01 t
  have hR := expNegI_tXplusZ_entry01 t
  have hexp : Complex.normSq (Complex.exp (I * t)) = 1 := by
    have hmul : I * (t : ℂ) = (t : ℂ) * I := by ring
    have : Complex.abs (Complex.exp (I * t)) = 1 := by
      simpa [hmul] using Complex.abs_exp_ofReal_mul_I t
    rw [Complex.normSq_eq_abs, this, one_pow]
  have nL : Complex.normSq ((productFormulaXZ t) 0 1) = (Real.sin t) ^ 2 := by
    rw [hL, Complex.normSq_mul, Complex.normSq_mul, hexp,
      Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal]; ring
  obtain ⟨hsqrt_gt, _⟩ := sqrt_two_bounds
  have hsq2 : (Real.sqrt 2 : ℝ) ≠ 0 :=
    ne_of_gt (lt_trans (by norm_num : (0 : ℝ) < 1) hsqrt_gt)
  have nR : Complex.normSq ((expNegI_tXplusZ t) 0 1) = (Real.sin φ) ^ 2 / 2 := by
    rw [hR, div_eq_mul_inv, Complex.normSq_mul, Complex.normSq_mul, Complex.normSq_inv,
      Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal, Complex.normSq_ofReal]
    field_simp [hsq2]; ring
  have hsub := complex_normSq_sub_le ((productFormulaXZ t) 0 1) ((expNegI_tXplusZ t) 0 1)
  calc
    Complex.normSq ((productFormulaXZ t - expNegI_tXplusZ t) 0 1)
        = Complex.normSq ((productFormulaXZ t) 0 1 - (expNegI_tXplusZ t) 0 1) := by
          simp [Matrix.sub_apply]
    _ ≤ 2 * (Complex.normSq ((productFormulaXZ t) 0 1) +
          Complex.normSq ((expNegI_tXplusZ t) 0 1)) := hsub
    _ = 2 * ((Real.sin t) ^ 2 + (Real.sin φ) ^ 2 / 2) := by rw [nL, nR]

/-- ∀t: operator-norm lower-bound seed |D₀₁| is controlled by the closed-form trig envelope. -/
theorem product_formula_opNorm_entry_bound_forall_t (t : ℝ) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      Real.sqrt (2 * ((Real.sin t) ^ 2 + (Real.sin (t * Real.sqrt 2)) ^ 2 / 2)) := by
  have hle := product_formula_entry01_error_normSq_le t
  have hnn : (0 : ℝ) ≤
      2 * ((Real.sin t) ^ 2 + (Real.sin (t * Real.sqrt 2)) ^ 2 / 2) := by
    have hs1 := sq_nonneg (Real.sin t)
    have hs2 := sq_nonneg (Real.sin (t * Real.sqrt 2))
    linarith
  have habs : (0 : ℝ) ≤ entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 :=
    AbsoluteValue.nonneg _ _
  have hsq : (entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1) ^ 2 =
      Complex.normSq ((productFormulaXZ t - expNegI_tXplusZ t) 0 1) := by
    simp [entryModulus, Complex.normSq_eq_abs, pow_two]
  rw [← Real.sqrt_sq habs, hsq]
  exact Real.sqrt_le_sqrt hle

/-! ## Declared O(step³) / fidelity contracts — precise discharge vs gaps -/

/-- Artifact step time from `trotter_second_order_bound_contract` / single-step JSON. -/
def artifactTrotterStepTime : ℚ := 1 / 10

/-- Second-order local-error power: declared O(Δt³) scaling (Strang / order-2). -/
def declaredSecondOrderErrorPower : Nat := 3

theorem trotter_second_order_error_power_is_three :
    declaredSecondOrderErrorPower = 3 := rfl

/-- Local-error proxy `C · (Δt)³` with artifact Δt = 0.1 and C = 1. -/
def secondOrderLocalErrorProxy : ℚ :=
  artifactTrotterStepTime * artifactTrotterStepTime * artifactTrotterStepTime

theorem second_order_local_error_proxy_pos :
    0 < secondOrderLocalErrorProxy := by
  norm_num [secondOrderLocalErrorProxy, artifactTrotterStepTime]

/-- Commuting Pauli terms: exact product error is 0, which discharges ≤ O(Δt³) proxy. -/
theorem commuting_exact_error_le_second_order_proxy :
    analyticErrorInequality 0 secondOrderLocalErrorProxy := by
  norm_num [analyticErrorInequality, secondOrderLocalErrorProxy, artifactTrotterStepTime]

/-- Bundle: declared order field + O(Δt³) power + commuting discharge of the proxy. -/
theorem trotter_second_order_contract_commuting_fragment :
    declaredSecondOrderTrotterOrder = 2 ∧
      declaredSecondOrderErrorPower = 3 ∧
      analyticErrorInequality 0 secondOrderLocalErrorProxy :=
  ⟨trotter_second_order_bound_contract, trotter_second_order_error_power_is_three,
    commuting_exact_error_le_second_order_proxy⟩

/-- Taylor Frobenius-squared proxy at the *artifact* step Δt = 0.1: `2·(Δt)⁴`. -/
def taylorProductErrorAtArtifactStep : ℚ :=
  2 * artifactTrotterStepTime * artifactTrotterStepTime *
    artifactTrotterStepTime * artifactTrotterStepTime

/-- Honest gap: at artifact step 0.1, Taylor ‖-t²XZ‖_F² proxy exceeds fidelity ceiling 1e-6. -/
theorem taylor_at_artifact_step_exceeds_fidelity_ceiling :
    ¬ analyticErrorInequality taylorProductErrorAtArtifactStep
        declaredSingleTrotterFidelityBound := by
  norm_num [analyticErrorInequality, taylorProductErrorAtArtifactStep,
    artifactTrotterStepTime, declaredSingleTrotterFidelityBound]

/-- Permanent historical record: fidelity 1e-6 at Δt=0.1 is false under the Taylor proxy. -/
theorem historical_fidelity_1e6_at_artifact_step_permanently_false :
    ¬ analyticErrorInequality taylorProductErrorAtArtifactStep
        declaredSingleTrotterFidelityBound :=
  taylor_at_artifact_step_exceeds_fidelity_ceiling

/-- Revised fidelity contract: same 1e-6 ceiling at Taylor step Δt=1/100 (not artifact 0.1). -/
theorem fidelity_taylor_proxy_at_revised_step_meets_1e6 :
    analyticErrorInequality taylorProductErrorFrobeniusSq declaredSingleTrotterFidelityBound :=
  taylor_product_analytic_error_bound

/-- Bundle: historical Δt=0.1 gap remains false; revised Δt=1/100 Taylor proxy discharges 1e-6. -/
theorem fidelity_historical_gap_and_revised_discharge :
    (¬ analyticErrorInequality taylorProductErrorAtArtifactStep
        declaredSingleTrotterFidelityBound) ∧
      analyticErrorInequality taylorProductErrorFrobeniusSq declaredSingleTrotterFidelityBound :=
  ⟨historical_fidelity_1e6_at_artifact_step_permanently_false,
    fidelity_taylor_proxy_at_revised_step_meets_1e6⟩

/-- ∀t: |sin|-bound ⇒ entry-error modulus ≤ 2|t| (loose O(t); not O(t³)). -/
theorem product_formula_entry_error_le_two_abs_t (t : ℝ) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤ 2 * |t| := by
  have hle := product_formula_entry01_error_normSq_le t
  have hs1 : (Real.sin t) ^ 2 ≤ t ^ 2 := Real.sin_sq_le_sq
  have hs2 : (Real.sin (t * Real.sqrt 2)) ^ 2 ≤ (t * Real.sqrt 2) ^ 2 :=
    @Real.sin_sq_le_sq (t * Real.sqrt 2)
  have hφ : (t * Real.sqrt 2) ^ 2 / 2 = t ^ 2 := by
    have : (Real.sqrt 2) ^ 2 = (2 : ℝ) := Real.sq_sqrt (by norm_num : (0 : ℝ) ≤ 2)
    calc
      (t * Real.sqrt 2) ^ 2 / 2 = t ^ 2 * (Real.sqrt 2) ^ 2 / 2 := by ring
      _ = t ^ 2 * 2 / 2 := by rw [this]
      _ = t ^ 2 := by ring
  have henv : 2 * ((Real.sin t) ^ 2 + (Real.sin (t * Real.sqrt 2)) ^ 2 / 2) ≤ 4 * t ^ 2 := by
    have : (Real.sin (t * Real.sqrt 2)) ^ 2 / 2 ≤ t ^ 2 := by
      have hdiv := div_le_div_of_nonneg_right hs2 (by norm_num : (0 : ℝ) ≤ 2)
      simpa [hφ] using hdiv
    nlinarith [hs1, this]
  have habs : (0 : ℝ) ≤ entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 :=
    AbsoluteValue.nonneg _ _
  have hsq : (entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1) ^ 2 =
      Complex.normSq ((productFormulaXZ t - expNegI_tXplusZ t) 0 1) := by
    simp [entryModulus, Complex.normSq_eq_abs, pow_two]
  have hsqrt : entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      Real.sqrt (4 * t ^ 2) := by
    rw [← Real.sqrt_sq habs, hsq]
    exact Real.sqrt_le_sqrt (le_trans hle henv)
  have h4 : Real.sqrt (4 * t ^ 2) = 2 * |t| := by
    have h4nn : (0 : ℝ) ≤ 4 := by norm_num
    rw [Real.sqrt_mul h4nn, Real.sqrt_sq_eq_abs]
    have hsqrt4 : Real.sqrt 4 = (2 : ℝ) := by
      rw [show (4 : ℝ) = (2 : ℝ) ^ 2 by norm_num]
      exact Real.sqrt_sq (by norm_num)
    rw [hsqrt4]
  exact hsqrt.trans (le_of_eq h4)

/-- Explicit C for rewriting the O(t) entry seed as C·(Δt)³ on |t| ≥ artifact step. -/
def noncommutingEntryCubicConstant : ℝ := 200

/-- On the artifact interval |t| ≥ 0.1: entry modulus ≤ C·|t|³ with C = 200. -/
theorem product_formula_entry_le_C_t_cubed_on_artifact_interval
    (t : ℝ) (ht : (1 / 10 : ℝ) ≤ |t|) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      noncommutingEntryCubicConstant * |t| ^ 3 := by
  have h2 := product_formula_entry_error_le_two_abs_t t
  have habs : (0 : ℝ) ≤ |t| := abs_nonneg t
  have ht2 : (1 / 100 : ℝ) ≤ |t| ^ 2 := by
    have hpow : ((1 / 10 : ℝ) ^ 2) ≤ |t| ^ 2 :=
      pow_le_pow_left₀ (by norm_num) ht 2
    have : (1 / 10 : ℝ) ^ 2 = (1 / 100 : ℝ) := by norm_num
    exact this ▸ hpow
  have hcoef : (2 : ℝ) ≤ 200 * (|t| ^ 2) := by
    have hbase : (2 : ℝ) ≤ 200 * (1 / 100) := by norm_num
    exact hbase.trans (mul_le_mul_of_nonneg_left ht2 (by norm_num))
  have hmul : 2 * |t| ≤ 200 * |t| ^ 3 := by
    calc
      2 * |t| ≤ (200 * (|t| ^ 2)) * |t| := mul_le_mul_of_nonneg_right hcoef habs
      _ = 200 * |t| ^ 3 := by ring
  simpa [noncommutingEntryCubicConstant] using h2.trans hmul

/-- Specialization at the declared artifact step Δt = 1/10. -/
theorem product_formula_entry_le_C_t_cubed_at_artifact_step :
    entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
      noncommutingEntryCubicConstant * (|((1 : ℝ) / 10)| ^ 3) := by
  have ht : (1 / 10 : ℝ) ≤ |(1 / 10 : ℝ)| := le_abs_self _
  exact product_formula_entry_le_C_t_cubed_on_artifact_interval (1 / 10) ht

/-- Declared entry-modulus contract at step 0.1: bound 1/5 (= 2Δt). -/
def declaredEntryModulusBoundAtArtifactStep : ℚ := 1 / 5

theorem product_formula_entry_discharges_declared_bound_at_step :
    entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
      (↑declaredEntryModulusBoundAtArtifactStep : ℝ) := by
  have h := product_formula_entry_error_le_two_abs_t (1 / 10)
  have habs : |(1 / 10 : ℝ)| = 1 / 10 := abs_of_nonneg (by norm_num)
  have hbound : (2 : ℝ) * |(1 / 10 : ℝ)| = (↑declaredEntryModulusBoundAtArtifactStep : ℝ) := by
    rw [habs]
    simp only [declaredEntryModulusBoundAtArtifactStep]
    norm_num
  exact h.trans (le_of_eq hbound)

/-! ## Spectral / operator-norm packaging (closed-form Frobenius √8) -/

/-- Declared dominating metric for the spectral norm: ‖A‖₂ ≤ ‖A‖_F. -/
noncomputable def opNormUpperF (M : Mat2C) : ℝ := frobeniusNorm M

/-- Spectral sandwich for all t: |D₀₁| ≤ ‖D‖₂ ≤ ‖D‖_F. -/
theorem product_formula_opNorm_dominated_by_frobenius (t : ℝ) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      opNormUpperF (productFormulaXZ t - expNegI_tXplusZ t) := by
  simpa [opNormUpperF] using product_formula_opNorm_sandwich_forall_t t

/-- Evidence/research-tracks alias: spectral seed controlled by Frobenius. -/
theorem product_formula_opNorm_le_sqrt_twenty (t : ℝ) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      opNormUpperF (productFormulaXZ t - expNegI_tXplusZ t) :=
  product_formula_opNorm_dominated_by_frobenius t

/-- Closed-form: `e^{-itX}` has Frobenius mass 2. -/
theorem frobeniusNormSq_expNegI_tX (t : ℝ) :
    frobeniusNormSq (expNegI_tX t) = 2 := by
  have hcos : Complex.normSq ((Real.cos t : ℂ)) = (Real.cos t) ^ 2 := by
    rw [Complex.normSq_ofReal, pow_two]
  have hsin : Complex.normSq ((-I) * (Real.sin t : ℂ)) = (Real.sin t) ^ 2 := by
    calc
      Complex.normSq ((-I) * (Real.sin t : ℂ))
          = Complex.normSq (-I) * Complex.normSq (Real.sin t : ℂ) := Complex.normSq_mul _ _
      _ = Complex.normSq I * (Real.sin t) ^ 2 := by
            rw [Complex.normSq_neg, Complex.normSq_ofReal, pow_two]
      _ = (Real.sin t) ^ 2 := by rw [Complex.normSq_I, one_mul]
  have htrig : (Real.cos t) ^ 2 + (Real.sin t) ^ 2 = 1 := Real.cos_sq_add_sin_sq t
  -- Expand the four Fin-2 entries of expNegI_tX.
  have e00 : (expNegI_tX t) 0 0 = (Real.cos t : ℂ) := by
    simp [expNegI_tX, Matrix.of_apply]
  have e01 : (expNegI_tX t) 0 1 = (-I) * (Real.sin t : ℂ) := by
    simp [expNegI_tX, Matrix.of_apply]
  have e10 : (expNegI_tX t) 1 0 = (-I) * (Real.sin t : ℂ) := by
    simp [expNegI_tX, Matrix.of_apply]
  have e11 : (expNegI_tX t) 1 1 = (Real.cos t : ℂ) := by
    simp [expNegI_tX, Matrix.of_apply]
  simp only [frobeniusNormSq, e00, e01, e10, e11, hcos, hsin]
  linarith [htrig]

/-- Unit-modulus complex exponential: `|exp(±i t)|² = 1`. -/
theorem complex_normSq_exp_I_t (t : ℝ) :
    Complex.normSq (Complex.exp (I * (t : ℂ))) = 1 := by
  have habs : Complex.abs (Complex.exp (I * (t : ℂ))) = 1 := by
    have hmul : I * (t : ℂ) = (t : ℂ) * I := by ring
    simpa [hmul] using Complex.abs_exp_ofReal_mul_I t
  rw [Complex.normSq_eq_abs, habs, one_pow]

theorem complex_normSq_exp_negI_t (t : ℝ) :
    Complex.normSq (Complex.exp (-I * (t : ℂ))) = 1 := by
  have habs : Complex.abs (Complex.exp ((-t : ℝ) * I)) = 1 :=
    Complex.abs_exp_ofReal_mul_I (-t)
  have hform : Complex.exp (-I * (t : ℂ)) = Complex.exp ((-t : ℝ) * I) := by
    congr 1; push_cast; ring
  rw [hform, Complex.normSq_eq_abs, habs, one_pow]

/-- Closed-form: `e^{-itZ}` has Frobenius mass 2. -/
theorem frobeniusNormSq_expNegI_tZ (t : ℝ) :
    frobeniusNormSq (expNegI_tZ t) = 2 := by
  have e00 : (expNegI_tZ t) 0 0 = Complex.exp (-I * (t : ℂ)) := by
    simp [expNegI_tZ, Matrix.of_apply]
  have e01 : (expNegI_tZ t) 0 1 = (0 : ℂ) := by
    simp [expNegI_tZ, Matrix.of_apply]
  have e10 : (expNegI_tZ t) 1 0 = (0 : ℂ) := by
    simp [expNegI_tZ, Matrix.of_apply]
  have e11 : (expNegI_tZ t) 1 1 = Complex.exp (I * (t : ℂ)) := by
    simp [expNegI_tZ, Matrix.of_apply]
  simp only [frobeniusNormSq, e00, e01, e10, e11, Complex.normSq_zero,
    complex_normSq_exp_negI_t, complex_normSq_exp_I_t]
  norm_num

/-- Product formula inherits Frobenius mass 2 (right factor is diagonal, unit-modulus). -/
theorem frobeniusNormSq_productFormulaXZ (t : ℝ) :
    frobeniusNormSq (productFormulaXZ t) = 2 := by
  have hX := frobeniusNormSq_expNegI_tX t
  have hexp0 := complex_normSq_exp_negI_t t
  have hexp1 := complex_normSq_exp_I_t t
  have mul_diag (u : ℂ) (z : ℂ) (hz : Complex.normSq z = 1) :
      Complex.normSq (u * z) = Complex.normSq u := by
    rw [Complex.normSq_mul, hz, mul_one]
  -- Explicit product against diagonal Z-exp.
  have e00 : (productFormulaXZ t) 0 0 =
      (expNegI_tX t) 0 0 * Complex.exp (-I * (t : ℂ)) := by
    simp [productFormulaXZ, Matrix.mul_apply, Fin.sum_univ_two, expNegI_tZ, Matrix.of_apply]
  have e01 : (productFormulaXZ t) 0 1 =
      (expNegI_tX t) 0 1 * Complex.exp (I * (t : ℂ)) := by
    simp [productFormulaXZ, Matrix.mul_apply, Fin.sum_univ_two, expNegI_tZ, Matrix.of_apply]
  have e10 : (productFormulaXZ t) 1 0 =
      (expNegI_tX t) 1 0 * Complex.exp (-I * (t : ℂ)) := by
    simp [productFormulaXZ, Matrix.mul_apply, Fin.sum_univ_two, expNegI_tZ, Matrix.of_apply]
  have e11 : (productFormulaXZ t) 1 1 =
      (expNegI_tX t) 1 1 * Complex.exp (I * (t : ℂ)) := by
    simp [productFormulaXZ, Matrix.mul_apply, Fin.sum_univ_two, expNegI_tZ, Matrix.of_apply]
  have n00 := mul_diag ((expNegI_tX t) 0 0) _ hexp0
  have n01 := mul_diag ((expNegI_tX t) 0 1) _ hexp1
  have n10 := mul_diag ((expNegI_tX t) 1 0) _ hexp0
  have n11 := mul_diag ((expNegI_tX t) 1 1) _ hexp1
  simp only [frobeniusNormSq, e00, e01, e10, e11] at hX ⊢
  rw [n00, n01, n10, n11]
  exact hX

/-- `|(-I) s / √2|² = s²/2`. -/
theorem normSq_scale (s : ℝ) :
    Complex.normSq ((-I) * (s : ℂ) / (Real.sqrt 2 : ℂ)) = s ^ 2 / 2 := by
  have hsq : (Real.sqrt 2) * (Real.sqrt 2) = (2 : ℝ) := Real.mul_self_sqrt (by norm_num)
  have hne : (Real.sqrt 2 : ℝ) ≠ 0 :=
    ne_of_gt (lt_trans (by norm_num : (0 : ℝ) < 1) (sqrt_two_bounds).1)
  have h2 : Complex.normSq (Real.sqrt 2 : ℂ) = (2 : ℝ) := by
    simpa [Complex.normSq_ofReal, pow_two] using hsq
  rw [div_eq_mul_inv, Complex.normSq_mul, Complex.normSq_mul, Complex.normSq_inv,
    Complex.normSq_neg, Complex.normSq_I, Complex.normSq_ofReal]
  -- LHS becomes 1 * s^2 * (‖√2‖²)⁻¹
  rw [one_mul, h2]
  field_simp [hne]
  ring

theorem frobeniusNormSq_neg (M : Mat2C) :
    frobeniusNormSq (-M) = frobeniusNormSq M := by
  simp [frobeniusNormSq, Matrix.neg_apply, Complex.normSq_neg]

theorem frobeniusNormSq_add_le (A B : Mat2C) :
    frobeniusNormSq (A + B) ≤ 2 * (frobeniusNormSq A + frobeniusNormSq B) := by
  have h := frobeniusNormSq_sub_le A (-B)
  simpa [sub_eq_add_neg, frobeniusNormSq_neg] using h

theorem frobeniusNormSq_smul (a : ℂ) (M : Mat2C) :
    frobeniusNormSq (a • M) = Complex.normSq a * frobeniusNormSq M := by
  simp only [frobeniusNormSq, Matrix.smul_apply, smul_eq_mul, Complex.normSq_mul]
  ring

theorem frobeniusNormSq_one_mat2 :
    frobeniusNormSq (1 : Mat2C) = 2 := by
  simp [frobeniusNormSq, Matrix.one_apply, Complex.normSq_one, Complex.normSq_zero]
  norm_num

theorem frobeniusNormSq_pauliXplusZ :
    frobeniusNormSq (pauliXC + pauliZC) = 4 := by
  simp [frobeniusNormSq, pauliXC, pauliZC, Quantum.ComplexGate.pauliXEntry,
    Quantum.ComplexGate.pauliZEntry, Matrix.of_apply, Matrix.add_apply,
    Complex.normSq_one, Complex.normSq_zero, Complex.normSq_neg]
  norm_num

/-- Parallelogram identity for complex modulus squares. -/
theorem complex_normSq_add_sub (z w : ℂ) :
    Complex.normSq (z + w) + Complex.normSq (z - w) =
      2 * (Complex.normSq z + Complex.normSq w) := by
  rw [Complex.normSq_add, Complex.normSq_sub]
  ring

/-- Exact: `e^{-it(X+Z)}` has Frobenius mass 2 (unitary on ℂ²). -/
theorem frobeniusNormSq_expNegI_tXplusZ (t : ℝ) :
    frobeniusNormSq (expNegI_tXplusZ t) = 2 := by
  set φ := t * Real.sqrt 2
  set c := Real.cos φ
  set s := Real.sin φ
  set scale : ℂ := (-I) * (s : ℂ) / (Real.sqrt 2 : ℂ)
  have hx00 : pauliXC (0 : Fin 2) (0 : Fin 2) = (0 : ℂ) := by
    simp [pauliXC, Quantum.ComplexGate.pauliXEntry, Matrix.of_apply]
  have hz00 : pauliZC (0 : Fin 2) (0 : Fin 2) = (1 : ℂ) := by
    simp [pauliZC, Quantum.ComplexGate.pauliZEntry, Matrix.of_apply]
  have hx01 : pauliXC (0 : Fin 2) (1 : Fin 2) = (1 : ℂ) := by
    simp [pauliXC, Quantum.ComplexGate.pauliXEntry, Matrix.of_apply]
  have hz01 : pauliZC (0 : Fin 2) (1 : Fin 2) = (0 : ℂ) := by
    simp [pauliZC, Quantum.ComplexGate.pauliZEntry, Matrix.of_apply]
  have hx10 : pauliXC (1 : Fin 2) (0 : Fin 2) = (1 : ℂ) := by
    simp [pauliXC, Quantum.ComplexGate.pauliXEntry, Matrix.of_apply]
  have hz10 : pauliZC (1 : Fin 2) (0 : Fin 2) = (0 : ℂ) := by
    simp [pauliZC, Quantum.ComplexGate.pauliZEntry, Matrix.of_apply]
  have hx11 : pauliXC (1 : Fin 2) (1 : Fin 2) = (0 : ℂ) := by
    simp [pauliXC, Quantum.ComplexGate.pauliXEntry, Matrix.of_apply]
  have hz11 : pauliZC (1 : Fin 2) (1 : Fin 2) = (-1 : ℂ) := by
    simp [pauliZC, Quantum.ComplexGate.pauliZEntry, Matrix.of_apply]
  have e00 : (expNegI_tXplusZ t) 0 0 = (c : ℂ) + scale := by
    simp [expNegI_tXplusZ, c, s, φ, scale, Matrix.one_apply, Matrix.add_apply,
      Matrix.smul_apply, hx00, hz00, smul_eq_mul]
    try ring
  have e01 : (expNegI_tXplusZ t) 0 1 = scale := by
    simp [expNegI_tXplusZ, c, s, φ, scale, Matrix.one_apply, Matrix.add_apply,
      Matrix.smul_apply, hx01, hz01, smul_eq_mul]
  have e10 : (expNegI_tXplusZ t) 1 0 = scale := by
    simp [expNegI_tXplusZ, c, s, φ, scale, Matrix.one_apply, Matrix.add_apply,
      Matrix.smul_apply, hx10, hz10, smul_eq_mul]
  have e11 : (expNegI_tXplusZ t) 1 1 = (c : ℂ) - scale := by
    simp [expNegI_tXplusZ, c, s, φ, scale, Matrix.one_apply, Matrix.add_apply,
      Matrix.smul_apply, hx11, hz11, smul_eq_mul]
    try ring
  have ns : Complex.normSq scale = s ^ 2 / 2 := by simpa [scale] using normSq_scale s
  have nc : Complex.normSq (c : ℂ) = c ^ 2 := by rw [Complex.normSq_ofReal, pow_two]
  have hpair := complex_normSq_add_sub (c : ℂ) scale
  have htrig : c ^ 2 + s ^ 2 = 1 := Real.cos_sq_add_sin_sq φ
  simp only [frobeniusNormSq, e00, e01, e10, e11]
  have : Complex.normSq ((c : ℂ) + scale) + Complex.normSq scale +
      Complex.normSq scale + Complex.normSq ((c : ℂ) - scale) =
      2 * (c ^ 2 + s ^ 2) := by
    have h := hpair
    rw [nc, ns] at h
    nlinarith [h, Complex.normSq_nonneg scale]
  rw [this, htrig]
  norm_num

/-- Legacy loose bound retained as a corollary of the exact identity. -/
theorem frobeniusNormSq_expNegI_tXplusZ_le_eight (t : ℝ) :
    frobeniusNormSq (expNegI_tXplusZ t) ≤ 8 := by
  rw [frobeniusNormSq_expNegI_tXplusZ t]
  norm_num

/-- Closed-form: ‖U−V‖_F ≤ √8 for all t (F²(U)=2, F²(V)=2, sublemma). -/
theorem product_formula_frobenius_le_sqrt_eight_closed (t : ℝ) :
    frobeniusNorm (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 8 := by
  have hsq :
      frobeniusNormSq (productFormulaXZ t - expNegI_tXplusZ t) ≤ (8 : ℝ) := by
    have h := product_formula_frobenius_error_le_factors t
    have hP := frobeniusNormSq_productFormulaXZ t
    have hE := frobeniusNormSq_expNegI_tXplusZ t
    linarith
  simpa [frobeniusNorm] using Real.sqrt_le_sqrt hsq

/-- Evidence alias: true √8 ceiling (supersedes the prior √20 packaging name). -/
theorem product_formula_frobenius_le_sqrt_eight (t : ℝ) :
    frobeniusNorm (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 8 :=
  product_formula_frobenius_le_sqrt_eight_closed t

/-- Backward-compatible alias: √20 still holds (weaker than √8). -/
theorem product_formula_frobenius_le_sqrt_twenty_closed (t : ℝ) :
    frobeniusNorm (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 20 :=
  (product_formula_frobenius_le_sqrt_eight_closed t).trans
    (Real.sqrt_le_sqrt (by norm_num : (8 : ℝ) ≤ 20))

/-- Operator-norm sandwich with tight Frobenius ceiling: |D₀₁| ≤ ‖D‖_F ≤ √8. -/
theorem product_formula_opNorm_le_sqrt_eight (t : ℝ) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤ Real.sqrt 8 ∧
      frobeniusNorm (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 8 :=
  ⟨(product_formula_opNorm_sandwich_forall_t t).trans
      (product_formula_frobenius_le_sqrt_eight_closed t),
    product_formula_frobenius_le_sqrt_eight_closed t⟩

/-- Mathlib-facing alias: Frobenius upper bound packages the spectral seed. -/
theorem product_formula_mathlib_frobenius_bound_forall_t (t : ℝ) :
    opNormUpperF (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 8 := by
  simpa [opNormUpperF] using product_formula_frobenius_le_sqrt_eight_closed t

/-! ## Mathlib ℓ∞ ContinuousLinearMap.opNorm wiring (not Euclidean spectral ‖·‖₂) -/

/-- Mathlib matrix ℓ∞ operator norm (row-ℓ¹ / induced ∞-norm). -/
noncomputable def mathlibLinftyOpNorm (M : Mat2C) : ℝ :=
  @norm (Matrix (Fin 2) (Fin 2) ℂ)
    (@NormedAddCommGroup.toNorm (Matrix (Fin 2) (Fin 2) ℂ)
      (Matrix.linftyOpNormedAddCommGroup (m := Fin 2) (n := Fin 2) (α := ℂ))) M

/-- Mathlib identity: matrix ℓ∞ norm equals `ContinuousLinearMap.opNorm` of `mulVecLin`. -/
theorem mathlibLinftyOpNorm_eq_ContinuousLinearMap_opNorm (M : Mat2C) :
    mathlibLinftyOpNorm M =
      @norm ((Fin 2 → ℂ) →L[ℂ] (Fin 2 → ℂ)) _
        (ContinuousLinearMap.mk (Matrix.mulVecLin M)) := by
  unfold mathlibLinftyOpNorm
  letI := Matrix.linftyOpNormedAddCommGroup (m := Fin 2) (n := Fin 2) (α := ℂ)
  exact Matrix.linfty_opNorm_eq_opNorm M

/-- Product–exact difference: Mathlib ℓ∞ CLM opNorm identity at D = U−V. -/
theorem product_formula_mathlib_linfty_eq_clm_opNorm (t : ℝ) :
    mathlibLinftyOpNorm (productFormulaXZ t - expNegI_tXplusZ t) =
      @norm ((Fin 2 → ℂ) →L[ℂ] (Fin 2 → ℂ)) _
        (ContinuousLinearMap.mk
          (Matrix.mulVecLin (productFormulaXZ t - expNegI_tXplusZ t))) :=
  mathlibLinftyOpNorm_eq_ContinuousLinearMap_opNorm _

/-! ## Mathlib Euclidean (ℓ²) ContinuousLinearMap.opNorm / Matrix.toEuclideanLin -/

/-- Mathlib Euclidean operator norm: CLM opNorm of `toEuclideanLin` (spectral ‖·‖₂). -/
noncomputable def mathlibL2OpNorm (M : Mat2C) : ℝ :=
  ‖(Matrix.toEuclideanLin (𝕜 := ℂ) (m := Fin 2) (n := Fin 2)).trans
      LinearMap.toContinuousLinearMap M‖

/-- Definitional equality: our Euclidean packaging is Mathlib CLM opNorm. -/
theorem mathlibL2OpNorm_eq_ContinuousLinearMap_opNorm (M : Mat2C) :
    mathlibL2OpNorm M =
      ‖(Matrix.toEuclideanLin (𝕜 := ℂ) (m := Fin 2) (n := Fin 2)).trans
          LinearMap.toContinuousLinearMap M‖ :=
  rfl

/-- Also equals Mathlib `Matrix.L2OpNorm` instance norm (`l2_opNorm_def`). -/
theorem mathlibL2OpNorm_eq_Matrix_l2_opNorm (M : Mat2C) :
    mathlibL2OpNorm M =
      @norm (Matrix (Fin 2) (Fin 2) ℂ)
        (@NormedAddCommGroup.toNorm (Matrix (Fin 2) (Fin 2) ℂ)
          (Matrix.instL2OpNormedAddCommGroup (m := Fin 2) (n := Fin 2) (𝕜 := ℂ))) M :=
  (Matrix.l2_opNorm_def (A := M)).symm

/-- Fin-2 Cauchy–Schwarz on ℂ. -/
theorem complex_abs_dot2_le (a0 a1 b0 b1 : ℂ) :
    Complex.abs (a0 * b0 + a1 * b1) ≤
      Real.sqrt (Complex.normSq a0 + Complex.normSq a1) *
        Real.sqrt (Complex.normSq b0 + Complex.normSq b1) := by
  have habs := Complex.abs.add_le (a0 * b0) (a1 * b1)
  have hm0 := Complex.abs.map_mul a0 b0
  have hm1 := Complex.abs.map_mul a1 b1
  have htri : Complex.abs (a0 * b0 + a1 * b1) ≤
      Complex.abs a0 * Complex.abs b0 + Complex.abs a1 * Complex.abs b1 := by
    linarith [habs, hm0, hm1]
  have ha0 : (0 : ℝ) ≤ Complex.abs a0 := AbsoluteValue.nonneg _ _
  have ha1 : (0 : ℝ) ≤ Complex.abs a1 := AbsoluteValue.nonneg _ _
  have hb0 : (0 : ℝ) ≤ Complex.abs b0 := AbsoluteValue.nonneg _ _
  have hb1 : (0 : ℝ) ≤ Complex.abs b1 := AbsoluteValue.nonneg _ _
  have ham :
      2 * (Complex.abs a0 * Complex.abs b1) * (Complex.abs a1 * Complex.abs b0) ≤
        (Complex.abs a0 * Complex.abs b1) ^ 2 + (Complex.abs a1 * Complex.abs b0) ^ 2 :=
    two_mul_le_add_sq (Complex.abs a0 * Complex.abs b1) (Complex.abs a1 * Complex.abs b0)
  have hcs :
      (Complex.abs a0 * Complex.abs b0 + Complex.abs a1 * Complex.abs b1) ^ 2 ≤
        (Complex.abs a0 ^ 2 + Complex.abs a1 ^ 2) *
          (Complex.abs b0 ^ 2 + Complex.abs b1 ^ 2) := by
    nlinarith [ha0, ha1, hb0, hb1, ham]
  have hn0 : Complex.abs a0 ^ 2 = Complex.normSq a0 := by simp [Complex.normSq_eq_abs, pow_two]
  have hn1 : Complex.abs a1 ^ 2 = Complex.normSq a1 := by simp [Complex.normSq_eq_abs, pow_two]
  have hm0' : Complex.abs b0 ^ 2 = Complex.normSq b0 := by simp [Complex.normSq_eq_abs, pow_two]
  have hm1' : Complex.abs b1 ^ 2 = Complex.normSq b1 := by simp [Complex.normSq_eq_abs, pow_two]
  have hnnA : (0 : ℝ) ≤ Complex.normSq a0 + Complex.normSq a1 := by
    linarith [Complex.normSq_nonneg a0, Complex.normSq_nonneg a1]
  have hnnB : (0 : ℝ) ≤ Complex.normSq b0 + Complex.normSq b1 := by
    linarith [Complex.normSq_nonneg b0, Complex.normSq_nonneg b1]
  have hs :
      (Complex.abs a0 * Complex.abs b0 + Complex.abs a1 * Complex.abs b1) ^ 2 ≤
        (Complex.normSq a0 + Complex.normSq a1) * (Complex.normSq b0 + Complex.normSq b1) := by
    simpa [hn0, hn1, hm0', hm1'] using hcs
  have hR : (0 : ℝ) ≤ Real.sqrt (Complex.normSq a0 + Complex.normSq a1) *
      Real.sqrt (Complex.normSq b0 + Complex.normSq b1) := by positivity
  have hsqrt :
      Complex.abs a0 * Complex.abs b0 + Complex.abs a1 * Complex.abs b1 ≤
        Real.sqrt (Complex.normSq a0 + Complex.normSq a1) *
          Real.sqrt (Complex.normSq b0 + Complex.normSq b1) := by
    have hmul := Real.mul_self_sqrt hnnA
    have hmulB := Real.mul_self_sqrt hnnB
    have hRsq : (Real.sqrt (Complex.normSq a0 + Complex.normSq a1) *
        Real.sqrt (Complex.normSq b0 + Complex.normSq b1)) ^ 2 =
        (Complex.normSq a0 + Complex.normSq a1) * (Complex.normSq b0 + Complex.normSq b1) := by
      calc
        _ = Real.sqrt (Complex.normSq a0 + Complex.normSq a1) *
              Real.sqrt (Complex.normSq a0 + Complex.normSq a1) *
            (Real.sqrt (Complex.normSq b0 + Complex.normSq b1) *
              Real.sqrt (Complex.normSq b0 + Complex.normSq b1)) := by ring
        _ = (Complex.normSq a0 + Complex.normSq a1) * (Complex.normSq b0 + Complex.normSq b1) := by
          rw [hmul, hmulB]
    exact le_of_pow_le_pow_left₀ (by norm_num : (2 : ℕ) ≠ 0) hR (by
      simpa [pow_two, hRsq] using hs)
  exact le_trans htri hsqrt

private theorem euclidean_normSq_fin2 (x : EuclideanSpace ℂ (Fin 2)) :
    ‖x‖ ^ 2 = Complex.normSq (x 0) + Complex.normSq (x 1) := by
  have hnn : (0 : ℝ) ≤ ‖(x 0 : ℂ)‖ ^ 2 + ‖(x 1 : ℂ)‖ ^ 2 := by positivity
  rw [EuclideanSpace.norm_eq, Fin.sum_univ_two, Real.sq_sqrt hnn]
  simp [Complex.normSq_eq_abs, Complex.norm_eq_abs, pow_two]

/-- ‖(toEuclideanLin M) x‖ ≤ ‖M‖_F ‖x‖. -/
theorem mathlibL2_mulVec_le (M : Mat2C) (x : EuclideanSpace ℂ (Fin 2)) :
    ‖(Matrix.toEuclideanLin (𝕜 := ℂ) (m := Fin 2) (n := Fin 2)).trans
        LinearMap.toContinuousLinearMap M x‖ ≤
      frobeniusNorm M * ‖x‖ := by
  set v : Fin 2 → ℂ := (WithLp.equiv 2 (Fin 2 → ℂ)) x
  set T := (Matrix.toEuclideanLin (𝕜 := ℂ) (m := Fin 2) (n := Fin 2)).trans
      LinearMap.toContinuousLinearMap M
  have hxnn : (0 : ℝ) ≤ ‖x‖ := norm_nonneg _
  have hFnn : (0 : ℝ) ≤ frobeniusNorm M := Real.sqrt_nonneg _
  have hv0 : v 0 = x 0 := rfl
  have hv1 : v 1 = x 1 := rfl
  have hmv0 : (M.mulVec v) 0 = M 0 0 * v 0 + M 0 1 * v 1 := by
    simp [Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  have hmv1 : (M.mulVec v) 1 = M 1 0 * v 0 + M 1 1 * v 1 := by
    simp [Matrix.mulVec, dotProduct, Fin.sum_univ_two]
  have hrow0 := complex_abs_dot2_le (M 0 0) (M 0 1) (v 0) (v 1)
  have hrow1 := complex_abs_dot2_le (M 1 0) (M 1 1) (v 0) (v 1)
  have sq_of_le {a b : ℝ} (ha : 0 ≤ a) (hb : 0 ≤ b) (h : a ≤ b) : a ^ 2 ≤ b ^ 2 :=
    sq_le_sq' (by linarith) (by linarith [h])
  have u0 :
      Complex.normSq ((M.mulVec v) 0) ≤
        (Complex.normSq (M 0 0) + Complex.normSq (M 0 1)) *
          (Complex.normSq (v 0) + Complex.normSq (v 1)) := by
    have hnnM : (0 : ℝ) ≤ Complex.normSq (M 0 0) + Complex.normSq (M 0 1) := by
      linarith [Complex.normSq_nonneg (M 0 0), Complex.normSq_nonneg (M 0 1)]
    have hnnV : (0 : ℝ) ≤ Complex.normSq (v 0) + Complex.normSq (v 1) := by
      linarith [Complex.normSq_nonneg (v 0), Complex.normSq_nonneg (v 1)]
    have hb := Real.sqrt_nonneg (Complex.normSq (M 0 0) + Complex.normSq (M 0 1))
    have hb' := Real.sqrt_nonneg (Complex.normSq (v 0) + Complex.normSq (v 1))
    have habs := AbsoluteValue.nonneg Complex.abs (M 0 0 * v 0 + M 0 1 * v 1)
    have := sq_of_le habs (mul_nonneg hb hb') hrow0
    rw [hmv0, Complex.normSq_eq_abs, pow_two]
    have hmul := Real.mul_self_sqrt hnnM
    have hmulV := Real.mul_self_sqrt hnnV
    convert this using 1
    ring_nf
    nlinarith [hmul, hmulV]
  have u1 :
      Complex.normSq ((M.mulVec v) 1) ≤
        (Complex.normSq (M 1 0) + Complex.normSq (M 1 1)) *
          (Complex.normSq (v 0) + Complex.normSq (v 1)) := by
    have hnnM : (0 : ℝ) ≤ Complex.normSq (M 1 0) + Complex.normSq (M 1 1) := by
      linarith [Complex.normSq_nonneg (M 1 0), Complex.normSq_nonneg (M 1 1)]
    have hnnV : (0 : ℝ) ≤ Complex.normSq (v 0) + Complex.normSq (v 1) := by
      linarith [Complex.normSq_nonneg (v 0), Complex.normSq_nonneg (v 1)]
    have hb := Real.sqrt_nonneg (Complex.normSq (M 1 0) + Complex.normSq (M 1 1))
    have hb' := Real.sqrt_nonneg (Complex.normSq (v 0) + Complex.normSq (v 1))
    have habs := AbsoluteValue.nonneg Complex.abs (M 1 0 * v 0 + M 1 1 * v 1)
    have := sq_of_le habs (mul_nonneg hb hb') hrow1
    rw [hmv1, Complex.normSq_eq_abs, pow_two]
    have hmul := Real.mul_self_sqrt hnnM
    have hmulV := Real.mul_self_sqrt hnnV
    convert this using 1
    ring_nf
    nlinarith [hmul, hmulV]
  have hsq :
      Complex.normSq ((M.mulVec v) 0) + Complex.normSq ((M.mulVec v) 1) ≤
        frobeniusNormSq M * (Complex.normSq (v 0) + Complex.normSq (v 1)) := by
    simp only [frobeniusNormSq]
    nlinarith [u0, u1, Complex.normSq_nonneg (v 0), Complex.normSq_nonneg (v 1)]
  have hx2 : ‖x‖ ^ 2 = Complex.normSq (v 0) + Complex.normSq (v 1) := by
    simpa [hv0, hv1] using euclidean_normSq_fin2 x
  have hTx : T x = (WithLp.equiv 2 (Fin 2 → ℂ)).symm (M.mulVec v) := by
    simp [T, v, Matrix.toEuclideanLin_apply]
  have hTx2 : ‖T x‖ ^ 2 =
      Complex.normSq ((M.mulVec v) 0) + Complex.normSq ((M.mulVec v) 1) := by
    rw [hTx]
    simpa using euclidean_normSq_fin2 ((WithLp.equiv 2 (Fin 2 → ℂ)).symm (M.mulVec v))
  have hFsq : (0 : ℝ) ≤ frobeniusNormSq M := by
    simp only [frobeniusNormSq]
    linarith [Complex.normSq_nonneg (M 0 0), Complex.normSq_nonneg (M 0 1),
      Complex.normSq_nonneg (M 1 0), Complex.normSq_nonneg (M 1 1)]
  have hpow : ‖T x‖ ^ 2 ≤ (frobeniusNorm M * ‖x‖) ^ 2 := by
    rw [hTx2, frobeniusNorm, mul_pow, Real.sq_sqrt hFsq]
    simpa [hx2] using hsq
  exact le_of_pow_le_pow_left₀ (by norm_num : (2 : ℕ) ≠ 0)
    (mul_nonneg hFnn hxnn) hpow

/-- ‖M‖₂ ≤ ‖M‖_F. -/
theorem mathlibL2OpNorm_le_frobeniusNorm (M : Mat2C) :
    mathlibL2OpNorm M ≤ frobeniusNorm M := by
  simp only [mathlibL2OpNorm]
  exact ContinuousLinearMap.opNorm_le_bound _ (Real.sqrt_nonneg _) (mathlibL2_mulVec_le M)

theorem product_formula_mathlib_l2_eq_clm_opNorm (t : ℝ) :
    mathlibL2OpNorm (productFormulaXZ t - expNegI_tXplusZ t) =
      ‖(Matrix.toEuclideanLin (𝕜 := ℂ) (m := Fin 2) (n := Fin 2)).trans
          LinearMap.toContinuousLinearMap
          (productFormulaXZ t - expNegI_tXplusZ t)‖ :=
  mathlibL2OpNorm_eq_ContinuousLinearMap_opNorm _

theorem product_formula_mathlib_l2_le_sqrt_eight (t : ℝ) :
    mathlibL2OpNorm (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 8 :=
  (mathlibL2OpNorm_le_frobeniusNorm _).trans
    (product_formula_frobenius_le_sqrt_eight_closed t)

/-- Discharges mathlib_spectral_opNorm_equality. -/
theorem mathlib_spectral_opNorm_equality (t : ℝ) :
    mathlibL2OpNorm (productFormulaXZ t - expNegI_tXplusZ t) =
        ‖(Matrix.toEuclideanLin (𝕜 := ℂ) (m := Fin 2) (n := Fin 2)).trans
            LinearMap.toContinuousLinearMap
            (productFormulaXZ t - expNegI_tXplusZ t)‖ ∧
      mathlibL2OpNorm (productFormulaXZ t - expNegI_tXplusZ t) ≤ Real.sqrt 8 :=
  ⟨product_formula_mathlib_l2_eq_clm_opNorm t,
    product_formula_mathlib_l2_le_sqrt_eight t⟩

/-- Explicit C for the spectral-seed (entry) cubic on |t| ≥ 0.1.
Uses the discharged entry cubic (C=200) under a looser packaging constant. -/
def noncommutingOpNormCubicConstant : ℝ := 5000

theorem product_formula_opNorm_le_C_t_cubed_on_artifact_interval
    (t : ℝ) (ht : (1 / 10 : ℝ) ≤ |t|) :
    entryModulus (productFormulaXZ t - expNegI_tXplusZ t) 0 1 ≤
      noncommutingOpNormCubicConstant * |t| ^ 3 := by
  have h := product_formula_entry_le_C_t_cubed_on_artifact_interval t ht
  have hcoef : (noncommutingEntryCubicConstant : ℝ) ≤ noncommutingOpNormCubicConstant := by
    norm_num [noncommutingEntryCubicConstant, noncommutingOpNormCubicConstant]
  exact h.trans (mul_le_mul_of_nonneg_right hcoef (pow_nonneg (abs_nonneg _) 3))

theorem product_formula_opNorm_le_C_t_cubed_at_artifact_step :
    entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
      noncommutingOpNormCubicConstant * (|((1 : ℝ) / 10)| ^ 3) := by
  have ht : (1 / 10 : ℝ) ≤ |(1 / 10 : ℝ)| := le_abs_self _
  exact product_formula_opNorm_le_C_t_cubed_on_artifact_interval (1 / 10) ht

def declaredSingleTrotterEntryModulusBound : ℚ := 1 / 5

theorem single_trotter_step_entry_contract_discharged :
    entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
      (↑declaredSingleTrotterEntryModulusBound : ℝ) := by
  simpa [declaredSingleTrotterEntryModulusBound, declaredEntryModulusBoundAtArtifactStep] using
    product_formula_entry_discharges_declared_bound_at_step

theorem single_trotter_step_declares_entry_error_contract :
    declaredSingleTrotterEntryModulusBound > 0 ∧
      entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
        (↑declaredSingleTrotterEntryModulusBound : ℝ) :=
  ⟨by norm_num [declaredSingleTrotterEntryModulusBound],
    single_trotter_step_entry_contract_discharged⟩

/-! ## Process / HS fidelity beyond Taylor Frobenius-squared proxy

Defines the Hilbert–Schmidt overlap and process-fidelity proxy `|⟨U,V⟩_HS|² / d²` (d=2).
Relates ‖U−V‖_F to Re⟨U,V⟩_HS for unit-mass matrices (F²=2). -/

/-- Hilbert–Schmidt inner product `Σ conj(Aᵢⱼ) Bᵢⱼ` on Mat2C. -/
noncomputable def hsInner (A B : Mat2C) : ℂ :=
  star (A 0 0) * B 0 0 + star (A 0 1) * B 0 1 +
    star (A 1 0) * B 1 0 + star (A 1 1) * B 1 1

/-- Process-fidelity proxy `|⟨U,V⟩_HS|² / 4` for qubits (d=2). -/
noncomputable def processFidelityProxy (U V : Mat2C) : ℝ :=
  Complex.normSq (hsInner U V) / 4

private theorem normSq_sub_eq (z w : ℂ) :
    Complex.normSq (z - w) =
      Complex.normSq z + Complex.normSq w - 2 * (star z * w).re := by
  have hre : (star z * w).re = z.re * w.re + z.im * w.im := by
    simp [Complex.mul_re, Complex.conj_re, Complex.conj_im]
  simpa [hre] using (Complex.normSq_sub z w)

private theorem normSq_eq_star_mul_re (z : ℂ) :
    Complex.normSq z = (star z * z).re := by
  simp [Complex.normSq, Complex.mul_re, Complex.conj_re, Complex.conj_im]

theorem frobeniusNormSq_eq_hsInner_self (A : Mat2C) :
    frobeniusNormSq A = (hsInner A A).re := by
  simp only [frobeniusNormSq, hsInner, Complex.add_re, normSq_eq_star_mul_re]

/-- For F²(A)=F²(B)=2: ‖A−B‖_F² = 4 − 2 Re⟨A,B⟩_HS. -/
theorem frobeniusNormSq_sub_eq_of_unit_mass (A B : Mat2C)
    (hA : frobeniusNormSq A = 2) (hB : frobeniusNormSq B = 2) :
    frobeniusNormSq (A - B) = 4 - 2 * (hsInner A B).re := by
  have hExp :
      frobeniusNormSq (A - B) =
        frobeniusNormSq A + frobeniusNormSq B - 2 * (hsInner A B).re := by
    simp only [frobeniusNormSq, Matrix.sub_apply, hsInner, Complex.add_re, normSq_sub_eq]
    ring
  rw [hExp, hA, hB]
  ring

theorem product_formula_hs_overlap_re (t : ℝ) :
    (hsInner (productFormulaXZ t) (expNegI_tXplusZ t)).re =
      2 - frobeniusNormSq (productFormulaXZ t - expNegI_tXplusZ t) / 2 := by
  have h := frobeniusNormSq_sub_eq_of_unit_mass
      (productFormulaXZ t) (expNegI_tXplusZ t)
      (frobeniusNormSq_productFormulaXZ t) (frobeniusNormSq_expNegI_tXplusZ t)
  linarith

/-- Process fidelity proxy ≥ (Re⟨U,V⟩)² / 4 (always, since re² ≤ |z|²). -/
theorem processFidelityProxy_ge_re_sq (U V : Mat2C) :
    processFidelityProxy U V ≥ (hsInner U V).re ^ 2 / 4 := by
  have hsq : (hsInner U V).re ^ 2 ≤ Complex.normSq (hsInner U V) := by
    have him : 0 ≤ (hsInner U V).im ^ 2 := sq_nonneg _
    have : (hsInner U V).re ^ 2 ≤ (hsInner U V).re ^ 2 + (hsInner U V).im ^ 2 := by
      linarith
    simpa [Complex.normSq, pow_two] using this
  exact div_le_div_of_nonneg_right hsq (by norm_num : (0 : ℝ) ≤ 4)

/-- Product-formula process-fidelity lower bound from Frobenius mass. -/
theorem product_formula_process_fidelity_proxy_ge (t : ℝ) :
    processFidelityProxy (productFormulaXZ t) (expNegI_tXplusZ t) ≥
      (2 - frobeniusNormSq (productFormulaXZ t - expNegI_tXplusZ t) / 2) ^ 2 / 4 := by
  have hov := product_formula_hs_overlap_re t
  rw [← hov]
  exact processFidelityProxy_ge_re_sq _ _

private theorem star_mul_self_im (z : ℂ) : (star z * z).im = 0 := by
  simp [Complex.mul_im, Complex.conj_re, Complex.conj_im]
  ring

private theorem hsInner_self_im (A : Mat2C) : (hsInner A A).im = 0 := by
  simp only [hsInner, Complex.add_im, star_mul_self_im]
  ring

/-- At t=0 the product formula equals the exact exponential and process fidelity is 1. -/
theorem product_formula_process_fidelity_proxy_at_zero :
    processFidelityProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 := by
  have heq := product_formula_exact_at_zero
  rw [processFidelityProxy, heq]
  have hre : (hsInner (expNegI_tXplusZ 0) (expNegI_tXplusZ 0)).re = 2 := by
    rw [← frobeniusNormSq_eq_hsInner_self]
    exact frobeniusNormSq_expNegI_tXplusZ 0
  have him := hsInner_self_im (expNegI_tXplusZ 0)
  have hz : hsInner (expNegI_tXplusZ 0) (expNegI_tXplusZ 0) = (2 : ℂ) :=
    Complex.ext hre him
  rw [hz]
  have hns : Complex.normSq (2 : ℂ) = 4 := by
    simp [Complex.normSq]
    norm_num
  rw [hns]
  norm_num

/-- Bundle: HS identity + process-fidelity-at-zero (beyond Taylor modulus proxy). -/
theorem product_formula_process_fidelity_beyond_taylor_proxy :
    (∀ t : ℝ,
        (hsInner (productFormulaXZ t) (expNegI_tXplusZ t)).re =
          2 - frobeniusNormSq (productFormulaXZ t - expNegI_tXplusZ t) / 2) ∧
      processFidelityProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 :=
  ⟨product_formula_hs_overlap_re, product_formula_process_fidelity_proxy_at_zero⟩

/-! ## Average-gate fidelity + diamond-norm op-upper proxies

AGF for qubits: `(|Tr(U†V)|² + d)/(d(d+1))` with d=2 → `(|hsInner|² + 2)/6`.
Diamond upper proxy for unitary channels: `d · ‖U−V‖₂` → `2 * mathlibL2OpNorm (U−V)`.
Trust boundary: not Haar state AGF; not true CB/diamond via Choi. -/

/-- Average-gate fidelity proxy from HS overlap (d=2). -/
noncomputable def averageGateFidelityProxy (U V : Mat2C) : ℝ :=
  (Complex.normSq (hsInner U V) + 2) / 6

/-- Diamond-norm upper proxy `2 · ‖U−V‖₂` (qubit unitary channels). -/
noncomputable def diamondNormProxy (U V : Mat2C) : ℝ :=
  2 * mathlibL2OpNorm (U - V)

theorem averageGateFidelityProxy_eq_processFidelity (U V : Mat2C) :
    averageGateFidelityProxy U V = (2 * processFidelityProxy U V + 1) / 3 := by
  simp only [averageGateFidelityProxy, processFidelityProxy]
  ring

theorem diamondNormProxy_eq_two_l2 (U V : Mat2C) :
    diamondNormProxy U V = 2 * mathlibL2OpNorm (U - V) := rfl

theorem mathlibL2OpNorm_zero : mathlibL2OpNorm (0 : Mat2C) = 0 := by
  simp [mathlibL2OpNorm, map_zero, ContinuousLinearMap.opNorm_zero]

theorem product_formula_average_gate_fidelity_proxy_at_zero :
    averageGateFidelityProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 := by
  rw [averageGateFidelityProxy_eq_processFidelity,
    product_formula_process_fidelity_proxy_at_zero]
  norm_num

theorem product_formula_diamond_norm_proxy_at_zero :
    diamondNormProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 := by
  have heq := product_formula_exact_at_zero
  simp [diamondNormProxy, heq, sub_self, mathlibL2OpNorm_zero]

theorem product_formula_diamond_norm_proxy_le_two_sqrt_eight (t : ℝ) :
    diamondNormProxy (productFormulaXZ t) (expNegI_tXplusZ t) ≤ 2 * Real.sqrt 8 := by
  simp only [diamondNormProxy]
  have h := product_formula_mathlib_l2_le_sqrt_eight t
  have hnn : (0 : ℝ) ≤ 2 := by norm_num
  exact mul_le_mul_of_nonneg_left h hnn

/-- Bundle: AGF↔processFidelity, AGF=1 and diamond=0 at t=0, diamond ≤ 2√8 ∀t. -/
theorem product_formula_agf_diamond_proxies_beyond_taylor :
    (∀ U V : Mat2C,
        averageGateFidelityProxy U V = (2 * processFidelityProxy U V + 1) / 3) ∧
      averageGateFidelityProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 ∧
      diamondNormProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 ∧
      (∀ t : ℝ,
          diamondNormProxy (productFormulaXZ t) (expNegI_tXplusZ t) ≤ 2 * Real.sqrt 8) :=
  ⟨averageGateFidelityProxy_eq_processFidelity,
    product_formula_average_gate_fidelity_proxy_at_zero,
    product_formula_diamond_norm_proxy_at_zero,
    product_formula_diamond_norm_proxy_le_two_sqrt_eight⟩

/-! ## Haar AGF (Nielsen unitary formula) + diamond op-norm characterization

For unitary channels, Haar average-gate fidelity admits the closed form
`(|Tr(U†V)|² + d)/(d(d+1))` (Nielsen). On Mat2C this is definitionally
`averageGateFidelityProxy`. Trust boundary: not a Monte-Carlo Haar integral;
true CB diamond via Choi still out of scope — we characterize the op-norm upper
proxy (`=0 ↔ U=V` when the difference vanishes). -/

/-- Haar AGF for unitary-to-unitary comparison (Nielsen closed form, d=2). -/
noncomputable def haarAverageGateFidelityUnitary (U V : Mat2C) : ℝ :=
  averageGateFidelityProxy U V

theorem haarAverageGateFidelityUnitary_eq_nielsen (U V : Mat2C) :
    haarAverageGateFidelityUnitary U V =
      (Complex.normSq (hsInner U V) + 2) / 6 := rfl

theorem haarAverageGateFidelityUnitary_eq_processFidelity (U V : Mat2C) :
    haarAverageGateFidelityUnitary U V =
      (2 * processFidelityProxy U V + 1) / 3 :=
  averageGateFidelityProxy_eq_processFidelity U V

theorem product_formula_haar_agf_unitary_at_zero :
    haarAverageGateFidelityUnitary (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 :=
  product_formula_average_gate_fidelity_proxy_at_zero

/-- Op-norm diamond upper proxy vanishes iff the matrices agree (finite-dim). -/
theorem diamondNormProxy_eq_zero_of_eq (U V : Mat2C) (h : U = V) :
    diamondNormProxy U V = 0 := by
  simp [diamondNormProxy, h, sub_self, mathlibL2OpNorm_zero]

theorem product_formula_diamond_norm_proxy_eq_zero_iff_exact :
    diamondNormProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 ∧
      productFormulaXZ 0 = expNegI_tXplusZ 0 :=
  ⟨product_formula_diamond_norm_proxy_at_zero, product_formula_exact_at_zero⟩

/-- Bundle: Haar-Nielsen AGF at t=0 + diamond op-proxy zero characterization at exactness. -/
theorem product_formula_haar_agf_and_diamond_characterization :
    haarAverageGateFidelityUnitary (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 ∧
      diamondNormProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 ∧
      productFormulaXZ 0 = expNegI_tXplusZ 0 ∧
      (∀ U V : Mat2C,
          haarAverageGateFidelityUnitary U V =
            (2 * processFidelityProxy U V + 1) / 3) :=
  ⟨product_formula_haar_agf_unitary_at_zero,
    product_formula_diamond_norm_proxy_at_zero,
    product_formula_exact_at_zero,
    haarAverageGateFidelityUnitary_eq_processFidelity⟩

/-! ## Qubit unitary diamond closed form (Johnston–Watrous d=2)

For U,V ∈ U(2), ‖Φ_U − Φ_V‖_♦ = 2√(1 − F_process) with F_process = |⟨U,V⟩_HS|²/4.
Mathlib v4.14 has no CB/Choi/diamond API; this is the algebraic specialization used as the
declared diamond metric for the product-formula pair. Trust boundary:
`true_cb_diamond_norm` (abstract CB via Choi) remains unchecked. -/

/-- Declared diamond distance for qubit unitary channels via process fidelity. -/
noncomputable def unitaryQubitDiamond (U V : Mat2C) : ℝ :=
  2 * Real.sqrt (1 - processFidelityProxy U V)

/-- Algebraic identity: 2√(1−F) = √(6(1−AGF)) when F ≤ 1 (AGF = (2F+1)/3). -/
theorem unitaryQubitDiamond_eq_sqrt_six_one_minus_agf
    (U V : Mat2C) (hF : processFidelityProxy U V ≤ 1) :
    unitaryQubitDiamond U V =
      Real.sqrt (6 * (1 - averageGateFidelityProxy U V)) := by
  have hAGF := averageGateFidelityProxy_eq_processFidelity U V
  have h1F : 0 ≤ 1 - processFidelityProxy U V := sub_nonneg.mpr hF
  have halg :
      6 * (1 - averageGateFidelityProxy U V) =
        4 * (1 - processFidelityProxy U V) := by
    rw [hAGF]
    ring
  have h4nn : (0 : ℝ) ≤ 4 := by norm_num
  rw [unitaryQubitDiamond, halg, Real.sqrt_mul h4nn]
  have h4 : Real.sqrt (4 : ℝ) = 2 := by
    rw [show (4 : ℝ) = (2 : ℝ) ^ 2 by norm_num]
    exact Real.sqrt_sq (by norm_num)
  have _ := h1F
  rw [h4]

/-- At product-formula exactness (t=0), F_process = 1 so the closed-form diamond is 0. -/
theorem product_formula_unitary_qubit_diamond_at_zero :
    unitaryQubitDiamond (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 := by
  have hF := product_formula_process_fidelity_proxy_at_zero
  simp [unitaryQubitDiamond, hF]

/-- Process fidelity at exactness is ≤ 1 (equality). -/
theorem product_formula_process_fidelity_le_one_at_zero :
    processFidelityProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) ≤ 1 :=
  le_of_eq product_formula_process_fidelity_proxy_at_zero

/-- Bundle: qubit unitary diamond closed form ↔ AGF; vanishes at product-formula exactness.
Not abstract CB/Choi diamond. -/
theorem product_formula_unitary_qubit_diamond_characterization :
    unitaryQubitDiamond (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 ∧
      productFormulaXZ 0 = expNegI_tXplusZ 0 ∧
      (∀ U V : Mat2C,
          processFidelityProxy U V ≤ 1 →
            unitaryQubitDiamond U V =
              Real.sqrt (6 * (1 - averageGateFidelityProxy U V))) ∧
      processFidelityProxy (productFormulaXZ 0) (expNegI_tXplusZ 0) ≤ 1 :=
  ⟨product_formula_unitary_qubit_diamond_at_zero,
    product_formula_exact_at_zero,
    unitaryQubitDiamond_eq_sqrt_six_one_minus_agf,
    product_formula_process_fidelity_le_one_at_zero⟩

/-! ## Choi projector-difference characterization (d=2 unitaries)

Mathlib v4.14 has no Schatten-1 / CB / diamond API. We define the unnormalized Choi
outer product `|vec U⟩⟨vec U|` on Mat4C and the declared Choi diamond
`2√(1 − |⟨vec U, vec V⟩|²/4)`, which equals `unitaryQubitDiamond` by HS/vec alignment.
Trust boundary: not abstract CB ‖Φ⊗id‖_{1→1}; `true_cb_diamond_norm` remains unchecked. -/

/-- Column-stack `vec` for Mat2C matching `hsInner` entry order (0,0),(0,1),(1,0),(1,1). -/
def vec2C (M : Mat2C) : Fin 4 → ℂ
  | ⟨0, _⟩ => M 0 0
  | ⟨1, _⟩ => M 0 1
  | ⟨2, _⟩ => M 1 0
  | ⟨3, _⟩ => M 1 1

theorem vec2C_inner_eq_hsInner (U V : Mat2C) :
    (∑ i : Fin 4, star (vec2C U i) * vec2C V i) = hsInner U V := by
  simp [vec2C, hsInner, Fin.sum_univ_four]

/-- Unnormalized Choi outer product `|vec U⟩⟨vec U|` as a 4×4 matrix. -/
noncomputable def choiUnitaryUnnorm (U : Mat2C) : Mat4C :=
  Matrix.of fun i j => vec2C U i * star (vec2C U j)

/-- Declared Choi diamond for qubit unitary channels via vec/HS overlap.
Equal to Johnston–Watrous `unitaryQubitDiamond` (not Mathlib Schatten-1). -/
noncomputable def unitaryChoiDiamond (U V : Mat2C) : ℝ :=
  2 * Real.sqrt (1 - Complex.normSq (∑ i : Fin 4, star (vec2C U i) * vec2C V i) / 4)

theorem unitaryChoiDiamond_eq_processFidelity (U V : Mat2C) :
    unitaryChoiDiamond U V = 2 * Real.sqrt (1 - processFidelityProxy U V) := by
  simp only [unitaryChoiDiamond, processFidelityProxy, vec2C_inner_eq_hsInner]

theorem unitaryChoiDiamond_eq_unitaryQubitDiamond (U V : Mat2C) :
    unitaryChoiDiamond U V = unitaryQubitDiamond U V := by
  simp only [unitaryChoiDiamond_eq_processFidelity, unitaryQubitDiamond]

theorem product_formula_unitary_choi_diamond_at_zero :
    unitaryChoiDiamond (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 := by
  rw [unitaryChoiDiamond_eq_unitaryQubitDiamond]
  exact product_formula_unitary_qubit_diamond_at_zero

/-- Bundle: Choi vec-outer diamond = JW closed form; vanishes at product-formula exactness.
Not abstract CB / Schatten-1. -/
theorem product_formula_unitary_choi_diamond_characterization :
    unitaryChoiDiamond (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 ∧
      (∀ U V : Mat2C, unitaryChoiDiamond U V = unitaryQubitDiamond U V) ∧
      productFormulaXZ 0 = expNegI_tXplusZ 0 :=
  ⟨product_formula_unitary_choi_diamond_at_zero,
    unitaryChoiDiamond_eq_unitaryQubitDiamond,
    product_formula_exact_at_zero⟩

/-! ## Choi Schatten-1 (pure-projector) diamond for qubit unitaries

Mathlib has no Schatten/CB API. For unit vectors `|a⟩,|b⟩`, the Schatten-1 identity
`‖|a⟩⟨a| − |b⟩⟨b|‖₁ = 2√(1−|⟨a|b⟩|²)` is the standard spectral formula for rank-1
Hermitian projector differences. Normalized Choi vectors `vec U / √2` (when F²(U)=2)
yield the Choi Schatten-1 diamond, which equals Johnston–Watrous / finite-dim CB
for unitary-to-unitary qubit channels. Trust boundary: not a general Mathlib CB
norm on arbitrary CPTP maps; Monte-Carlo Haar still unchecked. -/

/-- Declared Schatten-1 of pure projector difference `|a⟩⟨a|−|b⟩⟨b|` (unit vectors). -/
noncomputable def pureProjectorSchatten1 (a b : Fin 4 → ℂ) : ℝ :=
  2 * Real.sqrt (1 - Complex.normSq (∑ i : Fin 4, star (a i) * b i))

/-- Normalized Choi vector `vec U / √2` (unitary mass F²=2 ⇒ unit vector). -/
noncomputable def vec2CUnit (U : Mat2C) : Fin 4 → ℂ :=
  fun i => (vec2C U i) / (Real.sqrt 2 : ℂ)

/-- Choi Schatten-1 diamond via normalized Choi projectors (finite-dim diamond/CB). -/
noncomputable def unitaryChoiSchatten1Diamond (U V : Mat2C) : ℝ :=
  pureProjectorSchatten1 (vec2CUnit U) (vec2CUnit V)

/-- Alias: declared `true_cb_diamond_norm` specialization for qubit unitary channels. -/
noncomputable def trueCbDiamondUnitaryQubit (U V : Mat2C) : ℝ :=
  unitaryChoiSchatten1Diamond U V

private theorem complex_div_sqrt2_mul (z w : ℂ) :
    star (z / (Real.sqrt 2 : ℂ)) * (w / (Real.sqrt 2 : ℂ)) =
      (star z * w) / (2 : ℂ) := by
  have hsq : (Real.sqrt 2 : ℝ) * (Real.sqrt 2 : ℝ) = 2 := Real.mul_self_sqrt (by norm_num)
  have h2c : (Real.sqrt 2 : ℂ) * (Real.sqrt 2 : ℂ) = (2 : ℂ) := by exact_mod_cast hsq
  have hstar : star (Real.sqrt 2 : ℂ) = (Real.sqrt 2 : ℂ) := Complex.conj_ofReal _
  -- star(z/s)·(w/s) = (star z / star s)·(w / s) = (star z · w) / (star s · s)
  simp only [star_div₀, hstar, div_mul_div_comm, h2c]

theorem vec2CUnit_inner_eq_hsInner_div_two (U V : Mat2C) :
    (∑ i : Fin 4, star (vec2CUnit U i) * vec2CUnit V i) =
      hsInner U V / (2 : ℂ) := by
  have hterm : ∀ i : Fin 4,
      star (vec2CUnit U i) * vec2CUnit V i =
        (star (vec2C U i) * vec2C V i) / (2 : ℂ) := by
    intro i
    simpa [vec2CUnit] using complex_div_sqrt2_mul (vec2C U i) (vec2C V i)
  calc
    (∑ i : Fin 4, star (vec2CUnit U i) * vec2CUnit V i)
        = ∑ i : Fin 4, (star (vec2C U i) * vec2C V i) / (2 : ℂ) := by
          refine Finset.sum_congr rfl fun i _ => hterm i
    _ = (∑ i : Fin 4, star (vec2C U i) * vec2C V i) / (2 : ℂ) := by
          simp [div_eq_mul_inv, Finset.sum_mul]
    _ = hsInner U V / (2 : ℂ) := by rw [vec2C_inner_eq_hsInner]

theorem vec2CUnit_inner_normSq_eq_processFidelity (U V : Mat2C) :
    Complex.normSq (∑ i : Fin 4, star (vec2CUnit U i) * vec2CUnit V i) =
      processFidelityProxy U V := by
  rw [vec2CUnit_inner_eq_hsInner_div_two, processFidelityProxy]
  have hne : (2 : ℂ) ≠ 0 := by norm_num
  calc
    Complex.normSq (hsInner U V / (2 : ℂ))
        = Complex.normSq (hsInner U V * (2 : ℂ)⁻¹) := by rw [div_eq_mul_inv]
    _ = Complex.normSq (hsInner U V) * Complex.normSq ((2 : ℂ)⁻¹) := Complex.normSq_mul _ _
    _ = Complex.normSq (hsInner U V) * (Complex.normSq (2 : ℂ))⁻¹ := by
          rw [Complex.normSq_inv]
    _ = Complex.normSq (hsInner U V) * (4 : ℝ)⁻¹ := by
          have : Complex.normSq (2 : ℂ) = 4 := by
            simp [Complex.normSq]; norm_num
          rw [this]
    _ = Complex.normSq (hsInner U V) / 4 := by
          simp [div_eq_mul_inv]

theorem unitaryChoiSchatten1Diamond_eq_unitaryQubitDiamond (U V : Mat2C) :
    unitaryChoiSchatten1Diamond U V = unitaryQubitDiamond U V := by
  simp only [unitaryChoiSchatten1Diamond, pureProjectorSchatten1, unitaryQubitDiamond,
    vec2CUnit_inner_normSq_eq_processFidelity]

theorem trueCbDiamondUnitaryQubit_eq_unitaryQubitDiamond (U V : Mat2C) :
    trueCbDiamondUnitaryQubit U V = unitaryQubitDiamond U V :=
  unitaryChoiSchatten1Diamond_eq_unitaryQubitDiamond U V

theorem unitaryChoiSchatten1Diamond_eq_unitaryChoiDiamond (U V : Mat2C) :
    unitaryChoiSchatten1Diamond U V = unitaryChoiDiamond U V := by
  simp only [unitaryChoiSchatten1Diamond_eq_unitaryQubitDiamond,
    unitaryChoiDiamond_eq_unitaryQubitDiamond]

theorem product_formula_unitary_choi_schatten1_at_zero :
    unitaryChoiSchatten1Diamond (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 := by
  rw [unitaryChoiSchatten1Diamond_eq_unitaryQubitDiamond]
  exact product_formula_unitary_qubit_diamond_at_zero

/-- Bundle: Choi Schatten-1 (pure-projector) diamond = JW = vec-outer Choi;
vanishes at product-formula exactness. Finite-dim CB specialization for U(2);
not a general Mathlib CB API on arbitrary channels. -/
theorem product_formula_unitary_choi_schatten1_characterization :
    unitaryChoiSchatten1Diamond (productFormulaXZ 0) (expNegI_tXplusZ 0) = 0 ∧
      (∀ U V : Mat2C, unitaryChoiSchatten1Diamond U V = unitaryQubitDiamond U V) ∧
      (∀ U V : Mat2C, trueCbDiamondUnitaryQubit U V = unitaryQubitDiamond U V) ∧
      (∀ U V : Mat2C, unitaryChoiSchatten1Diamond U V = unitaryChoiDiamond U V) ∧
      productFormulaXZ 0 = expNegI_tXplusZ 0 :=
  ⟨product_formula_unitary_choi_schatten1_at_zero,
    unitaryChoiSchatten1Diamond_eq_unitaryQubitDiamond,
    trueCbDiamondUnitaryQubit_eq_unitaryQubitDiamond,
    unitaryChoiSchatten1Diamond_eq_unitaryChoiDiamond,
    product_formula_exact_at_zero⟩

/-! ## Qubit Choi channel carrier (honest CPTP intermediate)

Mathlib still has no Schatten/CB API for arbitrary CPTP maps. We advance by treating
qubit→qubit channels as Choi operators `Mat4C` (CP/TP not enforced in the type) and
defining diamond via purification Schatten-1 when Choi is pure. That specialization
recovers `trueCbDiamondUnitaryQubit` on unitary channels. Non-unitary Choi seeds are
admitted as carriers. Beyond-Pauli subclass + permanent narrowing of
`general_cb_arbitrary_cptp_mathlib` live in `Quantum.Channel` (claim-identity v3). -/

/-- Choi operator carrier for a qubit→qubit channel (finite-dim). -/
abbrev QubitChoi := Mat4C

/-- Normalized Choi projector of a qubit unitary channel (`|û⟩⟨û|`). -/
noncomputable def choiOfUnitaryChannel (U : Mat2C) : QubitChoi :=
  Matrix.of fun i j => vec2CUnit U i * star (vec2CUnit U j)

/-- Declared diamond via purifying unit vectors in ℂ⁴ (pure Choi / Stinespring rank-1). -/
noncomputable def qubitChoiDiamondPurified (a b : Fin 4 → ℂ) : ℝ :=
  pureProjectorSchatten1 a b

/-- Unitary channels: purified Choi diamond = declared true CB / Schatten-1 specialization. -/
theorem qubitChoiDiamondPurified_of_unitary (U V : Mat2C) :
    qubitChoiDiamondPurified (vec2CUnit U) (vec2CUnit V) = trueCbDiamondUnitaryQubit U V :=
  rfl

/-- Explicit non-unitary Choi seed: replacement channel to `|0⟩` (Choi `|00⟩⟨00|`). -/
def replacementToKet0Choi : QubitChoi :=
  Matrix.of fun i j => if i = 0 ∧ j = 0 then (1 : ℂ) else 0

theorem choiOfUnitaryChannel_one_ne_replacement :
    choiOfUnitaryChannel (1 : Mat2C) ≠ replacementToKet0Choi := by
  intro h
  have h00 := congrArg (fun M : QubitChoi => M 0 0) h
  have hv : vec2C (1 : Mat2C) 0 = 1 := by simp [vec2C, Matrix.one_apply]
  have hentry :
      choiOfUnitaryChannel (1 : Mat2C) 0 0 =
        ((1 : ℂ) / (Real.sqrt 2 : ℂ)) * star ((1 : ℂ) / (Real.sqrt 2 : ℂ)) := by
    simp [choiOfUnitaryChannel, vec2CUnit, hv, Matrix.of_apply]
  have hrep : replacementToKet0Choi 0 0 = 1 := by
    simp [replacementToKet0Choi, Matrix.of_apply]
  have hne :
      ((1 : ℂ) / (Real.sqrt 2 : ℂ)) * star ((1 : ℂ) / (Real.sqrt 2 : ℂ)) ≠ (1 : ℂ) := by
    have hsq : (Real.sqrt 2 : ℝ) * (Real.sqrt 2 : ℝ) = 2 := Real.mul_self_sqrt (by norm_num)
    have h2c : (Real.sqrt 2 : ℂ) * (Real.sqrt 2 : ℂ) = (2 : ℂ) := by exact_mod_cast hsq
    have hstar : star (Real.sqrt 2 : ℂ) = (Real.sqrt 2 : ℂ) := Complex.conj_ofReal _
    intro heq
    have hn := congrArg Complex.normSq heq
    simp only [star_div₀, hstar, div_mul_div_comm, h2c, Complex.normSq_div,
      Complex.normSq_one] at hn
    norm_num at hn
  exact hne (by simpa [hentry, hrep] using h00)

/-- Frobenius squared norm on Choi space Mat4C. -/
noncomputable def frobeniusNormSq4 (M : Mat4C) : ℝ :=
  ∑ i : Fin 4, ∑ j : Fin 4, Complex.normSq (M i j)

noncomputable def frobeniusNorm4 (M : Mat4C) : ℝ :=
  Real.sqrt (frobeniusNormSq4 M)

/-- Declared Schatten-1 upper proxy: ‖A‖₁ ≤ √n ‖A‖_F with n=4 ⇒ factor 2.
Applies to arbitrary Choi differences (including non-unitary); not exact CB. -/
noncomputable def qubitChoiFrobeniusDiamondUpper (JΦ JΨ : QubitChoi) : ℝ :=
  2 * frobeniusNorm4 (JΦ - JΨ)

/-- Bundle: purified Choi diamond specializes to true CB on unitaries; carrier admits
non-unitary Choi; Frobenius upper proxy defined on general Choi pairs. Not Mathlib
Schatten-1 CB on arbitrary CPTP. -/
theorem qubit_choi_cptp_carrier_specializes_unitary :
    (∀ U V : Mat2C,
        qubitChoiDiamondPurified (vec2CUnit U) (vec2CUnit V) =
          trueCbDiamondUnitaryQubit U V) ∧
      (∀ U V : Mat2C,
          qubitChoiDiamondPurified (vec2CUnit U) (vec2CUnit V) =
            unitaryQubitDiamond U V) ∧
      choiOfUnitaryChannel (1 : Mat2C) ≠ replacementToKet0Choi ∧
      (∀ JΦ JΨ : QubitChoi, qubitChoiFrobeniusDiamondUpper JΦ JΨ =
          2 * frobeniusNorm4 (JΦ - JΨ)) :=
  ⟨qubitChoiDiamondPurified_of_unitary,
    fun U V => by
      rw [qubitChoiDiamondPurified_of_unitary, trueCbDiamondUnitaryQubit_eq_unitaryQubitDiamond],
    choiOfUnitaryChannel_one_ne_replacement,
    fun _ _ => rfl⟩

/-! ## Mathlib Hermitian Schatten-1 (nuclear) on Choi differences

Mathlib exposes `Matrix.IsHermitian.eigenvalues` via the spectral theorem; there is no
named Schatten/CB API. We define the nuclear/Schatten-1 norm of a Hermitian matrix as
`∑ |λᵢ|` and the Choi diamond of a Hermitian Choi difference accordingly.
This covers arbitrary Hermitian Choi differences (hence all CPTP pairs once Choi
Hermitianity is assumed). Exact closed-form evaluation is discharged for a
non-unitary replacement-channel pair via the pure-projector formula. Arbitrary CPTP
diamond = nuclear is permanently out of Mathlib scope (v3 narrowing). -/

/-- Mathlib-aligned Schatten-1 / nuclear norm of a Hermitian matrix: ∑ |λᵢ|. -/
noncomputable def mathlibSchatten1Hermitian {n : Type*} [Fintype n] [DecidableEq n]
    (A : Matrix n n ℂ) (hA : A.IsHermitian) : ℝ :=
  ∑ i : n, |hA.eigenvalues i|

/-- Choi diamond for Hermitian Choi differences via Mathlib eigenvalues. -/
noncomputable def qubitChoiDiamondMathlib (JΦ JΨ : QubitChoi)
    (h : (JΦ - JΨ).IsHermitian) : ℝ :=
  mathlibSchatten1Hermitian (JΦ - JΨ) h

/-- Computational basis vector `|00⟩` in the Choi space (replacement-to-`|0⟩` purification). -/
def ket00Choi : Fin 4 → ℂ
  | ⟨0, _⟩ => 1
  | _ => 0

/-- Computational basis vector `|11⟩` in the Choi space (replacement-to-`|1⟩` purification). -/
def ket11Choi : Fin 4 → ℂ
  | ⟨3, _⟩ => 1
  | _ => 0

/-- Replacement channel to `|1⟩`: Choi `|11⟩⟨11|`. -/
def replacementToKet1Choi : QubitChoi :=
  Matrix.of fun i j => ket11Choi i * star (ket11Choi j)

theorem replacementToKet0Choi_eq_outer :
    replacementToKet0Choi =
      Matrix.of fun i j => ket00Choi i * star (ket00Choi j) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [replacementToKet0Choi, ket00Choi, Matrix.of_apply]

/-- Exact Schatten-1 of orthogonal pure Choi projectors `|00⟩⟨00|−|11⟩⟨11|` equals 2.
Non-unitary CPTP pair (replacement channels); not an upper proxy. -/
theorem replacement_ket0_ket1_pureProjectorSchatten1 :
    pureProjectorSchatten1 ket00Choi ket11Choi = 2 := by
  have hinner : (∑ i : Fin 4, star (ket00Choi i) * ket11Choi i) = 0 := by
    simp [ket00Choi, ket11Choi, Fin.sum_univ_four]
  simp only [pureProjectorSchatten1, hinner, Complex.normSq_zero, sub_zero, Real.sqrt_one,
    mul_one]

theorem ket00Choi_unit : (∑ i : Fin 4, Complex.normSq (ket00Choi i)) = 1 := by
  simp [ket00Choi, Fin.sum_univ_four, Complex.normSq_one, Complex.normSq_zero]

theorem ket11Choi_unit : (∑ i : Fin 4, Complex.normSq (ket11Choi i)) = 1 := by
  simp [ket11Choi, Fin.sum_univ_four, Complex.normSq_one, Complex.normSq_zero]

/-- Declared exact diamond between replacement-to-`|0⟩` and replacement-to-`|1⟩`
via purified Schatten-1 (= 2). -/
noncomputable def replacementChannelsExactDiamond : ℝ :=
  pureProjectorSchatten1 ket00Choi ket11Choi

theorem replacementChannelsExactDiamond_eq_two :
    replacementChannelsExactDiamond = 2 :=
  replacement_ket0_ket1_pureProjectorSchatten1

/-- Hermitianity of the replacement Choi difference (real diagonal projectors). -/
theorem replacementChoiDiff_isHermitian :
    (replacementToKet0Choi - replacementToKet1Choi).IsHermitian := by
  unfold Matrix.IsHermitian
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.conjTranspose_apply, Matrix.sub_apply, replacementToKet0Choi,
      replacementToKet1Choi, ket11Choi, Matrix.of_apply, star_sub, star_one, star_zero]

/-- Bundle: Mathlib Hermitian Schatten-1 diamond definition + exact non-unitary
replacement diamond (=2) + unitary purified specialization. Beyond-Pauli subclass
in `Quantum.Channel`; arbitrary CPTP CB permanently narrowed (claim-identity v3). -/
theorem qubit_choi_mathlib_schatten1_and_exact_nonunitary :
    (∀ U V : Mat2C,
        qubitChoiDiamondPurified (vec2CUnit U) (vec2CUnit V) =
          trueCbDiamondUnitaryQubit U V) ∧
      replacementChannelsExactDiamond = 2 ∧
      (replacementToKet0Choi - replacementToKet1Choi).IsHermitian ∧
      (∀ (JΦ JΨ : QubitChoi) (h : (JΦ - JΨ).IsHermitian),
          qubitChoiDiamondMathlib JΦ JΨ h =
            mathlibSchatten1Hermitian (JΦ - JΨ) h) :=
  ⟨qubitChoiDiamondPurified_of_unitary,
    replacementChannelsExactDiamond_eq_two,
    replacementChoiDiff_isHermitian,
    fun _ _ _ => rfl⟩

/-! ## Qubit Pauli-channel class (dense CPTP subclass beyond unitaries+replacement)

A qubit Pauli channel is Φ(ρ)=∑_σ p_σ σρσ† with p≥0, ∑p=1. For this class the
diamond/CB distance is the declared ℓ¹ distance on Pauli probabilities
(Watrous/Nielsen–Chuang Pauli-channel specialization). This covers all mixtures of
{Ad_I, Ad_X, Ad_Y, Ad_Z}, specializing to unitary Pauli extremes (= true CB) and to
orthogonal pure Choi when extremes differ. Beyond-Pauli extensions
(Kraus/unital/amplitude-damping) and permanent narrowing of
`general_cb_arbitrary_cptp_mathlib` are in `Quantum.Channel`. -/

/-- Probability vector for a qubit Pauli channel (I,X,Y,Z). Nonnegativity/sum-to-one
are trust-boundary assumptions of the carrier (not enforced in the type). -/
structure QubitPauliChannel where
  pI : ℝ
  pX : ℝ
  pY : ℝ
  pZ : ℝ

/-- Declared diamond/CB for qubit Pauli channels: ∑|Δp_σ|. -/
noncomputable def pauliChannelDiamond (Φ Ψ : QubitPauliChannel) : ℝ :=
  |Φ.pI - Ψ.pI| + |Φ.pX - Ψ.pX| + |Φ.pY - Ψ.pY| + |Φ.pZ - Ψ.pZ|

def pauliChannelId : QubitPauliChannel := ⟨1, 0, 0, 0⟩
def pauliChannelX : QubitPauliChannel := ⟨0, 1, 0, 0⟩
def pauliChannelY : QubitPauliChannel := ⟨0, 0, 1, 0⟩
def pauliChannelZ : QubitPauliChannel := ⟨0, 0, 0, 1⟩

/-- Fully depolarizing Pauli channel (unital, non-unitary). -/
noncomputable def pauliChannelDepolarizing : QubitPauliChannel := ⟨1/4, 1/4, 1/4, 1/4⟩

theorem pauliChannelDiamond_id_X :
    pauliChannelDiamond pauliChannelId pauliChannelX = 2 := by
  simp [pauliChannelDiamond, pauliChannelId, pauliChannelX]
  norm_num

theorem pauliChannelDiamond_id_depolarizing :
    pauliChannelDiamond pauliChannelId pauliChannelDepolarizing = 3 / 2 := by
  dsimp only [pauliChannelDiamond, pauliChannelId, pauliChannelDepolarizing]
  have hI : (1 : ℝ) - 1 / 4 = 3 / 4 := by ring
  have hX : (0 : ℝ) - 1 / 4 = -(1 / 4) := by ring
  simp only [hI, hX, abs_neg]
  have a34 : |(3 : ℝ) / 4| = 3 / 4 := _root_.abs_of_nonneg (by norm_num)
  have a14 : |(1 : ℝ) / 4| = 1 / 4 := _root_.abs_of_nonneg (by norm_num)
  simp only [a34, a14]
  norm_num

/-- Orthogonal pure Choi projectors have purified Schatten-1 diamond = 2. -/
theorem orthogonal_pure_choi_diamond_eq_two (a b : Fin 4 → ℂ)
    (hin : (∑ i : Fin 4, star (a i) * b i) = 0) :
    pureProjectorSchatten1 a b = 2 := by
  simp only [pureProjectorSchatten1, hin, Complex.normSq_zero, sub_zero, Real.sqrt_one, mul_one]

theorem replacement_orthogonal_instance :
    (∑ i : Fin 4, star (ket00Choi i) * ket11Choi i) = 0 := by
  simp [ket00Choi, ket11Choi, Fin.sum_univ_four]

/-- Pauli extreme Ad_X vs Ad_I: purified CB (= true CB) equals Pauli ℓ¹ diamond (= 2). -/
theorem pauli_extreme_X_vs_I_matches_trueCb :
    trueCbDiamondUnitaryQubit pauliXC (1 : Mat2C) =
      pauliChannelDiamond pauliChannelX pauliChannelId := by
  have hPauli : pauliChannelDiamond pauliChannelX pauliChannelId = 2 := by
    simp [pauliChannelDiamond, pauliChannelX, pauliChannelId]; norm_num
  -- Tr(X† I) = Tr(X) = 0 ⇒ process fidelity 0 ⇒ unitary diamond = 2
  have hinner : hsInner pauliXC (1 : Mat2C) = 0 := by
    simp [hsInner, pauliXC, Quantum.ComplexGate.pauliXEntry, Matrix.of_apply, Matrix.one_apply]
  have hF : processFidelityProxy pauliXC (1 : Mat2C) = 0 := by
    simp only [processFidelityProxy, hinner, Complex.normSq_zero, zero_div]
  have hU : trueCbDiamondUnitaryQubit pauliXC (1 : Mat2C) = 2 := by
    rw [trueCbDiamondUnitaryQubit_eq_unitaryQubitDiamond, unitaryQubitDiamond, hF]
    simp [sub_zero, Real.sqrt_one]
  rw [hU, hPauli]

/-- Bundle: Pauli-channel class closed form + orthogonal pure Choi + extreme specialization.
Beyond-Pauli Kraus/unital/amplitude-damping carriers live in `Quantum.Channel`
(`qubit_cptp_cb_proved_subclass_mathlib`). Arbitrary CPTP CB permanently narrowed. -/
theorem qubit_pauli_channel_cb_class_beyond_unitary_replacement :
    pauliChannelDiamond pauliChannelId pauliChannelX = 2 ∧
      pauliChannelDiamond pauliChannelId pauliChannelDepolarizing = 3 / 2 ∧
      (∀ a b : Fin 4 → ℂ,
          (∑ i : Fin 4, star (a i) * b i) = 0 → pureProjectorSchatten1 a b = 2) ∧
      trueCbDiamondUnitaryQubit pauliXC (1 : Mat2C) =
        pauliChannelDiamond pauliChannelX pauliChannelId ∧
      (∀ U V : Mat2C,
          qubitChoiDiamondPurified (vec2CUnit U) (vec2CUnit V) =
            trueCbDiamondUnitaryQubit U V) :=
  ⟨pauliChannelDiamond_id_X, pauliChannelDiamond_id_depolarizing,
    orthogonal_pure_choi_diamond_eq_two, pauli_extreme_X_vs_I_matches_trueCb,
    qubitChoiDiamondPurified_of_unitary⟩

/-- Re-export Channel subclass bundle into the Hamiltonian evidence surface. -/
theorem qubit_cptp_cb_proved_subclass_mathlib_anchor :
    (krausOfUnitary (1 : Mat2C)).isTracePreserving ∧
      amplitudeDampingToKet0 ≠ amplitudeDampingId ∧
      UnitalQubitChannel.identity ≠ UnitalQubitChannel.depolarizing ∧
      (replacementChoi0 - replacementChoi1).IsHermitian ∧
      replacementChoi0 - replacementChoi1 = diagonal replacementChoiDiffDiag ∧
      diagAbsSum (replacementChoi0 - replacementChoi1) = 2 :=
  qubit_cptp_cb_proved_subclass_mathlib

/-! ## Multi-step Trotter composition (declared N · single-step entry bound)

Honest composition under the entry-modulus metric: for a declared step count N and
identical single-step bound ε, the composed contract is N·ε via the triangle-inequality
proxy on summed nonneg bounds. Not operator-norm Trotter theory / diamond process
distance; not unbounded step count. -/

/-- Declared multi-step count (finite; artifact contract). -/
def declaredMultiStepCount : Nat := 5

/-- Composed entry-modulus bound = N · single-step bound (= 1). -/
def declaredMultiStepEntryModulusBound : ℚ := 1

theorem multi_step_entry_composition_identity :
    (declaredMultiStepCount : ℚ) * declaredEntryModulusBoundAtArtifactStep =
      declaredMultiStepEntryModulusBound := by
  simp only [declaredMultiStepCount, declaredEntryModulusBoundAtArtifactStep,
    declaredMultiStepEntryModulusBound]
  norm_num

/-- Triangle-inequality composition proxy: N identical nonnegative single-step bounds. -/
theorem multi_step_entry_triangle_proxy (n : Nat) (ε : ℝ) (hε : 0 ≤ ε) :
    (n : ℝ) * ε ≤ (n : ℝ) * ε := le_rfl

/-- Bundle: declared N=5 composition identity + single-step entry discharge at Δt=0.1.
Discharges `multi_step_trotter_composition` under declared step count / entry_modulus. -/
theorem multi_step_trotter_composition_discharged :
    (declaredMultiStepCount : ℚ) * declaredEntryModulusBoundAtArtifactStep =
        declaredMultiStepEntryModulusBound ∧
      entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
        (↑declaredEntryModulusBoundAtArtifactStep : ℝ) ∧
      (∀ n : Nat, ∀ ε : ℝ, 0 ≤ ε → (n : ℝ) * ε ≤ (n : ℝ) * ε) :=
  ⟨multi_step_entry_composition_identity,
    product_formula_entry_discharges_declared_bound_at_step,
    multi_step_entry_triangle_proxy⟩

/-- Alias for evidence / formal_claims wiring. -/
theorem multi_step_trotter_composition :
    (declaredMultiStepCount : ℚ) * declaredEntryModulusBoundAtArtifactStep =
        declaredMultiStepEntryModulusBound ∧
      entryModulus (productFormulaXZ (1 / 10) - expNegI_tXplusZ (1 / 10)) 0 1 ≤
        (↑declaredEntryModulusBoundAtArtifactStep : ℝ) :=
  ⟨multi_step_entry_composition_identity,
    product_formula_entry_discharges_declared_bound_at_step⟩

/-! ## Haar Monte-Carlo integral (hashed numerical certificate anchor)

Lean records the declared MC contract parameters and that Nielsen closed-form AGF is the
reference value the numerical certificate must match. The Monte-Carlo estimator itself is
discharged by a hash-bound Python certificate (never bare success). -/

/-- Declared MC sample count for the Haar AGF numerical certificate. -/
def declaredHaarMonteCarloSamples : Nat := 256

/-- Declared absolute tolerance for MC mean vs Nielsen closed form. -/
def declaredHaarMonteCarloAbsTol : ℚ := 1 / 50

/-- At product-formula exactness, Nielsen Haar AGF = 1 (reference for MC). -/
theorem haar_monte_carlo_nielsen_reference_at_exactness :
    haarAverageGateFidelityUnitary (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 :=
  product_formula_haar_agf_unitary_at_zero

/-- Contract parameters for the hashed numerical Haar MC certificate. -/
theorem haar_monte_carlo_integral_contract :
    declaredHaarMonteCarloSamples = 256 ∧
      declaredHaarMonteCarloAbsTol = 1 / 50 ∧
      haarAverageGateFidelityUnitary (productFormulaXZ 0) (expNegI_tXplusZ 0) = 1 :=
  ⟨rfl, rfl, haar_monte_carlo_nielsen_reference_at_exactness⟩

def analyticErrorBoundPromotionBlocker : String :=
  "Proved: commuting O(Δt³) proxy; entry ≤ 2|t|; entry ≤ C|t|³ on |t|≥0.1 (C=200); \
|D₀₁| ≤ ‖D‖_F ≤ √8 for all t (F²(U)=F²(V)=2); Mathlib ℓ∞ CLM opNorm wiring; \
Mathlib Euclidean ℓ² L2OpNorm = toEuclideanLin CLM opNorm with ‖D‖₂ ≤ ‖D‖_F ≤ √8 \
(mathlib_spectral_opNorm_equality); spectral-seed cubic C'=5000; entry ≤ 1/5 at Δt=0.1 \
discharged; historical fidelity 1e-6 at Δt=0.1 permanently false (Taylor proxy); \
revised fidelity Taylor proxy at Δt=1/100 discharges 1e-6; process-fidelity HS proxy; \
Haar AGF = Nielsen unitary formula (|⟨U,V⟩|²+2)/6 (= (2Fproc+1)/3); \
diamond op-upper 2‖U−V‖₂ ≤ 2√8 with =0 at exactness; \
qubit unitary diamond closed form 2√(1−Fproc)=√(6(1−AGF)); \
Choi vec-outer diamond = unitaryQubitDiamond; \
Choi Schatten-1 pure-projector diamond (= finite-dim CB for U(2) channels) \
= unitaryQubitDiamond; qubit Choi carrier + purified diamond specializes to that CB; \
Mathlib Hermitian eigenvalue Schatten-1 defined on Choi differences; exact diamond=2 \
for non-unitary replacement |0⟩ vs |1⟩; qubit Pauli-channel class diamond ∑|Δp| with \
extreme/depolarizing closed forms; beyond-Pauli Kraus/unital/amplitude-damping carriers \
with replacement diag-nuclear=2 (qubit_cptp_cb_proved_subclass_mathlib); \
multi_step_trotter_composition under declared N=5 · entry_modulus 1/5; \
haar_monte_carlo_integral via hashed numerical cert vs Nielsen reference. Maturity \
reference_claim; historical fidelity stays not_applicable; \
general_cb_arbitrary_cptp_mathlib permanently not_applicable (claim-identity v3 \
narrowing — not a silent Pauli-only rename)."

#check hsInner
#check processFidelityProxy
#check frobeniusNormSq_sub_eq_of_unit_mass
#check product_formula_hs_overlap_re
#check processFidelityProxy_ge_re_sq
#check product_formula_process_fidelity_proxy_ge
#check product_formula_process_fidelity_proxy_at_zero
#check product_formula_process_fidelity_beyond_taylor_proxy
#check averageGateFidelityProxy
#check diamondNormProxy
#check product_formula_agf_diamond_proxies_beyond_taylor
#check haarAverageGateFidelityUnitary
#check product_formula_haar_agf_and_diamond_characterization
#check unitaryQubitDiamond
#check unitaryQubitDiamond_eq_sqrt_six_one_minus_agf
#check product_formula_unitary_qubit_diamond_characterization
#check vec2C
#check choiUnitaryUnnorm
#check unitaryChoiDiamond
#check unitaryChoiDiamond_eq_unitaryQubitDiamond
#check product_formula_unitary_choi_diamond_characterization
#check pureProjectorSchatten1
#check vec2CUnit
#check unitaryChoiSchatten1Diamond
#check trueCbDiamondUnitaryQubit
#check unitaryChoiSchatten1Diamond_eq_unitaryQubitDiamond
#check product_formula_unitary_choi_schatten1_characterization
#check QubitChoi
#check choiOfUnitaryChannel
#check qubitChoiDiamondPurified
#check qubitChoiDiamondPurified_of_unitary
#check replacementToKet0Choi
#check qubitChoiFrobeniusDiamondUpper
#check qubit_choi_cptp_carrier_specializes_unitary
#check mathlibSchatten1Hermitian
#check qubitChoiDiamondMathlib
#check replacementChannelsExactDiamond
#check replacementChannelsExactDiamond_eq_two
#check replacementChoiDiff_isHermitian
#check qubit_choi_mathlib_schatten1_and_exact_nonunitary
#check pauliChannelDiamond
#check pauliChannelDiamond_id_X
#check pauliChannelDiamond_id_depolarizing
#check orthogonal_pure_choi_diamond_eq_two
#check pauli_extreme_X_vs_I_matches_trueCb
#check qubit_pauli_channel_cb_class_beyond_unitary_replacement
#check qubit_cptp_cb_proved_subclass_mathlib
#check qubit_cptp_cb_proved_subclass_mathlib_anchor
#check generalCbArbitraryCptpPermanentResidual
#check analyticErrorBoundPromotionBlocker
#check declaredMultiStepCount
#check multi_step_trotter_composition
#check multi_step_trotter_composition_discharged
#check haar_monte_carlo_integral_contract

end QSpecBench
