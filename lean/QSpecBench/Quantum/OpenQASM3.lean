import QSpecBench.Legacy.Matrix
import Mathlib.Tactic.FinCases
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import QSpecBench.Legacy.QFT2
import QSpecBench.Quantum.Gate

/-!
# Denotational OpenQASM 3 semantics for the benchmark gate subset.
-/

namespace QSpecBench.Quantum.OpenQASM3

open QSpecBench (Matrix2 Matrix4 mul2 mul4 id2 id4 kron2I kronI2 scale2 scale4 qft2 invqft2 qft2_mul_invqft2
  hadamard_conjugates_x hadamard_mul_self cnot_mul_self mul2_assoc)
open QSpecBench.Quantum (pauliY)

inductive SingleGate where
  | I | X | Y | Z | H | S | T
  deriving DecidableEq, Repr

inductive QasmOp where
  | gate (g : SingleGate) (q : Nat)
  | cx (control target : Nat)
  deriving Repr

def denotateGate : SingleGate → Matrix2
  | .I => id2
  | .X => pauliX2
  | .Y => pauliY
  | .Z => pauliZ2
  | .H => hadamard2
  | .S => id2
  | .T => id2

theorem qasm_H_denotes_hadamard (i j : Fin 2) :
    denotateGate .H i j = hadamard2 i j := rfl

theorem qasm_X_denotes_pauliX (i j : Fin 2) :
    denotateGate .X i j = pauliX2 i j := rfl

theorem qasm_Z_denotes_pauliZ (i j : Fin 2) :
    denotateGate .Z i j = pauliZ2 i j := rfl

def denotateCX : Matrix4 := cnot4

theorem qasm_CX_denotes_cnot (i j : Fin 4) :
    denotateCX i j = cnot4 i j := rfl

def denotateOps1 (ops : List QasmOp) : Matrix2 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g _ => fun i j => mul2 (denotateGate g) acc i j
    | .cx _ _ => acc) id2

def applySingle2 (g : SingleGate) (q : Nat) : Matrix4 :=
  if q = 0 then kron2I (denotateGate g) else kronI2 (denotateGate g)

def denotateOps2 (ops : List QasmOp) : Matrix4 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g q => fun i j => mul4 (applySingle2 g q) acc i j
    | .cx _ _ => fun i j => mul4 denotateCX acc i j) id4

def cnot_cx_cx : List QasmOp := [.cx 0 1, .cx 0 1]

def cnot_cx_cxMat (i j : Fin 4) : Int := mul4 cnot4 (mul4 cnot4 id4) i j

theorem denotateOps2_cnot_cx_cx (i j : Fin 4) : denotateOps2 cnot_cx_cx i j = cnot_cx_cxMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_cnot_self_inverse (i j : Fin 4) :
    denotateOps2 cnot_cx_cx i j = id4 i j := by
  rw [denotateOps2_cnot_cx_cx]
  fin_cases i <;> fin_cases j <;> rfl

def hadamard_hxh : List QasmOp := [.gate .H 0, .gate .X 0, .gate .H 0]

def hadamard_hxhMat (i j : Fin 2) : Int := mul2 hadamard2 (mul2 pauliX2 hadamard2) i j

theorem denotateOps1_hadamard_hxh (i j : Fin 2) : denotateOps1 hadamard_hxh i j = hadamard_hxhMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_hadamard_conjugates_x (i j : Fin 2) :
    denotateOps1 hadamard_hxh i j = scale2 2 pauliZ2 i j := by
  rw [denotateOps1_hadamard_hxh, hadamard_hxhMat, mul2_assoc, hadamard_conjugates_x]

def hadamard_hh : List QasmOp := [.gate .H 0, .gate .H 0]

def hadamard_hhMat (i j : Fin 2) : Int := mul2 hadamard2 hadamard2 i j

theorem denotateOps1_hadamard_hh (i j : Fin 2) : denotateOps1 hadamard_hh i j = hadamard_hhMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_hadamard_cancel (i j : Fin 2) :
    denotateOps1 hadamard_hh i j = scale2 2 id2 i j := by
  rw [denotateOps1_hadamard_hh, hadamard_hhMat, hadamard_mul_self]

def qft2_ops : List QasmOp := [.gate .H 0, .cx 0 1, .gate .H 0]

theorem denotateOps2_qft2_ops (i j : Fin 4) : denotateOps2 qft2_ops i j = qft2 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_qft2_inverse (i j : Fin 4) :
    mul4 (denotateOps2 qft2_ops) (denotateOps2 qft2_ops) i j = scale4 4 id4 i j := by
  have hf : denotateOps2 qft2_ops = qft2 := funext fun a => funext fun b => denotateOps2_qft2_ops a b
  suffices mul4 (denotateOps2 qft2_ops) (denotateOps2 qft2_ops) i j = mul4 qft2 invqft2 i j by
    simpa [invqft2] using qft2_mul_invqft2 i j ▸ this
  simp [hf, invqft2]

