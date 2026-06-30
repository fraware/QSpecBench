import Mathlib.Data.Fin.Basic
import Mathlib.Tactic.FinCases

/-!
# Projective measurement semantics (finite statevector scaffold).

Operational measurement update rules for small finite instances (`n ≤ 3` qubits,
`Fin (2^n)` amplitudes for n ∈ {1,2,3}). This module documents the intended
branch-probability / post-measurement state structure used by the Python
`dynamic_simulator.py`. Kernel-checked proofs of full OpenQASM measurement
semantics are not claimed here.

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

def ampSq (a : Int) : Nat := (a * a).natAbs

/-! ## Amplitude / statevector types (n ∈ {1,2,3} → Fin 2 / Fin 4 / Fin 8) -/

/-- Integer amplitude scaffold (real amplitudes in Z basis; sign encodes relative phase). -/
abbrev Amplitude := Int

abbrev StateVec2 := Fin 2 → Amplitude
abbrev StateVec4 := Fin 4 → Amplitude
abbrev StateVec8 := Fin 8 → Amplitude

/-- Branch weights and post-measurement states for projective Z measurement on qubit `q`. -/
structure MeasureZResult (α : Type) where
  weightZero : Nat
  weightOne : Nat
  postZero : α
  postOne : α
  deriving Repr

def amplitudeNormSq (a : Amplitude) : Nat := ampSq a

/-! ## Single-qubit basis-state scaffold (`Fin 2`, n = 1) -/

abbrev StateAmp2 := StateVec2

def stateAt2 (k : Fin 2) : StateAmp2 :=
  fun i => if i = k then 1 else 0

def state0 : StateAmp2 := stateAt2 ⟨0, by decide⟩
def state1 : StateAmp2 := stateAt2 ⟨1, by decide⟩

def weightQ0Zero2 (st : StateAmp2) : Nat := ampSq (st ⟨0, by decide⟩)
def weightQ0One2 (st : StateAmp2) : Nat := ampSq (st ⟨1, by decide⟩)

def measureZOutcomeQ0_2 (st : StateAmp2) : ZOutcome :=
  if weightQ0Zero2 st > weightQ0One2 st then .zero else .one

def postMeasureQ0_2 (st : StateAmp2) (outcome : ZOutcome) : StateAmp2 :=
  fun idx => if (outcome == .zero && idx.val = 0) || (outcome == .one && idx.val = 1) then st idx else 0

/-- Projective Z measurement on the sole qubit (`Fin 2`, arbitrary amplitudes). -/
def measureZ2 (st : StateVec2) : MeasureZResult StateVec2 :=
  { weightZero := amplitudeNormSq (st ⟨0, by decide⟩)
    weightOne := amplitudeNormSq (st ⟨1, by decide⟩)
    postZero := postMeasureQ0_2 st .zero
    postOne := postMeasureQ0_2 st .one }

theorem measureZ2_state0_branch_weights :
    (measureZ2 state0).weightZero = 1 ∧ (measureZ2 state0).weightOne = 0 := by native_decide

theorem measureZ2_state1_branch_weights :
    (measureZ2 state1).weightZero = 0 ∧ (measureZ2 state1).weightOne = 1 := by native_decide

theorem measureZ2_state0_post_zero :
    (measureZ2 state0).postZero = state0 := by
  funext i
  fin_cases i <;> simp [measureZ2, postMeasureQ0_2, state0, stateAt2]

/-- Alias: `measureZ2` on computational basis index (Fin 2 scaffold). -/
def measureZ2_stateAt (k : Fin 2) : MeasureZResult StateVec2 :=
  measureZ2 (stateAt2 k)

theorem measureZ2_state1_post_one :
    (measureZ2 state1).postOne = state1 := by
  funext i
  fin_cases i <;> simp [measureZ2, postMeasureQ0_2, state1, stateAt2]

theorem measure_state0_q0_zero : measureZOutcomeQ0_2 state0 = .zero := by native_decide

theorem postMeasure_state0_q0_zero_2 : postMeasureQ0_2 state0 .zero = state0 := by
  funext i
  fin_cases i <;> simp [postMeasureQ0_2, state0, stateAt2]

