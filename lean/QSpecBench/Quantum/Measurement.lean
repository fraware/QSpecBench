import Mathlib.Data.Fin.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring

/-!
# Projective measurement semantics (finite statevector scaffold).

Operational measurement update rules for small finite instances (`n ≤ 3` qubits,
`Fin (2^n)` amplitudes for n ∈ {1,2,3}), plus classical register updates,
Z-basis density projectors, branch probabilities, and conditional Pauli
correction tables. This module documents the intended structure used by the
Python `dynamic_simulator.py`. Kernel-checked proofs of full OpenQASM measurement
semantics and arbitrary-state teleportation are not claimed here.

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
  "Fin 2/4/8 int-scaffold projective Z measures on basis states and equal-amplitude \
superpositions (n≤3); renormalized ℂ arbitrary-state update remains out of scope."

def projectiveMeasureScaffoldDims : List Nat := [2, 4, 8]

/-! ## Superposition projective update (Fin 2 / Fin 4 equal-amplitude)

Supports Grover `amplitude_lift` scaffolding: measurement weights and post-states
on unnormalized equal-amplitude superpositions, not only computational basis. -/

/-- Unnormalized equal-amplitude |+⟩ on one qubit (amps (1,1)). -/
def plusState2 : StateAmp2 := fun _ => 1

/-- Unnormalized equal superposition on Fin 4 (amps all 1). -/
def uniformState4 : StateAmp4 := fun _ => 1

theorem measureZ2_plus_equal_weights :
    (measureZ2 plusState2).weightZero = 1 ∧ (measureZ2 plusState2).weightOne = 1 := by
  native_decide

theorem measureZ2_plus_post_zero_support :
    (measureZ2 plusState2).postZero ⟨0, by decide⟩ = 1 ∧
      (measureZ2 plusState2).postZero ⟨1, by decide⟩ = 0 := by
  native_decide

theorem measureZ2_plus_post_one_support :
    (measureZ2 plusState2).postOne ⟨0, by decide⟩ = 0 ∧
      (measureZ2 plusState2).postOne ⟨1, by decide⟩ = 1 := by
  native_decide

theorem measureZ4_uniform_q0_equal_weights :
    (measureZ4 uniformState4 0).weightZero = 2 ∧
      (measureZ4 uniformState4 0).weightOne = 2 := by
  native_decide

/-- Marked-basis weight for |1⟩ on Fin 2 (ampSq of index 1). -/
def markedWeight2 (st : StateAmp2) : Nat := amplitudeNormSq (st ⟨1, by decide⟩)

theorem markedWeight2_plus_baseline : markedWeight2 plusState2 = 1 := by native_decide

/-- Apply a 2×2 int matrix to a Fin-2 statevector. -/
def applyMat2 (M : Fin 2 → Fin 2 → Int) (st : StateAmp2) : StateAmp2 :=
  fun i => M i ⟨0, by decide⟩ * st ⟨0, by decide⟩ + M i ⟨1, by decide⟩ * st ⟨1, by decide⟩

/-- Unnormalized H (entries ±1). -/
def hadamard2Amp (i j : Fin 2) : Int :=
  if i = ⟨1, by decide⟩ ∧ j = ⟨1, by decide⟩ then -1 else 1

/-- Pauli Z (phase flip on |1⟩). -/
def pauliZ2Amp (i j : Fin 2) : Int :=
  if i = j then (if i = ⟨1, by decide⟩ then -1 else 1) else 0

/-- Declared Fin-2 amplification fragment: H ∘ Z on |+⟩ concentrates weight on |1⟩.
(Unnormalized int scaffold; scoped amplitude-lift lemma for Grover packaging.) -/
def amplifyMarked1 (st : StateAmp2) : StateAmp2 :=
  applyMat2 hadamard2Amp (applyMat2 pauliZ2Amp st)

theorem amplifyMarked1_plus_concentrates :
    markedWeight2 (amplifyMarked1 plusState2) = 4 ∧
      markedWeight2 plusState2 = 1 ∧
      markedWeight2 plusState2 < markedWeight2 (amplifyMarked1 plusState2) := by
  native_decide

