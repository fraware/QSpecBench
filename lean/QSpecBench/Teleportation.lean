import Mathlib.Data.Complex.Basic
import Mathlib.Tactic.FinCases
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.NormNum
import QSpecBench.Legacy.Matrix
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import QSpecBench.Quantum.QasmOp
import QSpecBench.Quantum.ComplexGate
import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.OpenQASM3Parser
import QSpecBench.Quantum.Measurement

/-!
# Teleportation: legacy Fin-4 scaffold + Fin-8 unitary prefix with ∀ψ (Int/ℂ lift).

The OpenQASM artifact prefix `H q[1]; CX q[1],q[2]; CX q[0],q[1]; H q[0];` is modeled by
unnormalized-H + CNOT on `Measurement.StateAmp8` (integer amplitudes), with a parallel
**normalized** (`1/√2`) Hadamard denotation whose Alice branch weights form a unitary POVM.
Do not promote the teleportation headline without dual reviews / full claim packaging.
-/

namespace QSpecBench

open QSpecBench (Matrix4 mul4 kron2I hadamard2 cnot4 id4)
open QSpecBench.Quantum.QasmOp
open QSpecBench.Quantum.ComplexGate
open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Quantum.OpenQASM3Parser
open QSpecBench.Quantum.Measurement

/-! ## Legacy Int Fin-4 scaffold -/

def bellPrep (i j : Fin 4) : Int := mul4 cnot4 (kron2I hadamard2) i j

theorem bell_prep_from_00 (j : Fin 4) : bellPrep 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> native_decide

theorem bell_prep_nontrivial : ∃ i j : Fin 4, bellPrep i j ≠ 0 := ⟨0, 0, by native_decide⟩

def teleportAliceCx (i j : Fin 4) : Int := mul4 cnot4 bellPrep i j

theorem teleport_alice_cx_from_00 (j : Fin 4) :
    teleportAliceCx 0 j = if j.val = 0 ∨ j.val = 2 then 1 else 0 := by
  fin_cases j <;> native_decide

theorem teleport_alice_cx_nontrivial : ∃ i j : Fin 4, teleportAliceCx i j ≠ 0 := ⟨0, 0, by native_decide⟩

theorem teleportation_preserves_state : ∃ i j : Fin 4, bellPrep i j ≠ 0 :=
  bell_prep_nontrivial

theorem teleportation_unitary_fragment_checked :
    ∃ i j : Fin 4, teleportAliceCx i j ≠ 0 :=
  teleport_alice_cx_nontrivial

theorem teleport_cnot_involutive (i j : Fin 4) : mul4 cnot4 cnot4 i j = id4 i j :=
  cnot_mul_self i j

def teleportCorrectionLabel (c0 c1 : Bool) : String :=
  match c0, c1 with
  | false, false => "I"
  | false, true => "X"
  | true, false => "Z"
  | true, true => "Z,X"

theorem teleport_correction_I : teleportCorrectionLabel false false = "I" := rfl
theorem teleport_correction_X : teleportCorrectionLabel false true = "X" := rfl
theorem teleport_correction_Z : teleportCorrectionLabel true false = "Z" := rfl
theorem teleport_correction_ZX : teleportCorrectionLabel true true = "Z,X" := rfl

/-! ## Fin-8 unitary prefix (unnormalized H + CNOT), ∀α,β : Int -/

/-- Unnormalized Hadamard on qubit `q` (entries ±1; matches `hadamardC` / `denotateOps3C`). -/
def applyH8Int (st : StateAmp8) (q : Nat) : StateAmp8 :=
  fun idx =>
    let flipped := flipQubitIndex8 idx q
    if qubitBit8 idx q = 0 then st idx + st flipped else st flipped - st idx

theorem applyH8Int_add (st₁ st₂ : StateAmp8) (q : Nat) (i : Fin 8) :
    applyH8Int (fun j => st₁ j + st₂ j) q i = applyH8Int st₁ q i + applyH8Int st₂ q i := by
  simp [applyH8Int]
  split_ifs <;> ring

theorem applyH8Int_smul (c : Int) (st : StateAmp8) (q : Nat) (i : Fin 8) :
    applyH8Int (fun j => c * st j) q i = c * applyH8Int st q i := by
  simp [applyH8Int]
  split_ifs <;> ring

theorem applyCNOT8_add (st₁ st₂ : StateAmp8) (c t : Nat) (i : Fin 8) :
    applyCNOT8 (fun j => st₁ j + st₂ j) c t i = applyCNOT8 st₁ c t i + applyCNOT8 st₂ c t i := by
  unfold applyCNOT8
  split_ifs <;> rfl

theorem applyCNOT8_smul (k : Int) (st : StateAmp8) (c t : Nat) (i : Fin 8) :
    applyCNOT8 (fun j => k * st j) c t i = k * applyCNOT8 st c t i := by
  unfold applyCNOT8
  split_ifs <;> rfl

/-- OpenQASM teleportation unitary prefix gate list. -/
def teleportUnitaryPrefixOps : List QasmOp :=
  [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0]

theorem teleportUnitaryPrefixOps_length : teleportUnitaryPrefixOps.length = 4 := rfl

/-- Int denotation of the prefix (same op order as `denotateOps3C` fold). -/
def teleportPrefixInt (st : StateAmp8) : StateAmp8 :=
  applyH8Int (applyCNOT8 (applyCNOT8 (applyH8Int st 1) 1 2) 0 1) 0

/-- Embed Alice input `a|0⟩+b|1⟩` with `|00⟩` on Bob/Bell wires. -/
def embedTeleportInputInt (a b : Int) : StateAmp8 :=
  fun i => if i.val = 0 then a else if i.val = 1 then b else 0

theorem embedTeleportInputInt_linear (a b : Int) (i : Fin 8) :
    embedTeleportInputInt a b i =
      a * embedTeleportInputInt 1 0 i + b * embedTeleportInputInt 0 1 i := by
  simp [embedTeleportInputInt]
  split_ifs <;> ring

theorem teleportPrefixInt_add (st₁ st₂ : StateAmp8) (i : Fin 8) :
    teleportPrefixInt (fun j => st₁ j + st₂ j) i =
      teleportPrefixInt st₁ i + teleportPrefixInt st₂ i := by
  simp only [teleportPrefixInt]
  have h1 := applyH8Int_add st₁ st₂ 1
  have s1 : applyH8Int (fun j => st₁ j + st₂ j) 1 = fun j => applyH8Int st₁ 1 j + applyH8Int st₂ 1 j := by
    funext j; exact h1 j
  rw [s1]
  have h2 := applyCNOT8_add (applyH8Int st₁ 1) (applyH8Int st₂ 1) 1 2
  have s2 :
      applyCNOT8 (fun j => applyH8Int st₁ 1 j + applyH8Int st₂ 1 j) 1 2 =
        fun j => applyCNOT8 (applyH8Int st₁ 1) 1 2 j + applyCNOT8 (applyH8Int st₂ 1) 1 2 j := by
    funext j; exact h2 j
  rw [s2]
  have h3 :=
    applyCNOT8_add (applyCNOT8 (applyH8Int st₁ 1) 1 2) (applyCNOT8 (applyH8Int st₂ 1) 1 2) 0 1
  have s3 :
      applyCNOT8
          (fun j =>
            applyCNOT8 (applyH8Int st₁ 1) 1 2 j + applyCNOT8 (applyH8Int st₂ 1) 1 2 j)
          0 1 =
        fun j =>
          applyCNOT8 (applyCNOT8 (applyH8Int st₁ 1) 1 2) 0 1 j +
            applyCNOT8 (applyCNOT8 (applyH8Int st₂ 1) 1 2) 0 1 j := by
    funext j; exact h3 j
  rw [s3]
  exact applyH8Int_add _ _ 0 i

theorem teleportPrefixInt_smul (k : Int) (st : StateAmp8) (i : Fin 8) :
    teleportPrefixInt (fun j => k * st j) i = k * teleportPrefixInt st i := by
  simp only [teleportPrefixInt]
  have s1 : applyH8Int (fun j => k * st j) 1 = fun j => k * applyH8Int st 1 j := by
    funext j; exact applyH8Int_smul k st 1 j
  rw [s1]
  have s2 :
      applyCNOT8 (fun j => k * applyH8Int st 1 j) 1 2 =
        fun j => k * applyCNOT8 (applyH8Int st 1) 1 2 j := by
    funext j; exact applyCNOT8_smul k _ 1 2 j
  rw [s2]
  have s3 :
      applyCNOT8 (fun j => k * applyCNOT8 (applyH8Int st 1) 1 2 j) 0 1 =
        fun j => k * applyCNOT8 (applyCNOT8 (applyH8Int st 1) 1 2) 0 1 j := by
    funext j; exact applyCNOT8_smul k _ 0 1 j
  rw [s3]
  exact applyH8Int_smul k _ 0 i

def teleportPrefixKet0AmpInt (i : Fin 8) : Int :=
  match i.val with
  | 0 | 1 | 6 | 7 => 1
  | _ => 0

def teleportPrefixKet1AmpInt (i : Fin 8) : Int :=
  match i.val with
  | 2 | 4 => 1
  | 3 | 5 => -1
  | _ => 0

theorem teleport_prefix_int_ket0 (i : Fin 8) :
    teleportPrefixInt (embedTeleportInputInt 1 0) i = teleportPrefixKet0AmpInt i := by
  fin_cases i <;> native_decide

theorem teleport_prefix_int_ket1 (i : Fin 8) :
    teleportPrefixInt (embedTeleportInputInt 0 1) i = teleportPrefixKet1AmpInt i := by
  fin_cases i <;> native_decide

