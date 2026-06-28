/- QSpecBench bridge codegen: regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.BellStatePreparation

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .cx 0 1]

end QSpecBench.Generated.BellStatePreparation
