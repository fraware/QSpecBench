/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def single_qubit_gate_cancellation_codegen_ops : List QasmOp := [.gate .H 0, .gate .H 0]