def clifford_hhs : List QasmOp := [.gate .H 0, .gate .H 0, .gate .S 0]

def clifford_hhsMat (i j : Fin 4) : Int := mul4 (kron2I id2) (mul4 (kron2I hadamard2) (kron2I hadamard2)) i j

def hadamard_hh2Mat (i j : Fin 4) : Int := mul4 (kron2I hadamard2) (kron2I hadamard2) i j

theorem denotateOps2_clifford_hhs (i j : Fin 4) : denotateOps2 clifford_hhs i j = clifford_hhsMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem denotateOps2_hadamard_hh2 (i j : Fin 4) : denotateOps2 hadamard_hh i j = hadamard_hh2Mat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem clifford_hhsMat_eq (i j : Fin 4) : clifford_hhsMat i j = hadamard_hh2Mat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_clifford_hhs_aux (i j : Fin 4) :
    denotateOps2 clifford_hhs i j = denotateOps2 hadamard_hh i j := by
  rw [denotateOps2_clifford_hhs, denotateOps2_hadamard_hh2, clifford_hhsMat_eq]

theorem bridge_clifford_hhs (i j : Fin 2) :
    denotateOps2 clifford_hhs (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) =
      denotateOps2 hadamard_hh (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) :=
  bridge_clifford_hhs_aux _ _

def cnot_single : List QasmOp := [.cx 0 1]

theorem bridge_cnot_single (i j : Fin 4) :
    denotateOps2 cnot_single i j = cnot4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

def xx_cancel : List QasmOp := [.gate .X 0, .gate .X 0]

def xx_cancelMat (i j : Fin 4) : Int := mul4 (kron2I pauliX2) (kron2I pauliX2) i j

theorem denotateOps2_xx_cancel (i j : Fin 4) : denotateOps2 xx_cancel i j = xx_cancelMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem xx_cancelMat_eq_id (i j : Fin 4) : xx_cancelMat i j = id4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_xx_cancel_aux (i j : Fin 4) :
    denotateOps2 xx_cancel i j = id4 i j := by
  rw [denotateOps2_xx_cancel, xx_cancelMat_eq_id]

theorem bridge_xx_cancel (i j : Fin 2) :
    denotateOps2 xx_cancel (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) =
      id4 (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) :=
  bridge_xx_cancel_aux _ _

def hxx_gate : List QasmOp := [.gate .H 0, .gate .X 0, .gate .X 0]

def hxx_gateMat (i j : Fin 4) : Int :=
  mul4 (kron2I hadamard2) (mul4 (kron2I pauliX2) (kron2I pauliX2)) i j

theorem denotateOps2_hxx_gate (i j : Fin 4) : denotateOps2 hxx_gate i j = hxx_gateMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem hxx_gateMat_eq (i j : Fin 4) : hxx_gateMat i j = mul4 (kron2I hadamard2) id4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_hxx_gate_aux (i j : Fin 4) :
    denotateOps2 hxx_gate i j = mul4 (kron2I hadamard2) id4 i j := by
  rw [denotateOps2_hxx_gate, hxx_gateMat_eq]

theorem bridge_hxx_gate (i j : Fin 2) :
    denotateOps2 hxx_gate (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) =
      mul4 (kron2I hadamard2) id4 (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) :=
  bridge_hxx_gate_aux _ _

def hs_gate : List QasmOp := [.gate .H 0, .gate .S 0]

def hs_gateMat (i j : Fin 4) : Int := mul4 (kron2I id2) (kron2I hadamard2) i j

theorem denotateOps2_hs_gate (i j : Fin 4) : denotateOps2 hs_gate i j = hs_gateMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem hs_gateMat_eq (i j : Fin 4) : hs_gateMat i j = kron2I hadamard2 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_hs_gate_aux (i j : Fin 4) :
    denotateOps2 hs_gate i j = kron2I hadamard2 i j := by
  rw [denotateOps2_hs_gate, hs_gateMat_eq]

theorem bridge_hs_gate (i j : Fin 2) :
    denotateOps2 hs_gate (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) =
      kron2I hadamard2 (⟨i.val, by omega⟩ : Fin 4) (⟨j.val, by omega⟩ : Fin 4) :=
  bridge_hs_gate_aux _ _

/-- Bell-pair preparation scaffold (H on q0, CX q0→q1). -/
def bell_prep_ops : List QasmOp := [.gate .H 0, .cx 0 1]

def bellPrepMatrix (i j : Fin 4) : Int := mul4 cnot4 (kron2I hadamard2) i j

theorem denotateOps2_bell_prep (i j : Fin 4) :
    denotateOps2 bell_prep_ops i j = bellPrepMatrix i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_teleportation_scaffold (i j : Fin 4) :
    denotateOps2 bell_prep_ops i j = bellPrepMatrix i j :=
  denotateOps2_bell_prep i j

end QSpecBench.Quantum.OpenQASM3