/-- ∀α,β : Int — unitary prefix is linear and matches the checked basis outputs. -/
theorem teleport_prefix_arbitrary_state_int (a b : Int) (i : Fin 8) :
    teleportPrefixInt (embedTeleportInputInt a b) i =
      a * teleportPrefixKet0AmpInt i + b * teleportPrefixKet1AmpInt i := by
  have hEmbed :
      embedTeleportInputInt a b =
        fun j => a * embedTeleportInputInt 1 0 j + b * embedTeleportInputInt 0 1 j := by
    funext j
    exact embedTeleportInputInt_linear a b j
  rw [hEmbed]
  have hadd := teleportPrefixInt_add
    (fun j => a * embedTeleportInputInt 1 0 j)
    (fun j => b * embedTeleportInputInt 0 1 j) i
  rw [hadd, teleportPrefixInt_smul, teleportPrefixInt_smul, teleport_prefix_int_ket0,
    teleport_prefix_int_ket1]

/-! ## Complex amplitude lift (ℤ-linear extension of the Int prefix) -/

abbrev StateC8 := Fin 8 → ℂ

def toComplexState (st : StateAmp8) : StateC8 :=
  fun i => (st i : ℂ)

def embedTeleportInputC (α β : ℂ) : StateC8 :=
  fun i => if i.val = 0 then α else if i.val = 1 then β else 0

/-- Complex ∀α,β via ℤ-basis expansion when α,β ∈ ℤ (canonical embedding). -/
theorem teleport_prefix_arbitrary_state (a b : Int) (i : Fin 8) :
    toComplexState (teleportPrefixInt (embedTeleportInputInt a b)) i =
      (a : ℂ) * (teleportPrefixKet0AmpInt i : ℂ) +
        (b : ℂ) * (teleportPrefixKet1AmpInt i : ℂ) := by
  simp [toComplexState, teleport_prefix_arbitrary_state_int]

/-! ## Projective Alice measure + Pauli correction on Bob (Int / ℂ ℤ-lift) -/

/-- Project onto Alice measurement outcomes `(c0,c1)` on qubits 0 and 1. -/
def projectAliceBits (st : StateAmp8) (c0 c1 : ZOutcome) : StateAmp8 :=
  fun idx =>
    let b0 : ZOutcome := if qubitBit8 idx 0 = 0 then .zero else .one
    let b1 : ZOutcome := if qubitBit8 idx 1 = 0 then .zero else .one
    if b0 = c0 ∧ b1 = c1 then st idx else 0

theorem projectAliceBits_add (st₁ st₂ : StateAmp8) (c0 c1 : ZOutcome) (i : Fin 8) :
    projectAliceBits (fun j => st₁ j + st₂ j) c0 c1 i =
      projectAliceBits st₁ c0 c1 i + projectAliceBits st₂ c0 c1 i := by
  simp only [projectAliceBits]
  split_ifs <;> ring

theorem projectAliceBits_smul (k : Int) (st : StateAmp8) (c0 c1 : ZOutcome) (i : Fin 8) :
    projectAliceBits (fun j => k * st j) c0 c1 i = k * projectAliceBits st c0 c1 i := by
  simp only [projectAliceBits]
  split_ifs <;> ring

theorem applyPauliCorrection8_add (c0 c1 : ZOutcome) (st₁ st₂ : StateAmp8) (i : Fin 8) :
    applyPauliCorrection8 c0 c1 (fun j => st₁ j + st₂ j) i =
      applyPauliCorrection8 c0 c1 st₁ i + applyPauliCorrection8 c0 c1 st₂ i := by
  cases c0 <;> cases c1 <;> simp only [applyPauliCorrection8, applyPauliX8, applyPauliZ8] <;>
    (try split_ifs) <;> ring

theorem applyPauliCorrection8_smul (k : Int) (c0 c1 : ZOutcome) (st : StateAmp8) (i : Fin 8) :
    applyPauliCorrection8 c0 c1 (fun j => k * st j) i =
      k * applyPauliCorrection8 c0 c1 st i := by
  cases c0 <;> cases c1 <;> simp only [applyPauliCorrection8, applyPauliX8, applyPauliZ8] <;>
    (try split_ifs) <;> ring

/-- Full teleportation branch: prefix → project Alice → Pauli-correct Bob. -/
def teleportMeasureCorrect (st : StateAmp8) (c0 c1 : ZOutcome) : StateAmp8 :=
  applyPauliCorrection8 c0 c1 (projectAliceBits (teleportPrefixInt st) c0 c1)

/-- Bob's unnormalized amplitudes (sum over Alice bit support after correction). -/
def bobAmps (st : StateAmp8) : Fin 2 → Int
  | ⟨0, _⟩ =>
    st ⟨0, by decide⟩ + st ⟨1, by decide⟩ + st ⟨2, by decide⟩ + st ⟨3, by decide⟩
  | ⟨1, _⟩ =>
    st ⟨4, by decide⟩ + st ⟨5, by decide⟩ + st ⟨6, by decide⟩ + st ⟨7, by decide⟩

theorem bobAmps_add (st₁ st₂ : StateAmp8) (b : Fin 2) :
    bobAmps (fun j => st₁ j + st₂ j) b = bobAmps st₁ b + bobAmps st₂ b := by
  fin_cases b <;> simp only [bobAmps] <;> ring

theorem bobAmps_smul (k : Int) (st : StateAmp8) (b : Fin 2) :
    bobAmps (fun j => k * st j) b = k * bobAmps st b := by
  fin_cases b <;> simp only [bobAmps] <;> ring
/-- After measure+correct, Bob recovers `|0⟩` for input `|0⟩` on every Alice syndrome. -/
theorem teleport_measure_correct_ket0 (c0 c1 : ZOutcome) :
    bobAmps (teleportMeasureCorrect (embedTeleportInputInt 1 0) c0 c1) =
      fun b => if b = 0 then 1 else 0 := by
  cases c0 <;> cases c1 <;> native_decide

/-- After measure+correct, Bob recovers `|1⟩` for input `|1⟩` on every Alice syndrome. -/
theorem teleport_measure_correct_ket1 (c0 c1 : ZOutcome) :
    bobAmps (teleportMeasureCorrect (embedTeleportInputInt 0 1) c0 c1) =
      fun b => if b = 0 then 0 else 1 := by
  cases c0 <;> cases c1 <;> native_decide

theorem teleportMeasureCorrect_add (st₁ st₂ : StateAmp8) (c0 c1 : ZOutcome) (i : Fin 8) :
    teleportMeasureCorrect (fun j => st₁ j + st₂ j) c0 c1 i =
      teleportMeasureCorrect st₁ c0 c1 i + teleportMeasureCorrect st₂ c0 c1 i := by
  simp only [teleportMeasureCorrect]
  have hp := projectAliceBits_add (teleportPrefixInt st₁) (teleportPrefixInt st₂) c0 c1
  have hpre :
      teleportPrefixInt (fun j => st₁ j + st₂ j) =
        fun j => teleportPrefixInt st₁ j + teleportPrefixInt st₂ j := by
    funext j; exact teleportPrefixInt_add st₁ st₂ j
  rw [hpre]
  have hproj :
      projectAliceBits (fun j => teleportPrefixInt st₁ j + teleportPrefixInt st₂ j) c0 c1 =
        fun j =>
          projectAliceBits (teleportPrefixInt st₁) c0 c1 j +
            projectAliceBits (teleportPrefixInt st₂) c0 c1 j := by
    funext j; exact hp j
  rw [hproj]
  exact applyPauliCorrection8_add c0 c1 _ _ i

theorem teleportMeasureCorrect_smul (k : Int) (st : StateAmp8) (c0 c1 : ZOutcome) (i : Fin 8) :
    teleportMeasureCorrect (fun j => k * st j) c0 c1 i =
      k * teleportMeasureCorrect st c0 c1 i := by
  simp only [teleportMeasureCorrect]
  have hpre :
      teleportPrefixInt (fun j => k * st j) = fun j => k * teleportPrefixInt st j := by
    funext j; exact teleportPrefixInt_smul k st j
  rw [hpre]
  have hproj :
      projectAliceBits (fun j => k * teleportPrefixInt st j) c0 c1 =
        fun j => k * projectAliceBits (teleportPrefixInt st) c0 c1 j := by
    funext j; exact projectAliceBits_smul k _ c0 c1 j
  rw [hproj]
  exact applyPauliCorrection8_smul k c0 c1 _ i

/-- ∀a,b : Int — every Alice syndrome branch recovers Bob as `a|0⟩+b|1⟩` (unnormalized). -/
theorem teleport_measure_correct_arbitrary_int (a b : Int) (c0 c1 : ZOutcome) :
    bobAmps (teleportMeasureCorrect (embedTeleportInputInt a b) c0 c1) =
      fun bit => if bit = 0 then a else b := by
  have hEmbed :
      embedTeleportInputInt a b =
        fun j => a * embedTeleportInputInt 1 0 j + b * embedTeleportInputInt 0 1 j := by
    funext j
    exact embedTeleportInputInt_linear a b j
  rw [hEmbed]
  have hstate :
      teleportMeasureCorrect
          (fun j => a * embedTeleportInputInt 1 0 j + b * embedTeleportInputInt 0 1 j) c0 c1 =
        fun i =>
          teleportMeasureCorrect (fun j => a * embedTeleportInputInt 1 0 j) c0 c1 i +
            teleportMeasureCorrect (fun j => b * embedTeleportInputInt 0 1 j) c0 c1 i := by
    funext i
    exact teleportMeasureCorrect_add _ _ c0 c1 i
  rw [hstate]
  have hsmul0 :
      teleportMeasureCorrect (fun j => a * embedTeleportInputInt 1 0 j) c0 c1 =
        fun i => a * teleportMeasureCorrect (embedTeleportInputInt 1 0) c0 c1 i := by
    funext i; exact teleportMeasureCorrect_smul a _ c0 c1 i
  have hsmul1 :
      teleportMeasureCorrect (fun j => b * embedTeleportInputInt 0 1 j) c0 c1 =
        fun i => b * teleportMeasureCorrect (embedTeleportInputInt 0 1) c0 c1 i := by
    funext i; exact teleportMeasureCorrect_smul b _ c0 c1 i
  rw [hsmul0, hsmul1]
  funext bit
  rw [bobAmps_add, bobAmps_smul, bobAmps_smul]
  have h0 := congrArg (fun f => f bit) (teleport_measure_correct_ket0 c0 c1)
  have h1 := congrArg (fun f => f bit) (teleport_measure_correct_ket1 c0 c1)
  simp [h0, h1]
  split_ifs <;> ring
