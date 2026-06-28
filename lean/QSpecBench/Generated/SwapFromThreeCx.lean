/- QSpecBench bridge codegen: regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.SwapFromThreeCx

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.cx 0 1, .cx 1 0, .cx 0 1]

end QSpecBench.Generated.SwapFromThreeCx
