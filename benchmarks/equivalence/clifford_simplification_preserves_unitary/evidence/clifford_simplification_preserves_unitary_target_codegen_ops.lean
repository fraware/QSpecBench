/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

open QSpecBench.Quantum.QasmOp

def clifford_simplification_preserves_unitary_target_codegen_ops : List QasmOp := [.gate .S 0]
