/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'toffoli_decomposition_equivalence_target' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.ToffoliDecompositionEquivalenceTarget

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 2, .cx 1 2, .gate .Tdg 2, .cx 0 2, .gate .T 2, .cx 1 2, .gate .Tdg 2, .cx 0 2, .gate .T 2, .gate .T 1, .gate .H 2, .cx 0 1, .gate .T 0, .gate .Tdg 1, .cx 0 1]

end QSpecBench.Generated.ToffoliDecompositionEquivalenceTarget