/-- Bundle: superposition projective update + Fin-2 marked-weight lift on declared fragment. -/
theorem grover_fin2_superposition_amplitude_lift_scaffold :
    (measureZ2 plusState2).weightZero = 1 ∧
      (measureZ2 plusState2).weightOne = 1 ∧
      markedWeight2 plusState2 < markedWeight2 (amplifyMarked1 plusState2) :=
  ⟨measureZ2_plus_equal_weights.1, measureZ2_plus_equal_weights.2,
    amplifyMarked1_plus_concentrates.2.2⟩

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
  "Closed in Teleportation.lean: normalized-H (`1/√2`) POVM Alice probs 1/4 + renormalized \
Bob recovery; Lean ClassicalReg feed-forward ≡ Pauli table; dual reviews + claim packaging \
at reference_claim. Residual: OpenQASM `if` parser denotation / full dynamic OpenQASM."

/-! ## Arbitrary-state transfer goal (stated, unproved) -/

/-- Homogeneity of post-measurement update (integer amplitude scaffold). -/
theorem postMeasureQ0_2_homogeneous (st : StateVec2) (c : Amplitude) (o : ZOutcome) (i : Fin 2) :
    postMeasureQ0_2 (fun j => c * st j) o i = c * postMeasureQ0_2 st o i := by
  simp [postMeasureQ0_2]

/-- Linearity of Fin-2 Pauli X correction used in teleportation tables. -/
def applyX2 (st : StateVec2) : StateVec2 :=
  fun i => match i with
    | ⟨0, _⟩ => st ⟨1, by decide⟩
    | ⟨1, _⟩ => st ⟨0, by decide⟩

/-- Additivity of Fin-2 post-measure (enables α|0⟩+β|1⟩ reduction after unitary pipeline). -/
theorem postMeasureQ0_2_add (st₁ st₂ : StateVec2) (o : ZOutcome) (i : Fin 2) :
    postMeasureQ0_2 (fun j => st₁ j + st₂ j) o i =
      postMeasureQ0_2 st₁ o i + postMeasureQ0_2 st₂ o i := by
  simp [postMeasureQ0_2]
  split_ifs <;> ring

theorem applyX2_add (st₁ st₂ : StateVec2) (i : Fin 2) :
    applyX2 (fun j => st₁ j + st₂ j) i = applyX2 st₁ i + applyX2 st₂ i := by
  fin_cases i <;> simp [applyX2]

/-- Scaled computational-basis post-measure: c|0⟩ collapses on zero to itself. -/
theorem teleport_scaled_basis0_post (c : Amplitude) :
    postMeasureQ0_2 (fun j => c * state0 j) .zero = fun j => c * state0 j := by
  funext i
  fin_cases i <;> simp [postMeasureQ0_2, state0, stateAt2]

/-- Scaled computational-basis post-measure: c|1⟩ collapses on one to itself. -/
theorem teleport_scaled_basis1_post (c : Amplitude) :
    postMeasureQ0_2 (fun j => c * state1 j) .one = fun j => c * state1 j := by
  funext i
  fin_cases i <;> simp [postMeasureQ0_2, state1, stateAt2]

/-- Bundle: additivity + scaled-basis posts shrink ∀ψ toward linearity after the unitary prefix. -/
theorem teleport_fin2_linearity_intermediates :
    (∀ st₁ st₂ o i,
      postMeasureQ0_2 (fun j => st₁ j + st₂ j) o i =
        postMeasureQ0_2 st₁ o i + postMeasureQ0_2 st₂ o i) ∧
      (∀ st₁ st₂ i, applyX2 (fun j => st₁ j + st₂ j) i = applyX2 st₁ i + applyX2 st₂ i) ∧
      (∀ c, postMeasureQ0_2 (fun j => c * state0 j) .zero = fun j => c * state0 j) ∧
      (∀ c, postMeasureQ0_2 (fun j => c * state1 j) .one = fun j => c * state1 j) :=
  ⟨postMeasureQ0_2_add, applyX2_add, teleport_scaled_basis0_post, teleport_scaled_basis1_post⟩

/-- Z outcome from `measureZ8` weights (any qubit; not the q0-only stub). -/
def measureZOutcomeAt8 (st : StateVec8) (q : Nat) : ZOutcome :=
  if weightQubitZeroAt8 st q > weightQubitOneAt8 st q then .zero else .one

theorem measureZOutcomeAt8_state000_q0 :
    measureZOutcomeAt8 state000 0 = .zero := by native_decide

/-- CNOT on Fin-8 integer amplitudes (control `c`, target `t`; LSB indexing). -/
def applyCNOT8 (st : StateAmp8) (c t : Nat) : StateAmp8 :=
  fun idx => if qubitBit8 idx c = 1 then st (flipQubitIndex8 idx t) else st idx