theorem single_qubit_basis0_lemma_chain :
    measureZOutcomeQ0_2 state0 = .zero ∧ postMeasureQ0_2 state0 .zero = state0 := by
  exact ⟨measure_state0_q0_zero, postMeasure_state0_q0_zero_2⟩

/-! ## Finite statevector scaffold (int amplitudes, `Fin 4`, n = 2) -/

abbrev StateAmp4 := StateVec4

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

def weightQubitZeroAt (st : StateVec4) (q : Nat) : Nat :=
  if q = 0 then weightQubitZero st
  else ampSq (st ⟨0, by decide⟩) + ampSq (st ⟨1, by decide⟩)

def weightQubitOneAt (st : StateVec4) (q : Nat) : Nat :=
  if q = 0 then weightQubitOne st
  else ampSq (st ⟨2, by decide⟩) + ampSq (st ⟨3, by decide⟩)

def postMeasureQ4 (st : StateVec4) (q : Nat) (outcome : ZOutcome) : StateVec4 :=
  fun idx =>
    if (outcome == .zero && qubitBit idx q = 0) ||
       (outcome == .one && qubitBit idx q = 1) then
      st idx
    else
      0

def measureZ4 (st : StateVec4) (q : Nat) : MeasureZResult StateVec4 :=
  { weightZero := weightQubitZeroAt st q
    weightOne := weightQubitOneAt st q
    postZero := postMeasureQ4 st q .zero
    postOne := postMeasureQ4 st q .one }

theorem measureZ4_state00_branch_weights :
    (measureZ4 state00 0).weightZero = 1 ∧ (measureZ4 state00 0).weightOne = 0 := by native_decide

theorem measureZ4_state01_branch_weights :
    (measureZ4 state01 0).weightZero = 0 ∧ (measureZ4 state01 0).weightOne = 1 := by native_decide

theorem measureZ4_state00_post_zero :
    (measureZ4 state00 0).postZero = state00 := by
  native_decide

/-- Alias: `measureZ4` on computational basis index at qubit `q`. -/
def measureZ4_stateAt (k : Fin 4) (q : Nat) : MeasureZResult StateVec4 :=
  measureZ4 (stateAt k) q

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

/-! ## Classical bit recording (measurement outcome stub) -/

structure RecordedBit where
  outcome : ZOutcome
  value : Bool
  deriving DecidableEq, Repr

def recordZOutcome (o : ZOutcome) : RecordedBit :=
  { outcome := o, value := o == .one }

theorem recordZOutcome_zero : (recordZOutcome .zero).value = false := rfl

theorem recordZOutcome_one : (recordZOutcome .one).value = true := rfl

structure RecordedSyndrome where
  c0 : RecordedBit
  c1 : RecordedBit
  deriving Repr

def recordSyndrome (o0 o1 : ZOutcome) : RecordedSyndrome :=
  { c0 := recordZOutcome o0, c1 := recordZOutcome o1 }

theorem record_syndrome00_values :
    (recordSyndrome .zero .zero).c0.value = false ∧
      (recordSyndrome .zero .zero).c1.value = false := by decide

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

/-! ## Conditional Pauli correction on Fin 4 (teleportation syndrome table) -/

def applyPauliCorrection4 (c0 c1 : ZOutcome) (st : StateAmp4) : StateAmp4 :=
  match c0, c1 with
  | .zero, .zero => st
  | .zero, .one => applyPauliX4 st teleportReceiverQubit4
  | .one, .zero => applyPauliZ4 st teleportReceiverQubit4
  | .one, .one => applyPauliZ4 (applyPauliX4 st teleportReceiverQubit4) teleportReceiverQubit4

theorem pauli_correction_I_state00 :
    applyPauliCorrection4 .zero .zero state00 = state00 := by native_decide

theorem pauli_correction_X_syndrome01 :
    applyPauliCorrection4 .zero .one state01 = state11 := by native_decide

/-- Basis-state |00⟩: measure q0→0, post-measure q0→0, identity correction preserves |00⟩. -/
theorem teleport_basis00_lemma_chain :
    measureZOutcomeQ0 state00 = .zero ∧
      measureZOutcomeQ0 (postMeasureQ0 state00 .zero) = .zero ∧
      applyPauliCorrection4 .zero .zero state00 = state00 := by
  exact ⟨measure_state00_q0_zero, syndrome00_from_state00.right, pauli_correction_I_state00⟩

