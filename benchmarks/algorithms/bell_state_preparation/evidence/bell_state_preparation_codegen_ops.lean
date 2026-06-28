/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'bell_state_preparation' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.BellStatePreparation

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .cx 0 1]

end QSpecBench.Generated.BellStatePreparation
