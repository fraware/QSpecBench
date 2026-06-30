/- QSpecBench evidence: source→target denotation equivalence (kernel progress).

benchmark_id = "clifford_simplification_preserves_unitary"
obligation_id = "compiler_source_target_denotation"
status = "partial"

Source trace: H H S on q[0] (`bridge_clifford_hhs`, manifest-bound).
Target trace: S on q[0] (`bridge_clifford_s_single`, manifest-bound + target codegen hashes).

Kernel-checked under compiler_trace_scaled policy (factor 2):
  `bridge_clifford_source_target_scaled` — unnormalized H·H = 2·I ⇒ HHS = 2·S.
Exact matrix equality remains false in unnormalized complex model; QCEC certifies physical
unitary equivalence. Policy: notes/normalized_unitary_policy.md.
-/

import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

theorem source_trace_is_hhs :
    clifford_hhs = [.gate .H 0, .gate .H 0, .gate .S 0] := rfl

theorem target_trace_is_single_s :
    clifford_s_single = [.gate .S 0] := rfl

theorem clifford_source_target_denotation_scaled (i j : Fin 2) :
    denotateOps1C clifford_hhs i j = (2 : ℂ) * denotateOps1C clifford_s_single i j :=
  bridge_clifford_source_target_scaled i j

#check QSpecBench.Quantum.OpenQASM3.bridge_clifford_hhs
#check QSpecBench.Quantum.OpenQASM3.bridge_clifford_s_single
#check QSpecBench.Quantum.OpenQASM3.bridge_clifford_source_target_scaled
