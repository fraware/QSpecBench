/- QSpecBench evidence: open source→target denotation equivalence (not kernel-checked).

benchmark_id = "clifford_simplification_preserves_unitary"
obligation_id = "compiler_source_target_denotation"
status = "open"

Source trace: H H S on q[0] (`bridge_clifford_hhs`, manifest-bound).
Target trace: S on q[0] (`bridge_clifford_s_single`, manifest-bound + target codegen hashes).

A kernel-checked compiler equivalence would require a Lean theorem relating
`denotateOps1C clifford_hhs` to `denotateOps1C clifford_s_single` (global phase policy
declared). QCEC certifies the pair externally; this file records the proof gap only.

## Checked lemmas (target-side codegen binding)

Target simplified trace `[.gate .S 0]` matches `clifford_s_single` and its complex denotation.
Source/target unitary equivalence remains open.
-/

import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.QasmOp

open QSpecBench.Quantum.OpenQASM3
open QSpecBench.Quantum.QasmOp

theorem target_trace_is_single_s :
    clifford_s_single = [.gate .S 0] := by native_decide

theorem target_codegen_denotes_clifford_s_single (i j : Fin 2) :
    denotateOps1C clifford_s_single i j = clifford_s_singleMatC i j :=
  denotateOps1C_clifford_s_single i j

#check bridge_clifford_hhs
#check bridge_clifford_s_single
#check target_trace_is_single_s
#check target_codegen_denotes_clifford_s_single
