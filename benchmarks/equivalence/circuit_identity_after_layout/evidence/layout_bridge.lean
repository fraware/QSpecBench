import QSpecBench.Quantum.OpenQASM3
import QSpecBench.Quantum.OpenQASM3Parser

/- QSpecBench evidence:
benchmark_id = "circuit_identity_after_layout"
obligation_id = "semantic_bridge"
theorem = "QSpecBench.Quantum.OpenQASM3.bridge_circuit_identity_after_layout_codegen"
artifact_sha256 = "ce49d4e871f80cc36e550cadd5559c84fb63af50a0cf3bf29a297d769ce723fa"
gate_trace_sha256 = "aadc7cef7d1187e3968ad43f4f624fcdcbdce440bc1a8bcbf4b7108c48cc811f"
-/

#check QSpecBench.Quantum.OpenQASM3.bridge_circuit_identity_after_layout_codegen
#check QSpecBench.Quantum.OpenQASM3Parser.parseQasmSource_layout_kernel_eq_generated_ops
