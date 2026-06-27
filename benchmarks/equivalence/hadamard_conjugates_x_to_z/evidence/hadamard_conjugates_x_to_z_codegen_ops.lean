/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def hadamard_conjugates_x_to_z_codegen_ops : List QasmOp := [.gate .H 0, .gate .X 0, .gate .H 0]