/-- Basis-state |01⟩ on receiver wire: syndrome (0,1) applies X correction to |11⟩ amplitude slot. -/
theorem teleport_basis01_lemma_chain :
    measureZOutcomeQ0 state01 = .one ∧
      applyPauliCorrection4 .zero .one state01 = state11 := by
  exact ⟨measure_state01_q0_one, pauli_correction_X_syndrome01⟩

/-- Classical recording matches Z-outcome for basis |00⟩. -/
theorem teleport_basis00_recorded_syndrome :
    (recordSyndrome (measureZOutcomeQ0 state00) (measureZOutcomeQ0 (postMeasureQ0 state00 .zero))).c0.outcome = .zero ∧
      (recordSyndrome (measureZOutcomeQ0 state00) (measureZOutcomeQ0 (postMeasureQ0 state00 .zero))).c1.outcome =
        .zero := by
  native_decide

theorem pauli_x_receiver_flip_index4 :
    flipQubitIndex4 ⟨1, by decide⟩ 1 = ⟨3, by decide⟩ := rfl

theorem pauli_x4_corrects_state01_at_receiver :
    applyPauliX4 state01 1 ⟨3, by decide⟩ = 1 := by native_decide

theorem pauli_z4_flips_sign_on_state11_at_basis :
    applyPauliZ4 state11 1 ⟨3, by decide⟩ = -1 := by native_decide

theorem postMeasure_state00_unchanged_at_basis :
    (postMeasureQ0 state00 .zero) ⟨0, by decide⟩ = 1 := by native_decide

def measurementTrustBoundaryNote : String :=
  "Fin 2/4/8 int-scaffold projective Z measures on basis states (n≤3); superpositions remain Python-only."

def projectiveMeasureScaffoldDims : List Nat := [2, 4, 8]

/-! ## Three-qubit basis-state scaffold (`Fin 8`) -/

abbrev StateAmp8 := StateVec8

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

def applyPauliCorrection8 (c0 c1 : ZOutcome) (st : StateAmp8) : StateAmp8 :=
  match c0, c1 with
  | .zero, .zero => st
  | .zero, .one => applyPauliX8 st teleportReceiverQubit8
  | .one, .zero => applyPauliZ8 st teleportReceiverQubit8
  | .one, .one => applyPauliZ8 (applyPauliX8 st teleportReceiverQubit8) teleportReceiverQubit8

theorem pauli_correction8_I_state000 :
    applyPauliCorrection8 .zero .zero state000 = state000 := by native_decide

theorem pauli_correction8_X_syndrome01 :
    applyPauliCorrection8 .zero .one state001 = state101 := by native_decide

theorem pauli_correction8_ZX_syndrome11_sign :
    applyPauliCorrection8 .one .one state001 ⟨5, by decide⟩ = -1 := by native_decide

def pauliCorrection4Table : List (ZOutcome × ZOutcome × String) :=
  [(.zero, .zero, "I"), (.zero, .one, "X"), (.one, .zero, "Z"), (.one, .one, "ZX")]

def pauliCorrection8Table : List (ZOutcome × ZOutcome × String) :=
  pauliCorrection4Table

def teleport_pauli_correction4_table : List (ZOutcome × ZOutcome × String) :=
  pauliCorrection4Table

def teleport_pauli_correction8_table : List (ZOutcome × ZOutcome × String) :=
  pauliCorrection8Table

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

def weightQubitZeroAt8 (st : StateVec8) (q : Nat) : Nat :=
  if q = 0 then weightQ0Zero8 st
  else if q = 1 then
    ampSq (st ⟨0, by decide⟩) + ampSq (st ⟨1, by decide⟩) + ampSq (st ⟨4, by decide⟩) +
      ampSq (st ⟨5, by decide⟩)
  else
    ampSq (st ⟨0, by decide⟩) + ampSq (st ⟨1, by decide⟩) + ampSq (st ⟨2, by decide⟩) +
      ampSq (st ⟨3, by decide⟩)

