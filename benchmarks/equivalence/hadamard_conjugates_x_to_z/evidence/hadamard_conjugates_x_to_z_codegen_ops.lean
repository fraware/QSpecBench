/- QSpecBench bridge codegen witness (hash must match package stub). -/
/- benchmark_id = 'hadamard_conjugates_x_to_z' -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.HadamardConjugatesXToZ

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .gate .X 0, .gate .H 0]

end QSpecBench.Generated.HadamardConjugatesXToZ
