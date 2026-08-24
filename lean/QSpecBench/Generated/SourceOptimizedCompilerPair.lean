/- Generated from the compiler flagship artifacts; regenerate via compiler_pair_codegen. -/
import QSpecBench.Quantum.QasmOp

namespace QSpecBench.Generated.SourceOptimizedCompilerPair

open QSpecBench.Quantum.QasmOp

def benchmarkId : String := "source_optimized_qasm_equivalence_small_instance"
def compilerId : String := "qspecbench.reference_qasm_peephole.v1"
def compilerVersion : String := "1.0.0"
def sourceSha256 : String := "ef022773134724a54f86931c3e90bebd416e5a0e8ccd30367433d2f59ede40d9"
def targetSha256 : String := "b0b1111a0363f9d90a405a33fbe23352771e64a85909ebb91758f8d82ecf6e60"
def sourceArtifact : String := "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[1] q;\nh q[0];\nx q[0];\nx q[0];\n"
def targetArtifact : String := "OPENQASM 3.0;\ninclude \"stdgates.inc\";\nqubit[1] q;\nh q[0];\n"
def sourceOps : List QasmOp := [.gate .H 0, .gate .X 0, .gate .X 0]
def targetOps : List QasmOp := [.gate .H 0]
def transformationTrace : List String := ["cancel_x_pair:q[0]"]

end QSpecBench.Generated.SourceOptimizedCompilerPair