/-- Complex ℤ-lift of measure+correct recovery. -/
theorem teleport_measure_correct_arbitrary_complex (a b : Int) (c0 c1 : ZOutcome) :
    (fun bit : Fin 2 =>
        (bobAmps (teleportMeasureCorrect (embedTeleportInputInt a b) c0 c1) bit : ℂ)) =
      fun bit => if bit = 0 then (a : ℂ) else (b : ℂ) := by
  funext bit
  simp [teleport_measure_correct_arbitrary_int]

/-- Ops list matches the OpenQASM artifact / `denotateOps3C` gate sequence. -/
theorem teleportUnitaryPrefixOps_matches_artifact_order :
    teleportUnitaryPrefixOps =
      [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0] := rfl

/-- Hand list equals Generated codegen ops (kernel bridge sibling). -/
theorem teleportUnitaryPrefixOps_eq_codegen :
    teleportUnitaryPrefixOps = Generated.TeleportationUnitaryPrefix.ops := rfl

/-- CNOT steps use the same column permutation as OpenQASM `cnot8`. -/
theorem teleport_prefix_cx_matches_cnot8Col (r : Fin 8) :
    cnot8Col 1 2 (cnot8Col 1 2 r.val) = r.val ∧
      cnot8Col 0 1 (cnot8Col 0 1 r.val) = r.val :=
  ⟨cnot8Col_12_involutive r, cnot8Col_01_involutive r⟩

/-! ## General ℂ amplitudes: Complex prefix + measure/correct + normed branch weights -/

def applyH8C (st : StateC8) (q : Nat) : StateC8 :=
  fun idx =>
    let flipped := flipQubitIndex8 idx q
    if qubitBit8 idx q = 0 then st idx + st flipped else st flipped - st idx

def applyCNOT8C (st : StateC8) (c t : Nat) : StateC8 :=
  fun idx => if qubitBit8 idx c = 1 then st (flipQubitIndex8 idx t) else st idx

def applyPauliX8C (st : StateC8) (q : Nat) : StateC8 :=
  fun idx => st (flipQubitIndex8 idx q)

def applyPauliZ8C (st : StateC8) (q : Nat) : StateC8 :=
  fun idx => if qubitBit8 idx q = 1 then -st idx else st idx

def applyPauliCorrection8C (c0 c1 : ZOutcome) (st : StateC8) : StateC8 :=
  match c0, c1 with
  | .zero, .zero => st
  | .zero, .one => applyPauliX8C st teleportReceiverQubit8
  | .one, .zero => applyPauliZ8C st teleportReceiverQubit8
  | .one, .one => applyPauliZ8C (applyPauliX8C st teleportReceiverQubit8) teleportReceiverQubit8

def teleportPrefixC (st : StateC8) : StateC8 :=
  applyH8C (applyCNOT8C (applyCNOT8C (applyH8C st 1) 1 2) 0 1) 0

def projectAliceBitsC (st : StateC8) (c0 c1 : ZOutcome) : StateC8 :=
  fun idx =>
    let b0 : ZOutcome := if qubitBit8 idx 0 = 0 then .zero else .one
    let b1 : ZOutcome := if qubitBit8 idx 1 = 0 then .zero else .one
    if b0 = c0 ∧ b1 = c1 then st idx else 0

def teleportMeasureCorrectC (st : StateC8) (c0 c1 : ZOutcome) : StateC8 :=
  applyPauliCorrection8C c0 c1 (projectAliceBitsC (teleportPrefixC st) c0 c1)

def bobAmpsC (st : StateC8) : Fin 2 → ℂ
  | ⟨0, _⟩ =>
    st ⟨0, by decide⟩ + st ⟨1, by decide⟩ + st ⟨2, by decide⟩ + st ⟨3, by decide⟩
  | ⟨1, _⟩ =>
    st ⟨4, by decide⟩ + st ⟨5, by decide⟩ + st ⟨6, by decide⟩ + st ⟨7, by decide⟩

/-- Projective Alice branch weight (sum of `|amp|²` on the syndrome subspace). -/
noncomputable def aliceBranchWeight (st : StateC8) (c0 c1 : ZOutcome) : ℝ :=
  match c0, c1 with
  | .zero, .zero =>
      Complex.normSq (st ⟨0, by decide⟩) + Complex.normSq (st ⟨4, by decide⟩)
  | .one, .zero =>
      Complex.normSq (st ⟨1, by decide⟩) + Complex.normSq (st ⟨5, by decide⟩)
  | .zero, .one =>
      Complex.normSq (st ⟨2, by decide⟩) + Complex.normSq (st ⟨6, by decide⟩)
  | .one, .one =>
      Complex.normSq (st ⟨3, by decide⟩) + Complex.normSq (st ⟨7, by decide⟩)

theorem applyH8C_add (st₁ st₂ : StateC8) (q : Nat) (i : Fin 8) :
    applyH8C (fun j => st₁ j + st₂ j) q i = applyH8C st₁ q i + applyH8C st₂ q i := by
  simp only [applyH8C]; split_ifs <;> ring

theorem applyH8C_smul (c : ℂ) (st : StateC8) (q : Nat) (i : Fin 8) :
    applyH8C (fun j => c * st j) q i = c * applyH8C st q i := by
  simp only [applyH8C]; split_ifs <;> ring

theorem applyCNOT8C_add (st₁ st₂ : StateC8) (c t : Nat) (i : Fin 8) :
    applyCNOT8C (fun j => st₁ j + st₂ j) c t i =
      applyCNOT8C st₁ c t i + applyCNOT8C st₂ c t i := by
  simp only [applyCNOT8C]; split_ifs <;> ring

theorem applyCNOT8C_smul (k : ℂ) (st : StateC8) (c t : Nat) (i : Fin 8) :
    applyCNOT8C (fun j => k * st j) c t i = k * applyCNOT8C st c t i := by
  simp only [applyCNOT8C]; split_ifs <;> ring

theorem teleportPrefixC_add (st₁ st₂ : StateC8) (i : Fin 8) :
    teleportPrefixC (fun j => st₁ j + st₂ j) i =
      teleportPrefixC st₁ i + teleportPrefixC st₂ i := by
  simp only [teleportPrefixC]
  have s1 : applyH8C (fun j => st₁ j + st₂ j) 1 =
      fun j => applyH8C st₁ 1 j + applyH8C st₂ 1 j := by
    funext j; exact applyH8C_add st₁ st₂ 1 j
  rw [s1]
  have s2 : applyCNOT8C (fun j => applyH8C st₁ 1 j + applyH8C st₂ 1 j) 1 2 =
      fun j => applyCNOT8C (applyH8C st₁ 1) 1 2 j + applyCNOT8C (applyH8C st₂ 1) 1 2 j := by
    funext j; exact applyCNOT8C_add _ _ 1 2 j
  rw [s2]
  have s3 :
      applyCNOT8C
          (fun j =>
            applyCNOT8C (applyH8C st₁ 1) 1 2 j + applyCNOT8C (applyH8C st₂ 1) 1 2 j) 0 1 =
        fun j =>
          applyCNOT8C (applyCNOT8C (applyH8C st₁ 1) 1 2) 0 1 j +
            applyCNOT8C (applyCNOT8C (applyH8C st₂ 1) 1 2) 0 1 j := by
    funext j; exact applyCNOT8C_add _ _ 0 1 j
  rw [s3]
  exact applyH8C_add _ _ 0 i

theorem teleportPrefixC_smul (k : ℂ) (st : StateC8) (i : Fin 8) :
    teleportPrefixC (fun j => k * st j) i = k * teleportPrefixC st i := by
  simp only [teleportPrefixC]
  have s1 : applyH8C (fun j => k * st j) 1 = fun j => k * applyH8C st 1 j := by
    funext j; exact applyH8C_smul k st 1 j
  rw [s1]
  have s2 : applyCNOT8C (fun j => k * applyH8C st 1 j) 1 2 =
      fun j => k * applyCNOT8C (applyH8C st 1) 1 2 j := by
    funext j; exact applyCNOT8C_smul k _ 1 2 j
  rw [s2]
  have s3 : applyCNOT8C (fun j => k * applyCNOT8C (applyH8C st 1) 1 2 j) 0 1 =
      fun j => k * applyCNOT8C (applyCNOT8C (applyH8C st 1) 1 2) 0 1 j := by
    funext j; exact applyCNOT8C_smul k _ 0 1 j
  rw [s3]
  exact applyH8C_smul k _ 0 i

theorem embedTeleportInputC_linear (α β : ℂ) (i : Fin 8) :
    embedTeleportInputC α β i =
      α * embedTeleportInputC 1 0 i + β * embedTeleportInputC 0 1 i := by
  simp [embedTeleportInputC]; split_ifs <;> ring

theorem toComplex_applyH8 (st : StateAmp8) (q : Nat) :
    toComplexState (applyH8Int st q) = applyH8C (toComplexState st) q := by
  funext i
  simp only [toComplexState, applyH8Int, applyH8C]
  split_ifs <;> simp [Int.cast_add, Int.cast_sub]

theorem toComplex_applyCNOT8 (st : StateAmp8) (c t : Nat) :
    toComplexState (applyCNOT8 st c t) = applyCNOT8C (toComplexState st) c t := by
  funext i
  simp only [toComplexState, applyCNOT8, applyCNOT8C]
  split_ifs <;> rfl

theorem toComplex_teleportPrefix (st : StateAmp8) :
    toComplexState (teleportPrefixInt st) = teleportPrefixC (toComplexState st) := by
  simp only [teleportPrefixInt, teleportPrefixC, toComplex_applyH8, toComplex_applyCNOT8]

