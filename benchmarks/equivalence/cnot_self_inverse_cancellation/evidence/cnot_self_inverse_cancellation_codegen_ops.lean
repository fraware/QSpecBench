/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def cnot_self_inverse_cancellation_codegen_ops : List QasmOp := [.cx 0 1, .cx 0 1]
