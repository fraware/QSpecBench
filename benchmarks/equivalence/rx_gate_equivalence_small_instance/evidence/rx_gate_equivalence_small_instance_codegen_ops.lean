/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def rx_gate_equivalence_small_instance_codegen_ops : List QasmOp := [.rx (Real.pi / 2) 0]