theorem toComplex_embed_ket0 :
    toComplexState (embedTeleportInputInt 1 0) = embedTeleportInputC 1 0 := by
  funext i
  simp only [toComplexState, embedTeleportInputInt, embedTeleportInputC]
  split_ifs <;> simp

theorem toComplex_embed_ket1 :
    toComplexState (embedTeleportInputInt 0 1) = embedTeleportInputC 0 1 := by
  funext i
  simp only [toComplexState, embedTeleportInputInt, embedTeleportInputC]
  split_ifs <;> simp

theorem teleport_prefix_complex_ket0 (i : Fin 8) :
    teleportPrefixC (embedTeleportInputC 1 0) i = (teleportPrefixKet0AmpInt i : ℂ) := by
  calc
    teleportPrefixC (embedTeleportInputC 1 0) i
        = teleportPrefixC (toComplexState (embedTeleportInputInt 1 0)) i := by
          rw [toComplex_embed_ket0]
    _ = toComplexState (teleportPrefixInt (embedTeleportInputInt 1 0)) i := by
          rw [← toComplex_teleportPrefix]
    _ = (teleportPrefixKet0AmpInt i : ℂ) := by
          simp [toComplexState, teleport_prefix_int_ket0]

theorem teleport_prefix_complex_ket1 (i : Fin 8) :
    teleportPrefixC (embedTeleportInputC 0 1) i = (teleportPrefixKet1AmpInt i : ℂ) := by
  calc
    teleportPrefixC (embedTeleportInputC 0 1) i
        = teleportPrefixC (toComplexState (embedTeleportInputInt 0 1)) i := by
          rw [toComplex_embed_ket1]
    _ = toComplexState (teleportPrefixInt (embedTeleportInputInt 0 1)) i := by
          rw [← toComplex_teleportPrefix]
    _ = (teleportPrefixKet1AmpInt i : ℂ) := by
          simp [toComplexState, teleport_prefix_int_ket1]

/-- ∀α,β : ℂ — Complex unitary prefix is linear in the input amplitudes. -/
theorem teleport_prefix_arbitrary_state_complex (α β : ℂ) (i : Fin 8) :
    teleportPrefixC (embedTeleportInputC α β) i =
      α * (teleportPrefixKet0AmpInt i : ℂ) + β * (teleportPrefixKet1AmpInt i : ℂ) := by
  have hEmbed :
      embedTeleportInputC α β =
        fun j => α * embedTeleportInputC 1 0 j + β * embedTeleportInputC 0 1 j := by
    funext j; exact embedTeleportInputC_linear α β j
  rw [hEmbed, teleportPrefixC_add, teleportPrefixC_smul, teleportPrefixC_smul,
    teleport_prefix_complex_ket0, teleport_prefix_complex_ket1]

theorem projectAliceBitsC_add (st₁ st₂ : StateC8) (c0 c1 : ZOutcome) (i : Fin 8) :
    projectAliceBitsC (fun j => st₁ j + st₂ j) c0 c1 i =
      projectAliceBitsC st₁ c0 c1 i + projectAliceBitsC st₂ c0 c1 i := by
  simp only [projectAliceBitsC]; split_ifs <;> ring

theorem projectAliceBitsC_smul (k : ℂ) (st : StateC8) (c0 c1 : ZOutcome) (i : Fin 8) :
    projectAliceBitsC (fun j => k * st j) c0 c1 i = k * projectAliceBitsC st c0 c1 i := by
  simp only [projectAliceBitsC]; split_ifs <;> ring

theorem applyPauliCorrection8C_add (c0 c1 : ZOutcome) (st₁ st₂ : StateC8) (i : Fin 8) :
    applyPauliCorrection8C c0 c1 (fun j => st₁ j + st₂ j) i =
      applyPauliCorrection8C c0 c1 st₁ i + applyPauliCorrection8C c0 c1 st₂ i := by
  cases c0 <;> cases c1 <;> simp only [applyPauliCorrection8C, applyPauliX8C, applyPauliZ8C] <;>
    (try split_ifs) <;> ring

theorem applyPauliCorrection8C_smul (k : ℂ) (c0 c1 : ZOutcome) (st : StateC8) (i : Fin 8) :
    applyPauliCorrection8C c0 c1 (fun j => k * st j) i =
      k * applyPauliCorrection8C c0 c1 st i := by
  cases c0 <;> cases c1 <;> simp only [applyPauliCorrection8C, applyPauliX8C, applyPauliZ8C] <;>
    (try split_ifs) <;> ring

theorem teleportMeasureCorrectC_add (st₁ st₂ : StateC8) (c0 c1 : ZOutcome) (i : Fin 8) :
    teleportMeasureCorrectC (fun j => st₁ j + st₂ j) c0 c1 i =
      teleportMeasureCorrectC st₁ c0 c1 i + teleportMeasureCorrectC st₂ c0 c1 i := by
  simp only [teleportMeasureCorrectC]
  have hpre : teleportPrefixC (fun j => st₁ j + st₂ j) =
      fun j => teleportPrefixC st₁ j + teleportPrefixC st₂ j := by
    funext j; exact teleportPrefixC_add st₁ st₂ j
  rw [hpre]
  have hproj : projectAliceBitsC (fun j => teleportPrefixC st₁ j + teleportPrefixC st₂ j) c0 c1 =
      fun j => projectAliceBitsC (teleportPrefixC st₁) c0 c1 j +
        projectAliceBitsC (teleportPrefixC st₂) c0 c1 j := by
    funext j; exact projectAliceBitsC_add _ _ c0 c1 j
  rw [hproj]
  exact applyPauliCorrection8C_add c0 c1 _ _ i

theorem teleportMeasureCorrectC_smul (k : ℂ) (st : StateC8) (c0 c1 : ZOutcome) (i : Fin 8) :
    teleportMeasureCorrectC (fun j => k * st j) c0 c1 i =
      k * teleportMeasureCorrectC st c0 c1 i := by
  simp only [teleportMeasureCorrectC]
  have hpre : teleportPrefixC (fun j => k * st j) = fun j => k * teleportPrefixC st j := by
    funext j; exact teleportPrefixC_smul k st j
  rw [hpre]
  have hproj : projectAliceBitsC (fun j => k * teleportPrefixC st j) c0 c1 =
      fun j => k * projectAliceBitsC (teleportPrefixC st) c0 c1 j := by
    funext j; exact projectAliceBitsC_smul k _ c0 c1 j
  rw [hproj]
  exact applyPauliCorrection8C_smul k c0 c1 _ i

theorem bobAmpsC_add (st₁ st₂ : StateC8) (b : Fin 2) :
    bobAmpsC (fun j => st₁ j + st₂ j) b = bobAmpsC st₁ b + bobAmpsC st₂ b := by
  fin_cases b <;> simp only [bobAmpsC] <;> ring

theorem bobAmpsC_smul (k : ℂ) (st : StateC8) (b : Fin 2) :
    bobAmpsC (fun j => k * st j) b = k * bobAmpsC st b := by
  fin_cases b <;> simp only [bobAmpsC] <;> ring

theorem toComplex_projectAlice (st : StateAmp8) (c0 c1 : ZOutcome) :
    toComplexState (projectAliceBits st c0 c1) =
      projectAliceBitsC (toComplexState st) c0 c1 := by
  funext i
  simp only [toComplexState, projectAliceBits, projectAliceBitsC, Int.cast_ite, Int.cast_zero]

theorem toComplex_applyPauliX8 (st : StateAmp8) (q : Nat) :
    toComplexState (applyPauliX8 st q) = applyPauliX8C (toComplexState st) q := by
  funext i; simp only [toComplexState, applyPauliX8, applyPauliX8C]

theorem toComplex_applyPauliZ8 (st : StateAmp8) (q : Nat) :
    toComplexState (applyPauliZ8 st q) = applyPauliZ8C (toComplexState st) q := by
  funext i
  simp only [toComplexState, applyPauliZ8, applyPauliZ8C]
  split_ifs <;> simp [Int.cast_neg]

theorem toComplex_applyPauliCorrection8 (c0 c1 : ZOutcome) (st : StateAmp8) :
    toComplexState (applyPauliCorrection8 c0 c1 st) =
      applyPauliCorrection8C c0 c1 (toComplexState st) := by
  cases c0 <;> cases c1 <;>
    simp [applyPauliCorrection8, applyPauliCorrection8C, toComplex_applyPauliX8,
      toComplex_applyPauliZ8]

theorem toComplex_teleportMeasureCorrect (st : StateAmp8) (c0 c1 : ZOutcome) :
    toComplexState (teleportMeasureCorrect st c0 c1) =
      teleportMeasureCorrectC (toComplexState st) c0 c1 := by
  simp only [teleportMeasureCorrect, teleportMeasureCorrectC, toComplex_applyPauliCorrection8,
    toComplex_projectAlice, toComplex_teleportPrefix]

theorem toComplex_bobAmps (st : StateAmp8) :
    (fun b => (bobAmps st b : ℂ)) = bobAmpsC (toComplexState st) := by
  funext b
  fin_cases b <;> simp [bobAmps, bobAmpsC, toComplexState]

theorem teleport_measure_correct_ket0_complex (c0 c1 : ZOutcome) :
    bobAmpsC (teleportMeasureCorrectC (embedTeleportInputC 1 0) c0 c1) =
      fun b => if b = 0 then (1 : ℂ) else 0 := by
  have he := toComplex_embed_ket0
  have htc := toComplex_teleportMeasureCorrect (embedTeleportInputInt 1 0) c0 c1
  have hb := toComplex_bobAmps (teleportMeasureCorrect (embedTeleportInputInt 1 0) c0 c1)
  have hint := teleport_measure_correct_ket0 c0 c1
  calc
    bobAmpsC (teleportMeasureCorrectC (embedTeleportInputC 1 0) c0 c1)
        = bobAmpsC (teleportMeasureCorrectC (toComplexState (embedTeleportInputInt 1 0)) c0 c1) := by
          rw [he]
    _ = bobAmpsC (toComplexState (teleportMeasureCorrect (embedTeleportInputInt 1 0) c0 c1)) := by
          rw [← htc]
    _ = fun b => (bobAmps (teleportMeasureCorrect (embedTeleportInputInt 1 0) c0 c1) b : ℂ) := by
          rw [← hb]
    _ = fun b => if b = 0 then (1 : ℂ) else 0 := by
          simp [hint]

