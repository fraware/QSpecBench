import Mathlib.Tactic.FinCases

/-!
# Three-qubit bit-flip code lookup-table decoder (single-X error model).

Kernel-checked scope: syndrome table + correction table for Pauli X errors on one qubit.
General decoder algorithm correctness and syndrome-extraction circuits are not claimed.
-/

namespace QSpecBench.QEC.BitFlip

/-- Pauli letter on one wire: 0 = I, 1 = Z, 2 = X, 3 = Y (legacy stabilizer encoding). -/
abbrev PauliLetter := Fin 4

abbrev Pauli3 := Fin 3 → PauliLetter

def pauliI : PauliLetter := 0
def pauliZ : PauliLetter := 1
def pauliX : PauliLetter := 2

def pauliIII : Pauli3 := fun _ => pauliI
def pauliZZI : Pauli3 := fun i => if i.val ≤ 1 then pauliZ else pauliI
def pauliIZZ : Pauli3 := fun i => if i.val = 0 then pauliI else pauliZ
def pauliZZZ : Pauli3 := fun _ => pauliZ

def singleX (q : Fin 3) : Pauli3 :=
  fun i => if i = q then pauliX else pauliI

def pauliXII : Pauli3 := singleX ⟨0, by decide⟩
def pauliIXI : Pauli3 := singleX ⟨1, by decide⟩
def pauliIIX : Pauli3 := singleX ⟨2, by decide⟩

def multiplyLetter (a b : PauliLetter) : PauliLetter :=
  if a = pauliI then b
  else if b = pauliI then a
  else if a = b then pauliI
  else if a = pauliX ∧ b = pauliZ ∨ a = pauliZ ∧ b = pauliX then 3
  else if a = pauliX ∧ b = 3 ∨ a = 3 ∧ b = pauliX then pauliZ
  else if a = pauliZ ∧ b = 3 ∨ a = 3 ∧ b = pauliZ then pauliX
  else pauliI

def multiplyPauli3 (a b : Pauli3) : Pauli3 :=
  fun i => multiplyLetter (a i) (b i)

inductive Syndrome where
  | s00 | s01 | s10 | s11
  deriving DecidableEq, Repr

/-- Syndrome bit s0: anticommute count with ZZI; s1: with IZZ (single-X model). -/
def syndromeFromSingleX (q : Fin 3) : Syndrome :=
  match q with
  | ⟨0, _⟩ => .s10
  | ⟨1, _⟩ => .s11
  | ⟨2, _⟩ => .s01

def lookupCorrection (s : Syndrome) : Pauli3 :=
  match s with
  | .s00 => pauliIII
  | .s10 => pauliXII
  | .s11 => pauliIXI
  | .s01 => pauliIIX

def isStabilizer (p : Pauli3) : Prop :=
  p = pauliIII ∨ p = pauliZZI ∨ p = pauliIZZ ∨ p = pauliZZZ

theorem multiply_singleX_lookup_residual_I (q : Fin 3) :
    multiplyPauli3 (singleX q) (lookupCorrection (syndromeFromSingleX q)) = pauliIII := by
  fin_cases q <;> native_decide

theorem bit_flip_lookup_decoder_correct :
    ∀ q : Fin 3, isStabilizer (multiplyPauli3 (singleX q) (lookupCorrection (syndromeFromSingleX q))) := by
  intro q
  rw [multiply_singleX_lookup_residual_I q]
  exact Or.inl rfl

theorem lookup_syndrome00_identity : lookupCorrection .s00 = pauliIII := rfl

theorem lookup_syndrome10_x0 : lookupCorrection .s10 = pauliXII := rfl

theorem lookup_syndrome11_x1 : lookupCorrection .s11 = pauliIXI := rfl

theorem lookup_syndrome01_x2 : lookupCorrection .s01 = pauliIIX := rfl

def decoderTrustBoundaryNote : String :=
  "Lookup-table decoder kernel-checked for single-X Pauli errors on three qubits; " ++
  "syndrome extraction circuits and general decoder algorithm not claimed."

#check bit_flip_lookup_decoder_correct
#check decoderTrustBoundaryNote

end QSpecBench.QEC.BitFlip
