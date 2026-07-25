/- QSpecBench bridge codegen: regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.CliffordSimplificationPreservesUnitary

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .gate .H 0, .gate .S 0]

end QSpecBench.Generated.CliffordSimplificationPreservesUnitary