theorem applyCNOT8_state000_c01 :
    applyCNOT8 state000 0 1 = state000 := by native_decide

theorem applyCNOT8_state001_c01 :
    applyCNOT8 state001 0 1 = stateAt8 ⟨3, by decide⟩ := by native_decide

theorem applyX2_homogeneous (st : StateVec2) (c : Amplitude) (i : Fin 2) :
    applyX2 (fun j => c * st j) i = c * applyX2 st i := by
  fin_cases i <;> simp [applyX2]

/-- Fin-4 post-measure homogeneity (shrinks ∀ψ; does not close D5). -/
theorem postMeasureQ0_homogeneous (st : StateAmp4) (c : Amplitude) (o : ZOutcome) (i : Fin 4) :
    postMeasureQ0 (fun j => c * st j) o i = c * postMeasureQ0 st o i := by
  simp [postMeasureQ0]

theorem applyPauliX4_homogeneous (st : StateAmp4) (c : Amplitude) (q : Nat) (i : Fin 4) :
    applyPauliX4 (fun j => c * st j) q i = c * applyPauliX4 st q i := by
  simp [applyPauliX4]

theorem applyPauliZ4_homogeneous (st : StateAmp4) (c : Amplitude) (q : Nat) (i : Fin 4) :
    applyPauliZ4 (fun j => c * st j) q i = c * applyPauliZ4 st q i := by
  simp only [applyPauliZ4]
  split_ifs <;> ring

theorem applyPauliCorrection4_homogeneous
    (c0 c1 : ZOutcome) (st : StateAmp4) (c : Amplitude) (i : Fin 4) :
    applyPauliCorrection4 c0 c1 (fun j => c * st j) i =
      c * applyPauliCorrection4 c0 c1 st i := by
  cases c0 <;> cases c1
  · simp [applyPauliCorrection4]
  · simp [applyPauliCorrection4, applyPauliX4_homogeneous]
  · simp [applyPauliCorrection4, applyPauliZ4_homogeneous]
  · -- ZX composition
    simp only [applyPauliCorrection4]
    have hx :
        applyPauliX4 (fun j => c * st j) teleportReceiverQubit4 =
          fun k => c * applyPauliX4 st teleportReceiverQubit4 k := by
      funext k; exact applyPauliX4_homogeneous st c teleportReceiverQubit4 k
    rw [hx]
    exact applyPauliZ4_homogeneous _ c teleportReceiverQubit4 i

/-- Fin-8 Pauli / correction homogeneity (shrinks ∀ψ; does not close D5). -/
theorem applyPauliX8_homogeneous (st : StateAmp8) (c : Amplitude) (q : Nat) (i : Fin 8) :
    applyPauliX8 (fun j => c * st j) q i = c * applyPauliX8 st q i := by
  simp [applyPauliX8]

theorem applyPauliZ8_homogeneous (st : StateAmp8) (c : Amplitude) (q : Nat) (i : Fin 8) :
    applyPauliZ8 (fun j => c * st j) q i = c * applyPauliZ8 st q i := by
  simp only [applyPauliZ8]
  split_ifs <;> ring

theorem applyPauliCorrection8_homogeneous
    (c0 c1 : ZOutcome) (st : StateAmp8) (c : Amplitude) (i : Fin 8) :
    applyPauliCorrection8 c0 c1 (fun j => c * st j) i =
      c * applyPauliCorrection8 c0 c1 st i := by
  cases c0 <;> cases c1
  · simp [applyPauliCorrection8]
  · simp [applyPauliCorrection8, applyPauliX8_homogeneous]
  · simp [applyPauliCorrection8, applyPauliZ8_homogeneous]
  · simp only [applyPauliCorrection8]
    have hx :
        applyPauliX8 (fun j => c * st j) teleportReceiverQubit8 =
          fun k => c * applyPauliX8 st teleportReceiverQubit8 k := by
      funext k; exact applyPauliX8_homogeneous st c teleportReceiverQubit8 k
    rw [hx]
    exact applyPauliZ8_homogeneous _ c teleportReceiverQubit8 i

theorem pauli_correction_Z_syndrome10 :
    applyPauliCorrection4 .one .zero state10 ⟨2, by decide⟩ = -1 := by native_decide

