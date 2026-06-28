/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

open QSpecBench.Quantum.QasmOp

def rx_gate_equivalence_small_instance_codegen_ops : List QasmOp := [.rx (Real.pi / 2) 0]
