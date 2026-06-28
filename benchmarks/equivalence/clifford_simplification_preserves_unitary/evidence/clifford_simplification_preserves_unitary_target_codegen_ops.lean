/- QSpecBench bridge codegen (pilot): regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.OpenQASM3

open QSpecBench.Quantum.OpenQASM3

def clifford_simplification_preserves_unitary_target_codegen_ops : List QasmOp := [.gate .S 0]