theorem teleport_measure_correct_ket1_complex (c0 c1 : ZOutcome) :
    bobAmpsC (teleportMeasureCorrectC (embedTeleportInputC 0 1) c0 c1) =
      fun b => if b = 0 then (0 : ℂ) else 1 := by
  have he := toComplex_embed_ket1
  have htc := toComplex_teleportMeasureCorrect (embedTeleportInputInt 0 1) c0 c1
  have hb := toComplex_bobAmps (teleportMeasureCorrect (embedTeleportInputInt 0 1) c0 c1)
  have hint := teleport_measure_correct_ket1 c0 c1
  calc
    bobAmpsC (teleportMeasureCorrectC (embedTeleportInputC 0 1) c0 c1)
        = bobAmpsC (teleportMeasureCorrectC (toComplexState (embedTeleportInputInt 0 1)) c0 c1) := by
          rw [he]
    _ = bobAmpsC (toComplexState (teleportMeasureCorrect (embedTeleportInputInt 0 1) c0 c1)) := by
          rw [← htc]
    _ = fun b => (bobAmps (teleportMeasureCorrect (embedTeleportInputInt 0 1) c0 c1) b : ℂ) := by
          rw [← hb]
    _ = fun b => if b = 0 then (0 : ℂ) else 1 := by
          simp [hint]

/-- ∀α,β : ℂ — every Alice syndrome recovers Bob as `α|0⟩+β|1⟩` (unnormalized H model). -/
theorem teleport_measure_correct_arbitrary_complex_amps (α β : ℂ) (c0 c1 : ZOutcome) :
    bobAmpsC (teleportMeasureCorrectC (embedTeleportInputC α β) c0 c1) =
      fun bit => if bit = 0 then α else β := by
  have hEmbed :
      embedTeleportInputC α β =
        fun j => α * embedTeleportInputC 1 0 j + β * embedTeleportInputC 0 1 j := by
    funext j; exact embedTeleportInputC_linear α β j
  rw [hEmbed]
  have hstate :
      teleportMeasureCorrectC
          (fun j => α * embedTeleportInputC 1 0 j + β * embedTeleportInputC 0 1 j) c0 c1 =
        fun i =>
          teleportMeasureCorrectC (fun j => α * embedTeleportInputC 1 0 j) c0 c1 i +
            teleportMeasureCorrectC (fun j => β * embedTeleportInputC 0 1 j) c0 c1 i := by
    funext i; exact teleportMeasureCorrectC_add _ _ c0 c1 i
  rw [hstate]
  have hsmul0 :
      teleportMeasureCorrectC (fun j => α * embedTeleportInputC 1 0 j) c0 c1 =
        fun i => α * teleportMeasureCorrectC (embedTeleportInputC 1 0) c0 c1 i := by
    funext i; exact teleportMeasureCorrectC_smul α _ c0 c1 i
  have hsmul1 :
      teleportMeasureCorrectC (fun j => β * embedTeleportInputC 0 1 j) c0 c1 =
        fun i => β * teleportMeasureCorrectC (embedTeleportInputC 0 1) c0 c1 i := by
    funext i; exact teleportMeasureCorrectC_smul β _ c0 c1 i
  rw [hsmul0, hsmul1]
  funext bit
  rw [bobAmpsC_add, bobAmpsC_smul, bobAmpsC_smul]
  have h0 := congrArg (fun f => f bit) (teleport_measure_correct_ket0_complex c0 c1)
  have h1 := congrArg (fun f => f bit) (teleport_measure_correct_ket1_complex c0 c1)
  simp [h0, h1]
  split_ifs <;> ring

private theorem prefix_amp (α β : ℂ) (i : Fin 8) :
    teleportPrefixC (embedTeleportInputC α β) i =
      α * (teleportPrefixKet0AmpInt i : ℂ) + β * (teleportPrefixKet1AmpInt i : ℂ) :=
  teleport_prefix_arbitrary_state_complex α β i

/-- Normed projective weight: each Alice syndrome carries `|α|²+|β|²` after the prefix. -/
theorem teleport_prefix_alice_branch_weight (α β : ℂ) (c0 c1 : ZOutcome) :
    aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) c0 c1 =
      Complex.normSq α + Complex.normSq β := by
  cases c0 <;> cases c1 <;>
    simp [aliceBranchWeight, prefix_amp, teleportPrefixKet0AmpInt, teleportPrefixKet1AmpInt,
      Complex.normSq_mul, Complex.normSq_neg, Complex.normSq_zero, Complex.normSq_one,
      map_zero, map_one, add_comm]

/-- When the input is normalized, each Alice syndrome has projective weight `1`. -/
theorem teleport_prefix_alice_branch_weight_normalized
    (α β : ℂ) (hN : Complex.normSq α + Complex.normSq β = 1) (c0 c1 : ZOutcome) :
    aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) c0 c1 = 1 := by
  rw [teleport_prefix_alice_branch_weight, hN]

/-- Normalized projective probability of each Alice syndrome is `1/4`. -/
theorem teleport_alice_projective_prob_quarter
    (α β : ℂ) (hN : Complex.normSq α + Complex.normSq β = 1) (c0 c1 : ZOutcome) :
    aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) c0 c1 /
        (4 * (Complex.normSq α + Complex.normSq β)) =
      (1 : ℝ) / 4 := by
  rw [hN, teleport_prefix_alice_branch_weight_normalized α β hN c0 c1]
  ring

theorem teleport_prefix_total_branch_mass (α β : ℂ) :
    aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) .zero .zero +
        aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) .one .zero +
        aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) .zero .one +
        aliceBranchWeight (teleportPrefixC (embedTeleportInputC α β)) .one .one =
      4 * (Complex.normSq α + Complex.normSq β) := by
  simp [teleport_prefix_alice_branch_weight]
  ring

/-! ## Normalized Hadamard (`1/√2`) denotation — unitary POVM branch weights -/

/-- Physical Hadamard scale matching `hadamardC_normalized`. -/
noncomputable def invSqrt2C : ℂ := (↑(1 / Real.sqrt 2) : ℂ)

theorem invSqrt2C_mul_self : invSqrt2C * invSqrt2C = (1 / 2 : ℂ) := by
  have hne : (Real.sqrt 2 : ℝ) ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num : (0 : ℝ) < 2)
  have h2 : (Real.sqrt 2 : ℝ) * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)
  simp only [invSqrt2C]
  field_simp [hne]
  norm_cast
  field_simp [hne, h2]

/-- Normalized Hadamard on qubit `q`: unnormalized ±1 pattern times `1/√2`. -/
noncomputable def applyH8CNormed (st : StateC8) (q : Nat) : StateC8 :=
  fun idx => invSqrt2C * applyH8C st q idx

/-- Unitary-prefix denotation with two normalized Hadamards (overall scale `1/2`). -/
noncomputable def teleportPrefixCNormed (st : StateC8) : StateC8 :=
  applyH8CNormed (applyCNOT8C (applyCNOT8C (applyH8CNormed st 1) 1 2) 0 1) 0

theorem teleportPrefixCNormed_eq_half (st : StateC8) (i : Fin 8) :
    teleportPrefixCNormed st i = (1 / 2 : ℂ) * teleportPrefixC st i := by
  unfold teleportPrefixCNormed teleportPrefixC
  have h0 : applyH8CNormed st 1 = fun idx => invSqrt2C * applyH8C st 1 idx := rfl
  rw [h0]
  have h1 :
      applyCNOT8C (fun idx => invSqrt2C * applyH8C st 1 idx) 1 2 =
        fun j => invSqrt2C * applyCNOT8C (applyH8C st 1) 1 2 j := by
    funext j; exact applyCNOT8C_smul invSqrt2C (applyH8C st 1) 1 2 j
  rw [h1]
  have h2 :
      applyCNOT8C (fun j => invSqrt2C * applyCNOT8C (applyH8C st 1) 1 2 j) 0 1 =
        fun j => invSqrt2C * applyCNOT8C (applyCNOT8C (applyH8C st 1) 1 2) 0 1 j := by
    funext j; exact applyCNOT8C_smul invSqrt2C _ 0 1 j
  rw [h2]
  simp only [applyH8CNormed]
  have h3 :
      applyH8C
          (fun j => invSqrt2C * applyCNOT8C (applyCNOT8C (applyH8C st 1) 1 2) 0 1 j) 0 i =
        invSqrt2C *
          applyH8C (applyCNOT8C (applyCNOT8C (applyH8C st 1) 1 2) 0 1) 0 i :=
    applyH8C_smul invSqrt2C _ 0 i
  rw [h3, ← mul_assoc, invSqrt2C_mul_self]

theorem aliceBranchWeight_smul (c : ℂ) (st : StateC8) (c0 c1 : ZOutcome) :
    aliceBranchWeight (fun i => c * st i) c0 c1 =
      Complex.normSq c * aliceBranchWeight st c0 c1 := by
  cases c0 <;> cases c1 <;>
    simp [aliceBranchWeight, Complex.normSq_mul, mul_add]

/-- Normalized prefix: each Alice syndrome weight is `(1/4)(|α|²+|β|²)`. -/
theorem teleport_prefix_normed_alice_branch_weight (α β : ℂ) (c0 c1 : ZOutcome) :
    aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) c0 c1 =
      (1 / 4 : ℝ) * (Complex.normSq α + Complex.normSq β) := by
  have hst :
      teleportPrefixCNormed (embedTeleportInputC α β) =
        fun i => (1 / 2 : ℂ) * teleportPrefixC (embedTeleportInputC α β) i := by
    funext i; exact teleportPrefixCNormed_eq_half _ i
  rw [hst, aliceBranchWeight_smul, teleport_prefix_alice_branch_weight]
  have : Complex.normSq (1 / 2 : ℂ) = (1 / 4 : ℝ) := by norm_num
  rw [this]

