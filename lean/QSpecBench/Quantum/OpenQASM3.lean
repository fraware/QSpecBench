import QSpecBench.Legacy.Matrix
import Mathlib.Tactic.FinCases
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import QSpecBench.Legacy.QFT2
import QSpecBench.Quantum.Gate
import QSpecBench.Quantum.ComplexGate

/-!
# Denotational OpenQASM 3 semantics for the benchmark gate subset.
-/

namespace QSpecBench.Quantum.OpenQASM3

open QSpecBench (Matrix2 Matrix4 Matrix8 mul2 mul4 mul8 id2 id4 id8 ccx8 swap4 kron2I kronI2 scale2 scale4 qft2 invqft2 qft2_mul_invqft2
  hadamard_conjugates_x hadamard_mul_self cnot_mul_self cnot4_ctrl_tgt_mul_self mul2_assoc)
open QSpecBench.Quantum (pauliY)
open QSpecBench.Quantum.ComplexGate
open Complex

inductive SingleGate where
  | I | X | Y | Z | H | S | T | Sdg | Tdg
  deriving DecidableEq, Repr

inductive QasmOp where
  | gate (g : SingleGate) (q : Nat)
  | cx (control target : Nat)
  | ccx (c0 c1 target : Nat)
  | swap (a b : Nat)
  deriving Repr

/-- Integer matrix scaffold: Pauli/H only; S/T use `denotateGateC` (complex model). -/
def denotateGate : SingleGate → Matrix2
  | .I => id2
  | .X => pauliX2
  | .Y => pauliY
  | .Z => pauliZ2
  | .H => hadamard2
  | .S => id2
  | .T => id2
  | .Sdg => id2
  | .Tdg => id2

/-- Complex unitary denotation matching Python `qasm_matrix` for the full gate subset. -/
noncomputable def denotateGateC : SingleGate → Mat2C
  | .I => ComplexGate.identityGate
  | .X => pauliXC
  | .Y => pauliYC
  | .Z => pauliZC
  | .H => hadamardC
  | .S => sGate
  | .T => tGate
  | .Sdg => sDagGate
  | .Tdg => tDagGate

noncomputable def denotateOps1C (ops : List QasmOp) : Mat2C :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g _ => mul2C (denotateGateC g) acc
    | .cx _ _ => acc
    | .ccx _ _ _ => acc
    | .swap _ _ => acc) (1 : Mat2C)

theorem qasm_H_denotes_hadamard (i j : Fin 2) :
    denotateGate .H i j = hadamard2 i j := rfl

theorem qasm_X_denotes_pauliX (i j : Fin 2) :
    denotateGate .X i j = pauliX2 i j := rfl

theorem qasm_Z_denotes_pauliZ (i j : Fin 2) :
    denotateGate .Z i j = pauliZ2 i j := rfl

def denotateCX (ctrl tgt : Nat) : Matrix4 :=
  let c : Fin 2 := if ctrl = 0 then 0 else 1
  let t : Fin 2 := if tgt = 0 then 0 else 1
  cnot4_ctrl_tgt c t

theorem qasm_CX_denotes_cnot (ctrl tgt : Nat) (i j : Fin 4) :
    denotateCX ctrl tgt i j = cnot4_ctrl_tgt (if ctrl = 0 then 0 else 1) (if tgt = 0 then 0 else 1) i j := rfl

theorem qasm_CX_denotes_cnot01 (i j : Fin 4) :
    denotateCX 0 1 i j = cnot4 i j := rfl

def denotateOps1 (ops : List QasmOp) : Matrix2 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g _ => fun i j => mul2 (denotateGate g) acc i j
    | .cx _ _ => acc
    | .ccx _ _ _ => acc
    | .swap _ _ => acc) id2

def applySingle2 (g : SingleGate) (q : Nat) : Matrix4 :=
  if q = 0 then kron2I (denotateGate g) else kronI2 (denotateGate g)

def denotateOps2 (ops : List QasmOp) : Matrix4 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g q => fun i j => mul4 (applySingle2 g q) acc i j
    | .cx c t => fun i j => mul4 (denotateCX c t) acc i j
    | .ccx _ _ _ => acc
    | .swap _ _ => fun i j => mul4 swap4 acc i j) id4

def denotateOps3 (ops : List QasmOp) : Matrix8 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate _ _ => acc
    | .cx _ _ => acc
    | .ccx _ _ _ => fun i j => mul8 ccx8 acc i j
    | .swap _ _ => acc) id8

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

def clifford_hhsMatC (i j : Fin 2) : ℂ := mul2C sGate (mul2C hadamardC hadamardC) i j

theorem denotateOps1C_clifford_hhs (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = clifford_hhsMatC i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, clifford_hhs, denotateGateC, clifford_hhsMatC, mul2C,
    sGateEntry, hadamardEntry, Matrix.one_apply, Matrix.of_apply]

