/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'single_qubit_gate_cancellation' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.SingleQubitGateCancellation

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .gate .H 0]

end QSpecBench.Generated.SingleQubitGateCancellation