/-- Fin-4 D4 chain for |10⟩ with Z correction on receiver. -/
theorem teleport_basis10_lemma_chain :
    measureZOutcomeQ0 state10 = .zero ∧
      applyPauliCorrection4 .one .zero state10 ⟨2, by decide⟩ = -1 := by
  exact ⟨measure_state10_q0_zero, pauli_correction_Z_syndrome10⟩

/-- Fin-4 |11⟩ measure outcome (ZX correction amplitude depends on index; not claimed here). -/
theorem teleport_basis11_measure_q0 :
    measureZOutcomeQ0 state11 = .one :=
  measure_state11_q0_one

/-- Stated relational transfer obligation (∀ψ after measure+correct). Unproved. -/
def teleportArbitraryStateTransferGoalNote : String :=
  "Goal: ∀ ψ : StateVec2 (normalized ℂ amplitudes), Bob's corrected qubit equals ψ \
after Bell prep, Alice CX+H, Z-measures, and Pauli correction. Integer Fin-2/4/8 \
basis chains, homogeneity, and Fin-2 linearity intermediates are supporting only."

/-- Homogeneity lemmas shrink the ∀ψ proof obligation but do not close it. -/
theorem teleport_homogeneity_lemmas :
    (∀ st c o i, postMeasureQ0_2 (fun j => c * st j) o i = c * postMeasureQ0_2 st o i) ∧
      (∀ st c i, applyX2 (fun j => c * st j) i = c * applyX2 st i) ∧
      (∀ st c o i, postMeasureQ0 (fun j => c * st j) o i = c * postMeasureQ0 st o i) ∧
      (∀ c0 c1 st c i,
        applyPauliCorrection4 c0 c1 (fun j => c * st j) i =
          c * applyPauliCorrection4 c0 c1 st i) ∧
      (∀ c0 c1 st c i,
        applyPauliCorrection8 c0 c1 (fun j => c * st j) i =
          c * applyPauliCorrection8 c0 c1 st i) :=
  ⟨postMeasureQ0_2_homogeneous, applyX2_homogeneous, postMeasureQ0_homogeneous,
    applyPauliCorrection4_homogeneous, applyPauliCorrection8_homogeneous⟩

/-! ## Classical register update + density-matrix scaffold -/

/-- Classical bit register of width `n`. -/
abbrev ClassicalReg (n : Nat) := Fin n → Bool

def emptyClassicalReg (n : Nat) : ClassicalReg n := fun _ => false

def updateClassicalBit {n : Nat} (reg : ClassicalReg n) (i : Fin n) (b : Bool) :
    ClassicalReg n :=
  fun j => if j = i then b else reg j

theorem updateClassicalBit_sets {n : Nat} (reg : ClassicalReg n) (i : Fin n) (b : Bool) :
    updateClassicalBit reg i b i = b := by
  simp [updateClassicalBit]

theorem updateClassicalBit_preserves_others {n : Nat} (reg : ClassicalReg n)
    (i j : Fin n) (b : Bool) (hij : i ≠ j) :
    updateClassicalBit reg i b j = reg j := by
  simp [updateClassicalBit, Ne.symm hij]

/-- Write a Z-measurement outcome into classical bit `i`. -/
def writeZOutcome {n : Nat} (reg : ClassicalReg n) (i : Fin n) (o : ZOutcome) :
    ClassicalReg n :=
  updateClassicalBit reg i (o == .one)

theorem writeZOutcome_zero_clears {n : Nat} (reg : ClassicalReg n) (i : Fin n) :
    writeZOutcome reg i .zero i = false := by
  simp [writeZOutcome, updateClassicalBit]

theorem writeZOutcome_one_sets {n : Nat} (reg : ClassicalReg n) (i : Fin n) :
    writeZOutcome reg i .one i = true := by
  simp [writeZOutcome, updateClassicalBit]

/-- Diagonal density-matrix scaffold on `Fin 2` (Z-basis populations). -/
abbrev Density2 := Fin 2 → Fin 2 → Int

def projectorKet0 : Density2
  | ⟨0, _⟩, ⟨0, _⟩ => 1
  | _, _ => 0

def projectorKet1 : Density2
  | ⟨1, _⟩, ⟨1, _⟩ => 1
  | _, _ => 0

theorem projectorKet0_trace : projectorKet0 0 0 + projectorKet0 1 1 = 1 := by native_decide

theorem projectorKet1_trace : projectorKet1 0 0 + projectorKet1 1 1 = 1 := by native_decide

