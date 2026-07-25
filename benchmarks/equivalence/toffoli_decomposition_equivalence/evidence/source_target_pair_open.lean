/- QSpecBench evidence: Toffoli source→target pair equivalence (normalized algebra closed).

benchmark_id = "toffoli_decomposition_equivalence"
obligation_id = "decomposition_pair_denotation"
status = "partial"

Source: native CCX (`bridge_toffoli_codegen_ccx`, `bridge_toffoli_codegen_ccxC`).
Target: 15-gate H/T/CX decomposition (`toffoli_target_codegen_ops`, parse theorem bound).

Kernel-checked normalized equality:
  `QSpecBench.Quantum.CliffordTAlg.toffoli_source_target_normalized_exact`
  (and `ToffoliDecomposition.toffoli_normalized_source_target_exact`).

Exact unnormalized `denotateOps3C` source = target remains false. ABRC promotion blocked on
elaborator binding, reviews, CT↔Complex.exp fold agreement, and declared wire/phase policy
wiring. Policy: notes/pair_equivalence_policy.md.
-/

import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.OpenQASM3Parser
import QSpecBench.Quantum.ToffoliDecomposition
import QSpecBench.Quantum.CliffordTAlg

#check QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccx
#check QSpecBench.Quantum.OpenQASM3.bridge_toffoli_codegen_ccxC
#check QSpecBench.Quantum.OpenQASM3.toffoli_target_codegen_ops_eq_generated
#check QSpecBench.Quantum.OpenQASM3Parser.parseQasmSource_toffoli_target_kernel_eq_generated_ops
#check QSpecBench.Quantum.OpenQASM3Parser.bridge_toffoli_ccx_eq_target_decomposition
#check QSpecBench.Quantum.OpenQASM3.denotateOps3C_toffoli_target
#check QSpecBench.Quantum.ToffoliDecomposition.toffoli_source_denotes_ccx8C
#check QSpecBench.Quantum.ToffoliDecomposition.toffoli_gate_semantics_T_Tdg
#check QSpecBench.Quantum.ToffoliDecomposition.toffoli_cx_involutive_on_decomposition_wires
#check QSpecBench.Quantum.ToffoliDecomposition.toffoli_normalized_hadamard_involutive
#check QSpecBench.Quantum.ToffoliDecomposition.toffoli_normalized_source_target_exact
#check QSpecBench.Quantum.CliffordTAlg.toffoli_source_target_normalized_exact
#check QSpecBench.Quantum.CliffordTAlg.toffoli_target_matches_ccxA
