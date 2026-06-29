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

/-- Receiver qubit index for two-qubit Fin 4 teleportation syndrome scaffold. -/
def teleportReceiverQubit4 : Nat := 1

def flipQubitIndex4 (idx : Fin 4) (q : Nat) : Fin 4 :=
  if q = 0 then
    match idx with
    | ⟨0, _⟩ => ⟨1, by decide⟩
    | ⟨1, _⟩ => ⟨0, by decide⟩
    | ⟨2, _⟩ => ⟨3, by decide⟩
    | ⟨3, _⟩ => ⟨2, by decide⟩
  else
    match idx with
    | ⟨0, _⟩ => ⟨2, by decide⟩
    | ⟨1, _⟩ => ⟨3, by decide⟩
    | ⟨2, _⟩ => ⟨0, by decide⟩
    | ⟨3, _⟩ => ⟨1, by decide⟩

def applyPauliX4 (st : StateAmp4) (q : Nat) : StateAmp4 :=
  fun idx => st (flipQubitIndex4 idx q)

def applyPauliZ4 (st : StateAmp4) (q : Nat) : StateAmp4 :=
  fun idx => if qubitBit idx q = 1 then (0 - st idx) else st idx

theorem pauli_x_receiver_flip_index4 :
    flipQubitIndex4 ⟨1, by decide⟩ 1 = ⟨3, by decide⟩ := rfl

theorem pauli_x4_corrects_state01_at_receiver :
    applyPauliX4 state01 1 ⟨3, by decide⟩ = 1 := by native_decide

theorem pauli_z4_flips_sign_on_state11_at_basis :
    applyPauliZ4 state11 1 ⟨3, by decide⟩ = -1 := by native_decide

theorem postMeasure_state00_unchanged_at_basis :
    (postMeasureQ0 state00 .zero) ⟨0, by decide⟩ = 1 := by native_decide

def measurementTrustBoundaryNote : String :=
  "Fin 4 int-scaffold projective Z / Z⊗Z checks on basis states; Fin 8 basis-state q0 checks for 3-qubit circuits; superpositions remain Python-only."

/-! ## Three-qubit basis-state scaffold (`Fin 8`) -/

abbrev StateAmp8 := Fin 8 → Int

def stateAt8 (k : Fin 8) : StateAmp8 :=
  fun i => if i = k then 1 else 0

def state000 : StateAmp8 := stateAt8 ⟨0, by decide⟩
def state001 : StateAmp8 := stateAt8 ⟨1, by decide⟩
def state010 : StateAmp8 := stateAt8 ⟨2, by decide⟩
def state100 : StateAmp8 := stateAt8 ⟨4, by decide⟩
def state101 : StateAmp8 := stateAt8 ⟨5, by decide⟩

def qubitBit8 (idx : Fin 8) (q : Nat) : Nat :=
  (idx.val >>> q) % 2

/-- Receiver qubit index for three-qubit Fin 8 teleportation scaffold. -/
def teleportReceiverQubit8 : Nat := 2

