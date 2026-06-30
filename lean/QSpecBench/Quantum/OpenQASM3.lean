import QSpecBench.Quantum.QasmOp
import QSpecBench.Legacy.Matrix
import Mathlib.Tactic.FinCases
import QSpecBench.Legacy.Pauli
import QSpecBench.Legacy.CNOT
import QSpecBench.Legacy.QFT2
import QSpecBench.Quantum.Gate
import QSpecBench.Quantum.ComplexGate
import QSpecBench.Generated.CnotSelfInverse
import QSpecBench.Generated.HadamardConjugatesXToZ
import QSpecBench.Generated.SingleQubitGateCancellation
import QSpecBench.Generated.BellStatePreparation
import QSpecBench.Generated.SwapFromThreeCx
import QSpecBench.Generated.ToffoliDecompositionEquivalence
import QSpecBench.Generated.ToffoliDecompositionEquivalenceTarget
import QSpecBench.Generated.CircuitIdentityAfterLayout
import QSpecBench.Quantum.BridgeMetadata

/-!
# Denotational OpenQASM 3 semantics for the benchmark gate subset.

## Denotation split

- `denotateOps1IntScaffold`: integer Pauli/H matrix model (RX at π/2 maps to unnormalized H).
- `denotateOps1Complex` / `denotateOps1C`: complex unitary model (RX/H match Python `qasm_matrix`).
- Prefer `QSpecBench.Generated.*.ops` for codegen traces (legacy `*_codegen_ops` aliases deprecated).
-/

namespace QSpecBench.Quantum.OpenQASM3

open QSpecBench (Matrix2 Matrix4 Matrix8 mul2 mul4 mul8 id2 id4 id8 ccx8 swap4 kron2I kronI2 scale2 scale4 qft2 invqft2 qft2_mul_invqft2
  hadamard_conjugates_x hadamard_mul_self cnot_mul_self cnot4_ctrl_tgt_mul_self mul2_assoc)
open QSpecBench.Quantum (pauliY)
open QSpecBench.Quantum.ComplexGate
open QSpecBench.Quantum.QasmOp
open QSpecBench.Generated
open Complex

open QasmOp (SingleGate QasmOp)

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
    | .rx θ _ => mul2C (rxGate θ) acc
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

/-- Integer Pauli/H scaffold (1-qubit); RX(π/2) denoted as unnormalized H. -/
noncomputable def denotateOps1IntScaffold (ops : List QasmOp) : Matrix2 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g _ => fun i j => mul2 (denotateGate g) acc i j
    | .rx θ q => fun i j => mul2 (if θ = Real.pi / 2 then hadamard2 else id2) acc i j
    | .cx _ _ => acc
    | .ccx _ _ _ => acc
    | .swap _ _ => acc) id2

/-- Complex single-qubit denotation (H/S/T/RX); matches Python complex `qasm_matrix`. -/
noncomputable def denotateOps1Complex (ops : List QasmOp) : Mat2C := denotateOps1C ops

def applySingle2 (g : SingleGate) (q : Nat) : Matrix4 :=
  if q = 0 then kron2I (denotateGate g) else kronI2 (denotateGate g)

def denotateOps2 (ops : List QasmOp) : Matrix4 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g q => fun i j => mul4 (applySingle2 g q) acc i j
    | .cx c t => fun i j => mul4 (denotateCX c t) acc i j
    | .rx _ _ => acc
    | .ccx _ _ _ => acc
    | .swap _ _ => fun i j => mul4 swap4 acc i j) id4

def denotateOps3 (ops : List QasmOp) : Matrix8 :=
  ops.foldl (fun acc op =>
    match op with
    | .gate _ _ => acc
    | .cx _ _ => acc
    | .rx _ _ => acc
    | .ccx _ _ _ => fun i j => mul8 ccx8 acc i j
    | .swap _ _ => acc) id8

def cnot_cx_cx : List QasmOp := [.cx 0 1, .cx 0 1]

open QSpecBench.Quantum.BridgeMetadata

@[deprecated QSpecBench.Generated.CnotSelfInverse.ops (since := "2026-06-28")]
def cnot_self_inverse_codegen_ops : List QasmOp := Generated.CnotSelfInverse.ops

