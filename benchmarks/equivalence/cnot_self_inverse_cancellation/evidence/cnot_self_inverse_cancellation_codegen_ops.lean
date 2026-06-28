/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'cnot_self_inverse_cancellation' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.CnotSelfInverse

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.cx 0 1, .cx 0 1]

end QSpecBench.Generated.CnotSelfInverse
