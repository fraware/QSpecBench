/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def swap_from_three_cx_codegen_ops : List QasmOp := [.cx 0 1, .cx 1 0, .cx 0 1]