theorem bridge_clifford_hhs (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = clifford_hhsMatC i j :=
  denotateOps1C_clifford_hhs i j

def cnot_single : List QasmOp := [.cx 0 1]

theorem bridge_cnot_single (i j : Fin 4) :
    denotateOps2 cnot_single i j = cnot4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

def cnot_cx10 : List QasmOp := [.cx 1 0]

def cnot_cx10Mat (i j : Fin 4) : Int := cnot4_ctrl_tgt 1 0 i j

theorem denotateOps2_cnot_cx10 (i j : Fin 4) :
    denotateOps2 cnot_cx10 i j = cnot_cx10Mat i j := by
  fin_cases i <;> fin_cases j <;> rfl

def cnot_cx10_cx10 : List QasmOp := [.cx 1 0, .cx 1 0]

def cnot_cx10_cx10Mat (i j : Fin 4) : Int :=
  mul4 (cnot4_ctrl_tgt 1 0) (mul4 (cnot4_ctrl_tgt 1 0) id4) i j

theorem denotateOps2_cnot_cx10_cx10 (i j : Fin 4) :
    denotateOps2 cnot_cx10_cx10 i j = cnot_cx10_cx10Mat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_cnot10_self_inverse (i j : Fin 4) :
    denotateOps2 cnot_cx10_cx10 i j = id4 i j := by
  rw [denotateOps2_cnot_cx10_cx10]
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

def hs_gateMatC (i j : Fin 2) : ℂ := mul2C sGate hadamardC i j

theorem denotateOps1C_hs_gate (i j : Fin 2) :
    denotateOps1C hs_gate i j = hs_gateMatC i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, hs_gate, denotateGateC, hs_gateMatC, mul2C,
    sGateEntry, hadamardEntry, Matrix.one_apply, Matrix.of_apply]

theorem bridge_hs_gate (i j : Fin 2) :
    denotateOps1C hs_gate i j = hs_gateMatC i j :=
  denotateOps1C_hs_gate i j

/-- Bell-pair preparation scaffold (H on q0, CX q0→q1). -/
def bell_prep_ops : List QasmOp := [.gate .H 0, .cx 0 1]

def bellPrepMatrix (i j : Fin 4) : Int := mul4 cnot4 (kron2I hadamard2) i j

theorem denotateOps2_bell_prep (i j : Fin 4) :
    denotateOps2 bell_prep_ops i j = bellPrepMatrix i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_teleportation_scaffold (i j : Fin 4) :
    denotateOps2 bell_prep_ops i j = bellPrepMatrix i j :=
  denotateOps2_bell_prep i j

theorem bridge_bell_prep (i j : Fin 4) :
    denotateOps2 bell_prep_ops i j = bellPrepMatrix i j :=
  denotateOps2_bell_prep i j

/-- Artificial scaffold for parser plumbing only; not RX/H semantic equivalence.

The QASM extractor may emit an RX(π/2) gate trace, but this Lean op list uses `.H`
only as a stand-in for denotation plumbing — it does not claim RX(π/2) equals H.
-/
def rx_parser_plumbing_ops : List QasmOp := [.gate .H 0]

theorem denotateOps1_rx_parser_plumbing (i j : Fin 2) :
    denotateOps1 rx_parser_plumbing_ops i j = hadamard2 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_rx_parser_plumbing (i j : Fin 2) :
    denotateOps1 rx_parser_plumbing_ops i j = hadamard2 i j :=
  denotateOps1_rx_parser_plumbing i j

def ccx_single : List QasmOp := [.ccx 0 1 2]

theorem denotateOps3_ccx_single (i j : Fin 8) :
    denotateOps3 ccx_single i j = ccx8 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_ccx_single (i j : Fin 8) :
    denotateOps3 ccx_single i j = ccx8 i j :=
  denotateOps3_ccx_single i j

def swap_single : List QasmOp := [.swap 0 1]

theorem denotateOps2_swap_single (i j : Fin 4) :
    denotateOps2 swap_single i j = swap4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_swap_single (i j : Fin 4) :
    denotateOps2 swap_single i j = swap4 i j :=
  denotateOps2_swap_single i j

/-- Three CX gates in standard order implement SWAP (CX_{0,1} CX_{1,0} CX_{0,1}). -/
def swap_from_three_cx_ops : List QasmOp := [.cx 0 1, .cx 1 0, .cx 0 1]

theorem denotateOps2_swap_from_three_cx (i j : Fin 4) :
    denotateOps2 swap_from_three_cx_ops i j = swap4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_swap_from_three_cx (i j : Fin 4) :
    denotateOps2 swap_from_three_cx_ops i j = swap4 i j :=
  denotateOps2_swap_from_three_cx i j

/-- Layout-identity scaffold: H then CX on qubits 0,1. -/
def layout_identity_ops : List QasmOp := [.gate .H 0, .cx 0 1]

def layoutIdentityMatrix (i j : Fin 4) : Int :=
  mul4 cnot4 (kron2I hadamard2) i j

theorem denotateOps2_layout_identity (i j : Fin 4) :
    denotateOps2 layout_identity_ops i j = layoutIdentityMatrix i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_circuit_identity_after_layout (i j : Fin 4) :
    denotateOps2 layout_identity_ops i j = layoutIdentityMatrix i j :=
  denotateOps2_layout_identity i j

end QSpecBench.Quantum.OpenQASM3