theorem cnot_codegen_ops_eq_hand_trace : Generated.CnotSelfInverse.ops = cnot_cx_cx := rfl

def cnot_cx_cxMat (i j : Fin 4) : Int := mul4 cnot4 (mul4 cnot4 id4) i j

theorem denotateOps2_cnot_cx_cx (i j : Fin 4) : denotateOps2 cnot_cx_cx i j = cnot_cx_cxMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_cnot_self_inverse (i j : Fin 4) :
    denotateOps2 cnot_cx_cx i j = id4 i j := by
  rw [denotateOps2_cnot_cx_cx]
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_cnot_codegen_self_inverse (i j : Fin 4) :
    denotateOps2 Generated.CnotSelfInverse.ops i j = id4 i j := by
  rw [cnot_codegen_ops_eq_hand_trace, bridge_cnot_self_inverse]

/-- Codegen trace denotation matches the declared artifact matrix model. -/
theorem bridge_cnot_codegen_denotes_artifact (i j : Fin 4) :
    denotateOps2 Generated.CnotSelfInverse.ops i j = cnot_cx_cxMat i j := by
  rw [cnot_codegen_ops_eq_hand_trace, denotateOps2_cnot_cx_cx]

/-- Codegen-aligned H-X-H trace (matches bridge-codegen stub). -/
@[deprecated QSpecBench.Generated.HadamardConjugatesXToZ.ops (since := "2026-06-28")]
def hadamard_conjugates_x_to_z_codegen_ops : List QasmOp := Generated.HadamardConjugatesXToZ.ops

def hadamard_hxh : List QasmOp := Generated.HadamardConjugatesXToZ.ops

theorem hadamard_codegen_ops_eq_hand_trace : Generated.HadamardConjugatesXToZ.ops = hadamard_hxh := rfl

def hadamard_hxhMat (i j : Fin 2) : Int := mul2 hadamard2 (mul2 pauliX2 hadamard2) i j

theorem denotateOps1IntScaffold_hadamard_hxh (i j : Fin 2) :
    denotateOps1IntScaffold hadamard_hxh i j = hadamard_hxhMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_hadamard_conjugates_x (i j : Fin 2) :
    denotateOps1IntScaffold hadamard_hxh i j = scale2 2 pauliZ2 i j := by
  rw [denotateOps1IntScaffold_hadamard_hxh, hadamard_hxhMat, mul2_assoc, hadamard_conjugates_x]

theorem bridge_hadamard_codegen_conjugates_x (i j : Fin 2) :
    denotateOps1IntScaffold Generated.HadamardConjugatesXToZ.ops i j = scale2 2 pauliZ2 i j := by
  rw [hadamard_codegen_ops_eq_hand_trace, bridge_hadamard_conjugates_x]

theorem bridge_hadamard_codegen_denotes_artifact (i j : Fin 2) :
    denotateOps1IntScaffold Generated.HadamardConjugatesXToZ.ops i j = hadamard_hxhMat i j := by
  rw [hadamard_codegen_ops_eq_hand_trace, denotateOps1IntScaffold_hadamard_hxh]

@[deprecated QSpecBench.Generated.SingleQubitGateCancellation.ops (since := "2026-06-28")]
def single_qubit_gate_cancellation_codegen_ops : List QasmOp := Generated.SingleQubitGateCancellation.ops

def hadamard_hh : List QasmOp := Generated.SingleQubitGateCancellation.ops

theorem hadamard_cancel_codegen_ops_eq_hand_trace :
    Generated.SingleQubitGateCancellation.ops = hadamard_hh := rfl

def hadamard_hhMat (i j : Fin 2) : Int := mul2 hadamard2 hadamard2 i j

theorem denotateOps1IntScaffold_hadamard_hh (i j : Fin 2) :
    denotateOps1IntScaffold hadamard_hh i j = hadamard_hhMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_hadamard_cancel (i j : Fin 2) :
    denotateOps1IntScaffold hadamard_hh i j = scale2 2 id2 i j := by
  rw [denotateOps1IntScaffold_hadamard_hh, hadamard_hhMat, hadamard_mul_self]