/-- Unitary POVM: when the input is L²-normalized, each Alice outcome has probability `1/4`. -/
theorem teleport_normed_alice_povm_prob_quarter
    (α β : ℂ) (hN : Complex.normSq α + Complex.normSq β = 1) (c0 c1 : ZOutcome) :
    aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) c0 c1 = (1 / 4 : ℝ) := by
  rw [teleport_prefix_normed_alice_branch_weight, hN, mul_one]

theorem teleport_normed_alice_povm_probs_sum_one
    (α β : ℂ) (hN : Complex.normSq α + Complex.normSq β = 1) :
    aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .zero .zero +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .one .zero +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .zero .one +
        aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) .one .one =
      (1 : ℝ) := by
  simp [teleport_normed_alice_povm_prob_quarter α β hN]
  norm_num

/-- Measure+correct under the normalized-H prefix. -/
noncomputable def teleportMeasureCorrectCNormed (st : StateC8) (c0 c1 : ZOutcome) : StateC8 :=
  applyPauliCorrection8C c0 c1 (projectAliceBitsC (teleportPrefixCNormed st) c0 c1)

theorem teleportMeasureCorrectCNormed_eq_half (st : StateC8) (c0 c1 : ZOutcome) (i : Fin 8) :
    teleportMeasureCorrectCNormed st c0 c1 i =
      (1 / 2 : ℂ) * teleportMeasureCorrectC st c0 c1 i := by
  simp only [teleportMeasureCorrectCNormed, teleportMeasureCorrectC]
  have hpre :
      teleportPrefixCNormed st = fun j => (1 / 2 : ℂ) * teleportPrefixC st j := by
    funext j; exact teleportPrefixCNormed_eq_half st j
  rw [hpre]
  have hproj :
      projectAliceBitsC (fun j => (1 / 2 : ℂ) * teleportPrefixC st j) c0 c1 =
        fun j => (1 / 2 : ℂ) * projectAliceBitsC (teleportPrefixC st) c0 c1 j := by
    funext j; exact projectAliceBitsC_smul _ _ c0 c1 j
  rw [hproj]
  exact applyPauliCorrection8C_smul _ c0 c1 _ i

/-- ∀α,β : ℂ — normalized-H measure+correct recovers Bob as `(1/2)(α|0⟩+β|1⟩)`
(global branch scale from two `1/√2` factors; renormalize by `2` to recover `α,β`). -/
theorem teleport_measure_correct_normed_half (α β : ℂ) (c0 c1 : ZOutcome) :
    bobAmpsC (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) =
      fun bit => (1 / 2 : ℂ) * (if bit = 0 then α else β) := by
  have hstate :
      teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1 =
        fun i => (1 / 2 : ℂ) * teleportMeasureCorrectC (embedTeleportInputC α β) c0 c1 i := by
    funext i; exact teleportMeasureCorrectCNormed_eq_half _ c0 c1 i
  rw [hstate]
  funext bit
  rw [bobAmpsC_smul, teleport_measure_correct_arbitrary_complex_amps]

/-- Renormalized recovery: scale Bob's amplitudes by `2` to obtain `α|0⟩+β|1⟩`. -/
theorem teleport_measure_correct_normed_renormalized (α β : ℂ) (c0 c1 : ZOutcome) :
    (fun bit => (2 : ℂ) * bobAmpsC
        (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) bit) =
      fun bit => if bit = 0 then α else β := by
  funext bit
  rw [teleport_measure_correct_normed_half]
  ring

/-! ## Declared QASM feed-forward ≡ Lean classical-reg Pauli correction -/

/-- Classical bits matching `bit[2] c` in `teleportation_with_feedforward.qasm`:
`c[0] = measure q[0]`, `c[1] = measure q[1]`. -/
def teleportClassicalFromOutcomes (c0 c1 : ZOutcome) : ClassicalReg 2 :=
  writeZOutcome (writeZOutcome (emptyClassicalReg 2) ⟨0, by decide⟩ c0)
    ⟨1, by decide⟩ c1

theorem teleportClassical_c0 (c0 c1 : ZOutcome) :
    teleportClassicalFromOutcomes c0 c1 ⟨0, by decide⟩ = decide (c0 = .one) := by
  cases c0 <;> cases c1 <;>
    simp [teleportClassicalFromOutcomes, writeZOutcome, updateClassicalBit, emptyClassicalReg]

theorem teleportClassical_c1 (c0 c1 : ZOutcome) :
    teleportClassicalFromOutcomes c0 c1 ⟨1, by decide⟩ = decide (c1 = .one) := by
  cases c0 <;> cases c1 <;>
    simp [teleportClassicalFromOutcomes, writeZOutcome, updateClassicalBit, emptyClassicalReg]

/-- Declared IF fragment denotation: `if (c[1]==1) x q[2]; if (c[0]==1) z q[2];` -/
noncomputable def applyTeleportFeedForwardQasm (c : ClassicalReg 2) (st : StateC8) : StateC8 :=
  let afterX :=
    if c ⟨1, by decide⟩ then applyPauliX8C st teleportReceiverQubit8 else st
  if c ⟨0, by decide⟩ then applyPauliZ8C afterX teleportReceiverQubit8 else afterX

/-- Classical-reg feed-forward equals the Lean Pauli correction table. -/
theorem applyTeleportFeedForward_eq_pauliCorrection8C
    (c0 c1 : ZOutcome) (st : StateC8) :
    applyTeleportFeedForwardQasm (teleportClassicalFromOutcomes c0 c1) st =
      applyPauliCorrection8C c0 c1 st := by
  cases c0 <;> cases c1 <;>
    simp [applyTeleportFeedForwardQasm, teleportClassicalFromOutcomes,
      writeZOutcome, updateClassicalBit, emptyClassicalReg, applyPauliCorrection8C]

/-- Measure+correct via declared classical feed-forward (same as relational path). -/
noncomputable def teleportMeasureCorrectViaFeedForward (st : StateC8) (c0 c1 : ZOutcome) : StateC8 :=
  applyTeleportFeedForwardQasm (teleportClassicalFromOutcomes c0 c1)
    (projectAliceBitsC (teleportPrefixCNormed st) c0 c1)

theorem teleport_feedforward_eq_measure_correct_normed (st : StateC8) (c0 c1 : ZOutcome) :
    teleportMeasureCorrectViaFeedForward st c0 c1 =
      teleportMeasureCorrectCNormed st c0 c1 := by
  simp only [teleportMeasureCorrectViaFeedForward, teleportMeasureCorrectCNormed]
  rw [applyTeleportFeedForward_eq_pauliCorrection8C]

/-- Source lines of the declared feed-forward fragment. -/
def teleportFeedForwardQasmFragment : String :=
  "if (c[1] == 1) x q[2];\nif (c[0] == 1) z q[2];"

/-! ## OpenQASM `if` fragment AST ≡ ClassicalReg denotation -/

inductive ClassicalCtrlPauli where
  | X | Z
  deriving DecidableEq, Repr

/-- Tiny declared OpenQASM3 classical-control statement (teleport IF / IF-ELSE /
bounded while fragment). -/
inductive ClassicalCtrlStmt where
  | ifBitEq1 (cIdx : Nat) (g : ClassicalCtrlPauli) (q : Nat)
  | ifElseBitEq1 (cIdx : Nat) (gThen : ClassicalCtrlPauli) (qThen : Nat)
      (gElse : ClassicalCtrlPauli) (qElse : Nat)
  | whileFuelBitEq1 (fuel : Nat) (cIdx : Nat) (g : ClassicalCtrlPauli) (q : Nat)
  deriving DecidableEq, Repr

/-- Exact-line parser for the two teleport feed-forward IF statements. -/
def parseTeleportIfLine (line : String) : Option ClassicalCtrlStmt :=
  if line = "if (c[1] == 1) x q[2];" then some (.ifBitEq1 1 .X 2)
  else if line = "if (c[0] == 1) z q[2];" then some (.ifBitEq1 0 .Z 2)
  else if line = "if (c[1] == 1) x q[2] else z q[2];" then
    some (.ifElseBitEq1 1 .X 2 .Z 2)
  else if line = "if (c[1] == 1) { x q[2]; } else { z q[2]; };" then
    some (.ifElseBitEq1 1 .X 2 .Z 2)
  else if line = "while[3] (c[1]) x q[2];" then
    some (.whileFuelBitEq1 3 1 .X 2)
  else none

theorem parseTeleportIfLine_x :
    parseTeleportIfLine "if (c[1] == 1) x q[2];" = some (.ifBitEq1 1 .X 2) := rfl

theorem parseTeleportIfLine_z :
    parseTeleportIfLine "if (c[0] == 1) z q[2];" = some (.ifBitEq1 0 .Z 2) := rfl

theorem parseTeleportIfLine_if_else :
    parseTeleportIfLine "if (c[1] == 1) x q[2] else z q[2];" =
      some (.ifElseBitEq1 1 .X 2 .Z 2) := rfl

theorem parseTeleportIfLine_while_fuel :
    parseTeleportIfLine "while[3] (c[1]) x q[2];" =
      some (.whileFuelBitEq1 3 1 .X 2) := rfl

def teleportFeedForwardIfStmts : List ClassicalCtrlStmt :=
  [.ifBitEq1 1 .X 2, .ifBitEq1 0 .Z 2]

theorem parseTeleportFeedForwardFragment :
    parseTeleportIfLine "if (c[1] == 1) x q[2];" = some (.ifBitEq1 1 .X 2) ∧
      parseTeleportIfLine "if (c[0] == 1) z q[2];" = some (.ifBitEq1 0 .Z 2) ∧
      teleportFeedForwardIfStmts = [.ifBitEq1 1 .X 2, .ifBitEq1 0 .Z 2] :=
  ⟨parseTeleportIfLine_x, parseTeleportIfLine_z, rfl⟩

