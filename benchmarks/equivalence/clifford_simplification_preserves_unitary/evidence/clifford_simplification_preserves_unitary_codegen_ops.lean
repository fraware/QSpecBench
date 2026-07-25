/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'clifford_simplification_preserves_unitary' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.CliffordSimplificationPreservesUnitary

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .gate .H 0, .gate .S 0]

end QSpecBench.Generated.CliffordSimplificationPreservesUnitary
