import QSpecBench.Quantum.QasmOp
import QSpecBench.Quantum.ComplexGate
import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.CliffordTAlg
import QSpecBench.Generated.ToffoliDecompositionEquivalence
import QSpecBench.Generated.ToffoliDecompositionEquivalenceTarget
import Mathlib.Tactic.FinCases

/-!
# Toffoli decomposition: lemma library and normalized pair equality.

## Status

- Source CCX: `denotateOps3C` equals `ccx8C` (kernel-checked in `OpenQASM3`).
- **Closed (normalized Clifford+T model):**
  `CliffordTAlg.toffoli_source_target_normalized_exact` /
  `OpenQASM3.bridge_toffoli_decomposition_normalized_exact` —
  `denotateOps3C_normalized` source = target = `ccx8C` (LSB wires, algebraic H/T).
- Gate atoms H/T/Tdg match ComplexGate; CT Array fold is the trusted composition
  semantics for the pair claim.
- Phase policy φ = 0 and LSB wire-order lemmas discharge the corresponding obligations.
- Benchmark maturity: `artifact_bound_reference_claim` under the narrowed informal claim.
- Unnormalized `denotateOps3C` / default Python `qasm_matrix` Hadamard: exact entrywise
  equality remains **out of scope**.
-/

namespace QSpecBench.Quantum.ToffoliDecomposition

open QSpecBench.Quantum.ComplexGate
open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Quantum.CliffordTAlg
open QSpecBench.Quantum.QasmOp
open QSpecBench.Generated
open Complex

/-- Exact matrix equality (too strong under unnormalized H). -/
def ExactDenotationEq (A B : Mat8C) : Prop :=
  ∀ i j : Fin 8, A i j = B i j

/-- Global-phase equivalence: ∃ φ, A = e^{iφ} · B entrywise. -/
def EquivUpToGlobalPhase (A B : Mat8C) : Prop :=
  ∃ φ : ℝ, ∀ i j : Fin 8, A i j = Complex.exp (I * φ) * B i j

/-- Nonzero complex scale (covers unnormalized H·H = 2·I style factors). -/
def EquivUpToNonzeroScale (A B : Mat8C) : Prop :=
  ∃ c : ℂ, c ≠ 0 ∧ ∀ i j : Fin 8, A i j = c * B i j

theorem denotateOps3C_nil : denotateOps3C ([] : List QasmOp) = (1 : Mat8C) := rfl

theorem denotateOps3C_singleton_gate (g : SingleGate) (q : Nat) (i j : Fin 8) :
    denotateOps3C [.gate g q] i j = applySingle3C (denotateGateC g) q i j := by
  simp [denotateOps3C, mul8C_mat, Matrix.of_apply, mul8C_one_right]

theorem denotateOps3C_singleton_cx (c t : Nat) (i j : Fin 8) :
    denotateOps3C [.cx c t] i j = cnot8 c t i j := by
  simp [denotateOps3C, mul8C_mat, Matrix.of_apply, mul8C_one_right]

theorem denotateOps3C_singleton_ccx (i j : Fin 8) :
    denotateOps3C [.ccx 0 1 2] i j = ccx8C i j :=
  denotateOps3C_toffoli_generated i j

theorem toffoli_source_ops_length :
    Generated.ToffoliDecompositionEquivalence.ops.length = 1 := rfl

theorem toffoli_target_ops_length :
    Generated.ToffoliDecompositionEquivalenceTarget.ops.length = 15 := rfl

theorem toffoli_target_head_is_H2 :
    Generated.ToffoliDecompositionEquivalenceTarget.ops.head? =
      some (.gate .H 2) := rfl

theorem toffoli_target_prefix1_denotation (i j : Fin 8) :
    denotateOps3C [.gate .H 2] i j = applySingle3C hadamardC 2 i j := by
  simpa [denotateGateC] using denotateOps3C_singleton_gate .H 2 i j

/-- Source denotation is the native CCX permutation matrix. -/
theorem toffoli_source_denotes_ccx8C (i j : Fin 8) :
    denotateOps3C Generated.ToffoliDecompositionEquivalence.ops i j = ccx8C i j :=
  denotateOps3C_toffoli_generated i j

/-- Wire-order: source CCX uses controls 0,1 and target 2 (LSB = q0). -/
theorem toffoli_source_wire_order_ccx :
    ccx8C ⟨3, by decide⟩ ⟨7, by decide⟩ = 1 ∧
      ccx8C ⟨7, by decide⟩ ⟨3, by decide⟩ = 1 :=
  ⟨ccx8C_flips_011_111.1, ccx8C_flips_011_111.2.1⟩

/-- Gate-semantics anchors used inside the 15-gate product. -/
theorem toffoli_gate_semantics_T_Tdg :
    (∀ i j : Fin 2, mul2C tGate tDagGate i j = ComplexGate.identityGate i j) ∧
      (∀ i j : Fin 2, mul2C tDagGate tGate i j = ComplexGate.identityGate i j) :=
  ⟨tGate_mul_tDagGate, tDagGate_mul_tGate⟩