theorem bridge_hadamard_codegen_cancel (i j : Fin 2) :
    denotateOps1IntScaffold Generated.SingleQubitGateCancellation.ops i j = scale2 2 id2 i j := by
  rw [hadamard_cancel_codegen_ops_eq_hand_trace, bridge_hadamard_cancel]

theorem bridge_hadamard_codegen_cancel_denotes_artifact (i j : Fin 2) :
    denotateOps1IntScaffold Generated.SingleQubitGateCancellation.ops i j = hadamard_hhMat i j := by
  rw [hadamard_cancel_codegen_ops_eq_hand_trace, denotateOps1IntScaffold_hadamard_hh]

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

/-- Target trace after Clifford simplification (single S gate). -/
def clifford_s_single : List QasmOp := [.gate .S 0]

def clifford_s_singleMatC (i j : Fin 2) : ℂ := sGate i j

theorem denotateOps1C_clifford_s_single (i j : Fin 2) :
    denotateOps1C clifford_s_single i j = clifford_s_singleMatC i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, clifford_s_single, denotateGateC, clifford_s_singleMatC,
    sGateEntry, Matrix.of_apply, mul2C, mul2C_one_right]

theorem bridge_clifford_s_single (i j : Fin 2) :
    denotateOps1C clifford_s_single i j = clifford_s_singleMatC i j :=
  denotateOps1C_clifford_s_single i j

def clifford_hhsMatC (i j : Fin 2) : ℂ := mul2C sGate (mul2C hadamardC hadamardC) i j

theorem denotateOps1C_clifford_hhs (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = clifford_hhsMatC i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, clifford_hhs, denotateGateC, clifford_hhsMatC, mul2C,
    sGateEntry, hadamardEntry, Matrix.of_apply, mul2C_one_right, hadamardC_mul_self]

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
def bell_prep_ops : List QasmOp := Generated.BellStatePreparation.ops

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

/-- Codegen-aligned Bell prep trace (matches bridge-codegen stub). -/
@[deprecated QSpecBench.Generated.BellStatePreparation.ops (since := "2026-06-28")]
def bell_state_preparation_codegen_ops : List QasmOp := Generated.BellStatePreparation.ops

theorem bell_codegen_ops_eq_hand_trace :
    Generated.BellStatePreparation.ops = bell_prep_ops := rfl

theorem bridge_bell_codegen_prep (i j : Fin 4) :
    denotateOps2 Generated.BellStatePreparation.ops i j = bellPrepMatrix i j := by
  rw [bell_codegen_ops_eq_hand_trace, denotateOps2_bell_prep]

theorem bridge_bell_codegen_denotes_artifact (i j : Fin 4) :
    denotateOps2 Generated.BellStatePreparation.ops i j = bellPrepMatrix i j := by
  rw [bell_codegen_ops_eq_hand_trace, denotateOps2_bell_prep]

/-- RX(π/2) on qubit 0; int scaffold maps π/2 to unnormalized H. -/
noncomputable def rx_pi2_ops : List QasmOp := [.rx (Real.pi / 2) 0]

theorem denotateOps1C_rx_pi2 (i j : Fin 2) :
    denotateOps1C rx_pi2_ops i j = rxGate (Real.pi / 2) i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, rx_pi2_ops, rxGate, rxGateEntry, mul2C]

theorem denotateOps1IntScaffold_rx_pi2 (i j : Fin 2) :
    denotateOps1IntScaffold rx_pi2_ops i j = hadamard2 i j := by
  unfold denotateOps1IntScaffold rx_pi2_ops hadamard2
  fin_cases i <;> fin_cases j <;> simp [mul2, id2]

/-- Complex denotation of RX(π/2) matches standard rotation matrix (not unnormalized H). -/
theorem bridge_rx_pi2_denotation (i j : Fin 2) :
    denotateOps1C rx_pi2_ops i j = rxGate (Real.pi / 2) i j :=
  denotateOps1C_rx_pi2 i j

/-- Int scaffold: RX(π/2) denoted as unnormalized H (Python int-bridge model). -/
theorem bridge_rx_pi2_int_eq_h (i j : Fin 2) :
    denotateOps1IntScaffold rx_pi2_ops i j = hadamard2 i j :=
  denotateOps1IntScaffold_rx_pi2 i j

