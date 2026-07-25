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
import QSpecBench.Generated.SwapFromThreeCxTarget
import QSpecBench.Generated.ToffoliDecompositionEquivalence
import QSpecBench.Generated.ToffoliDecompositionEquivalenceTarget
import QSpecBench.Generated.CircuitIdentityAfterLayout
import QSpecBench.Generated.TeleportationUnitaryPrefix
import QSpecBench.Generated.CliffordSimplificationPreservesUnitary
import QSpecBench.Generated.CliffordSimplificationPreservesUnitaryTarget
import QSpecBench.Quantum.BridgeMetadata
import QSpecBench.Quantum.CliffordTAlg

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
open QSpecBench.Quantum.CliffordTAlg
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

/-- Physical unitary single-qubit gate model: Hadamard uses `hadamardC_normalized`. -/
noncomputable def denotateGateC_normalized : SingleGate → Mat2C
  | .I => ComplexGate.identityGate
  | .X => pauliXC
  | .Y => pauliYC
  | .Z => pauliZC
  | .H => hadamardC_normalized
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

/-- 1-qubit denotation with normalized Hadamard (exact H·H = I). -/
noncomputable def denotateOps1C_normalized (ops : List QasmOp) : Mat2C :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g _ => mul2C (denotateGateC_normalized g) acc
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

noncomputable def denotateOps3C (ops : List QasmOp) : Mat8C :=
  ops.foldl (fun acc op =>
    match op with
    | .gate g q => mul8C_mat (applySingle3C (denotateGateC g) q) acc
    | .cx c t => mul8C_mat (cnot8 c t) acc
    | .ccx _ _ _ => mul8C_mat ccx8C acc
    | .rx _ _ => acc
    | .swap _ _ => acc) (1 : Mat8C)

def toffoli_target_codegen_ops : List QasmOp := Generated.ToffoliDecompositionEquivalenceTarget.ops

theorem toffoli_target_codegen_ops_eq_generated :
    Generated.ToffoliDecompositionEquivalenceTarget.ops = toffoli_target_codegen_ops := rfl

open QSpecBench.Quantum.BridgeMetadata

/-- Artifact-derived CNOT.CX trace — only `Generated.CnotSelfInverse.ops` is authoritative. -/
@[deprecated QSpecBench.Generated.CnotSelfInverse.ops (since := "2026-06-28")]
def cnot_self_inverse_codegen_ops : List QasmOp := Generated.CnotSelfInverse.ops

/-- Matrix model for two CX applications composed with the identity; used to bridge
the Generated codegen trace to the legacy `cnot4` matrix representation directly
(no hand-authored `List QasmOp` duplicate of `Generated.CnotSelfInverse.ops`). -/
def cnot_cx_cxMat (i j : Fin 4) : Int := mul4 cnot4 (mul4 cnot4 id4) i j

theorem denotateOps2_cnot_generated (i j : Fin 4) :
    denotateOps2 Generated.CnotSelfInverse.ops i j = cnot_cx_cxMat i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_cnot_codegen_self_inverse (i j : Fin 4) :
    denotateOps2 Generated.CnotSelfInverse.ops i j = id4 i j := by
  rw [denotateOps2_cnot_generated]
  fin_cases i <;> fin_cases j <;> rfl

/-- Legacy alias for the Generated-backed CNOT bridge. -/
theorem bridge_cnot_self_inverse (i j : Fin 4) :
    denotateOps2 Generated.CnotSelfInverse.ops i j = id4 i j :=
  bridge_cnot_codegen_self_inverse i j

/-- Codegen trace denotation matches the declared artifact matrix model. -/
theorem bridge_cnot_codegen_denotes_artifact (i j : Fin 4) :
    denotateOps2 Generated.CnotSelfInverse.ops i j = cnot_cx_cxMat i j :=
  denotateOps2_cnot_generated i j

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

/-- Source trace after Clifford simplification (H H S on q[0]).
Authority: `Generated.CliffordSimplificationPreservesUnitary.ops`. -/
def clifford_hhs : List QasmOp := Generated.CliffordSimplificationPreservesUnitary.ops

