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

/-- Diagonal embedding helper shared by single-qubit gate matrices. -/
def ifDiag (i j : Fin 2) (d : ℂ) : ℂ :=
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

/-- RX(θ) = exp(-i θ/2 X). Int scaffold maps π/2 to unnormalized H; complex model uses standard rotation. -/
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

/-- RX(π/2) and unnormalized Hadamard differ on (0,1): rotation uses `-i sin(θ/2)`, H uses `1`.
Global-phase equivalence to H is therefore not claimed under the complex model. -/
theorem rx_pi2_entry01_ne_hadamard_entry01 :
    rxGateEntry (Real.pi / 2) (0 : Fin 2) (1 : Fin 2) ≠ hadamardEntry (0 : Fin 2) (1 : Fin 2) := by
  have hrx :
      rxGateEntry (Real.pi / 2) (0 : Fin 2) (1 : Fin 2) =
        -I * (Real.sin (Real.pi / 4) : ℂ) := by
    simp [rxGateEntry, show Real.pi / 2 / 2 = Real.pi / 4 by ring]
  have hhad : hadamardEntry (0 : Fin 2) (1 : Fin 2) = 1 := by simp [hadamardEntry]
  rw [hrx, hhad]
  intro h
  have him := congrArg Complex.im h
  simp [Complex.mul_im, Complex.I_im, Complex.I_re, Complex.ofReal_im, Real.sin_pi_div_four] at him

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

/-- CCX with controls q0,q1 and target q2 (LSB = q0): swaps |011⟩↔|111⟩. -/
def ccx8Entry (i j : Fin 8) : ℂ :=
  if (i.val = 3 ∧ j.val = 7) ∨ (i.val = 7 ∧ j.val = 3) then (1 : ℂ)
  else if i = j ∧ i.val ≠ 3 ∧ i.val ≠ 7 then (1 : ℂ)
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

theorem mul2C_one_right (A : Mat2C) (i j : Fin 2) :
    mul2C A (1 : Mat2C) i j = A i j := by
  fin_cases i <;> fin_cases j <;> simp [mul2C, Matrix.one_apply, Fin.sum_univ_two]

theorem hadamardC_mul_self (i j : Fin 2) :
    mul2C hadamardC hadamardC i j = (2 : ℂ) * identityGate i j := by
  fin_cases i <;> fin_cases j <;>
    simp [mul2C, hadamardC, hadamardEntry, identityGate, identityEntry, Matrix.of_apply] <;> norm_num

theorem mul2C_smul_identity_right (A : Mat2C) (c : ℂ) (i j : Fin 2) :
    mul2C A (Matrix.of (fun i' j' => c * identityEntry i' j')) i j = c * A i j := by
  fin_cases i <;> fin_cases j <;> simp [mul2C, identityEntry, Matrix.of_apply] <;> ring

theorem mul2C_sGate_hadamard_sq (i j : Fin 2) :
    mul2C sGate (mul2C hadamardC hadamardC) i j = (2 : ℂ) * sGate i j := by
  rw [show mul2C hadamardC hadamardC = Matrix.of (fun i' j' => (2 : ℂ) * identityEntry i' j') from by
    ext i' j'
    simp [hadamardC_mul_self, identityGate, identityEntry, Matrix.of_apply]]
  exact mul2C_smul_identity_right sGate (2 : ℂ) i j

def mul8C (A B : Mat8C) (i j : Fin 8) : ℂ :=
  A i 0 * B 0 j + A i 1 * B 1 j + A i 2 * B 2 j + A i 3 * B 3 j +
    A i 4 * B 4 j + A i 5 * B 5 j + A i 6 * B 6 j + A i 7 * B 7 j

def mul8C_mat (A B : Mat8C) : Mat8C := Matrix.of (mul8C A B)

private def tensorIdx3 (i : Fin 8) : Fin 2 × Fin 2 × Fin 2 :=
  (⟨i.val % 2, by omega⟩, ⟨(i.val / 2) % 2, by omega⟩, ⟨i.val / 4, by omega⟩)

def kron3Entry (A B C : Mat2C) (i j : Fin 8) : ℂ :=
  let (i0, i1, i2) := tensorIdx3 i
  let (j0, j1, j2) := tensorIdx3 j
  A i0 j0 * B i1 j1 * C i2 j2

def kron3 (A B C : Mat2C) : Mat8C := Matrix.of (kron3Entry A B C)

def applySingle3C (g : Mat2C) (q : Nat) : Mat8C :=
  kron3
    (if q = 0 then g else identityGate)
    (if q = 1 then g else identityGate)
    (if q = 2 then g else identityGate)

/-- Column permutation for CNOT (XOR target bit when control is set). Aligns with Python. -/
def cnot8Col (ctrl tgt row : Nat) : Nat :=
  if (row >>> ctrl) &&& 1 = 1 then row ^^^ (1 <<< tgt) else row

def cnot8Entry (ctrl tgt : Nat) (i j : Fin 8) : ℂ :=
  if j.val = cnot8Col ctrl tgt i.val then (1 : ℂ) else 0

def cnot8 (ctrl tgt : Nat) : Mat8C := Matrix.of (cnot8Entry ctrl tgt)

theorem mul8C_one_right (A : Mat8C) (i j : Fin 8) :
    mul8C A (1 : Mat8C) i j = A i j := by
  fin_cases j <;> fin_cases i <;> simp [mul8C, Matrix.one_apply]

theorem mul8C_one_left (A : Mat8C) (i j : Fin 8) :
    mul8C (1 : Mat8C) A i j = A i j := by
  fin_cases j <;> fin_cases i <;> simp [mul8C, Matrix.one_apply]