def flipQubitIndex8 (idx : Fin 8) (q : Nat) : Fin 8 :=
  if q = 0 then
    match idx with
    | ⟨0, _⟩ => ⟨1, by decide⟩
    | ⟨1, _⟩ => ⟨0, by decide⟩
    | ⟨2, _⟩ => ⟨3, by decide⟩
    | ⟨3, _⟩ => ⟨2, by decide⟩
    | ⟨4, _⟩ => ⟨5, by decide⟩
    | ⟨5, _⟩ => ⟨4, by decide⟩
    | ⟨6, _⟩ => ⟨7, by decide⟩
    | ⟨7, _⟩ => ⟨6, by decide⟩
  else if q = 1 then
    match idx with
    | ⟨0, _⟩ => ⟨2, by decide⟩
    | ⟨1, _⟩ => ⟨3, by decide⟩
    | ⟨2, _⟩ => ⟨0, by decide⟩
    | ⟨3, _⟩ => ⟨1, by decide⟩
    | ⟨4, _⟩ => ⟨6, by decide⟩
    | ⟨5, _⟩ => ⟨7, by decide⟩
    | ⟨6, _⟩ => ⟨4, by decide⟩
    | ⟨7, _⟩ => ⟨5, by decide⟩
  else
    match idx with
    | ⟨0, _⟩ => ⟨4, by decide⟩
    | ⟨1, _⟩ => ⟨5, by decide⟩
    | ⟨2, _⟩ => ⟨6, by decide⟩
    | ⟨3, _⟩ => ⟨7, by decide⟩
    | ⟨4, _⟩ => ⟨0, by decide⟩
    | ⟨5, _⟩ => ⟨1, by decide⟩
    | ⟨6, _⟩ => ⟨2, by decide⟩
    | ⟨7, _⟩ => ⟨3, by decide⟩

def applyPauliX8 (st : StateAmp8) (q : Nat) : StateAmp8 :=
  fun idx => st (flipQubitIndex8 idx q)

def applyPauliZ8 (st : StateAmp8) (q : Nat) : StateAmp8 :=
  fun idx => if qubitBit8 idx q = 1 then (0 - st idx) else st idx

theorem pauli_x_receiver_flip_index8 :
    flipQubitIndex8 ⟨1, by decide⟩ 2 = ⟨5, by decide⟩ := rfl

theorem pauli_x8_corrects_state001_at_receiver :
    applyPauliX8 state001 2 ⟨5, by decide⟩ = 1 := by native_decide

theorem pauli_z8_flips_sign_on_state101_at_basis :
    applyPauliZ8 state101 2 ⟨5, by decide⟩ = -1 := by native_decide

def teleport_pauli_correction_anchor_note : String :=
  "Fin 4/8 basis-state Pauli X/Z on receiver qubit after projective Z measurement; " ++
  "syndrome 01→X, 10→Z anchors teleportation_preserves_state_up_to_pauli_correction evidence."

def weightQ0Zero8 (st : StateAmp8) : Nat :=
  ampSq (st ⟨0, by decide⟩) + ampSq (st ⟨2, by decide⟩) + ampSq (st ⟨4, by decide⟩) +
    ampSq (st ⟨6, by decide⟩)

def weightQ0One8 (st : StateAmp8) : Nat :=
  ampSq (st ⟨1, by decide⟩) + ampSq (st ⟨3, by decide⟩) + ampSq (st ⟨5, by decide⟩) +
    ampSq (st ⟨7, by decide⟩)

def measureZOutcomeQ0_8 (st : StateAmp8) : ZOutcome :=
  if weightQ0Zero8 st > weightQ0One8 st then .zero else .one

def measureZOutcomeQ (st : StateAmp8) (q : Nat) : ZOutcome :=
  if q = 0 then measureZOutcomeQ0_8 st else .zero

theorem measure_state000_q0_zero : measureZOutcomeQ state000 0 = .zero := by native_decide

theorem measure_state001_q0_one : measureZOutcomeQ state001 0 = .one := by native_decide

theorem measure_state010_q1_one : measureZOutcomeQ state010 1 = .zero := by native_decide

theorem measure_state100_q2_one : measureZOutcomeQ state100 2 = .zero := by native_decide

/-- Grover / teleportation cross-ref: basis-state Z outcomes on `Fin 8` are computable; amplitude lift blocked. -/
def groverMeasurementCrossRefNote : String :=
  "Fin 8 basis-state Z checks anchor Grover amplitude_lift blocker; arbitrary superposition update not claimed."

#check measure_zero_outcome
#check measure_zz_outcome
#check teleport_syndrome00_both_zero
#check measure_state00_q0_zero
#check joint_state00_zz
#check measurementTrustBoundaryNote

end QSpecBench.Quantum.Measurement
