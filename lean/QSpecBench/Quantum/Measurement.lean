import Mathlib.Data.Fin.Basic
import Mathlib.Tactic.FinCases

/-!
# Projective measurement semantics (finite statevector scaffold).

Operational measurement update rules for small finite instances (`n ≤ 2` qubits,
`Fin 4` amplitudes). This module documents the intended branch-probability /
post-measurement state structure used by the Python `dynamic_simulator.py`.
Kernel-checked proofs of full OpenQASM measurement semantics are not claimed here.

Evidence anchor: `teleportation_preserves_state_up_to_pauli_correction` uses
`reference_scaffold` only — not `reference_claim`.
-/

namespace QSpecBench.Quantum.Measurement

/-- Classical outcome for a single-qubit projective measurement in the Z basis. -/
inductive ZOutcome where
  | zero
  | one
  deriving DecidableEq, Repr

structure Branch where
  outcome : ZOutcome
  numerator : Nat
  denominator : Nat
  deriving Repr

def measureZeroBranch : Branch :=
  { outcome := .zero, numerator := 1, denominator := 1 }

theorem measure_zero_outcome : measureZeroBranch.outcome = .zero := rfl

theorem measure_zero_probability_one :
    measureZeroBranch.numerator = measureZeroBranch.denominator := rfl

def measureOneBranch : Branch :=
  { outcome := .one, numerator := 1, denominator := 1 }

theorem measure_one_outcome : measureOneBranch.outcome = .one := rfl

theorem measure_one_probability_one :
    measureOneBranch.numerator = measureOneBranch.denominator := rfl

theorem measure_zero_not_one : measureZeroBranch.outcome ≠ .one := by decide

inductive TwoQubitZOutcome where
  | zz | zo | oz | oo
  deriving DecidableEq, Repr

structure TwoQubitBranch where
  outcome : TwoQubitZOutcome
  numerator : Nat
  denominator : Nat
  deriving Repr

def measureZeroZeroBranch : TwoQubitBranch :=
  { outcome := .zz, numerator := 1, denominator := 1 }

theorem measure_zz_outcome : measureZeroZeroBranch.outcome = .zz := rfl

theorem measure_zz_probability_one :
    measureZeroZeroBranch.numerator = measureZeroZeroBranch.denominator := rfl

def measureOneOneBranch : TwoQubitBranch :=
  { outcome := .oo, numerator := 1, denominator := 1 }

theorem measure_oo_outcome : measureOneOneBranch.outcome = .oo := rfl

theorem measure_oo_probability_one :
    measureOneOneBranch.numerator = measureOneOneBranch.denominator := rfl

theorem measure_zz_not_oo : measureZeroZeroBranch.outcome ≠ .oo := by decide

structure SequentialMeasure where
  q0 : ZOutcome
  q1 : ZOutcome
  deriving DecidableEq, Repr

def teleportSyndrome00 : SequentialMeasure := { q0 := .zero, q1 := .zero }

theorem teleport_syndrome00_both_zero :
    teleportSyndrome00.q0 = .zero ∧ teleportSyndrome00.q1 = .zero := by decide

/-! ## Finite statevector scaffold (int amplitudes, `Fin 4`) -/

abbrev StateAmp4 := Fin 4 → Int

def ampSq (a : Int) : Nat := (a * a).natAbs

/-- Computational-basis bit of qubit `q` in index `idx` (q0 = LSB). -/
def qubitBit (idx : Fin 4) (q : Nat) : Nat :=
  if q = 0 then idx.val % 2 else idx.val / 2

def stateAt (k : Fin 4) : StateAmp4 :=
  fun i => if i = k then 1 else 0

def state00 : StateAmp4 := stateAt ⟨0, by decide⟩
def state01 : StateAmp4 := stateAt ⟨1, by decide⟩
def state10 : StateAmp4 := stateAt ⟨2, by decide⟩
def state11 : StateAmp4 := stateAt ⟨3, by decide⟩

def weightQubitZero (st : StateAmp4) : Nat :=
  ampSq (st ⟨0, by decide⟩) + ampSq (st ⟨2, by decide⟩)

def weightQubitOne (st : StateAmp4) : Nat :=
  ampSq (st ⟨1, by decide⟩) + ampSq (st ⟨3, by decide⟩)

def measureZOutcomeQ0 (st : StateAmp4) : ZOutcome :=
  if weightQubitZero st > weightQubitOne st then .zero else .one

def postMeasureQ0 (st : StateAmp4) (outcome : ZOutcome) : StateAmp4 :=
  fun idx =>
    if (outcome == .zero && qubitBit idx 0 = 0) ||
       (outcome == .one && qubitBit idx 0 = 1) then
      st idx
    else
      0

def jointZOutcomeOfIndex (idx : Fin 4) : TwoQubitZOutcome :=
  match idx.val with
  | 0 => .zz
  | 1 => .zo
  | 2 => .oz
  | _ => .oo

theorem measure_state00_q0_zero : measureZOutcomeQ0 state00 = .zero := by native_decide

theorem measure_state01_q0_one : measureZOutcomeQ0 state01 = .one := by native_decide

theorem measure_state10_q0_zero : measureZOutcomeQ0 state10 = .zero := by native_decide

theorem measure_state11_q0_one : measureZOutcomeQ0 state11 = .one := by native_decide

theorem postMeasure_state00_q0_zero : postMeasureQ0 state00 .zero = state00 := by
  funext i
  fin_cases i <;> simp [postMeasureQ0, state00, stateAt, qubitBit]

theorem postMeasure_state01_q0_one : postMeasureQ0 state01 .one = state01 := by
  funext i
  fin_cases i <;> simp [postMeasureQ0, state01, stateAt, qubitBit]

theorem joint_state00_zz : jointZOutcomeOfIndex ⟨0, by decide⟩ = .zz := rfl

theorem joint_state11_oo : jointZOutcomeOfIndex ⟨3, by decide⟩ = .oo := rfl

theorem syndrome00_from_state00 :
    measureZOutcomeQ0 state00 = .zero ∧
      measureZOutcomeQ0 (postMeasureQ0 state00 .zero) = .zero := by native_decide

theorem measure_zero_branch_matches_state00 :
    (measureZOutcomeQ0 state00 == .zero) ∧ measureZeroBranch.outcome = .zero := by
  refine ⟨?_, rfl⟩
  native_decide

theorem measure_zz_branch_matches_state00 :
    jointZOutcomeOfIndex ⟨0, by decide⟩ = .zz ∧ measureZeroZeroBranch.outcome = .zz := by
  exact ⟨joint_state00_zz, rfl⟩

def measurementTrustBoundaryNote : String :=
  "Fin 4 int-scaffold projective Z / Z⊗Z checks on basis states; n>2 and superpositions remain Python-only."

#check measure_zero_outcome
#check measure_zz_outcome
#check teleport_syndrome00_both_zero
#check measure_state00_q0_zero
#check joint_state00_zz
#check measurementTrustBoundaryNote

end QSpecBench.Quantum.Measurement
