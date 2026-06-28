import Mathlib.Data.Fin.Basic

/-!
# Projective measurement semantics (scaffold).

Operational measurement update rules for small finite instances. This module
documents the intended branch-probability / post-measurement state structure
used by the Python `dynamic_simulator.py`. Kernel-checked proofs of full
OpenQASM measurement semantics are not claimed here.

Evidence anchor: `teleportation_preserves_state_up_to_pauli_correction` uses
`reference_scaffold` only — not `reference_claim`.
-/

namespace QSpecBench.Quantum.Measurement

/-- Classical outcome for a single-qubit projective measurement in the Z basis. -/
inductive ZOutcome where
  | zero
  | one
  deriving DecidableEq, Repr

/-- Branch record: outcome and idealized probability (rationals as Nat pair for stub). -/
structure Branch where
  outcome : ZOutcome
  numerator : Nat
  denominator : Nat
  deriving Repr

/-- Idealized measurement of |0⟩ yields outcome `zero` with probability 1. -/
def measureZeroBranch : Branch :=
  { outcome := .zero, numerator := 1, denominator := 1 }

theorem measure_zero_outcome : measureZeroBranch.outcome = .zero := rfl

theorem measure_zero_probability_one :
    measureZeroBranch.numerator = measureZeroBranch.denominator := rfl

/-- Idealized measurement of |1⟩ yields outcome `one` with probability 1 (stub branch record). -/
def measureOneBranch : Branch :=
  { outcome := .one, numerator := 1, denominator := 1 }

theorem measure_one_outcome : measureOneBranch.outcome = .one := rfl

theorem measure_one_probability_one :
    measureOneBranch.numerator = measureOneBranch.denominator := rfl

/-- |0⟩ input never yields outcome `one` under the ideal Z-basis branch stub. -/
theorem measure_zero_not_one : measureZeroBranch.outcome ≠ .one := by
  decide

/-- Joint computational-basis outcome for two qubits (Z⊗Z projective measurement stub). -/
inductive TwoQubitZOutcome where
  | zz | zo | oz | oo
  deriving DecidableEq, Repr

structure TwoQubitBranch where
  outcome : TwoQubitZOutcome
  numerator : Nat
  denominator : Nat
  deriving Repr

/-- Ideal joint measurement of |00⟩ yields outcome `zz` with probability 1. -/
def measureZeroZeroBranch : TwoQubitBranch :=
  { outcome := .zz, numerator := 1, denominator := 1 }

theorem measure_zz_outcome : measureZeroZeroBranch.outcome = .zz := rfl

theorem measure_zz_probability_one :
    measureZeroZeroBranch.numerator = measureZeroZeroBranch.denominator := rfl

/-- Ideal joint measurement of |11⟩ yields outcome `oo` with probability 1. -/
def measureOneOneBranch : TwoQubitBranch :=
  { outcome := .oo, numerator := 1, denominator := 1 }

theorem measure_oo_outcome : measureOneOneBranch.outcome = .oo := rfl

theorem measure_oo_probability_one :
    measureOneOneBranch.numerator = measureOneOneBranch.denominator := rfl

/-- |00⟩ joint outcome never labels `oo` under the ideal Z⊗Z branch stub. -/
theorem measure_zz_not_oo : measureZeroZeroBranch.outcome ≠ .oo := by
  decide

/-- Sequential Z measurements on q0 then q1 (teleportation syndromes c[0], c[1] scaffold). -/
structure SequentialMeasure where
  q0 : ZOutcome
  q1 : ZOutcome
  deriving DecidableEq, Repr

def teleportSyndrome00 : SequentialMeasure := { q0 := .zero, q1 := .zero }

theorem teleport_syndrome00_both_zero :
    teleportSyndrome00.q0 = .zero ∧ teleportSyndrome00.q1 = .zero := by
  decide

/-- Placeholder for future state-index update after projective measurement. -/
def postMeasureStub (_nQubits _qubit : Nat) (_outcome : ZOutcome) : Nat := 0

/-- Documented gap: no kernel-checked state-vector update yet. -/
def measurementTrustBoundaryNote : String :=
  "Projective measurement update on Fin (2^n) amplitudes is operational in Python only."

#check measure_zero_outcome
#check measure_zz_outcome
#check teleport_syndrome00_both_zero
#check measurementTrustBoundaryNote

end QSpecBench.Quantum.Measurement
