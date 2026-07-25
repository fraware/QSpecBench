/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'native_ccx_artifact_denotes_toffoli_unitary' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.ToffoliDecompositionEquivalence

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.ccx 0 1 2]

end QSpecBench.Generated.ToffoliDecompositionEquivalence
