/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'circuit_identity_after_layout' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.CircuitIdentityAfterLayout

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .cx 0 1]

end QSpecBench.Generated.CircuitIdentityAfterLayout