/-- Column map for CX is an involution on the 3-qubit computational basis (Nat-level). -/
theorem cnot8Col_01_involutive (r : Fin 8) :
    cnot8Col 0 1 (cnot8Col 0 1 r.val) = r.val := by
  fin_cases r <;> decide

theorem cnot8Col_10_involutive (r : Fin 8) :
    cnot8Col 1 0 (cnot8Col 1 0 r.val) = r.val := by
  fin_cases r <;> decide

theorem cnot8Col_12_involutive (r : Fin 8) :
    cnot8Col 1 2 (cnot8Col 1 2 r.val) = r.val := by
  fin_cases r <;> decide

theorem cnot8Col_02_involutive (r : Fin 8) :
    cnot8Col 0 2 (cnot8Col 0 2 r.val) = r.val := by
  fin_cases r <;> decide

/-- T · T† = I (exact phase cancellation). -/
theorem tGate_mul_tDagGate (i j : Fin 2) :
    mul2C tGate tDagGate i j = identityGate i j := by
  have hexp :
      Complex.exp (I * (Real.pi / 4)) * Complex.exp (-(I * (Real.pi / 4))) = 1 := by
    rw [← Complex.exp_add]
    have : (I * (Real.pi / 4) + -(I * (Real.pi / 4)) : ℂ) = 0 := by ring
    simp [this, Complex.exp_zero]
  fin_cases i <;> fin_cases j <;>
    simp [mul2C, tGate, tDagGate, tGateEntry, tDagGateEntry, identityGate, identityEntry,
      ifDiag, Matrix.of_apply, hexp, show (-I * (Real.pi / 4) : ℂ) = -(I * (Real.pi / 4)) by ring]

theorem tDagGate_mul_tGate (i j : Fin 2) :
    mul2C tDagGate tGate i j = identityGate i j := by
  have hexp :
      Complex.exp (-(I * (Real.pi / 4))) * Complex.exp (I * (Real.pi / 4)) = 1 := by
    rw [← Complex.exp_add]
    have : (-(I * (Real.pi / 4)) + I * (Real.pi / 4) : ℂ) = 0 := by ring
    simp [this, Complex.exp_zero]
  fin_cases i <;> fin_cases j <;>
    simp [mul2C, tGate, tDagGate, tGateEntry, tDagGateEntry, identityGate, identityEntry,
      ifDiag, Matrix.of_apply, hexp, show (-I * (Real.pi / 4) : ℂ) = -(I * (Real.pi / 4)) by ring]

theorem sGate_mul_sDagGate (i j : Fin 2) :
    mul2C sGate sDagGate i j = identityGate i j := by
  fin_cases i <;> fin_cases j <;>
    simp [mul2C, sGate, sDagGate, sGateEntry, sDagGateEntry, identityGate, identityEntry,
      ifDiag, Matrix.of_apply, Complex.I_mul_I] <;> ring

/-- Normalized Hadamard entry (physical unitary convention). -/
noncomputable def hadamardC_normalizedEntry (i j : Fin 2) : ℂ :=
  (1 / Real.sqrt 2 : ℂ) * hadamardEntry i j

noncomputable def hadamardC_normalized : Mat2C := Matrix.of hadamardC_normalizedEntry

theorem hadamardC_normalized_mul_self (i j : Fin 2) :
    mul2C hadamardC_normalized hadamardC_normalized i j = identityGate i j := by
  have hsqrt : (Real.sqrt 2 : ℝ) ≠ 0 := Real.sqrt_ne_zero'.mpr (by norm_num : (0 : ℝ) < 2)
  have h2 : (Real.sqrt 2 : ℝ) * Real.sqrt 2 = 2 := Real.mul_self_sqrt (by norm_num)
  fin_cases i <;> fin_cases j <;>
    simp [mul2C, hadamardC_normalized, hadamardC_normalizedEntry, hadamardEntry,
      identityGate, identityEntry, Matrix.of_apply] <;>
    field_simp [hsqrt] <;> norm_cast <;> simp [h2] <;> norm_num

/-- Normalized H·H = I as a matrix equality (for rewriting under `mul2C`). -/
theorem hadamardC_normalized_mul_self_mat :
    mul2C hadamardC_normalized hadamardC_normalized = (1 : Mat2C) := by
  ext i j
  simpa [identityGate, identityEntry, Matrix.of_apply, Matrix.one_apply] using
    hadamardC_normalized_mul_self i j

/-- S · (H_n · H_n) = S under normalized Hadamard (exact unitary cancellation). -/
theorem mul2C_sGate_hadamard_normalized_sq (i j : Fin 2) :
    mul2C sGate (mul2C hadamardC_normalized hadamardC_normalized) i j = sGate i j := by
  rw [hadamardC_normalized_mul_self_mat]
  exact mul2C_one_right sGate i j

/-- CCX wire-order: controls on qubits 0,1 and target on qubit 2 flip |011⟩↔|111⟩ (LSB = q0). -/
theorem ccx8C_flips_011_111 :
    ccx8C ⟨3, by decide⟩ ⟨7, by decide⟩ = 1 ∧
      ccx8C ⟨7, by decide⟩ ⟨3, by decide⟩ = 1 ∧
      ccx8C ⟨3, by decide⟩ ⟨3, by decide⟩ = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · simp only [ccx8C, Matrix.of_apply, ccx8Entry]; rfl
  · simp only [ccx8C, Matrix.of_apply, ccx8Entry]; rfl
  · simp only [ccx8C, Matrix.of_apply, ccx8Entry]; rfl

end QSpecBench.Quantum.ComplexGate
