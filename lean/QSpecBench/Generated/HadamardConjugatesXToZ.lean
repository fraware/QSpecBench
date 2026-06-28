/- QSpecBench bridge codegen: regenerate via `qspecbench bridge-codegen generate`. -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.HadamardConjugatesXToZ

open QSpecBench.Quantum.QasmOp

def ops : List QasmOp := [.gate .H 0, .gate .X 0, .gate .H 0]

end QSpecBench.Generated.HadamardConjugatesXToZ