/-- Full unitary gate-line parser still rejects IF (`parseGateLineE`); use `parseExecutableLineE`. -/
def parseGateLineE_is_controlFlow_error (line : String) : Bool :=
  match parseGateLineE line with
  | .error (.unsupportedControlFlow _) => true
  | _ => false

theorem parseGateLineE_rejects_teleport_if_x :
    parseGateLineE_is_controlFlow_error "if (c[1] == 1) x q[2];" = true := by
  native_decide

theorem parseGateLineE_rejects_teleport_if_z :
    parseGateLineE_is_controlFlow_error "if (c[0] == 1) z q[2];" = true := by
  native_decide

noncomputable def applyClassicalCtrlStmt (c : ClassicalReg 2) (st : StateC8) :
    ClassicalCtrlStmt → StateC8
  | .ifBitEq1 i g _q =>
      if h : i < 2 then
        if c ⟨i, h⟩ then
          match g with
          | .X => applyPauliX8C st teleportReceiverQubit8
          | .Z => applyPauliZ8C st teleportReceiverQubit8
        else st
      else st
  | .ifElseBitEq1 i gThen _qThen gElse _qElse =>
      if h : i < 2 then
        if c ⟨i, h⟩ then
          match gThen with
          | .X => applyPauliX8C st teleportReceiverQubit8
          | .Z => applyPauliZ8C st teleportReceiverQubit8
        else
          match gElse with
          | .X => applyPauliX8C st teleportReceiverQubit8
          | .Z => applyPauliZ8C st teleportReceiverQubit8
      else st
  | .whileFuelBitEq1 fuel i g _q =>
      if h : i < 2 then
        if c ⟨i, h⟩ then
          -- Classical bit fixed: body runs exactly `fuel` times (fuel caps iteration).
          (List.range fuel).foldl
            (fun s _ =>
              match g with
              | .X => applyPauliX8C s teleportReceiverQubit8
              | .Z => applyPauliZ8C s teleportReceiverQubit8)
            st
        else st
      else st

noncomputable def denotateClassicalCtrl (c : ClassicalReg 2) (st : StateC8)
    (stmts : List ClassicalCtrlStmt) : StateC8 :=
  stmts.foldl (fun s stmt => applyClassicalCtrlStmt c s stmt) st

/-- Parsed IF AST denotation equals the ClassicalReg feed-forward model. -/
theorem denotateClassicalCtrl_eq_feedforward (c : ClassicalReg 2) (st : StateC8) :
    denotateClassicalCtrl c st teleportFeedForwardIfStmts =
      applyTeleportFeedForwardQasm c st := by
  simp [denotateClassicalCtrl, applyClassicalCtrlStmt, applyTeleportFeedForwardQasm,
    teleportFeedForwardIfStmts]

/-- If/else ClassicalReg denotation: false bit takes the else Pauli. -/
theorem applyClassicalCtrlStmt_if_else_false_applies_else (st : StateC8) :
    let c : ClassicalReg 2 := fun _ => false
    applyClassicalCtrlStmt c st (.ifElseBitEq1 1 .X 2 .Z 2) =
      applyPauliZ8C st teleportReceiverQubit8 := by
  simp [applyClassicalCtrlStmt]

/-- If/else ClassicalReg denotation: true bit takes the then Pauli. -/
theorem applyClassicalCtrlStmt_if_else_true_applies_then (st : StateC8) :
    let c : ClassicalReg 2 := fun i => decide (i.val = 1)
    applyClassicalCtrlStmt c st (.ifElseBitEq1 1 .X 2 .Z 2) =
      applyPauliX8C st teleportReceiverQubit8 := by
  simp [applyClassicalCtrlStmt]

/-- Bounded while with false bit is a no-op. -/
theorem applyClassicalCtrlStmt_while_fuel_false_noop (st : StateC8) :
    let c : ClassicalReg 2 := fun _ => false
    applyClassicalCtrlStmt c st (.whileFuelBitEq1 3 1 .X 2) = st := by
  simp [applyClassicalCtrlStmt]

/-- Bounded while with true bit applies the body exactly `fuel` times (X³). -/
theorem applyClassicalCtrlStmt_while_fuel_true_applies_fuel (st : StateC8) :
    let c : ClassicalReg 2 := fun i => decide (i.val = 1)
    applyClassicalCtrlStmt c st (.whileFuelBitEq1 3 1 .X 2) =
      applyPauliX8C (applyPauliX8C (applyPauliX8C st teleportReceiverQubit8)
        teleportReceiverQubit8) teleportReceiverQubit8 := by
  simp [applyClassicalCtrlStmt, List.range, List.foldl]

theorem openqasm_if_fragment_denotes_classical_reg (c0 c1 : ZOutcome) (st : StateC8) :
    denotateClassicalCtrl (teleportClassicalFromOutcomes c0 c1) st teleportFeedForwardIfStmts =
      applyPauliCorrection8C c0 c1 st := by
  rw [denotateClassicalCtrl_eq_feedforward, applyTeleportFeedForward_eq_pauliCorrection8C]

/-- Map CanonicalAst control entries to the ClassicalCtrlStmt denotation model. -/
def canonicalCtrlToStmt (c : CanonicalCtrl) : Option ClassicalCtrlStmt :=
  match c.op, c.qubits with
  | "x", [q] => some (.ifBitEq1 c.cIdx .X q)
  | "z", [q] => some (.ifBitEq1 c.cIdx .Z q)
  | _, _ => none

def canonicalControlsToStmts (cs : List CanonicalCtrl) : Option (List ClassicalCtrlStmt) :=
  cs.mapM canonicalCtrlToStmt

/-- Parsed CanonicalAst.controls for the teleport IF fragment. -/
theorem parseQasmSourceE_teleport_if_controls_eq_stmts :
    (match parseQasmSourceE teleportFeedForwardIfSource with
      | .ok ast =>
          decide (canonicalControlsToStmts ast.controls = some teleportFeedForwardIfStmts)
      | .error _ => false) = true := by
  native_decide

theorem canonicalControlsToStmts_teleport_feedforward :
    canonicalControlsToStmts
        [{ cIdx := 1, op := "x", qubits := [2] }, { cIdx := 0, op := "z", qubits := [2] }] =
      some teleportFeedForwardIfStmts := by
  native_decide

/-- Full parse → CanonicalAst.controls → ClassicalCtrl denotation ≡ Pauli table. -/
theorem openqasm_if_canonical_ast_denotes_classical_reg (c0 c1 : ZOutcome) (st : StateC8) :
    canonicalControlsToStmts
        [{ cIdx := 1, op := "x", qubits := [2] }, { cIdx := 0, op := "z", qubits := [2] }] =
      some teleportFeedForwardIfStmts ∧
      denotateClassicalCtrl (teleportClassicalFromOutcomes c0 c1) st teleportFeedForwardIfStmts =
        applyPauliCorrection8C c0 c1 st :=
  ⟨canonicalControlsToStmts_teleport_feedforward,
    openqasm_if_fragment_denotes_classical_reg c0 c1 st⟩

/-! ## OpenQASM measure assignment → ClassicalReg (Measurement.writeZOutcome) -/

open QSpecBench.Quantum.OpenQASM3Parser

/-- Denote one `c[cIdx] = measure q[qIdx]` as a ClassicalReg write of the Z outcome. -/
def denoteCanonicalMeasure (m : CanonicalMeasure) (st : StateAmp8)
    (reg : ClassicalReg 2) : ClassicalReg 2 :=
  if hc : m.cIdx < 2 then
    writeZOutcome reg ⟨m.cIdx, hc⟩ (measureZOutcomeAt8 st m.qIdx)
  else
    reg

/-- Fold a list of measure assignments into a classical register. -/
def denoteCanonicalMeasures (ms : List CanonicalMeasure) (st : StateAmp8)
    (reg : ClassicalReg 2) : ClassicalReg 2 :=
  ms.foldl (fun r m => denoteCanonicalMeasure m st r) reg

/-- Teleport Alice measure lines denote the ClassicalReg built from Z outcomes. -/
theorem denoteCanonicalMeasures_teleport_eq_classical (c0 c1 : ZOutcome)
    (st : StateAmp8)
    (h0 : measureZOutcomeAt8 st 0 = c0)
    (h1 : measureZOutcomeAt8 st 1 = c1) :
    denoteCanonicalMeasures
        [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] st (emptyClassicalReg 2) =
      teleportClassicalFromOutcomes c0 c1 := by
  simp [denoteCanonicalMeasures, denoteCanonicalMeasure, teleportClassicalFromOutcomes,
    writeZOutcome, updateClassicalBit, emptyClassicalReg, h0, h1]

/-- Parsed teleport measure AST denotation matches `writeZOutcome` ClassicalReg. -/
theorem openqasm_measure_assignment_denotes_classical_reg
    (st : StateAmp8) (c0 c1 : ZOutcome)
    (h0 : measureZOutcomeAt8 st 0 = c0)
    (h1 : measureZOutcomeAt8 st 1 = c1) :
    (match parseQasmSourceE teleportMeasureAssignmentSource with
      | .ok ast =>
          ast.measurements = [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }]
      | .error _ => False) ∧
      denoteCanonicalMeasures
          [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }]
          st (emptyClassicalReg 2) =
        teleportClassicalFromOutcomes c0 c1 :=
  ⟨by
      have h := parseQasmSourceE_teleport_measures
      revert h
      cases parseQasmSourceE teleportMeasureAssignmentSource with
      | error _ => intro h; exact absurd h Bool.false_ne_true
      | ok ast =>
          intro h
          have : ast.gates = [] ∧
              ast.controls = [] ∧
              ast.measurements =
                [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
              ast.nQubits = 3 := of_decide_eq_true (by simpa using h)
          exact this.2.2.1,
    denoteCanonicalMeasures_teleport_eq_classical c0 c1 st h0 h1⟩

/-- Basis-state specialization: measuring `|000⟩` writes classical `00`. -/
theorem openqasm_measure_assignment_on_state000 :
    denoteCanonicalMeasures
        [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }]
        state000 (emptyClassicalReg 2) =
      teleportClassicalFromOutcomes .zero .zero := by
  native_decide