/-- Legacy parser-plumbing alias; prefer `rx_pi2_ops`. -/
noncomputable def rx_parser_plumbing_ops : List QasmOp := rx_pi2_ops

theorem bridge_rx_parser_plumbing (i j : Fin 2) :
    denotateOps1IntScaffold rx_parser_plumbing_ops i j = hadamard2 i j :=
  denotateOps1IntScaffold_rx_pi2 i j

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
def swap_from_three_cx_ops : List QasmOp := Generated.SwapFromThreeCx.ops

theorem denotateOps2_swap_from_three_cx (i j : Fin 4) :
    denotateOps2 swap_from_three_cx_ops i j = swap4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_swap_from_three_cx (i j : Fin 4) :
    denotateOps2 swap_from_three_cx_ops i j = swap4 i j :=
  denotateOps2_swap_from_three_cx i j

/-- Codegen-aligned three-CX SWAP trace (matches bridge-codegen stub). -/
@[deprecated QSpecBench.Generated.SwapFromThreeCx.ops (since := "2026-06-28")]
def swap_from_three_cx_codegen_ops : List QasmOp := Generated.SwapFromThreeCx.ops

theorem swap_codegen_ops_eq_hand_trace :
    Generated.SwapFromThreeCx.ops = swap_from_three_cx_ops := rfl

theorem bridge_swap_from_three_cx_codegen (i j : Fin 4) :
    denotateOps2 Generated.SwapFromThreeCx.ops i j = swap4 i j := by
  rw [swap_codegen_ops_eq_hand_trace, denotateOps2_swap_from_three_cx]

theorem bridge_swap_from_three_cx_codegen_denotes_artifact (i j : Fin 4) :
    denotateOps2 Generated.SwapFromThreeCx.ops i j = denotateOps2 swap_from_three_cx_ops i j := rfl

/-- Codegen-aligned CCX trace (matches bridge-codegen stub for toffoli source artifact). -/
@[deprecated QSpecBench.Generated.ToffoliDecompositionEquivalence.ops (since := "2026-06-28")]
def toffoli_codegen_ops : List QasmOp := Generated.ToffoliDecompositionEquivalence.ops

theorem toffoli_codegen_ops_eq_hand_trace :
    Generated.ToffoliDecompositionEquivalence.ops = ccx_single := rfl

theorem bridge_toffoli_codegen_ccx (i j : Fin 8) :
    denotateOps3 Generated.ToffoliDecompositionEquivalence.ops i j = ccx8 i j := by
  rw [toffoli_codegen_ops_eq_hand_trace, denotateOps3_ccx_single]

/-- Layout-identity scaffold: H then CX on qubits 0,1. -/
def layout_identity_ops : List QasmOp := Generated.CircuitIdentityAfterLayout.ops

theorem layout_identity_ops_eq_codegen :
    layout_identity_ops = Generated.CircuitIdentityAfterLayout.ops := rfl

def layoutIdentityMatrix (i j : Fin 4) : Int :=
  mul4 cnot4 (kron2I hadamard2) i j

theorem denotateOps2_layout_identity (i j : Fin 4) :
    denotateOps2 layout_identity_ops i j = layoutIdentityMatrix i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_circuit_identity_after_layout (i j : Fin 4) :
    denotateOps2 layout_identity_ops i j = layoutIdentityMatrix i j :=
  denotateOps2_layout_identity i j

theorem bridge_circuit_identity_after_layout_codegen (i j : Fin 4) :
    denotateOps2 Generated.CircuitIdentityAfterLayout.ops i j = layoutIdentityMatrix i j := by
  rw [← layout_identity_ops_eq_codegen, denotateOps2_layout_identity]

/-- On a 2-qubit register, CX q[0]→q[1] denotation matches legacy `cnot4` (int-scaffold and operational wire models agree). -/
theorem cnot_wire_order_models_agree_on_two_qubits (i j : Fin 4) :
    denotateOps2 [.cx 0 1] i j = cnot4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench.Quantum.OpenQASM3