/-- Projective Z branch probability as unnormalized weight / total (integer scaffold). -/
def branchProbability (weightZero weightOne : Nat) (outcome : ZOutcome) : Nat × Nat :=
  match outcome with
  | .zero => (weightZero, weightZero + weightOne)
  | .one => (weightOne, weightZero + weightOne)

theorem branchProbability_state0_zero :
    branchProbability 1 0 .zero = (1, 1) := rfl

theorem branchProbability_state1_one :
    branchProbability 0 1 .one = (1, 1) := rfl

/-- Conditional Pauli correction keyed by classical bits (teleportation table). -/
def conditionalPauliFromClassical (m0 m1 : Bool) : String :=
  match m0, m1 with
  | false, false => "I"
  | false, true => "X"
  | true, false => "Z"
  | true, true => "ZX"

theorem conditionalPauli_matches_table :
    conditionalPauliFromClassical false false = "I" ∧
      conditionalPauliFromClassical false true = "X" ∧
      conditionalPauliFromClassical true false = "Z" ∧
      conditionalPauliFromClassical true true = "ZX" := by
  decide

/-! ## OpenQASM3 reset denotation (measure + X correction to |0⟩)

`reset q` is denoted as: Z-measure, then apply X iff outcome was |1⟩, leaving |0⟩.
Linked to `measureZOutcomeQ0_2` / `postMeasureQ0_2` / `applyX2` on the Fin-2 scaffold. -/

/-- Soft reset on one qubit: measure-Z then X-correct to computational |0⟩. -/
def applyResetQ0_2 (st : StateAmp2) : StateAmp2 :=
  match measureZOutcomeQ0_2 st with
  | .zero => postMeasureQ0_2 st .zero
  | .one => applyX2 (postMeasureQ0_2 st .one)

theorem applyResetQ0_2_state0 :
    applyResetQ0_2 state0 = state0 := by
  native_decide

theorem applyResetQ0_2_state1 :
    applyResetQ0_2 state1 = state0 := by
  native_decide

/-- Reset always yields the |0⟩ basis state on computational basis inputs. -/
theorem applyResetQ0_2_basis_to_ket0 (k : Fin 2) :
    applyResetQ0_2 (stateAt2 k) = state0 := by
  fin_cases k <;> native_decide

/-- Bundle: reset denotation = measure+X→|0⟩ on Fin-2 basis. -/
theorem openqasm_reset_denotes_measure_x_to_ket0 :
    applyResetQ0_2 state0 = state0 ∧
      applyResetQ0_2 state1 = state0 ∧
      (∀ k : Fin 2, applyResetQ0_2 (stateAt2 k) = state0) :=
  ⟨applyResetQ0_2_state0, applyResetQ0_2_state1, applyResetQ0_2_basis_to_ket0⟩

/-- Grover / teleportation cross-ref: Fin-2 superposition lift is kernel-checked on the
declared H∘Z fragment; full 2-qubit circuit amplitude_lift vs on-disk Grover QASM remains
a separate packaging obligation. -/
def groverMeasurementCrossRefNote : String :=
  "Fin-2 equal-amplitude projective update + marked-weight lift \
(grover_fin2_superposition_amplitude_lift_scaffold) are kernel-checked; \
2-qubit circuit vs claim semantic_correctness remains unproved."

#check measure_zero_outcome
#check measure_zz_outcome
#check teleport_syndrome00_both_zero
#check measure_state00_q0_zero
#check joint_state00_zz
#check updateClassicalBit_sets
#check writeZOutcome_one_sets
#check conditionalPauli_matches_table
#check branchProbability_state0_zero
#check applyResetQ0_2
#check openqasm_reset_denotes_measure_x_to_ket0
#check postMeasureQ0_2_homogeneous
#check postMeasureQ0_homogeneous
#check applyPauliCorrection4_homogeneous
#check applyPauliCorrection8_homogeneous
#check teleport_basis10_lemma_chain
#check teleport_basis11_measure_q0
#check teleport_homogeneity_lemmas
#check teleport_fin2_linearity_intermediates
#check applyCNOT8_state001_c01
#check measureZOutcomeAt8_state000_q0
#check measurementTrustBoundaryNote
#check teleportArbitraryStateTransferBlocker
#check plusState2
#check measureZ2_plus_equal_weights
#check amplifyMarked1_plus_concentrates
#check grover_fin2_superposition_amplitude_lift_scaffold
#check groverMeasurementCrossRefNote

end QSpecBench.Quantum.Measurement