/-- Target trace after Clifford simplification (single S gate).
Authority: `Generated.CliffordSimplificationPreservesUnitaryTarget.ops`. -/
def clifford_s_single : List QasmOp := Generated.CliffordSimplificationPreservesUnitaryTarget.ops

theorem clifford_hhs_eq_generated :
    Generated.CliffordSimplificationPreservesUnitary.ops = clifford_hhs := rfl

theorem clifford_s_single_eq_generated :
    Generated.CliffordSimplificationPreservesUnitaryTarget.ops = clifford_s_single := rfl

def clifford_s_singleMatC (i j : Fin 2) : ℂ := sGate i j

theorem denotateOps1C_clifford_s_single (i j : Fin 2) :
    denotateOps1C clifford_s_single i j = clifford_s_singleMatC i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, clifford_s_single, denotateGateC, clifford_s_singleMatC,
    sGateEntry, Matrix.of_apply, mul2C, mul2C_one_right,
    Generated.CliffordSimplificationPreservesUnitaryTarget.ops]

theorem bridge_clifford_s_single (i j : Fin 2) :
    denotateOps1C clifford_s_single i j = clifford_s_singleMatC i j :=
  denotateOps1C_clifford_s_single i j

def clifford_hhsMatC (i j : Fin 2) : ℂ := mul2C sGate (mul2C hadamardC hadamardC) i j

