import QSpecBench.Pauli
import QSpecBench.Quantum.OpenQASM3

/- QSpecBench evidence:
benchmark_id = "single_qubit_gate_cancellation"
obligation_id = "semantic_bridge"
theorem = "QSpecBench.Quantum.OpenQASM3.bridge_hadamard_cancel"
artifact_sha256 = "90faff4ad649320098f82328250b15f2eaa595b44c7bb9f30afaf06cc5de8e22"
gate_trace_sha256 = "cbd175e0734480d649b0768d8698257ab120816947553c7f2b570a840dceab53"
-/

#check QSpecBench.Quantum.OpenQASM3.bridge_hadamard_cancel
