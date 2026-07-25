/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'teleportation_preserves_state_up_to_pauli_correction' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.TeleportationUnitaryPrefix

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 1, .cx 1 2, .cx 0 1, .gate .H 0]

end QSpecBench.Generated.TeleportationUnitaryPrefix
