import Mathlib.Data.Complex.Basic
import Mathlib.Data.Complex.Exponential
import Mathlib.Data.Matrix.Notation
import Mathlib.Data.Real.Basic
import Mathlib.Analysis.SpecialFunctions.Trigonometric.Basic
import Mathlib.Tactic.FinCases

/-!
# Complex unitary gate matrices for OpenQASM 3 semantics.

Matches the Python `qasm_matrix` model: unnormalized Hadamard integers, exact phase
on diagonal for S/T, and standard RX(θ) = exp(-i θ/2 X).
-/

namespace QSpecBench.Quantum.ComplexGate

open Matrix Complex Real

abbrev Mat2C := Matrix (Fin 2) (Fin 2) ℂ
abbrev Mat4C := Matrix (Fin 4) (Fin 4) ℂ
abbrev Mat8C := Matrix (Fin 8) (Fin 8) ℂ

private def ifDiag (i j : Fin 2) (d : ℂ) : ℂ :=
  if i = j then d else 0

/-- Identity on one qubit. -/
def identityEntry (i j : Fin 2) : ℂ :=
  if i = j then (1 : ℂ) else 0

def identityGate : Mat2C := Matrix.of identityEntry

/-- Unnormalized Hadamard (OpenQASM carries 1/√2 per gate). -/
def hadamardEntry (i j : Fin 2) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨0, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨1, _⟩ => (-1 : ℂ)

def hadamardC : Mat2C := Matrix.of hadamardEntry

def pauliXEntry (i j : Fin 2) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | _, _ => 0

def pauliXC : Mat2C := Matrix.of pauliXEntry

def pauliYEntry (i j : Fin 2) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨1, _⟩ => (-I : ℂ)
  | ⟨1, _⟩, ⟨0, _⟩ => (I : ℂ)
  | _, _ => 0

def pauliYC : Mat2C := Matrix.of pauliYEntry

def pauliZEntry (i j : Fin 2) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨1, _⟩ => (-1 : ℂ)
  | _, _ => 0

def pauliZC : Mat2C := Matrix.of pauliZEntry

/-- S gate: diag(1, i). -/
def sGateEntry (i j : Fin 2) : ℂ :=
  ifDiag i j (if i = 0 then (1 : ℂ) else I)

def sGate : Mat2C := Matrix.of sGateEntry

/-- T gate: diag(1, e^{iπ/4}). -/
noncomputable def tGateEntry (i j : Fin 2) : ℂ :=
  ifDiag i j (if i = 0 then (1 : ℂ) else Complex.exp (I * (Real.pi / 4)))

noncomputable def tGate : Mat2C := Matrix.of tGateEntry

/-- S† gate: diag(1, -i). -/
def sDagGateEntry (i j : Fin 2) : ℂ :=
  ifDiag i j (if i = 0 then (1 : ℂ) else -I)

def sDagGate : Mat2C := Matrix.of sDagGateEntry

/-- T† gate: diag(1, e^{-iπ/4}). -/
noncomputable def tDagGateEntry (i j : Fin 2) : ℂ :=
  ifDiag i j (if i = 0 then (1 : ℂ) else Complex.exp (-I * (Real.pi / 4)))

noncomputable def tDagGate : Mat2C := Matrix.of tDagGateEntry

/-- RX(θ) = exp(-i θ/2 X); θ = π/2 matches unnormalized H in the Python bridge. -/
noncomputable def rxGateEntry (θ : ℝ) (i j : Fin 2) : ℂ :=
  let half := θ / 2
  let c := Real.cos half
  let s := Real.sin half
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => c
  | ⟨0, _⟩, ⟨1, _⟩ => -I * s
  | ⟨1, _⟩, ⟨0, _⟩ => -I * s
  | ⟨1, _⟩, ⟨1, _⟩ => c

noncomputable def rxGate (θ : ℝ) : Mat2C := Matrix.of (rxGateEntry θ)

/-- CNOT with control qubit 0 and target qubit 1 (lexicographic |00⟩,…,|11⟩). -/
private def cnot4_01Entry (i j : Fin 4) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | _, _ => 0

/-- CNOT with control qubit 1 and target qubit 0. -/
private def cnot4_10Entry (i j : Fin 4) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | _, _ => 0

private def cnot4_01C : Mat4C := Matrix.of cnot4_01Entry
private def cnot4_10C : Mat4C := Matrix.of cnot4_10Entry

/-- Indexed two-qubit CNOT matching OpenQASM `cx q[ctrl], q[tgt]` (qubit 0 = LSB). -/
def cnot4CtrlTgt (ctrl tgt : Fin 2) : Mat4C :=
  match ctrl, tgt with
  | ⟨0, _⟩, ⟨1, _⟩ => cnot4_01C
  | ⟨1, _⟩, ⟨0, _⟩ => cnot4_10C
  | _, _ => (1 : Mat4C)

def cnot4C : Mat4C := cnot4CtrlTgt 0 1

/-- SWAP on qubits 0 and 1. -/
def swap4Entry (i j : Fin 4) : ℂ :=
  match i, j with
  | ⟨0, _⟩, ⟨0, _⟩ => (1 : ℂ)
  | ⟨1, _⟩, ⟨2, _⟩ => (1 : ℂ)
  | ⟨2, _⟩, ⟨1, _⟩ => (1 : ℂ)
  | ⟨3, _⟩, ⟨3, _⟩ => (1 : ℂ)
  | _, _ => 0

def swap4C : Mat4C := Matrix.of swap4Entry

/-- CCX with controls q0,q1 and target q2. -/
def ccx8Entry (i j : Fin 8) : ℂ :=
  if i = j then (1 : ℂ)
  else if (i.val = 3 ∧ j.val = 7) ∨ (i.val = 7 ∧ j.val = 3) then (1 : ℂ)
  else 0

def ccx8C : Mat8C := Matrix.of ccx8Entry

/-- Kronecker I₂ ⊗ A (A on the second tensor factor). -/
def kronI2 (A : Mat2C) (i j : Fin 4) : ℂ :=
  let i0 : Fin 2 := ⟨i.val / 2, by omega⟩
  let i1 : Fin 2 := ⟨i.val % 2, by omega⟩
  let j0 : Fin 2 := ⟨j.val / 2, by omega⟩
  let j1 : Fin 2 := ⟨j.val % 2, by omega⟩
  if i0 = j0 then A i1 j1 else 0

def kronI2M (A : Mat2C) : Mat4C := Matrix.of (kronI2 A)

/-- Kronecker A ⊗ I₂ (A on the first tensor factor). -/
def kron2I (A : Mat2C) (i j : Fin 4) : ℂ :=
  let i0 : Fin 2 := ⟨i.val / 2, by omega⟩
  let i1 : Fin 2 := ⟨i.val % 2, by omega⟩
  let j0 : Fin 2 := ⟨j.val / 2, by omega⟩
  let j1 : Fin 2 := ⟨j.val % 2, by omega⟩
  if i1 = j1 then A i0 j0 else 0

def kron2IM (A : Mat2C) : Mat4C := Matrix.of (kron2I A)

/-- Matrix product for 2×2 complex gates (left-to-right circuit order). -/
def mul2C (A B : Mat2C) (i j : Fin 2) : ℂ :=
  A i 0 * B 0 j + A i 1 * B 1 j

def mul2C_mat (A B : Mat2C) : Mat2C := Matrix.of (mul2C A B)

end QSpecBench.Quantum.ComplexGate