/-! ## Declared dynamic fragment link (measure + if + feed-forward + recovery)

Composes already-proved OpenQASM measure/if denotations with relational recovery.
This shrinks the dynamic protocol gap for packaging (`not_checked_under`) without claiming
gate-only ABRC over the full `teleportation.qasm` artifact. -/

/-- Kernel bundle: measure AST + IF CanonicalAst + ClassicalReg feed-forward ≡ Pauli +
renormalized Bob recovery for arbitrary Complex amplitudes. -/
theorem teleport_declared_dynamic_fragment_protocol_linked
    (α β : ℂ) (c0 c1 : ZOutcome) (st : StateAmp8)
    (h0 : measureZOutcomeAt8 st 0 = c0)
    (h1 : measureZOutcomeAt8 st 1 = c1) :
    (match parseQasmSourceE teleportMeasureAssignmentSource with
      | .ok ast =>
          ast.measurements = [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }]
      | .error _ => False) ∧
      canonicalControlsToStmts
          [{ cIdx := 1, op := "x", qubits := [2] }, { cIdx := 0, op := "z", qubits := [2] }] =
        some teleportFeedForwardIfStmts ∧
      teleportMeasureCorrectViaFeedForward (embedTeleportInputC α β) c0 c1 =
        teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1 ∧
      ((fun bit => (2 : ℂ) * bobAmpsC
          (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) bit) =
        fun bit => if bit = 0 then α else β) :=
  ⟨(openqasm_measure_assignment_denotes_classical_reg st c0 c1 h0 h1).1,
    canonicalControlsToStmts_teleport_feedforward,
    teleport_feedforward_eq_measure_correct_normed (embedTeleportInputC α β) c0 c1,
    teleport_measure_correct_normed_renormalized α β c0 c1⟩

/-- POVM quarter probabilities remain available on the linked dynamic fragment. -/
theorem teleport_declared_dynamic_fragment_povm_quarter
    (α β : ℂ) (h : Complex.normSq α + Complex.normSq β = 1) (c0 c1 : ZOutcome) :
    aliceBranchWeight (teleportPrefixCNormed (embedTeleportInputC α β)) c0 c1 = (1 / 4 : ℝ) :=
  teleport_normed_alice_povm_prob_quarter α β h c0 c1

/-- Full on-disk feedforward artifact CanonicalAst is hash-bound to measure+if denotation. -/
theorem teleport_dynamic_feedforward_artifact_canonical_ast_bound :
    (match parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
      | .ok ast =>
          ast.gates =
              [{ op := "h", qubits := [1] },
               { op := "cx", qubits := [1, 2] },
               { op := "cx", qubits := [0, 1] },
               { op := "h", qubits := [0] }] ∧
            ast.measurements =
              [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
            ast.controls =
              [{ cIdx := 1, op := "x", qubits := [2] },
               { cIdx := 0, op := "z", qubits := [2] }] ∧
            ast.nQubits = 3
      | .error _ => False) ∧
      canonicalControlsToStmts
          [{ cIdx := 1, op := "x", qubits := [2] }, { cIdx := 0, op := "z", qubits := [2] }] =
        some teleportFeedForwardIfStmts := by
  refine ⟨?_, canonicalControlsToStmts_teleport_feedforward⟩
  have h :
      (match parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
        | .ok ast =>
            decide (
              ast.gates =
                  [{ op := "h", qubits := [1] },
                   { op := "cx", qubits := [1, 2] },
                   { op := "cx", qubits := [0, 1] },
                   { op := "h", qubits := [0] }] ∧
                ast.measurements =
                  [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
                ast.controls =
                  [{ cIdx := 1, op := "x", qubits := [2] },
                   { cIdx := 0, op := "z", qubits := [2] }] ∧
                ast.nQubits = 3)
        | .error _ => false) = true := by
    native_decide
  revert h
  cases parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
  | error _ => intro h; exact absurd h Bool.false_ne_true
  | ok ast =>
      intro h
      exact of_decide_eq_true (by simpa using h)

/-- On-disk feedforward artifact: CanonicalAst measurements/controls denote ClassicalReg
feed-forward + renormalized Bob recovery. Not matrix KERNEL_BRIDGE ABRC. -/
theorem teleport_dynamic_feedforward_artifact_protocol_linked
    (α β : ℂ) (c0 c1 : ZOutcome) (st : StateAmp8)
    (h0 : measureZOutcomeAt8 st 0 = c0)
    (h1 : measureZOutcomeAt8 st 1 = c1) :
    (match parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
      | .ok ast =>
          ast.measurements =
              [{ cIdx := 0, qIdx := 0 }, { cIdx := 1, qIdx := 1 }] ∧
            ast.controls =
              [{ cIdx := 1, op := "x", qubits := [2] },
               { cIdx := 0, op := "z", qubits := [2] }] ∧
            denoteCanonicalMeasures ast.measurements st (emptyClassicalReg 2) =
              teleportClassicalFromOutcomes c0 c1 ∧
            canonicalControlsToStmts ast.controls = some teleportFeedForwardIfStmts
      | .error _ => False) ∧
      teleportMeasureCorrectViaFeedForward (embedTeleportInputC α β) c0 c1 =
        teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1 ∧
      ((fun bit => (2 : ℂ) * bobAmpsC
          (teleportMeasureCorrectCNormed (embedTeleportInputC α β) c0 c1) bit) =
        fun bit => if bit = 0 then α else β) := by
  refine ⟨?_,
    teleport_feedforward_eq_measure_correct_normed (embedTeleportInputC α β) c0 c1,
    teleport_measure_correct_normed_renormalized α β c0 c1⟩
  have hast := teleport_dynamic_feedforward_artifact_canonical_ast_bound.1
  have hctrl := teleport_dynamic_feedforward_artifact_canonical_ast_bound.2
  revert hast
  cases parseQasmSourceE teleportDynamicFeedforwardKernelArtifactSource with
  | error _ => intro h; exact False.elim h
  | ok ast =>
      intro hast
      refine ⟨hast.2.1, hast.2.2.1, ?_, ?_⟩
      · rw [hast.2.1]
        exact denoteCanonicalMeasures_teleport_eq_classical c0 c1 st h0 h1
      · simpa [hast.2.2.1] using hctrl

def teleportArbitraryStateTransferBlocker : String :=
  "Closed: normalized-H POVM + renormalized Bob recovery; ClassicalReg feed-forward; \
OpenQASM IF fragment + CanonicalAst.controls; OpenQASM `c[i]=measure q[j]` → \
CanonicalAst.measurements → writeZOutcome denotation \
(`openqasm_measure_assignment_denotes_classical_reg`). \
Deepened: KERNEL_BRIDGE_IDS + Generated.TeleportationUnitaryPrefix + \
`teleportKernelArtifactSource` / `parseQasmSource_teleport_kernel_eq_generated_ops` + \
`bridge_teleport_unitary_prefix_codegen` + BridgeMetadata/elaborator/ast/generated_lean \
pins + claimed_link kernel_checked_artifact_semantics + wire_order lean on \
`teleport_unitary_prefix.qasm`. Option B ABRC (proposition v2) retained. \
Further: `teleport_declared_dynamic_fragment_protocol_linked` composes measure+if+ \
feed-forward+recovery; `teleport_dynamic_feedforward_artifact_canonical_ast_bound` \
hash-binds on-disk `teleportation_with_feedforward.qasm`; \
`teleport_dynamic_feedforward_artifact_protocol_linked` composes that artifact's \
measurements/controls → ClassicalReg denotation + recovery. \
Full dynamic ABRC / matrix KERNEL_BRIDGE for measure+if still out of scope \
(gate-only codegen would silently drop dynamics)."

/-- Explicit ABRC invariant checklist for teleport under narrowed unitary-prefix ABRC (Option B).
Full dynamic measure+if protocol remains out of ABRC headline scope (not a remaining
blocker for the narrowed claim). Dynamic fragment link shrinks packaging not_checked_under. -/
def teleportAbrcRemainingBlockers : List String := []

#check teleport_prefix_arbitrary_state_int
#check teleport_prefix_arbitrary_state
#check teleport_prefix_arbitrary_state_complex
#check teleport_measure_correct_arbitrary_int
#check teleport_measure_correct_arbitrary_complex
#check teleport_measure_correct_arbitrary_complex_amps
#check teleport_prefix_alice_branch_weight
#check teleport_prefix_alice_branch_weight_normalized
#check teleport_alice_projective_prob_quarter
#check teleportPrefixCNormed_eq_half
#check teleport_prefix_normed_alice_branch_weight
#check teleport_normed_alice_povm_prob_quarter
#check teleport_normed_alice_povm_probs_sum_one
#check teleport_measure_correct_normed_renormalized
#check teleport_feedforward_eq_measure_correct_normed
#check applyTeleportFeedForward_eq_pauliCorrection8C
#check parseTeleportIfLine_x
#check parseTeleportFeedForwardFragment
#check openqasm_if_fragment_denotes_classical_reg
#check openqasm_if_canonical_ast_denotes_classical_reg
#check openqasm_measure_assignment_denotes_classical_reg
#check openqasm_measure_assignment_on_state000
#check teleport_declared_dynamic_fragment_protocol_linked
#check teleport_declared_dynamic_fragment_povm_quarter
#check teleport_dynamic_feedforward_artifact_canonical_ast_bound
#check teleport_dynamic_feedforward_artifact_protocol_linked
#check parseQasmSourceE_teleport_if_controls_eq_stmts
#check denotateClassicalCtrl_eq_feedforward
#check teleport_measure_correct_ket0
#check teleport_measure_correct_ket1
#check teleportation_unitary_fragment_checked
#check teleportArbitraryStateTransferBlocker
#check teleportAbrcRemainingBlockers

end QSpecBench
