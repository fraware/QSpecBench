/- QSpecBench evidence: Toffoli source→target pair equivalence (partial kernel progress).

benchmark_id = "toffoli_decomposition_equivalence"
obligation_id = "decomposition_pair_denotation"
status = "partial"

Source: native CCX (`bridge_toffoli_codegen_ccx`, `bridge_toffoli_codegen_ccxC`).
Target: 15-gate H/T/CX decomposition (`toffoli_target_codegen_ops`, parse theorem bound).

Scoped pair bridge `bridge_toffoli_ccx_eq_target_decomposition` (source CCX + target parse) is
kernel-checked; full `denotateOps3C` source = target (exact or global phase) remains open.
QCEC certifies physical equivalence externally. Policy: notes/pair_equivalence_policy.md.
-/

import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.OpenQASM3Parser

#check QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccx
#check QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccxC
#check QSpecBench.Quantum.OpenQASM3.toffoli_target_codegen_ops_eq_hand_trace
#check QSpecBench.Quantum.OpenQASM3Parser.parseQasmSource_toffoli_target_kernel_eq_generated_ops
#check QSpecBench.Quantum.OpenQASM3Parser.bridge_toffoli_ccx_eq_target_decomposition
#check QSpecBench.Quantum.OpenQASM3.denotateOps3C_toffoli_target