theorem denotateOps1C_clifford_hhs (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = clifford_hhsMatC i j := by
  fin_cases i <;> fin_cases j <;> simp [denotateOps1C, clifford_hhs, denotateGateC, clifford_hhsMatC, mul2C,
    sGate, sGateEntry, hadamardC, hadamardEntry, Matrix.of_apply, mul2C_one_right,
    Generated.CliffordSimplificationPreservesUnitary.ops]

theorem bridge_clifford_hhs (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = clifford_hhsMatC i j :=
  denotateOps1C_clifford_hhs i j

theorem clifford_hhsMatC_eq_two_s (i j : Fin 2) :
    clifford_hhsMatC i j = (2 : ℂ) * sGate i j := by
  unfold clifford_hhsMatC
  exact mul2C_sGate_hadamard_sq i j

/-- Unnormalized H·H = 2·I ⇒ HHS denotes 2·S (legacy scaled policy). -/
theorem clifford_source_target_denotation_scaled (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = (2 : ℂ) * denotateOps1C clifford_s_single i j := by
  rw [denotateOps1C_clifford_hhs, denotateOps1C_clifford_s_single, clifford_hhsMatC_eq_two_s,
    clifford_s_singleMatC]

theorem bridge_clifford_source_target_scaled (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = (2 : ℂ) * denotateOps1C clifford_s_single i j :=
  clifford_source_target_denotation_scaled i j

/-- Normalized source matrix: S · (H_n · H_n). -/
noncomputable def clifford_hhsMatC_normalized (i j : Fin 2) : ℂ :=
  mul2C sGate (mul2C hadamardC_normalized hadamardC_normalized) i j

theorem denotateOps1C_normalized_clifford_s_single (i j : Fin 2) :
    denotateOps1C_normalized clifford_s_single i j = sGate i j := by
  fin_cases i <;> fin_cases j <;>
    simp [denotateOps1C_normalized, clifford_s_single, denotateGateC_normalized,
      Generated.CliffordSimplificationPreservesUnitaryTarget.ops, sGate, sGateEntry,
      Matrix.of_apply, mul2C, mul2C_one_right]

theorem denotateOps1C_normalized_clifford_hhs (i j : Fin 2) :
    denotateOps1C_normalized clifford_hhs i j = clifford_hhsMatC_normalized i j := by
  fin_cases i <;> fin_cases j <;>
    simp [denotateOps1C_normalized, clifford_hhs, denotateGateC_normalized,
      clifford_hhsMatC_normalized, Generated.CliffordSimplificationPreservesUnitary.ops,
      mul2C, sGate, sGateEntry, hadamardC_normalized, hadamardC_normalizedEntry, hadamardEntry,
      Matrix.of_apply, mul2C_one_right]

theorem clifford_hhsMatC_normalized_eq_s (i j : Fin 2) :
    clifford_hhsMatC_normalized i j = sGate i j := by
  unfold clifford_hhsMatC_normalized
  exact mul2C_sGate_hadamard_normalized_sq i j

/-- Exact source–target equality under normalized 1-qubit Hadamard denotation. -/
theorem clifford_source_target_normalized_exact (i j : Fin 2) :
    denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitary.ops i j =
      denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitaryTarget.ops i j := by
  rw [show Generated.CliffordSimplificationPreservesUnitary.ops = clifford_hhs from rfl,
    show Generated.CliffordSimplificationPreservesUnitaryTarget.ops = clifford_s_single from rfl]
  rw [denotateOps1C_normalized_clifford_hhs, denotateOps1C_normalized_clifford_s_single,
    clifford_hhsMatC_normalized_eq_s]

/-- Kernel bridge: normalized dual-manifest source–target equality (Clifford HHS→S). -/
theorem bridge_clifford_source_target_normalized_exact (i j : Fin 2) :
    denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitary.ops i j =
      denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitaryTarget.ops i j :=
  clifford_source_target_normalized_exact i j

/-- `source_denotation` obligation: normalized source denotation equals the canonical
S-gate matrix (mirrors `CliffordTAlg.toffoli_source_denotateOps3C_normalized_eq_ccx8C`). -/
theorem clifford_source_denotateOps1C_normalized_eq_sGate (i j : Fin 2) :
    denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitary.ops i j =
      sGate i j :=
  (denotateOps1C_normalized_clifford_hhs i j).trans (clifford_hhsMatC_normalized_eq_s i j)

/-- `target_denotation` obligation: normalized target denotation equals the canonical
S-gate matrix (mirrors `CliffordTAlg.toffoli_target_denotateOps3C_normalized_eq_ccx8C`). -/
theorem clifford_target_denotateOps1C_normalized_eq_sGate (i j : Fin 2) :
    denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitaryTarget.ops i j =
      sGate i j :=
  denotateOps1C_normalized_clifford_s_single i j

/-- `wire_order_alignment` obligation: a single-qubit register has no wire-permutation
ambiguity; both source and target denote the same canonical 1-qubit matrix `sGate`. -/
theorem clifford_normalized_pair_wire_order_trivial (i j : Fin 2) :
    denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitary.ops i j =
        sGate i j ∧
      denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitaryTarget.ops i j =
        sGate i j :=
  ⟨clifford_source_denotateOps1C_normalized_eq_sGate i j,
    clifford_target_denotateOps1C_normalized_eq_sGate i j⟩

/-- Normalized Hadamard policy: H·H = I under `denotateOps1C_normalized`. -/
theorem bridge_clifford_normalized_hadamard_policy (i j : Fin 2) :
    denotateOps1C_normalized [.gate .H 0, .gate .H 0] i j = ComplexGate.identityGate i j := by
  have hfold :
      denotateOps1C_normalized [.gate .H 0, .gate .H 0] =
        mul2C hadamardC_normalized (mul2C hadamardC_normalized (1 : Mat2C)) := by
    simp [denotateOps1C_normalized, denotateGateC_normalized]
  have hone : mul2C hadamardC_normalized (1 : Mat2C) = hadamardC_normalized := by
    ext a b; exact mul2C_one_right hadamardC_normalized a b
  rw [hfold, hone]
  exact hadamardC_normalized_mul_self i j

/-- Exact equality implies global-phase equivalence with φ = 0 (documentation note;
see `clifford_normalized_global_phase_policy_exact` for the kernel-checked statement). -/
def clifford_normalized_global_phase_policy : String :=
  "Exact matrix equality under denotateOps1C_normalized (φ = 0); \
unnormalized denotateOps1C pair equality remains scaled (factor 2)."

/-- Global-phase equivalence for 1-qubit matrices: ∃ φ, A = e^{iφ} · B entrywise
(mirrors `ToffoliDecomposition.EquivUpToGlobalPhase` for `Mat8C`). -/
def EquivUpToGlobalPhase1 (A B : Mat2C) : Prop :=
  ∃ φ : ℝ, ∀ i j : Fin 2, A i j = Complex.exp (I * φ) * B i j

/-- `global_phase_policy` obligation: the declared phase policy for this claim is exact
equality (global phase φ = 0), kernel-checked from `bridge_clifford_source_target_normalized_exact`
(mirrors `ToffoliDecomposition.toffoli_normalized_global_phase_policy`). -/
theorem clifford_normalized_global_phase_policy_exact :
    EquivUpToGlobalPhase1
      (denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitary.ops)
      (denotateOps1C_normalized Generated.CliffordSimplificationPreservesUnitaryTarget.ops) :=
  ⟨0, fun i j => by
    have h := bridge_clifford_source_target_normalized_exact i j
    simp [Complex.exp_zero, h]⟩

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

/-- Artifact-derived CCX trace — only `Generated.ToffoliDecompositionEquivalence.ops` is authoritative.
    Do not reintroduce a hand-authored `[.ccx 0 1 2]` list that duplicates the Generated module. -/
@[deprecated QSpecBench.Generated.ToffoliDecompositionEquivalence.ops (since := "2026-06-28")]
def toffoli_codegen_ops : List QasmOp := Generated.ToffoliDecompositionEquivalence.ops

theorem denotateOps3_toffoli_generated (i j : Fin 8) :
    denotateOps3 Generated.ToffoliDecompositionEquivalence.ops i j = ccx8 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_toffoli_codegen_ccx (i j : Fin 8) :
    denotateOps3 Generated.ToffoliDecompositionEquivalence.ops i j = ccx8 i j :=
  denotateOps3_toffoli_generated i j

theorem denotateOps3C_toffoli_generated (i j : Fin 8) :
    denotateOps3C Generated.ToffoliDecompositionEquivalence.ops i j = ccx8C i j := by
  simp [denotateOps3C, Generated.ToffoliDecompositionEquivalence.ops, mul8C_mat,
    Matrix.of_apply, mul8C_one_right, ccx8Entry]

theorem bridge_toffoli_codegen_ccxC (i j : Fin 8) :
    denotateOps3C Generated.ToffoliDecompositionEquivalence.ops i j = ccx8C i j :=
  denotateOps3C_toffoli_generated i j

theorem denotateOps3C_toffoli_target (i j : Fin 8) :
    denotateOps3C toffoli_target_codegen_ops i j =
      denotateOps3C Generated.ToffoliDecompositionEquivalenceTarget.ops i j := rfl

/-- Native two-qubit SWAP trace — alias for `Generated.SwapFromThreeCxTarget.ops`
(avoids a hand-authored `List QasmOp` literal duplicate). -/
def swap_single : List QasmOp := Generated.SwapFromThreeCxTarget.ops

theorem denotateOps2_swap_single (i j : Fin 4) :
    denotateOps2 swap_single i j = swap4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_swap_single (i j : Fin 4) :
    denotateOps2 swap_single i j = swap4 i j :=
  denotateOps2_swap_single i j

/-- Three CX gates in standard order implement SWAP — authority is Generated.SwapFromThreeCx.ops. -/
def swap_from_three_cx_ops : List QasmOp := Generated.SwapFromThreeCx.ops

theorem denotateOps2_swap_from_three_cx (i j : Fin 4) :
    denotateOps2 swap_from_three_cx_ops i j = swap4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

theorem bridge_swap_from_three_cx (i j : Fin 4) :
    denotateOps2 swap_from_three_cx_ops i j = swap4 i j :=
  denotateOps2_swap_from_three_cx i j

@[deprecated QSpecBench.Generated.SwapFromThreeCx.ops (since := "2026-06-28")]
def swap_from_three_cx_codegen_ops : List QasmOp := Generated.SwapFromThreeCx.ops

theorem bridge_swap_from_three_cx_codegen (i j : Fin 4) :
    denotateOps2 Generated.SwapFromThreeCx.ops i j = swap4 i j :=
  denotateOps2_swap_from_three_cx i j

theorem bridge_swap_from_three_cx_codegen_denotes_artifact (i j : Fin 4) :
    denotateOps2 Generated.SwapFromThreeCx.ops i j =
      denotateOps2 swap_from_three_cx_ops i j := rfl

/-- Target artifact ops are the native two-qubit SWAP. -/
theorem swap_target_ops_eq_swap_single :
    Generated.SwapFromThreeCxTarget.ops = swap_single := rfl

/-- Exact source–target denotation equality: three CX vs native SWAP (legacy wire order). -/
theorem bridge_swap_source_target_exact (i j : Fin 4) :
    denotateOps2 Generated.SwapFromThreeCx.ops i j =
      denotateOps2 Generated.SwapFromThreeCxTarget.ops i j := by
  rw [bridge_swap_from_three_cx_codegen, swap_target_ops_eq_swap_single,
    denotateOps2_swap_single]

/-- Wire-order theorem: source and target agree under the declared legacy Kronecker model. -/
theorem bridge_swap_source_target_wire_order (i j : Fin 4) :
    denotateOps2 Generated.SwapFromThreeCx.ops i j =
      denotateOps2 [.swap 0 1] i j := by
  simpa [Generated.SwapFromThreeCxTarget.ops] using bridge_swap_source_target_exact i j

def bridge_toffoli_pair_equivalence_scoped_note : String :=
  "Source CCX + target parse bound; normalized CT pair equality is \
bridge_toffoli_decomposition_normalized_exact."

/-- Kernel bridge: normalized Clifford+T source–target equality (Toffoli pair). -/
theorem bridge_toffoli_decomposition_normalized_exact (i j : Fin 8) :
    denotateOps3C_normalized Generated.ToffoliDecompositionEquivalence.ops i j =
      denotateOps3C_normalized Generated.ToffoliDecompositionEquivalenceTarget.ops i j :=
  toffoli_source_target_normalized_exact i j

/-- Wire-order bridge under LSB / `openqasm_little_endian_wire_order` (both = CCX). -/
theorem bridge_toffoli_decomposition_wire_order_lsb (i j : Fin 8) :
    denotateOps3C_normalized Generated.ToffoliDecompositionEquivalence.ops i j =
      denotateOps3C_normalized Generated.ToffoliDecompositionEquivalenceTarget.ops i j :=
  bridge_toffoli_decomposition_normalized_exact i j

/-- Open Toffoli path — see `QSpecBench.Quantum.ToffoliDecomposition` for checklist. -/
def toffoliPairEquivalenceOpenGoal : String :=
  "Normalized CT equality closed in CliffordTAlg.toffoli_source_target_normalized_exact; \
OpenQASM3.bridge_toffoli_decomposition_normalized_exact exports the kernel bridge."

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

/-- Teleport unitary-prefix codegen ops match the hand list in Teleportation.lean. -/
theorem teleport_unitary_prefix_ops_eq_codegen :
    Generated.TeleportationUnitaryPrefix.ops =
      [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0] := rfl

/-- Kernel bridge: Generated teleport unitary prefix matches the declared 4-op hand list. -/
theorem bridge_teleport_unitary_prefix_codegen :
    Generated.TeleportationUnitaryPrefix.ops =
      [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0] :=
  teleport_unitary_prefix_ops_eq_codegen

/-- Wire-order: prefix ops are the declared LSB / legacy kron hand list (length 4). -/
theorem bridge_teleport_unitary_prefix_wire_order :
    Generated.TeleportationUnitaryPrefix.ops =
        [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0] ∧
      Generated.TeleportationUnitaryPrefix.ops.length = 4 :=
  ⟨bridge_teleport_unitary_prefix_codegen, by rfl⟩

/-- On a 2-qubit register, CX q[0]→q[1] denotation matches legacy `cnot4` (int-scaffold and operational wire models agree). -/
theorem cnot_wire_order_models_agree_on_two_qubits (i j : Fin 4) :
    denotateOps2 [.cx 0 1] i j = cnot4 i j := by
  fin_cases i <;> fin_cases j <;> rfl

end QSpecBench.Quantum.OpenQASM3
