/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'swap_from_three_cx' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.SwapFromThreeCx

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.cx 0 1, .cx 1 0, .cx 0 1]

end QSpecBench.Generated.SwapFromThreeCx
