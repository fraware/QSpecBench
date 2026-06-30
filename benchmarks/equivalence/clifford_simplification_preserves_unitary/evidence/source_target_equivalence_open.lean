/- QSpecBench evidence: open source→target denotation equivalence (partial kernel progress).

benchmark_id = "clifford_simplification_preserves_unitary"
obligation_id = "compiler_source_target_denotation"
status = "partial"

Source trace: H H S on q[0] (`bridge_clifford_hhs`, manifest-bound).
Target trace: S on q[0] (`bridge_clifford_s_single`, manifest-bound + target codegen hashes).

Kernel-checked: source/target codegen traces denote declared complex matrices; HHS = 2·S under
unnormalized Hadamard normalization (global phase / scale policy in semantic_bridge).
Exact matrix equality `denotateOps1C clifford_hhs = denotateOps1C clifford_s_single` remains
blocked on normalized-unitary policy; QCEC certifies pair equivalence externally.
-/

import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.QasmOp

open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Quantum.QasmOp
open Complex

theorem source_trace_is_hhs :
    clifford_hhs = [.gate .H 0, .gate .H 0, .gate .S 0] := by native_decide

theorem target_trace_is_single_s :
    clifford_s_single = [.gate .S 0] := by native_decide

theorem target_codegen_denotes_clifford_s_single (i j : Fin 2) :
    denotateOps1C clifford_s_single i j = clifford_s_singleMatC i j :=
  denotateOps1C_clifford_s_single i j

theorem source_codegen_denotes_clifford_hhs (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = clifford_hhsMatC i j :=
  denotateOps1C_clifford_hhs i j

/-- Unnormalized H·H = 2·I ⇒ HHS denotes 2·S (complex model). -/
theorem clifford_source_target_denotation_scaled (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = (2 : ℂ) * denotateOps1C clifford_s_single i j := by
  rw [denotateOps1C_clifford_hhs, denotateOps1C_clifford_s_single]
  fin_cases i <;> fin_cases j <;>
    simp [clifford_hhsMatC, clifford_s_singleMatC, mul2C, hadamardC_mul_self, sGateEntry,
      identityGate, identityEntry, Matrix.of_apply, mul2C_one_right]

#check bridge_clifford_hhs
#check bridge_clifford_s_single
#check source_trace_is_hhs
#check target_trace_is_single_s
#check clifford_source_target_denotation_scaled
