/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

open QSpecBench.Quantum.QasmOp

def circuit_identity_after_layout_codegen_ops : List QasmOp := [.gate .H 0, .cx 0 1]
