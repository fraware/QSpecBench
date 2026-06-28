/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def bell_state_preparation_codegen_ops : List QasmOp := [.gate .H 0, .cx 0 1]