theorem toffoli_cx_involutive_on_decomposition_wires :
    (∀ r : Fin 8, cnot8Col 1 2 (cnot8Col 1 2 r.val) = r.val) ∧
      (∀ r : Fin 8, cnot8Col 0 2 (cnot8Col 0 2 r.val) = r.val) ∧
      (∀ r : Fin 8, cnot8Col 0 1 (cnot8Col 0 1 r.val) = r.val) :=
  ⟨cnot8Col_12_involutive, cnot8Col_02_involutive, cnot8Col_01_involutive⟩

/-- Normalized H·H = I (physical convention). -/
theorem toffoli_normalized_hadamard_involutive (i j : Fin 2) :
    mul2C hadamardC_normalized hadamardC_normalized i j = ComplexGate.identityGate i j :=
  hadamardC_normalized_mul_self i j

/-- Kernel-checked exact pair equality under `denotateOps3C_normalized`. -/
theorem toffoli_normalized_source_target_exact (i j : Fin 8) :
    denotateOps3C_normalized Generated.ToffoliDecompositionEquivalence.ops i j =
      denotateOps3C_normalized Generated.ToffoliDecompositionEquivalenceTarget.ops i j :=
  toffoli_source_target_normalized_exact i j

theorem toffoli_normalized_exact_denotation_eq :
    ExactDenotationEq
      (denotateOps3C_normalized Generated.ToffoliDecompositionEquivalence.ops)
      (denotateOps3C_normalized Generated.ToffoliDecompositionEquivalenceTarget.ops) :=
  toffoli_normalized_source_target_exact

/-- Declared phase policy for this claim: exact equality (global phase φ = 0). -/
theorem toffoli_normalized_global_phase_policy :
    EquivUpToGlobalPhase
      (denotateOps3C_normalized Generated.ToffoliDecompositionEquivalence.ops)
      (denotateOps3C_normalized Generated.ToffoliDecompositionEquivalenceTarget.ops) :=
  ⟨0, fun i j => by
    have h := toffoli_normalized_source_target_exact i j
    simp [Complex.exp_zero, h]⟩

/-- Pair wire-order: both sides equal native CCX under LSB (`openqasm_little_endian_wire_order`). -/
theorem toffoli_normalized_pair_wire_order_lsb (i j : Fin 8) :
    denotateOps3C_normalized Generated.ToffoliDecompositionEquivalence.ops i j = ccx8C i j ∧
      denotateOps3C_normalized Generated.ToffoliDecompositionEquivalenceTarget.ops i j =
        ccx8C i j :=
  ⟨toffoli_source_denotateOps3C_normalized_eq_ccx8C i j,
    toffoli_target_denotateOps3C_normalized_eq_ccx8C i j⟩

/-- Gate-atom bridges: CT H/T/Tdg match ComplexGate normalized / exp matrices. -/
theorem toffoli_ct_gate_atoms_match_complexGate (i j : Fin 2) :
    (gate2 .H i.val j.val).toComplex = hadamardC_normalized i j ∧
      (gate2 .T i.val j.val).toComplex = tGate i j ∧
      (gate2 .Tdg i.val j.val).toComplex = tDagGate i j :=
  ⟨hadamardN_toComplex i j, tGateCT_toComplex i j, tDagGateCT_toComplex i j⟩

/-- Remaining residual gaps (algebra + ABRC wiring closed under narrowed claim). -/
def toffoliPairEquivalenceOpenGoal : String :=
  "Normalized Clifford+T denotation equality is kernel-checked and ABRC-bound \
(`bridge_toffoli_decomposition_normalized_exact`). Residual out-of-scope: \
unnormalized denotateOps3C pair equality; default Python 3-qubit legacy Kron."

/-- Checklist: algebra + ABRC closed under CT normalized claim. -/
def toffoliPairProofChecklist : List String :=
  [ "denotateOps3C fold/cons lemmas (partial: nil + singletons)",
    "T/Tdg and CX involution on decomposition wires (done)",
    "normalized Hadamard model + H·H = I (done)",
    "denotateOps3C_normalized target = ccx8C (done: CliffordTAlg)",
    "ExactDenotationEq source ↔ target under normalized CT model (done)",
    "global_phase_policy φ=0 from ExactDenotationEq (done)",
    "wire_order_alignment LSB / CCX (done)",
    "CT gate atoms ↔ hadamardC_normalized / tGate / tDagGate (done)",
    "ABRC elaborator + reviews + semantic_bridge (done under narrowed claim)" ]

#check toffoli_source_denotes_ccx8C
#check toffoli_target_ops_length
#check toffoli_gate_semantics_T_Tdg
#check toffoli_cx_involutive_on_decomposition_wires
#check toffoli_normalized_hadamard_involutive
#check toffoli_normalized_source_target_exact
#check toffoli_normalized_exact_denotation_eq
#check toffoli_normalized_global_phase_policy
#check toffoli_normalized_pair_wire_order_lsb
#check toffoli_ct_gate_atoms_match_complexGate
#check toffoliPairEquivalenceOpenGoal

end QSpecBench.Quantum.ToffoliDecomposition