def weightQubitOneAt8 (st : StateVec8) (q : Nat) : Nat :=
  if q = 0 then weightQ0One8 st
  else if q = 1 then
    ampSq (st ⟨2, by decide⟩) + ampSq (st ⟨3, by decide⟩) + ampSq (st ⟨6, by decide⟩) +
      ampSq (st ⟨7, by decide⟩)
  else
    ampSq (st ⟨4, by decide⟩) + ampSq (st ⟨5, by decide⟩) + ampSq (st ⟨6, by decide⟩) +
      ampSq (st ⟨7, by decide⟩)

def postMeasureQ8 (st : StateVec8) (q : Nat) (outcome : ZOutcome) : StateVec8 :=
  fun idx =>
    if (outcome == .zero && qubitBit8 idx q = 0) ||
       (outcome == .one && qubitBit8 idx q = 1) then
      st idx
    else
      0

def measureZ8 (st : StateVec8) (q : Nat) : MeasureZResult StateVec8 :=
  { weightZero := weightQubitZeroAt8 st q
    weightOne := weightQubitOneAt8 st q
    postZero := postMeasureQ8 st q .zero
    postOne := postMeasureQ8 st q .one }

theorem measureZ8_state000_branch_weights :
    (measureZ8 state000 0).weightZero = 1 ∧ (measureZ8 state000 0).weightOne = 0 := by native_decide

theorem measureZ8_state001_branch_weights :
    (measureZ8 state001 0).weightZero = 0 ∧ (measureZ8 state001 0).weightOne = 1 := by native_decide

theorem measureZ8_state000_post_zero :
    (measureZ8 state000 0).postZero = state000 := by
  native_decide

/-- Alias: `measureZ8` on computational basis index at qubit 0. -/
def measureZ8_stateAt_q0 (k : Fin 8) : MeasureZResult StateVec8 :=
  measureZ8 (stateAt8 k) 0

def measureZOutcomeQ (st : StateAmp8) (q : Nat) : ZOutcome :=
  if q = 0 then measureZOutcomeQ0_8 st else .zero

theorem measure_state000_q0_zero : measureZOutcomeQ state000 0 = .zero := by native_decide

/-- Three-qubit basis |0⟩ on wire 0: Z measure → 0, identity correction. -/
theorem teleport_basis000_lemma_chain :
    measureZOutcomeQ state000 0 = .zero ∧
      applyPauliCorrection8 .zero .zero state000 = state000 := by
  exact ⟨measure_state000_q0_zero, pauli_correction8_I_state000⟩

theorem measure_state001_q0_one : measureZOutcomeQ state001 0 = .one := by native_decide

/-- Fin 8 teleportation: |001⟩ → measure q0→1, X correction on receiver → |101⟩. -/
theorem teleport_basis001_lemma_chain :
    (measureZ8 state001 0).weightOne = 1 ∧
      applyPauliCorrection8 .zero .one state001 = state101 := by
  exact ⟨measureZ8_state001_branch_weights.2, pauli_correction8_X_syndrome01⟩

theorem measure_state010_q1_one : measureZOutcomeQ state010 1 = .zero := by native_decide

theorem measure_state100_q2_one : measureZOutcomeQ state100 2 = .zero := by native_decide

/-- Fin 4 basis-state D4 chain: |00⟩ measure→0, post-measure→0, identity correction. -/
theorem teleport_basis_input_transfer_fin4 :
    measureZOutcomeQ0 state00 = .zero ∧
      measureZOutcomeQ0 (postMeasureQ0 state00 .zero) = .zero ∧
      applyPauliCorrection4 .zero .zero state00 = state00 := by
  exact teleport_basis00_lemma_chain

/-- Fin 2 single-qubit anchor (n=1): basis |0⟩ Z-measure → 0, post-measure preserved. -/
theorem teleport_basis_input_transfer_fin2 :
    measureZOutcomeQ0_2 state0 = .zero ∧ postMeasureQ0_2 state0 .zero = state0 := by
  exact single_qubit_basis0_lemma_chain

def teleportArbitraryStateTransferBlocker : String :=
  "D5 blocked: relational ∀ψ transfer requires general amplitude normalization lemmas; " ++
  "only basis-state Fin 2/4/8 chains are kernel-checked."

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
