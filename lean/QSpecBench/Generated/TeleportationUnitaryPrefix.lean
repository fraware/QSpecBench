/- QSpecBench bridge codegen: regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.TeleportationUnitaryPrefix

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0]

end QSpecBench.Generated.TeleportationUnitaryPrefix
